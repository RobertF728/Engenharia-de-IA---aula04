# Model Card v1

> Documento interno · primeira versão · Aula 04
> Defesa de decisão de modelo para a etapa atual do produto.

## Identificação

| Campo | Valor |
|---|---|
| **Produto** | <!-- EducIAção ou DesignMind AI --> |
| **Aluno responsável** | |
| **Data da decisão** | |
| **Modelo escolhido** | |
| **Provider** | |
| **Run tag avaliada** | run_v1 |

## Dataset usado para decidir

| Campo | Valor |
|---|---|
| **Nome / versão** | golden-v1 |
| **Tamanho** | 10 prompts (5 ancorados + 5 originais) |
| **Cobertura (categorias)** | <!-- listar categorias presentes --> |
| **Limitações conhecidas** | <!-- viés de cobertura, casos edge ausentes, etc --> |

## Rubrica usada

| Dimensão | Peso | Justificativa do peso |
|---|---|---|
| | | |
| | | |
| | | |
| | | |
| | | |

## Resultados sintéticos

| Modelo | Qualidade ponderada | Custo USD/1k resp | Latência p95 | Privacidade |
|---|---|---|---|---|
| Candidato A | | | | |
| Candidato B | | | | |
| Candidato C | | | | |

**Conjunto Pareto-ótimo:** <!-- listar modelos não-dominados -->

## Decisão

### Modelo campeão
<!-- Nome do modelo + provider -->

### Por que este modelo?
<!-- 3-5 frases. Conectar à restrição do produto e à matriz. -->

### Trade-off aceito
<!-- O que perdi escolhendo este e não outro? -->

### Fallback consciente
<!-- Qual modelo assumiria se uma restrição mudasse? Em que cenário? -->

## Limites declarados

### Vieses do juiz
- Juiz utilizado: <!-- modelo -->
- Vieses esperados: <!-- position bias, length bias, etc. -->
- Como mitiguei: <!-- pointwise, âncoras, anti-comprimento, etc. -->

### Cenários não testados
<!-- O que ficou de fora do golden v1? -->

### O que falsearia esta decisão
<!-- Qual evidência mudaria minha escolha? Útil para definir o que coletar a seguir. -->

## Lições da defesa em sala
<!-- Preencher após Fase 7. Mínimo 2 lições aprendidas, mesmo que negativas. -->

1.
2.

## Próximas iterações

- [ ] Aumentar golden dataset para 25 prompts (Aula 5)
- [ ] Cruzar com avaliação RAG (RAGAS) na Aula 5
- [ ] Comparar contra modelo fine-tuned (Aula 6)
- [ ] Testar em pipeline agentic (Aula 7)
