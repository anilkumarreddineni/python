# Step 8: keep the history short.
# Step 7 sent every earlier message on every call, so the input tokens kept growing.
# Here we keep the full history for your records, but send only the most recent messages.

import os

import anthropic

model = os.environ.get("ANTHROPIC_MODEL") or "claude-opus-5-5"
client = anthropic.Anthropic()

SYSTEM_PROMPT = "You are a friendly tutor. Answer in at most three short sentences of plain text."

# How many of the latest messages to send. Older ones are not sent to Claude.
MAX_MESSAGES = 6


def trim(history: list) -> list:
    """Return the last MAX_MESSAGES messages, starting with a user message."""
    recent = history[-MAX_MESSAGES:]
    # The conversation must start with a user message, so drop a leading
    # assistant reply if the cut landed on one.
    while recent and recent[0]["role"] != "user":
        recent = recent[1:]
    return recent


history = []
print(f"Chatting with {model}. Type 'quit' to exit.")

while True:
    try:
        question = input("You: ").strip()
    except (EOFError, KeyboardInterrupt):
        break
    if question.lower() in {"quit", "exit"}:
        break
    if not question:
        continue

    history.append({"role": "user", "content": question})
    to_send = trim(history)
    try:
        response = client.messages.create(
            model=model,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            messages=to_send,
        )
    except anthropic.APIError as error:
        history.pop()  # forget the unanswered question so the history stays valid
        print(f"The call failed: {error}")
        continue

    history.append({"role": "assistant", "content": response.content})

    if response.stop_reason == "refusal":
        print("Claude: Sorry, I can't help with that.")
    else:
        print("Claude:", "".join(block.text for block in response.content if block.type == "text"))

    # Watch this number: it stays flat once the history is longer than MAX_MESSAGES
    print(f"[sent {len(to_send)} of {len(history)} messages, "
          f"input_tokens={response.usage.input_tokens}]")

print(f"Bye! The conversation had {len(history)} messages.")
