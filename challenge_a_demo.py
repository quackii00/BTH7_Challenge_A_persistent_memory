import os
import sys
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware

from agent_tools import (
    harness,
    memory_store,
    save_convention_safe,
    read_topic_detail_safe
)
from display import (
    title,
    user_prompt,
    injected_context,
    act,
    observe,
    final_answer,
    proof_banner
)

load_dotenv()


def run_independent_session(session_id: str, session_title: str, user_request: str) -> str:
    """
    Khởi chạy một Session MỚI HOÀN TOÀN:
    - Lịch sử hội thoại (`messages`) trống rỗng, chỉ chứa duy nhất câu hỏi của session hiện tại.
    - Harness đọc Persistent Memory từ ổ đĩa (`MEMORY.md`) và inject vào System Prompt.
    - In ra phần Memory đã được inject vào Context để kiểm chứng.
    """
    title(f"{session_id.upper()} - {session_title}")

    # 1. Harness mở session mới & đọc memory từ ổ đĩa
    harness.start_new_session(session_id=session_id)
    injected_mem = harness.get_injected_memory_text()
    injected_context(injected_mem)

    user_prompt(user_request)

    # 2. Khởi tạo LLM và Agent mới cho session này
    model = ChatGroq(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        temperature=0
    )

    agent = create_agent(
        model=model,
        tools=[
            save_convention_safe,
            read_topic_detail_safe
        ],
        system_prompt=harness.build_system_prompt(),
        middleware=[
            ModelCallLimitMiddleware(
                run_limit=5,
                exit_behavior="end"
            )
        ]
    )

    # 3. Gọi Agent với lịch sử chỉ có đúng 1 message của phiên hiện tại
    result = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": user_request
            }
        ]
    })

    # 4. Hiển thị quá trình ACT / OBSERVE / FINAL ANSWER
    last_ai_text = ""
    for message in result["messages"]:
        if message.type == "ai":
            if getattr(message, "tool_calls", None):
                for tool_call in message.tool_calls:
                    act(f'{tool_call["name"]}({tool_call["args"]})')
            if message.content:
                last_ai_text = message.content
        elif message.type == "tool":
            observe(message.content)

    final_answer(last_ai_text)
    return last_ai_text


def run_session_1():
    memory_store.reset_all()
    run_independent_session(
        session_id="session_1",
        session_title="Thiết lập quy ước dự án ban đầu (Lưu vào Persistent Memory)",
        user_request=(
            "Chào bạn, chúng ta thống nhất quy ước dự án như sau nhé:\n"
            "1. Chủ đề 'stack': Sử dụng PostgreSQL, TypeScript và REST API chuẩn camelCase.\n"
            "2. Chủ đề 'auth': Authentication sử dụng JWT (JSON Web Token).\n"
            "Hãy lưu cả 2 quy ước này vào bộ nhớ dự án."
        )
    )


def run_session_2():
    ans_session_2 = run_independent_session(
        session_id="session_2",
        session_title="CHỨNG MINH 1: Mở Session mới hoàn toàn - Kiểm tra Agent nhớ quy ước cũ",
        user_request=(
            "Mình vừa mở một session mới. Hãy trả lời thật ngắn gọn (tối đa 4 dòng): "
            "Dự án của chúng ta đang dùng stack (database, ngôn ngữ, chuẩn API) gì và "
            "cơ chế authentication nào?"
        )
    )
    proof_1_ok = (
        "postgresql" in ans_session_2.lower()
        and "typescript" in ans_session_2.lower()
        and "jwt" in ans_session_2.lower()
    )
    proof_banner(
        "CHỨNG MINH 1 (Session mới vẫn dùng đúng quy ước PostgreSQL + TypeScript + JWT)",
        passed=proof_1_ok
    )


def run_session_3():
    run_independent_session(
        session_id="session_3",
        session_title="Thay đổi quy ước Authentication từ JWT sang Session Cookie",
        user_request=(
            "Cập nhật quy ước dự án cho chủ đề 'auth': "
            "Chuyển từ JWT sang sử dụng Session Cookie (HTTP-only) để tránh rủi ro XSS. "
            "Hãy cập nhật lại bộ nhớ dự án."
        )
    )


def run_session_4():
    ans_session_4 = run_independent_session(
        session_id="session_4",
        session_title="CHỨNG MINH 2: Mở Session mới sau khi đổi quy ước - Kiểm tra dùng quy ước mới",
        user_request=(
            "Mình đang ở session mới (Session 4). Hãy gọi tool kiểm tra chi tiết lịch sử quy ước 'auth' "
            "và trả lời thật ngắn gọn trong 3 gạch đầu dòng:\n"
            "1. Quy ước authentication HIỆN HÀNH của dự án là gì?\n"
            "2. Quy ước nào ĐÃ BỊ THAY THẾ (lưu từ session nào)?\n"
            "3. Khi viết API login bây giờ phải trả về gì cho client (1 dòng ngắn)?"
        )
    )
    proof_2_ok = "cookie" in ans_session_4.lower()
    proof_banner(
        "CHỨNG MINH 2 (Quy ước đổi thì các session sau dùng quy ước mới Session Cookie & đánh dấu JWT đã bị thay thế)",
        passed=proof_2_ok
    )


def main():
    if len(sys.argv) > 1:
        step = sys.argv[1].strip()
        if step == "1":
            run_session_1()
        elif step == "2":
            run_session_2()
        elif step == "3":
            run_session_3()
        elif step == "4":
            run_session_4()
        else:
            print("Sử dụng: python challenge_a_demo.py [1|2|3|4]")
        return

    run_session_1()
    run_session_2()
    run_session_3()
    run_session_4()


if __name__ == "__main__":
    main()
