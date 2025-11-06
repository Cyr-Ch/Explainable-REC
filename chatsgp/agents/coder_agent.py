import json
import re
from pathlib import Path
from ..utils.debug import debug_prompt, debug_response, debug_data
from ..utils.validation import validate_question, validate_operations

class CoderAgent:
    def __init__(self, icl_examples, llm=None):
        self.icl = icl_examples
        self.llm = llm
        self._system_prompt = None
        self._user_template = None
        self._load_prompt_templates()
    
    def _rule_based_parse(self, q):
        """Fallback rule-based parsing for when LLM is not available"""
        q = q.lower()
        def pct():
            m = re.search(r'(-?\d+(?:\.\d+)?)\s*%', q)
            return float(m.group(1)) if m else None
        
        p = pct()
        ops = []
        
        if 'import' in q and p is not None:
            ops.append({'op': 'scale_series', 'target': 'Pimp', 'scale_pct': p})
        elif 'export' in q and p is not None:
            ops.append({'op': 'scale_series', 'target': 'Pexp', 'scale_pct': p})
        elif 'pv' in q and p is not None:
            ops.append({'op': 'scale_series', 'target': 'PV', 'scale_pct': p})
        elif 'shift' in q and p is not None:
            hh = re.findall(r'(?:from|at)\s+(\d{1,2}).*?(?:to)\s+(\d{1,2})', q)
            a, b = (13, 14) if not hh else (int(hh[0][0]), int(hh[0][1]))
            ops.append({'op': 'shift_load', 'percentage': p, 'from_hour': a, 'to_hour': b})
        
        return {'ops': ops, 'explanation': 'rule-based'}
    
    def _load_prompt_templates(self):
        """Load prompt templates from files, with fallback to hardcoded prompts"""
        try:
            # Try to find prompts directory relative to project root
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent
            prompts_dir = project_root / 'prompts'
            
            system_prompt_path = prompts_dir / 'coder_system.txt'
            user_template_path = prompts_dir / 'coder_user_template.txt'
            
            if system_prompt_path.exists() and user_template_path.exists():
                self._system_prompt = system_prompt_path.read_text(encoding='utf-8').strip()
                self._user_template = user_template_path.read_text(encoding='utf-8').strip()
                debug_data("CoderAgent", "PROMPT TEMPLATES", "Loaded from template files")
            else:
                # Fallback to hardcoded prompts
                self._system_prompt = None
                self._user_template = None
                debug_data("CoderAgent", "PROMPT TEMPLATES", "Using hardcoded prompts (template files not found)")
        except Exception as e:
            # Fallback to hardcoded prompts on any error
            self._system_prompt = None
            self._user_template = None
            debug_data("CoderAgent", "PROMPT TEMPLATES ERROR", str(e))
    
    def _build_icl_prompt(self, question):
        """Build a prompt with ICL examples for few-shot learning"""
        examples_text = ""
        for ex in self.icl[:3]:  # Use first 3 examples
            examples_text += f"Question: {ex.get('question', '')}\n"
            examples_text += f"Modifications: {json.dumps(ex.get('ops', []))}\n\n"
        
        # Use template files if available, otherwise use hardcoded prompt
        if self._system_prompt and self._user_template:
            # Load from template files
            user_prompt = self._user_template.format(
                examples_text=examples_text,
                question=question
            )
            # Combine system and user prompts
            prompt = f"{self._system_prompt}\n\n{user_prompt}"
        else:
            # Fallback to hardcoded prompt
            prompt = f"""You are an energy system analyst. Given a natural language question about energy scenarios, extract the modifications needed for the optimization model.

Available operations:
1. scale_series: Scale a series (PV, Load, Pimp, Pexp) by a percentage
   Format: {{"op": "scale_series", "target": "PV|Load|Pimp|Pexp", "scale_pct": number}}
2. shift_load: Shift load from one hour to another
   Format: {{"op": "shift_load", "percentage": number, "from_hour": number, "to_hour": number}}

Examples:
{examples_text}

Question: {question}

Extract the modifications as a JSON array of operations. Return only the JSON array, no other text.

Example output format:
[{{"op": "scale_series", "target": "PV", "scale_pct": 20}}]"""
        
        return prompt
    
    def propose_modifications(self, q):
        """
        Propose modifications using LLM with ICL if available, otherwise rule-based
        
        Args:
            q: Question string
        
        Returns:
            Dictionary with 'ops' (list of operations) and 'explanation' (method used)
        
        Raises:
            ValueError: If question is invalid
        """
        # Validate input
        is_valid, error_msg = validate_question(q)
        if not is_valid:
            raise ValueError(f"Invalid question: {error_msg}")
        
        debug_data("CoderAgent", "INPUT QUESTION", q)
        debug_data("CoderAgent", "ICL EXAMPLES", self.icl)
        
        # Check if LLM is available
        if self.llm and self.llm.client is not None:
            debug_data("CoderAgent", "LLM STATUS", "LLM client is available - will attempt LLM-based parsing")
        else:
            debug_data("CoderAgent", "LLM STATUS", f"LLM client is NOT available (no API key?) - falling back to rule-based parsing")
        
        # Try LLM-based parsing if LLM is available and ICL examples exist
        if self.llm and self.llm.client is not None and len(self.icl) > 0:
            try:
                prompt = self._build_icl_prompt(q)
                debug_prompt("CoderAgent", prompt)
                
                response = self.llm.complete(prompt, temperature=0.0, max_tokens=300)
                debug_response("CoderAgent", response)
                
                # Try to extract JSON array from response
                json_match = re.search(r'\[.*?\]', response, re.DOTALL)
                if json_match:
                    ops_json = json_match.group(0)
                    ops = json.loads(ops_json)
                    # Validate operations structure
                    if isinstance(ops, list) and len(ops) > 0:
                        # Validate each operation has required fields
                        valid_ops = []
                        for op in ops:
                            if op.get('op') == 'scale_series' and 'target' in op and 'scale_pct' in op:
                                valid_ops.append(op)
                            elif op.get('op') == 'shift_load' and 'percentage' in op and 'from_hour' in op and 'to_hour' in op:
                                valid_ops.append(op)
                        
                        if valid_ops:
                            # Validate operations
                            is_valid, error_msg = validate_operations(valid_ops)
                            if not is_valid:
                                debug_data("CoderAgent", "LLM VALIDATION ERROR", error_msg)
                                # Fall through to rule-based
                            else:
                                result = {'ops': valid_ops, 'explanation': 'llm-with-icl'}
                                debug_data("CoderAgent", "OUTPUT OPERATIONS", result)
                                return result
            except Exception as e:
                debug_data("CoderAgent", "LLM ERROR", str(e))
                # Fallback to rule-based if LLM fails
                pass
        
        # Fallback to rule-based parsing
        result = self._rule_based_parse(q)
        debug_data("CoderAgent", "OUTPUT OPERATIONS (rule-based)", result)
        return result
