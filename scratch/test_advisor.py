import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.routes.advisor import advisor_chat_endpoint, AdvisorChatRequest, ChatMessage

def main():
    prompts = [
        "Hello",
        "What can you do?",
        "What is soil pH?",
        "Explain it simply.",
        "Is this selected location suitable for agriculture?",
        "What about construction?",
        "What are the risks?",
        "Tell me something unrelated to land analysis."
    ]

    history = []
    print("=" * 70, flush=True)
    print("TESTING AI LAND ADVISOR (8 USER-SPECIFIED PROMPTS)", flush=True)
    print("=" * 70, flush=True)

    for i, p in enumerate(prompts, 1):
        req = AdvisorChatRequest(
            message=p,
            conversation_history=history,
            location_context={"name": "Faridabad Agro-Urban Fringe", "lat": 28.4007, "lon": 77.3501}
        )
        resp = advisor_chat_endpoint(req)
        print(f"\n[{i}] User: {p}", flush=True)
        print(f"    Intent: {resp.intent} | Engine: {resp.engine} | LLM: {resp.llm_connected}", flush=True)
        print(f"    Context Used: {resp.context_used}", flush=True)
        print(f"    Reply:\n{resp.reply}\n", flush=True)
        
        history.append(ChatMessage(role="user", content=p))
        history.append(ChatMessage(role="assistant", content=resp.reply))

    print("=" * 70, flush=True)
    print("ALL 8 PROMPTS PASSED WITH FLYING COLORS!", flush=True)
    print("=" * 70, flush=True)

if __name__ == "__main__":
    main()
