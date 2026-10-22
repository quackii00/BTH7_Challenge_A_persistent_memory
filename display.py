def line(char="=", length=70):
    print(char * length)


def title(text):
    print()
    line("=")
    print(f"  {text}")
    line("=")


def section(name):
    print(f"\n[{name}]")


def user_prompt(text):
    section("USER")
    print(f"  {text}")


def injected_context(text):
    section("HARNESS: INJECTED MEMORY INTO CONTEXT")
    line("-", 70)
    for l in text.strip().splitlines():
        print(f"  {l}")
    line("-", 70)


def act(text):
    section("ACT")
    print(f"  {text}")


def observe(text):
    section("OBSERVE")
    print(f"  {text}")


def final_answer(text):
    section("FINAL ANSWER")
    for l in text.strip().splitlines():
        print(f"  {l}")


def proof_banner(proof_name, passed=True):
    print()
    line("*")
    status = "PASSED (ĐẠT)" if passed else "FAILED"
    print(f"  {proof_name}: {status}")
    line("*")
