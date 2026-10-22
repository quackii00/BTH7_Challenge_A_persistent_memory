from budget import StepBudget
from loop_detector import LoopDetector
from memory_store import MemoryStore


class Harness:
    """
    Agent Harness:
    - Quản lý StepBudget và LoopDetector
    - Quản lý MemoryStore (Persistent Memory trên ổ đĩa)
    - Quyết định lưu thông tin nào, truy xuất thông tin nào và inject lại gì vào Context
      của mỗi Session mới.
    """

    def __init__(
        self,
        memory_store: MemoryStore,
        session_id: str = "session_1",
        max_steps: int = 8
    ):
        self.memory_store = memory_store
        self.session_id = session_id
        self.max_steps = max_steps
        self.loop_detector = LoopDetector(repeat_k=3)
        self.budget = StepBudget(max_steps=max_steps)

    def start_new_session(self, session_id: str):
        """
        Chuyển sang một Session mới:
        - Reset lại StepBudget và LoopDetector của phiên
        - Giữ nguyên MemoryStore trên ổ đĩa
        """
        self.session_id = session_id
        self.loop_detector = LoopDetector(repeat_k=3)
        self.budget = StepBudget(max_steps=self.max_steps)

    def get_injected_memory_text(self) -> str:
        """
        Đọc Index ngắn `MEMORY.md` từ ổ đĩa.
        """
        return self.memory_store.read_index_markdown()

    def build_system_prompt(self) -> str:
        """
        Đưa phần Persistent Memory từ ổ đĩa vào System Prompt của Session hiện tại.
        """
        injected_memory = self.get_injected_memory_text()

        return (
            f"Bạn là trợ lý phát triển phần mềm cho dự án (Đang ở phiên làm việc: {self.session_id}).\n\n"
            "=== PERSISTENT MEMORY ĐƯỢC HARNESS INJECT TỪ Ổ ĐĨA ===\n"
            f"{injected_memory}\n"
            "======================================================\n\n"
            "Quy tắc bắt buộc:\n"
            "1. Khi người dùng đưa ra quy ước dự án mới (ví dụ: database, ngôn ngữ, framework, "
            "cơ chế authentication, quy ước API) HOẶC yêu cầu thay đổi quy ước cũ, bạn PHẢI gọi tool "
            "`save_convention_safe` cho từng chủ đề (`stack`, `auth`, `api`, v.v.) để lưu bền vững xuống ổ đĩa.\n"
            "2. Khi người dùng hỏi hoặc yêu cầu viết code theo quy ước dự án ở một session mới, "
            "hãy dựa vào phần PERSISTENT MEMORY đã được inject ở trên (hoặc gọi `read_topic_detail_safe` "
            "nếu cần xem lịch sử các quy ước cũ đã bị thay thế).\n"
            "3. Luôn ưu tiên tuân thủ quy ước HIỆN HÀNH (Active), tuyệt đối không dùng lại quy ước cũ "
            "đã bị thay thế (Superseded).\n"
            "4. Trả lời cực kỳ ngắn gọn (tối đa 4-5 dòng gạch đầu dòng), đi thẳng vào trọng tâm bằng tiếng Việt."
        )

    def save_convention(self, topic: str, rule: str, reason: str) -> dict:
        """
        Harness kiểm soát việc ghi/cập nhật quy ước vào Persistent Memory.
        """
        if not self.budget.consume():
            return {
                "status": "stopped",
                "reason": "budget_exhausted"
            }

        is_loop = self.loop_detector.record(
            "save_convention",
            {"topic": topic, "rule": rule}
        )
        if is_loop:
            return {
                "status": "stopped",
                "reason": "loop_detected"
            }

        return self.memory_store.upsert_convention(
            topic=topic,
            rule=rule,
            reason=reason,
            session_id=self.session_id
        )

    def read_topic_detail(self, topic: str) -> dict:
        """
        Harness kiểm soát việc đọc chi tiết file chủ đề `memory/<topic>.md`.
        """
        if not self.budget.consume():
            return {
                "status": "stopped",
                "reason": "budget_exhausted"
            }

        is_loop = self.loop_detector.record(
            "read_topic_detail",
            {"topic": topic}
        )
        if is_loop:
            return {
                "status": "stopped",
                "reason": "loop_detected"
            }

        return self.memory_store.read_topic_markdown(topic=topic)
