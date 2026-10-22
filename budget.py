class StepBudget:

    def __init__(self, max_steps: int = 8):
        self.max_steps = max_steps
        self.steps = 0

    def consume(self) -> bool:
        """
        Tăng số step.
        Trả về True nếu vẫn còn budget.
        Trả về False nếu đã hết budget.
        """
        if self.steps >= self.max_steps:
            return False

        self.steps += 1
        return True

    def exhausted(self) -> bool:
        return self.steps >= self.max_steps
