from ..utils.llm_backend import LLM
from ..utils.debug import debug_prompt, debug_response, debug_data
import numpy as np

import json
import os

class InterpreterAgent:
    def __init__(self, llm=None, icl_examples=None):
        self.llm = llm if llm is not None else LLM()
        self.icl = icl_examples if icl_examples is not None else self._load_default_icl()
    
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
        
        prompt = f"""You are an energy system analyst. Interpret the following optimization results:

{examples_text if examples_text else ""}Scenario: {modifications}
Optimization Status: {status}
Total Cost: EUR {objective:.2f}
{f"Baseline Cost: EUR {baseline_obj:.2f}" if baseline_obj is not None else ""}
{f"Cost Change: EUR {change:.2f} ({change_pct:+.1f}%)" if change is not None else ""}

PV Generation Profile: {data.get('PV', [])}
Load Profile: {data.get('Load', [])}
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
