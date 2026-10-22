# Challenge A: Persistent Memory

## Mục tiêu
Agent nhớ được quy ước dự án qua nhiều session và tự động cập nhật khi quy ước thay đổi.

## Yêu cầu
- Kế thừa kiến trúc Agent đã có.
- **Chứng minh 1:** Session mới vẫn dùng đúng quy ước đã thống nhất.
- **Chứng minh 2:** Quy ước đổi thì các session sau dùng quy ước mới (đánh dấu quy ước cũ đã bị thay thế kèm nguồn và thời điểm).

## Hướng dẫn chạy Test

### 1. Cấu hình `.env`
```powershell
Copy-Item .env.example .env
```
*(Điền `GROQ_API_KEY` vào file `.env`)*

### 2. Chạy tự động toàn bộ kịch bản (4 Sessions)
```powershell
python .\challenge_a_demo.py
```

### 3. Chạy từng Session (Để quan sát memory thay đổi theo từng bước)
```powershell
python .\challenge_a_demo.py 1   # Session 1: Lưu quy ước ban đầu (PostgreSQL, TypeScript, JWT)
python .\challenge_a_demo.py 2   # Session 2: Chứng minh 1 - Session mới nhớ đúng quy ước cũ
python .\challenge_a_demo.py 3   # Session 3: Đổi quy ước auth từ JWT sang Session Cookie
python .\challenge_a_demo.py 4   # Session 4: Chứng minh 2 - Session mới dùng quy ước mới
```
