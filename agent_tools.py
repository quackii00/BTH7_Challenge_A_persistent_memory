from pathlib import Path
from langchain_core.tools import tool

from harness import Harness
from memory_store import MemoryStore


BASE_DIR = Path(__file__).resolve().parent
memory_store = MemoryStore(base_dir=str(BASE_DIR))
harness = Harness(memory_store=memory_store, session_id="session_1")


@tool
def save_convention_safe(topic: str, rule: str, reason: str = "Thống nhất quy ước dự án"):
    """
    Lưu mới hoặc cập nhật một quy ước của dự án vào Persistent Memory thông qua Harness.
    - topic: Tên chủ đề ngắn gọn (ví dụ: 'stack', 'auth', 'api').
    - rule: Nội dung quy ước hiện hành (ví dụ: 'PostgreSQL, TypeScript', 'Sử dụng JWT', 'Sử dụng Session Cookie').
    - reason: Lý do chọn hoặc lý do thay đổi quy ước.
    """
    return harness.save_convention(topic=topic, rule=rule, reason=reason)


@tool
def read_topic_detail_safe(topic: str):
    """
    Đọc chi tiết quy ước hiện hành và lịch sử các quy ước đã bị thay thế của một chủ đề
    từ file `memory/<topic>.md` thông qua Harness.
    - topic: Tên chủ đề cần tra cứu (ví dụ: 'stack', 'auth').
    """
    return harness.read_topic_detail(topic=topic)
