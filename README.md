# aula04-eval-harness

Harness reproduzível de avaliação comparativa de LLMs.
Aula 04 — Engenharia de IA · Seleção, Avaliação e Comparação de Modelos.

## O que isto faz

Roda 10 prompts ancorados (golden dataset) contra 3 modelos candidatos via API,
avalia as respostas com um juiz LLM (LLM-as-Judge) usando rubrica explícita, e
produz uma matriz de trade-offs Qualidade × Custo × Latência × Privacidade que
fundamenta a escolha do modelo campeão para o produto do aluno.

## Stack

- **Inferência (candidatos):** Groq Cloud (free tier)
- **Juiz:** Claude 3.5 Sonnet ou GPT-4o-mini via OpenRouter
- **Tracing:** Langfuse Cloud (free tier)
- **Eval framework:** harness próprio + DeepEval (opcional)
- **IDE:** GitHub Codespaces ou VSCode local + Python 3.11

## Quick start

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Copiar template de variáveis de ambiente e preencher
cp .env.example .env
# editar .env com suas chaves de API

# 3. Smoke test (validar que todas APIs respondem)
python smoke_test.py

# 4. Validar candidatos antes de rodar evaluation completa
python check_candidates.py

# 5. Rodar avaliação completa
python run_eval.py

# 6. Analisar resultados e gerar matriz
python analyze.py
```

## Produto designado

Cada aluno recebe um dos dois produtos (sorteio cego no início da aula):

- **EducIAção** — tutor pedagógico para alunos em vulnerabilidade.
- **DesignMind AI** — multi-agente de Design Thinking para PMEs.

Use o golden dataset e a rubrica correspondentes ao seu produto.

## Estrutura

```
aula04-eval-harness/
├── data/                       # Golden datasets (CSV)
│   ├── golden_educiacao.csv
│   └── golden_designmind.csv
├── config/                     # Configuração de rubricas e candidatos
│   ├── rubric_educiacao.yaml
│   ├── rubric_designmind.yaml
│   └── candidates.yaml
├── results/                    # Outputs da execução (não versionar)
├── templates/                  # Templates de entrega
│   └── model_card_template.md
├── smoke_test.py               # Valida 3 APIs respondem
├── check_candidates.py         # Valida disponibilidade dos modelos
├── run_eval.py                 # Harness principal
├── judge_prompt.py             # Construção do prompt do juiz com mitigação de viés
├── analyze.py                  # Agregação e matriz de trade-offs
├── requirements.txt
├── .env.example
└── .gitignore
```

## Entregas obrigatórias da aula

1. `data/golden_<produto>.csv` com 10 prompts (5 ancorados + 5 originais), commitado com tag `golden-v1`.
2. `config/rubric_<produto>.yaml` com 5 dimensões e pesos somando 1.00.
3. `config/candidates.yaml` com 3 modelos validados.
4. `results/run_v1.csv` e `results/run_v1_summary.md` populados.
5. `docs/model_card_v1.md` preenchido a partir do template.
6. Tag `aula04-final` aplicada no git.
