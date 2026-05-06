"""run_eval.py — Harness principal de avaliação.

Roda cada prompt do golden dataset contra cada candidato, avalia com juiz LLM,
salva traces no Langfuse e CSV em results/run_v1.csv.

Uso:
  python run_eval.py
  python run_eval.py --product educiacao --run-tag run_v1
  python run_eval.py --product designmind --max-prompts 3   # debug rápido
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import pandas as pd
import yaml
from dotenv import load_dotenv
from openai import OpenAI

from judge_prompt import build_judge_prompt, parse_judge_output, weighted_score

load_dotenv()

ROOT = Path(__file__).parent
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def make_groq() -> OpenAI:
    return OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.environ["GROQ_API_KEY"],
    )


def make_openrouter() -> OpenAI:
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )


def make_langfuse():
    try:
        from langfuse import Langfuse

        return Langfuse(
            public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
            secret_key=os.environ["LANGFUSE_SECRET_KEY"],
            host=os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        )
    except Exception as exc:
        print(f"  [WARN] Langfuse desabilitado: {exc}")
        return None


def run_candidate(
    client: OpenAI,
    model_id: str,
    prompt: str,
    max_tokens: int = 1200,
    retries: int = 2,
) -> dict:
    """Chama um candidato com retry exponencial. Retorna output, tokens, latência."""
    last_exc = None
    for attempt in range(retries + 1):
        try:
            t0 = time.time()
            r = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.3,
            )
            return {
                "output": r.choices[0].message.content,
                "input_tokens": r.usage.prompt_tokens,
                "output_tokens": r.usage.completion_tokens,
                "latency_s": round(time.time() - t0, 3),
                "error": None,
            }
        except Exception as exc:
            last_exc = exc
            wait = 2 ** attempt
            print(f"    retry {attempt+1}/{retries} em {wait}s ({exc})")
            time.sleep(wait)
    return {
        "output": "",
        "input_tokens": 0,
        "output_tokens": 0,
        "latency_s": 0,
        "error": str(last_exc),
    }


def run_judge(client: OpenAI, judge_model: str, judge_prompt: str, rubric: dict) -> dict:
    """Chama o juiz e parseia a resposta JSON."""
    r = client.chat.completions.create(
        model=judge_model,
        messages=[{"role": "user", "content": judge_prompt}],
        max_tokens=600,
        temperature=0.0,
    )
    raw = r.choices[0].message.content
    try:
        parsed = parse_judge_output(raw, rubric)
        parsed["_raw_judge_output"] = raw[:500]
        return parsed
    except ValueError as exc:
        return {
            "_error": str(exc),
            "_raw_judge_output": raw[:500],
        }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--product",
        default=os.environ.get("PRODUCT", "educiacao"),
        choices=["educiacao", "designmind"],
    )
    ap.add_argument("--run-tag", default="run_v1")
    ap.add_argument("--max-prompts", type=int, default=None,
                    help="Limita N primeiros prompts (debug rápido)")
    args = ap.parse_args()

    print(f"\n[ aula04 · run_eval · produto={args.product} · tag={args.run_tag} ]\n")

    golden_path = ROOT / "data" / f"golden_{args.product}.csv"
    rubric_path = ROOT / "config" / f"rubric_{args.product}.yaml"
    cand_path = ROOT / "config" / "candidates.yaml"

    golden = pd.read_csv(golden_path)
    if args.max_prompts:
        golden = golden.head(args.max_prompts)

    rubric = yaml.safe_load(open(rubric_path))
    cfg = yaml.safe_load(open(cand_path))
    candidates = cfg["candidates"]
    judge_model = cfg["judge"]["model_id"]

    print(f"  Prompts: {len(golden)}  ·  Candidatos: {len(candidates)}  ·  Juiz: {judge_model}")
    print(f"  Total de chamadas estimado: {len(golden)*len(candidates)} candidatos + "
          f"{len(golden)*len(candidates)} juiz\n")

    groq = make_groq()
    openrouter = make_openrouter()
    lf = make_langfuse()

    results = []
    student = os.environ.get("STUDENT_NAME", "anon")

    for cand in candidates:
        client = groq if cand["provider"] == "groq" else openrouter
        for _, row in golden.iterrows():
            print(f"  [{cand['name']:12s}] {row['id']} ({row['category']})...", end=" ", flush=True)

            cand_run = run_candidate(client, cand["model_id"], row["input"])

            if cand_run["error"]:
                print(f"FALHA · {cand_run['error']}")
                results.append({
                    "model": cand["name"], "id": row["id"], "category": row["category"],
                    "weighted": None, "error": cand_run["error"],
                })
                continue

            jp = build_judge_prompt(
                user_input=row["input"],
                candidate_output=cand_run["output"],
                expected_pattern=row["expected_pattern"],
                red_flags=row["red_flags"],
                rubric=rubric,
            )
            scores = run_judge(openrouter, judge_model, jp, rubric)

            if "_error" in scores:
                print(f"JUIZ FALHOU · {scores['_error'][:80]}")
                weighted = None
            else:
                weighted = weighted_score(scores, rubric)
                print(f"weighted={weighted:.2f}  lat={cand_run['latency_s']:.2f}s  "
                      f"out={cand_run['output_tokens']}tok")

            row_out = {
                "model": cand["name"],
                "model_id": cand["model_id"],
                "id": row["id"],
                "category": row["category"],
                "weight_in_dataset": row["weight"],
                "weighted": weighted,
                "latency_s": cand_run["latency_s"],
                "input_tokens": cand_run["input_tokens"],
                "output_tokens": cand_run["output_tokens"],
                "error": cand_run["error"],
                "judge_error": scores.get("_error"),
            }
            for dim in rubric["dimensions"]:
                row_out[dim["name"]] = scores.get(dim["name"])
            row_out["red_flags_acionadas"] = json.dumps(
                scores.get("red_flags_acionadas", []), ensure_ascii=False
            )
            row_out["justificativa"] = scores.get("justificativa_curta", "")
            row_out["candidate_output"] = cand_run["output"][:2000]
            results.append(row_out)

            if lf:
                try:
                    lf.create_event(
                        name=f"eval/{cand['name']}/{row['id']}",
                        input=row["input"],
                        output=cand_run["output"],
                        metadata={
                            "model": cand["name"], "model_id": cand["model_id"],
                            "category": row["category"], "weighted": weighted,
                            "latency_s": cand_run["latency_s"],
                            "tokens": cand_run["input_tokens"] + cand_run["output_tokens"],
                            "scores": {k: scores.get(k) for k in
                                       [d["name"] for d in rubric["dimensions"]]},
                            "student": student, "run_tag": args.run_tag,
                            "product": args.product,
                        },
                    )
                except Exception as exc:
                    print(f"    [warn] langfuse falhou: {exc}")

    if lf:
        try:
            lf.flush()
        except Exception:
            pass

    df = pd.DataFrame(results)
    out_path = RESULTS_DIR / f"{args.run_tag}_{args.product}.csv"
    df.to_csv(out_path, index=False)
    print(f"\n  Resultados salvos em {out_path.relative_to(ROOT)}")
    print(f"  Total de linhas: {len(df)}")
    if "weighted" in df.columns:
        print("\n  Média ponderada por modelo:")
        agg = df.groupby("model")["weighted"].mean().sort_values(ascending=False)
        for m, s in agg.items():
            print(f"    {m:15s}  {s:.3f}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
