import json
import shutil
from datetime import datetime
from pathlib import Path


class MemoryStore:
    """
    Quản lý bộ nhớ bền vững (Persistent Memory) trên ổ đĩa:
    - Lưu trữ dữ liệu có cấu trúc trong `memory_store.json`
    - Tự động đồng bộ ra hệ thống file Markdown:
      + `MEMORY.md`: Index ngắn chứa các quy ước hiện hành (nạp vào Context đầu mỗi session)
      + `memory/<topic>.md`: File chi tiết từng chủ đề (chứa cả quy ước hiện hành
        và lịch sử các quy ước cũ đã bị thay thế kèm nguồn + thời điểm)
    """

    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.json_path = self.base_dir / "memory_store.json"
        self.index_md_path = self.base_dir / "MEMORY.md"
        self.topic_dir = self.base_dir / "memory"
        self.topic_dir.mkdir(parents=True, exist_ok=True)

    def reset_all(self):
        """Xóa sạch memory cũ trên ổ đĩa để bắt đầu chạy kịch bản từ đầu."""
        if self.json_path.exists():
            self.json_path.unlink()
        if self.index_md_path.exists():
            self.index_md_path.unlink()
        if self.topic_dir.exists():
            shutil.rmtree(self.topic_dir)
        self.topic_dir.mkdir(parents=True, exist_ok=True)

    def _load_data(self) -> dict:
        if not self.json_path.exists():
            return {"conventions": {}}
        with open(self.json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_data(self, data: dict):
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self._sync_markdown_files(data)

    def _sync_markdown_files(self, data: dict):
        """
        Đồng bộ dữ liệu ra `MEMORY.md` (Index ngắn) và `memory/<topic>.md` (Chi tiết).
        """
        conventions = data.get("conventions", {})

        # 1. Ghi file MEMORY.md (Index ngắn)
        index_lines = [
            "# PROJECT MEMORY INDEX (MEMORY.md)",
            "> Index ngắn chứa quy ước HIỆN HÀNH của dự án. Chi tiết lịch sử xem tại `memory/<topic>.md`.",
            ""
        ]

        if not conventions:
            index_lines.append("*(Chưa có quy ước dự án nào được lưu)*")
        else:
            for topic, item in conventions.items():
                active_rule = item["active_rule"]
                updated_at = item["updated_at"]
                source_session = item["source_session"]
                superseded_count = len(item.get("superseded_history", []))
                history_note = (
                    f" *(đã thay thế {superseded_count} quy ước cũ - xem `memory/{topic}.md`)*"
                    if superseded_count > 0 else ""
                )
                index_lines.append(
                    f"- **{topic}**: {active_rule} "
                    f"(Nguồn: `{source_session}`, Cập nhật: `{updated_at}`){history_note}"
                )

        with open(self.index_md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(index_lines) + "\n")

        # 2. Ghi từng file chi tiết `memory/<topic>.md`
        for topic, item in conventions.items():
            topic_file = self.topic_dir / f"{topic}.md"
            t_lines = [
                f"# Quy ước chủ đề: `{topic}`",
                "",
                "## 1. Quy định HIỆN HÀNH (Active Convention)",
                f"- **Nội dung**: {item['active_rule']}",
                f"- **Lý do / Ghi chú**: {item.get('reason', 'Thống nhất trong dự án')}",
                f"- **Nguồn (Session)**: `{item['source_session']}`",
                f"- **Thời điểm áp dụng**: `{item['updated_at']}`",
                ""
            ]

            history = item.get("superseded_history", [])
            t_lines.append("## 2. Lịch sử quy định ĐÃ BỊ THAY THẾ (Superseded / Deprecated)")
            if not history:
                t_lines.append("*(Chưa có quy định cũ nào bị thay thế)*")
            else:
                for idx, old in enumerate(history, start=1):
                    t_lines.append(
                        f"- **[ĐÃ BỊ THAY THẾ #{idx}]** `{old['rule']}`\n"
                        f"  + Nguồn ban đầu: `{old['source_session']}` (lúc `{old['created_at']}`)\n"
                        f"  + Đã bị thay thế bởi: `{old['superseded_by_session']}` lúc `{old['superseded_at']}`\n"
                        f"  + Lý do thay thế: {old.get('superseded_reason', 'Cập nhật quy ước mới')}"
                    )

            with open(topic_file, "w", encoding="utf-8") as f:
                f.write("\n".join(t_lines) + "\n")

    def upsert_convention(
        self,
        topic: str,
        rule: str,
        reason: str,
        session_id: str
    ) -> dict:
        """
        Ghi mới hoặc cập nhật quy ước dự án:
        - Nếu chủ đề `topic` chưa tồn tại -> tạo mới.
        - Nếu chủ đề `topic` đã tồn tại với quy ước khác -> Đánh dấu quy ước cũ
          là ĐÃ BỊ THAY THẾ (lưu nguồn và thời điểm), rồi đặt quy ước mới làm HIỆN HÀNH.
        """
        topic_key = topic.strip().lower().replace(" ", "_")
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data = self._load_data()
        conventions = data.setdefault("conventions", {})

        if topic_key not in conventions:
            conventions[topic_key] = {
                "topic": topic_key,
                "active_rule": rule,
                "reason": reason,
                "source_session": session_id,
                "updated_at": now_str,
                "superseded_history": []
            }
            action_type = "created"
            old_rule = None
        else:
            current = conventions[topic_key]
            old_rule = current["active_rule"]

            if old_rule.strip().lower() == rule.strip().lower():
                current["updated_at"] = now_str
                current["reason"] = reason
                action_type = "unchanged"
            else:
                superseded_entry = {
                    "rule": old_rule,
                    "source_session": current["source_session"],
                    "created_at": current["updated_at"],
                    "superseded_at": now_str,
                    "superseded_by_session": session_id,
                    "superseded_reason": reason
                }
                current.setdefault("superseded_history", []).append(superseded_entry)

                current["active_rule"] = rule
                current["reason"] = reason
                current["source_session"] = session_id
                current["updated_at"] = now_str
                action_type = "updated_and_superseded_old"

        self._save_data(data)

        return {
            "status": "ok",
            "action": action_type,
            "topic": topic_key,
            "active_rule": rule,
            "superseded_old_rule": old_rule if action_type == "updated_and_superseded_old" else None,
            "updated_at": now_str,
            "source_session": session_id,
            "files_updated": ["MEMORY.md", f"memory/{topic_key}.md", "memory_store.json"]
        }

    def read_index_markdown(self) -> str:
        """Đọc file Index ngắn `MEMORY.md` để inject vào Context đầu mỗi session."""
        if not self.index_md_path.exists():
            return "# PROJECT MEMORY INDEX (MEMORY.md)\n*(Chưa có quy ước dự án nào được lưu trên ổ đĩa)*"
        with open(self.index_md_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def read_topic_markdown(self, topic: str) -> dict:
        """Đọc file chi tiết `memory/<topic>.md` khi Agent cần tra cứu lịch sử."""
        topic_key = topic.strip().lower().replace(" ", "_")
        topic_file = self.topic_dir / f"{topic_key}.md"
        if not topic_file.exists():
            return {
                "status": "not_found",
                "topic": topic_key,
                "message": f"Chưa có file memory/{topic_key}.md"
            }
        with open(topic_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
        return {
            "status": "ok",
            "topic": topic_key,
            "file": f"memory/{topic_key}.md",
            "content": content
        }
