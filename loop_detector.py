from collections import deque


class LoopDetector:

    def __init__(self, repeat_k: int = 3):
        self.history = deque(maxlen=repeat_k)
        self.repeat_k = repeat_k

    def record(self, tool_name: str, args: dict) -> bool:
        action = (
            tool_name,
            tuple(sorted(args.items()))
        )

        self.history.append(action)

        # Kiểm tra action cuối có lặp repeat_k lần liên tiếp không
        if len(self.history) < self.repeat_k:
            return False

        return len(set(self.history)) == 1
