from ..utils.llm_backend import LLM
from ..utils.debug import debug_prompt, debug_response, debug_data
import numpy as np

import json
import os
from pathlib import Path

class InterpreterAgent:
    def __init__(self, llm=None, icl_examples=None):
        self.llm = llm if llm is not None else LLM()
        self.icl = icl_examples if icl_examples is not None else self._load_default_icl()
        self._system_prompt = None
        self._user_template = None
        self._load_prompt_templates()
    
    def _load_default_icl(self):
        """Load default ICL examples for interpreter"""
        icl_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icl', 'interpreter_examples.jsonl')
        examples = []
        if os.path.exists(icl_path):
            try:
                with open(icl_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            examples.append(json.loads(line))
            except Exception:
                pass
        return examples
    
    def _load_prompt_templates(self):
        """Load prompt templates from files, with fallback to hardcoded prompts"""
        try:
            # Try to find prompts directory relative to project root
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent
            prompts_dir = project_root / 'prompts'
            
            system_prompt_path = prompts_dir / 'interpreter_system.txt'
            user_template_path = prompts_dir / 'interpreter_user_template.txt'
            
            if system_prompt_path.exists() and user_template_path.exists():
                self._system_prompt = system_prompt_path.read_text(encoding='utf-8').strip()
                self._user_template = user_template_path.read_text(encoding='utf-8').strip()
                debug_data("InterpreterAgent", "PROMPT TEMPLATES", "Loaded from template files")
            else:
                # Fallback to hardcoded prompts
                self._system_prompt = None
                self._user_template = None
                debug_data("InterpreterAgent", "PROMPT TEMPLATES", "Using hardcoded prompts (template files not found)")
        except Exception as e:
            # Fallback to hardcoded prompts on any error
            self._system_prompt = None
            self._user_template = None
            debug_data("InterpreterAgent", "PROMPT TEMPLATES ERROR", str(e))
    
    def _calculate_baseline(self):
        """Calculate baseline scenario for comparison"""
        from .optimizer_agent import OptimizerAgent
        opt = OptimizerAgent()
        debug_data("InterpreterAgent", "CALCULATING BASELINE", "Running baseline optimization...")
        baseline_data, baseline_res = opt.run({'ops': []}, solver='pulp')
        baseline_obj = baseline_res.get('objective', float('inf'))
        debug_data("InterpreterAgent", "BASELINE RESULT", {'objective': baseline_obj})
        return baseline_obj
    
    def _interpret_with_llm(self, data, result, ops):
        """Use LLM to generate human-readable interpretation"""
        status = result.get('status', 'unknown')
        objective = result.get('objective', 0)
        
        # Get baseline for comparison
        try:
            baseline_obj = self._calculate_baseline()
            change = objective - baseline_obj
            change_pct = (change / baseline_obj * 100) if baseline_obj > 0 else 0
        except:
            baseline_obj = None
            change = None
            change_pct = None
        
        # Build description of modifications
        mods_desc = []
        for op in ops.get('ops', []):
            if op['op'] == 'scale_series':
                target = op['target']
                pct = op['scale_pct']
                if target == 'PV':
                    mods_desc.append(f"PV generation increased by {pct}%")
                elif target == 'Load':
                    mods_desc.append(f"Load/consumption increased by {pct}%")
                elif target == 'Pimp':
                    mods_desc.append(f"Import capacity increased by {pct}%")
                elif target == 'Pexp':
                    mods_desc.append(f"Export capacity increased by {pct}%")
            elif op['op'] == 'shift_load':
                pct = op['percentage']
                from_h = op['from_hour']
                to_h = op['to_hour']
                mods_desc.append(f"{pct}% of load shifted from hour {from_h} to hour {to_h}")
        
        modifications = "; ".join(mods_desc) if mods_desc else "No modifications (baseline scenario)"
        
        # Build ICL examples section
        examples_text = ""
        if len(self.icl) > 0:
            for ex in self.icl[:3]:  # Use first 3 examples
                examples_text += f"Example:\n"
                examples_text += f"Scenario: {ex.get('scenario', '')}\n"
                examples_text += f"Status: {ex.get('status', '')}\n"
                examples_text += f"Objective: EUR {ex.get('objective', 0):.2f}\n"
                if ex.get('baseline'):
                    examples_text += f"Baseline: EUR {ex.get('baseline', 0):.2f}\n"
                examples_text += f"Interpretation: {ex.get('interpretation', '')}\n\n"
        
        # Prepare template variables
        baseline_info = f"Baseline Cost: EUR {baseline_obj:.2f}" if baseline_obj is not None else ""
        cost_change_info = f"Cost Change: EUR {change:.2f} ({change_pct:+.1f}%)" if change is not None else ""
        
        # Get data values (handle numpy arrays)
        pv_profile = data.get('PV', [])
        if isinstance(pv_profile, np.ndarray):
            pv_profile = pv_profile.tolist()
        
        load_profile = data.get('Load', [])
        if isinstance(load_profile, np.ndarray):
            load_profile = load_profile.tolist()
        
        # Use template files if available, otherwise use hardcoded prompt
        if self._system_prompt and self._user_template:
            # Load from template files
            # Format objective value for template
            objective_str = f"{objective:.2f}"
            user_prompt = self._user_template.format(
                examples_text=examples_text if examples_text else "",
                modifications=modifications,
                status=status,
                objective=objective_str,
                baseline_info=baseline_info,
                cost_change_info=cost_change_info,
                pv_profile=pv_profile,
                load_profile=load_profile,
                battery_capacity_kwh=data.get('battery_capacity_kwh', 0),
                price_import=data.get('price_import', 0),
                price_export=data.get('price_export', 0)
            )
            # Combine system and user prompts
            prompt = f"{self._system_prompt}\n\n{user_prompt}"
        else:
            # Fallback to hardcoded prompt
            prompt = f"""You are an energy system analyst. Interpret the following optimization results:

{examples_text if examples_text else ""}Scenario: {modifications}
Optimization Status: {status}
Total Cost: EUR {objective:.2f}
{baseline_info}
{cost_change_info}

PV Generation Profile: {pv_profile}
Load Profile: {load_profile}
Battery Capacity: {data.get('battery_capacity_kwh', 0)} kWh
Import Price: EUR {data.get('price_import', 0)}/kWh
Export Price: EUR {data.get('price_export', 0)}/kWh

Provide a clear, concise interpretation in 2-3 sentences explaining:
1. What the scenario change means
2. The impact on total energy costs
3. Key insights about the optimization result

Answer in plain language for a non-technical audience."""
        
        debug_prompt("InterpreterAgent", prompt)
        interpretation = self.llm.complete(prompt, temperature=0.3, max_tokens=300)
        debug_response("InterpreterAgent", interpretation)
        
        if interpretation and interpretation.strip():
            return interpretation.strip()
        else:
            # Fallback to rule-based if LLM fails
            return self._interpret_rule_based(data, result, ops, baseline_obj)
    
    def _interpret_rule_based(self, data, result, ops, baseline_obj=None):
        """Rule-based interpretation as fallback"""
        status = result.get('status', 'unknown')
        objective = result.get('objective', 0)
        
        if status != 'optimal':
            return f"The optimization could not find an optimal solution. Status: {status}"
        
        # Describe modifications
        mods_desc = []
        for op in ops.get('ops', []):
            if op['op'] == 'scale_series':
                target = op['target']
                pct = op['scale_pct']
                if target == 'PV':
                    mods_desc.append(f"PV generation increased by {pct}%")
                elif target == 'Load':
                    mods_desc.append(f"consumption increased by {pct}%")
                elif target == 'Pimp':
                    mods_desc.append(f"import capacity increased by {pct}%")
                elif target == 'Pexp':
                    mods_desc.append(f"export capacity increased by {pct}%")
            elif op['op'] == 'shift_load':
                pct = op['percentage']
                from_h = op['from_hour']
                to_h = op['to_hour']
                mods_desc.append(f"{pct}% of load shifted from hour {from_h} to hour {to_h}")
        
        modifications = "; ".join(mods_desc) if mods_desc else "baseline scenario"
        
        # Compare with baseline
        if baseline_obj is not None and baseline_obj != float('inf'):
            change = objective - baseline_obj
            change_pct = (change / baseline_obj * 100) if baseline_obj > 0 else 0
            
            if abs(change_pct) < 0.1:
                cost_impact = f"The total cost remains approximately the same (EUR {objective:.2f}), with only a minor change of {change_pct:+.1f}% compared to the baseline."
            elif change > 0:
                cost_impact = f"The total cost increases to EUR {objective:.2f}, which is {change_pct:+.1f}% higher than the baseline scenario (EUR {baseline_obj:.2f})."
            else:
                cost_impact = f"The total cost decreases to EUR {objective:.2f}, which is {abs(change_pct):.1f}% lower than the baseline scenario (EUR {baseline_obj:.2f})."
        else:
            cost_impact = f"The optimized total energy cost is EUR {objective:.2f}."
        
        return f"In the scenario where {modifications}, {cost_impact} The optimization found the most cost-effective way to manage energy storage, grid imports, and exports over the 24-hour period."
    
    def interpret(self, data, result, ops=None):
        """Interpret optimization results and return human-readable answer"""
        if ops is None:
            ops = {'ops': []}
        
        debug_data("InterpreterAgent", "ICL EXAMPLES", self.icl)
        debug_data("InterpreterAgent", "INPUT DATA", {
            'result': result,
            'ops': ops,
            'data_summary': {
                'PV': data.get('PV', []).tolist() if isinstance(data.get('PV'), np.ndarray) else data.get('PV', []),
                'Load': data.get('Load', []).tolist() if isinstance(data.get('Load'), np.ndarray) else data.get('Load', []),
                'battery_capacity_kwh': data.get('battery_capacity_kwh', 0),
                'price_import': data.get('price_import', 0),
                'price_export': data.get('price_export', 0)
            }
        })
        
        # Try LLM interpretation first if available
        if self.llm.client is not None:
            try:
                answer = self._interpret_with_llm(data, result, ops)
                debug_data("InterpreterAgent", "OUTPUT ANSWER (LLM)", answer)
                return answer
            except Exception as e:
                debug_data("InterpreterAgent", "LLM ERROR", str(e))
                # Fallback to rule-based if LLM fails
                pass
        
        # Calculate baseline for comparison
        try:
            baseline_obj = self._calculate_baseline()
        except:
            baseline_obj = None
        
        answer = self._interpret_rule_based(data, result, ops, baseline_obj)
        debug_data("InterpreterAgent", "OUTPUT ANSWER (rule-based)", answer)
        return answer
