"""check_candidates.py — valida disponibilidade dos modelos candidatos.
Roda 1 chamada de teste em cada candidato declarado em config/candidates.yaml.
Modelo que falhar precisa ser substituído antes da Fase 5.
"""
import os
import sys
import time

import yaml
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

PROBE = "Em uma frase, o que é fração equivalente?"


def make_client(provider: str) -> OpenAI:
    if provider == "groq":
        return OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.environ["GROQ_API_KEY"],
        )
    if provider == "openrouter":
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"],
        )
    raise ValueError(f"Provider desconhecido: {provider}")


def probe(cand: dict) -> dict:
    client = make_client(cand["provider"])
    t0 = time.time()
    try:
        r = client.chat.completions.create(
            model=cand["model_id"],
            messages=[{"role": "user", "content": PROBE}],
            max_tokens=120,
        )
        dt = time.time() - t0
        return {
            "name": cand["name"],
            "ok": True,
            "latency_s": round(dt, 2),
            "tokens": r.usage.total_tokens,
            "sample": r.choices[0].message.content[:120].replace("\n", " "),
        }
    except Exception as exc:
        return {
            "name": cand["name"],
            "ok": False,
            "latency_s": round(time.time() - t0, 2),
            "error": str(exc),
        }


if __name__ == "__main__":
    cfg = yaml.safe_load(open("config/candidates.yaml"))
    print("\n[ aula04 · check candidates ]\n")
    all_ok = True
    for cand in cfg["candidates"]:
        result = probe(cand)
        status = "OK " if result["ok"] else "FAIL"
        if result["ok"]:
            print(
                f"  [{status}] {result['name']:20s} · {result['latency_s']:>5.2f}s · "
                f"{result['tokens']:>4} tok · {result['sample']!r}"
            )
        else:
            print(f"  [{status}] {result['name']:20s} · ERRO: {result['error']}")
            all_ok = False
    print()
    if all_ok:
        print("Todos os candidatos respondem. Avance para Fase 4 (harness).\n")
        sys.exit(0)
    else:
        print("Substitua os candidatos que falharam em config/candidates.yaml.\n")
        sys.exit(1)
