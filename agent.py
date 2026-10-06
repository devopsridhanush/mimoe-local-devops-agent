import os
import sys

from dotenv import load_dotenv
from openai import OpenAI, APIConnectionError, APIStatusError


load_dotenv()

BASE_URL = os.getenv("MIMOE_BASE_URL")
API_KEY = os.getenv("MIMOE_API_KEY")
MODEL = os.getenv("MIMOE_MODEL")

if not BASE_URL or not API_KEY or not MODEL:
    print("Missing mimOE configuration.")
    print("Check MIMOE_BASE_URL, MIMOE_API_KEY and MIMOE_MODEL in .env")
    sys.exit(1)


client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)

SYSTEM_PROMPT = """
You are a local DevOps troubleshooting assistant.

Your job is to help engineers troubleshoot:
- Docker
- Kubernetes
- Linux
- CI/CD
- cloud infrastructure
- application deployment problems

Give concise and practical answers.
When suggesting commands, explain briefly what each command checks.
Do not claim that you executed a command.
Ask for additional information when there is not enough context.
""".strip()


messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT,
    }
]


def trim_history():
    """
    Keep the system prompt plus only the most recent conversation
    messages because the local model has a relatively small context.
    """
    global messages

    if len(messages) > 7:
        messages = [messages[0]] + messages[-6:]


def ask_agent(question: str) -> str:
    messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    trim_history()

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=False,
    )

    answer = response.choices[0].message.content or ""

    messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    trim_history()

    return answer


def health_check():
    print("\nChecking local mimOE inference...")

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": "Reply with only: OK",
                }
            ],
            stream=False,
        )

        if response.choices:
            print("mimOE status : Connected")
            print(f"Model        : {MODEL}")
            print(f"Endpoint     : {BASE_URL}")
            print("Inference    : Local")
        else:
            print("mimOE responded, but no completion was returned.")

    except Exception as exc:
        print("Health check failed.")
        print(f"Reason: {exc}")


def main():
    print("=" * 55)
    print(" mimOE Local DevOps Assistant")
    print("=" * 55)
    print(f"Model    : {MODEL}")
    print(f"Endpoint : {BASE_URL}")
    print()
    print("Commands:")
    print("  /health  Check local mimOE inference")
    print("  /clear   Clear conversation history")
    print("  /exit    Exit")
    print()

    global messages

    while True:
        try:
            question = input("You: ").strip()

            if not question:
                continue

            if question.lower() in {"/exit", "exit", "quit"}:
                print("Agent stopped.")
                break

            if question.lower() == "/health":
                health_check()
                print()
                continue

            if question.lower() == "/clear":
                messages = [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    }
                ]
                print("Conversation history cleared.\n")
                continue

            answer = ask_agent(question)

            print(f"\nAgent: {answer}\n")

        except KeyboardInterrupt:
            print("\nAgent stopped.")
            break

        except APIConnectionError:
            print("\nUnable to connect to mimOE.")
            print("Make sure:")
            print("1. mimOE Studio is running.")
            print("2. The local runtime is connected.")
            print("3. smollm-360m is loaded.")
            print("4. The endpoint in .env matches Studio.\n")

        except APIStatusError as exc:
            print(f"\nmimOE returned HTTP {exc.status_code}.")
            print(f"{exc.message}\n")

        except Exception as exc:
            print(f"\nUnexpected error: {exc}\n")


if __name__ == "__main__":
    main()
