# Quy ước chủ đề: `auth`

## 1. Quy định HIỆN HÀNH (Active Convention)
- **Nội dung**: Sử dụng Session Cookie (HTTP-only)
- **Lý do / Ghi chú**: Chuyển từ JWT sang Session Cookie để tránh rủi ro XSS
- **Nguồn (Session)**: `session_3`
- **Thời điểm áp dụng**: `2026-10-22 22:06:47`

## 2. Lịch sử quy định ĐÃ BỊ THAY THẾ (Superseded / Deprecated)
- **[ĐÃ BỊ THAY THẾ #1]** `Authentication sử dụng JWT (JSON Web Token)`
  + Nguồn ban đầu: `session_1` (lúc `2026-10-22 22:06:43`)
  + Đã bị thay thế bởi: `session_3` lúc `2026-10-22 22:06:47`
  + Lý do thay thế: Chuyển từ JWT sang Session Cookie để tránh rủi ro XSS
