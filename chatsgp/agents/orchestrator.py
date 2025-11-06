from .coder_agent import CoderAgent
from .optimizer_agent import OptimizerAgent
from .interpreter_agent import InterpreterAgent
from ..utils.validation import validate_question, validate_optimization_result

class Orchestrator:
    def __init__(self, coder, optimizer, interpreter):
        self.coder = coder
        self.optimizer = optimizer
        self.interpreter = interpreter
    
    def run_question(self, q, solver='pulp'):
        """
        Run the full pipeline for a question
        
        Args:
            q: Question string
            solver: Solver to use ('pulp' or 'gurobi')
        
        Returns:
            Dictionary with 'ops', 'result', and 'answer'
        
        Raises:
            ValueError: If question is invalid
            RuntimeError: If optimization fails
        """
        # Validate question
        is_valid, error_msg = validate_question(q)
        if not is_valid:
            raise ValueError(f"Invalid question: {error_msg}")
        
        try:
            ops = self.coder.propose_modifications(q)
            data, res = self.optimizer.run(ops, solver=solver)
            
            # Validate optimization result
            is_valid, error_msg = validate_optimization_result(res)
            if not is_valid:
                raise RuntimeError(f"Invalid optimization result: {error_msg}")
            
            ans = self.interpreter.interpret(data, res, ops)
            return {'ops': ops, 'result': res, 'answer': ans}
        except Exception as e:
            # Provide helpful error message
            error_msg = f"Pipeline failed: {str(e)}"
            if "Invalid question" in str(e):
                error_msg += "\nTip: Make sure your question includes a percentage and a valid keyword (import, export, PV, shift)."
            elif "Optimization error" in str(e):
                error_msg += "\nTip: Check if the scenario is feasible. Try adjusting the parameters."
            raise RuntimeError(error_msg) from e
