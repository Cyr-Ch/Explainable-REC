class InterpreterAgent:
    def interpret(self, data, result):
        s=result.get('status');
        if s=='optimal': return f"Objective: €{result['objective']:.2f}"
        return f"Status: {s}"
