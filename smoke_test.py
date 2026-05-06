"""smoke_test.py — valida que as 3 APIs respondem.
Rode antes de qualquer outra coisa. Se algum 'OK' não aparecer, pare e debugue.
"""
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def test_groq() -> bool:
    """Inferência dos candidatos."""
    try:
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.environ["GROQ_API_KEY"],
        )
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Diga apenas: pong"}],
            max_tokens=10,
        )
        print(f"  [GROQ]       OK · resposta: {r.choices[0].message.content!r}")
        return True
    except Exception as exc:
        print(f"  [GROQ]       FALHOU · {exc}")
        return False


def test_openrouter() -> bool:
    """Juiz LLM."""
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"],
        )
        r = client.chat.completions.create(
            model="anthropic/claude-3.5-haiku",
            messages=[{"role": "user", "content": "Diga apenas: pong"}],
            max_tokens=10,
        )
        print(f"  [OPENROUTER] OK · resposta: {r.choices[0].message.content!r}")
        return True
    except Exception as exc:
        print(f"  [OPENROUTER] FALHOU · {exc}")
        return False


def test_langfuse() -> bool:
    """Observabilidade."""
    try:
        from langfuse import Langfuse

        lf = Langfuse(
            public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
            secret_key=os.environ["LANGFUSE_SECRET_KEY"],
            host=os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        )
        lf.create_event(name="aula04-smoke-test", metadata={"ok": True})
        lf.flush()
        print("  [LANGFUSE]   OK · evento enviado")
        return True
    except Exception as exc:
        print(f"  [LANGFUSE]   FALHOU · {exc}")
        return False


if __name__ == "__main__":
    print("\n[ aula04-eval-harness · smoke test ]\n")
    results = [test_groq(), test_openrouter(), test_langfuse()]
    print()
    if all(results):
        print("Tudo verde. Avance para check_candidates.py.\n")
        sys.exit(0)
    else:
        print("Pelo menos um teste falhou. Revise .env e cotas antes de continuar.\n")
        sys.exit(1)
