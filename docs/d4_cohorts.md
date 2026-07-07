# D4 — Catálogo de coortes clínicas (CAR-T / TCE / biespecíficos)

> **Objetivo:** validar a assinatura ISCI (eixos de controlabilidade do Marson Perturb-seq) em produtos/células T de pacientes com desfecho clínico conhecido.  
> **Escopo hackathon:** preparar material agora; análise mínima viável se D0–D2 fecharem a tempo.  
> **Última busca:** 2026-07-07 (PubMed, GEO, Cancer Cell, Blood abstracts, Zenodo, tcellMIL).

---

## Recomendação executiva

| Prioridade | Coorte | Por quê | Viabilidade até 13/jul |
|------------|--------|---------|------------------------|
| **P0** | Functional CAR-T atlas (Zenodo / scVI-hub) | >1M células, 13 estudos, fenótipos + response/ICANS; **sem** precisar treinar modelo de outcome | Alta — enrichment de assinatura ISCI |
| **P0** | Dang *Cancer Cell* 2023 — **GSE216571** | **Único TCE (BCMA×CD3) com R/NR publicado + scRNA+TCR** | Média — 16 pts, BM longitudinal |
| **P1** | GSE151511 (+ GSE150992) — Deng 2020 | IPs CAR-T LBCL, response + tox; processado público | Alta — 24 amostras, ~133k células |
| **P1** | Haradhvala GSE197268 | 32 pts, IP + PBMC, CAR-Treg em NR | Média — raw em dbGaP; suppl. processado |
| **P2** | GSE223655 — prem-manufacture 58 DLBCL | TSCM/CD8 memória → resposta durável | Média — bulk + scRNA |
| **P2** | tcellMIL / tcellwarehouse (64 pts) | Baseline comparativo (MIL + SCENIC) | Baixa para reimplementar; usar como referência |
| **P3** | ResisTec, blinatumomab CITE-seq | TCE “puro” hemato; **dados ainda não públicos** | Pós-hackathon / contato autores |

**Estratégia em 2 degraus (não bloqueia D0):**

1. **Phenotype floor (D4 mínimo):** projetar score ISCI / eixos no atlas CAR-T → enriquecimento em memória vs exaustão (figura “clinical bridge” sem ML de outcome).
2. **Outcome test (D4 stretch):** associar pseudobulk do score ISCI por paciente com `Response` em GSE216571 ou GSE151511 (Spearman + LOO simples; comparar com tcellMIL features).

---

## Camada A — T-cell engagers / biespecíficos (TCE)

### A1. Dang et al. — *Cancer Cell* 2023 (referência principal TCE)

| Campo | Valor |
|-------|-------|
| **Título** | The pre-existing T cell landscape determines the response to bispecific T cell engagers in multiple myeloma patients |
| **DOI** | [10.1016/j.ccell.2023.01.008](https://doi.org/10.1016/j.ccell.2023.01.008) |
| **Terapia** | BCMA×CD3 bispecific (TCE) monoterapia em MM RR |
| **n pacientes** | 18 RRMM em TCE (+ 7 NDMM, 5 HBM controles) |
| **Desfecho** | **9 respondedores (R) vs 7 não-respondedores (NR)** — expansão clonal CD8_effector_CX3CR1 em R |
| **Amostras** | BM longitudinal (pre / on-treatment) + PB; scRNA + scTCR |
| **Células T** | ~248k T cells com αβ TCR detectado |
| **GEO processado** | **GSE216571** |
| **GEO raw** | **GSE217245** |
| **Controles** | GSE124310 (BM saudável / NDMM) |
| **Mecanismo relevante ISCI** | Diferenciação naive→effector sob TCE; **não** exaustão canônica como driver principal em PB (ResisTec confirma) |
| **Viabilidade CPU** | Sim — Seurat/scanpy + pseudobulk por paciente |
| **Notas** | Melhor dataset **TCE com label R/NR** disponível publicamente. Priorizar CD4/CD8 T do BM pre-tratamento. |

### A2. Multi-omic BCMA-BsAb serial — Blood 2024

| Campo | Valor |
|-------|-------|
| **Título** | Multi-Omic Single-Cell Characterization of Paired and Serial Samples in Responding and Non-Responding Patients Receiving BCMA Bispecific Antibody Therapy |
| **DOI** | [10.1182/blood-2024-210080](https://doi.org/10.1182/blood-2024-210080) |
| **Terapia** | teclistamab (N=8) + outros BCMA-BsAb trial (N=6) |
| **n** | 14 RRMM — **12 R, 2 NR** (SD/PD) |
| **Dados** | scRNA + scTCR + scBCR; BM pareado baseline/on/post |
| **Acesso** | **Não encontrado em GEO** (abstract ASH/Blood); mesmo grupo Dang — solicitar suppl. |
| **ISCI** | Complementar a A1 se dados liberados |

### A3. ResisTec — IFM real-world teclistamab

| Campo | Valor |
|-------|-------|
| **Título** | The ResisTec study: Dissecting immune correlates of resistance and response to teclistamab in real-world multiple myeloma |
| **DOI** | [10.1182/blood-2025-918](https://doi.org/10.1182/blood-2025-918) |
| **Trial** | **NCT05945524** — 100 pts longitudinal |
| **Achados** | BM lymphoid-rich → resposta; falha expansão CD8⁺ citotóxica + Treg incompleta em NR; **sem exaustão canônica em PB** |
| **Dados** | **Não públicos** (estudo ativo) |
| **ISCI** | Validação futura IDOR/IFM; citar no pitch como “coorte alvo” |

### A4. Teclistamab HR-SMM vs RRMM longitudinal — Blood 2024

| Campo | Valor |
|-------|-------|
| **DOI** | [10.1182/blood-2024-207299](https://doi.org/10.1182/blood-2024-207299) |
| **n** | 46 amostras PBMC (27 pre, 19 paired post) |
| **Dados** | scRNA + TCR; ~123k células imunes |
| **Acesso** | Abstract — **sem GEO** identificado |
| **ISCI** | Dinâmica temporal pós-TCE; útil se suppl. disponível |

### A5. Blinatumomab (CD3×CD19 BiTE) — literatura

| Estudo | n | Desfecho | Dados públicos |
|--------|---|----------|----------------|
| CITE-seq LMU — Blood 2023-188970 | 13 BCP-ALL | 10 R / 3 NR | **Não em GEO** (477-gene panel + 7 AbSeq) |
| ZNF683⁺ CD8 — Blood 2025-5086 | 8 B-ALL BiTE | 4 R / 4 NR | **Não em GEO** |
| Pediatric blina — Blood 2024-204307 | 7 ped BCP-ALL | 5 sensitive / 2 insensitive MRD | **Não em GEO** |
| AALL1331 TCL1A — ASH 2024 | trial cohort | R vs NR (relapse) | bulk Nanostring + scRNA subset |

**Conclusão TCE:** para o hackathon, **GSE216571 é a aposta TCE**. Blinatumomab: citar mecanismo (TCF7/BCL11B, PRDM1 em NR) mas **não contar com download imediato**.

---

## Camada B — CAR-T (ponte mecanística mais madura)

### B1. Deng et al. — *Nat Med* 2020

| Campo | Valor |
|-------|-------|
| **DOI** | [10.1038/s41591-020-1061-7](https://doi.org/10.1038/s41591-020-1061-7) |
| **Doença** | LBCL — produtos anti-CD19 (axi-cel, tisa-cel) |
| **n** | 24 infusion products |
| **Desfecho** | Response + neurotoxicidade (metadados suppl.) |
| **GEO** | **GSE151511** (scRNA), **GSE150992** (CapID) |
| **Tamanho** | ~133k células (reanálises publicadas) |
| **ISCI** | Exaustão CD4/CD8 em PD; memória em PR — alinha eixo exhaustion/memory |

### B2. Haradhvala et al. — *Nat Med* 2022

| Campo | Valor |
|-------|-------|
| **DOI** | [10.1038/s41591-022-01959-0](https://doi.org/10.1038/s41591-022-01959-0) |
| **n** | 32 pts — IP + PBMC serial |
| **Desfecho** | OR vs NR; **CAR-Treg CD4+ HELIOS+** em NR |
| **GEO** | **GSE197268** (processado suppl.; raw **dbGaP** controlado) |
| **Nota** | Haradhvala também reusa **GSE151511** para axi-cel IPs |
| **ISCI** | Eixo Treg + memory CD8 — teste direto da hipótese ISCI |

### B3. Premanufacture CD8⁺ TSCM — *Sig Transduct Target Ther* 2023

| Campo | Valor |
|-------|-------|
| **PMID** | [37875502](https://pubmed.ncbi.nlm.nih.gov/37875502/) |
| **n** | 58 r/r DLBCL — tandem CD19/CD20 CAR-T |
| **Desfecho** | DR vs resistant vs relapse |
| **GEO** | **GSE223655** (bulk+scRNA), **GSE243325** (produto + aférese) |
| **ISCI** | TSCM (TCF7, CCR7, LEF1) — overlap direto com eixo memory-like |

### B4. Functional CAR-T atlas — meta-recurso

| Campo | Valor |
|-------|-------|
| **Zenodo** | [10.5281/zenodo.17213452](https://doi.org/10.5281/zenodo.17213452) |
| **GitHub** | [ML4BM-Lab/Functional-cart-atlas](https://github.com/ML4BM-Lab/Functional-cart-atlas) |
| **scVI-hub** | `sergiocamarap/Functional-cart-atlas-model` |
| **Explorador** | [ShinyCell](https://wholebioinfo.shinyapps.io/shinyatlas/) · [UCSC Cell Browser](https://car-t-atlas.cells.ucsc.edu) |
| **Escala** | >1M células, 13 estudos, 11 fenótipos |
| **Metadados** | response, ICANS, produto, estudo |
| **ISCI** | **Melhor figura D4 rápida:** projetar assinatura no espaço latente scVI; enrichment por fenótipo |

### B5. tcellMIL — baseline comparativo

| Campo | Valor |
|-------|-------|
| **Paper** | Blood 2025-5897; NeurIPS 2025 |
| **GitHub** | [zinagoodlab/tcellMIL](https://github.com/zinagoodlab/tcellMIL) |
| **Dados** | [tcellwarehouse.com](https://tcellwarehouse.com/) — 64 pts multi-coorte |
| **Input** | SCENIC AUCell matrix + `Response_3m` (OR/NR) |
| **ISCI** | Não reimplementar MIL; reportar se assinatura ISCI correlaciona com mesmos regulons (TBX21, RORC) |

### B6. Outros CAR-T (menor n ou sem outcome claro)

| GEO | n | Notas |
|-----|---|-------|
| GSE235760 | 5 B-ALL adulto | CARpos/CARneg IP + pico expansão |
| GSE241783, GSE253872, GSE273170 | variável | perfil serial produto — verificar metadata response |

---

## Matriz de decisão — qual análise fazer com quanto tempo

| Tempo restante | Entregável D4 | Dataset |
|----------------|---------------|---------|
| **2–3 h** | Heatmap enrichment ISCI axes × 11 fenótipos atlas | Functional CAR-T |
| **4–6 h** | + boxplot score ISCI memory axis: R vs NR (pseudobulk) | GSE151511 ou GSE216571 pre-Tx |
| **8–12 h** | + LOO AUC simples vs magnitude DE-only baseline | GSE216571 (TCE) |
| **>12 h** | Integração multi-coorte + comparação verbal tcellMIL | tcellwarehouse + atlas |

---

## Plano de download (CPU-local, Mac 24GB)

```bash
# 1. TCE principal (prioridade)
# GSE216571 — processed matrices via GEO supplementary
# https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE216571

# 2. CAR-T infusion products (rápido)
# GSE151511_RAW.tar (~1.1 GB)
# https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE151511

# 3. Meta-atlas (maior; usar scVI-hub query em subset)
# Zenodo 10.5281/zenodo.17213452
# HuggingFace: sergiocamarap/Functional-cart-atlas-model
```

**Governança:** todos PUBLIC/CONFIDENTIAL — sem PHI; adequado para pipeline hackathon.

---

## Hipóteses testáveis (pré-registro D4)

1. **H1:** Score ISCI (eixo memory-like − exhaustion-like) é **maior** em respondedores vs não-respondedores no produto pré/infusão (GSE151511, GSE216571 pre).
2. **H2:** Projeção no atlas CAR-T enriquece fenótipos **stem-like/memory** nos top controllers ISCI do Marson.
3. **H3:** Assinatura ISCI **não** é redundante com magnitude DE bruta nem com único regulon SCENIC (ablation D2 estendida).
4. **H4 (negativa):** Em TCE MM, sinal pode estar em **dinâmica** (pre→on) mais que baseline — alinhar com ResisTec/Blood 2024.

---

## O que pedir aos advisors IDOR

1. Endpoint preferido em MM: **MRD**, **BOR**, ou **PFS** para rotular “R”?
2. Coorte IDOR teclistamab/blinatumomab — existe bulk RNA ou flow com desfecho sob governança?
3. CD4+ como foco ISCI: em CAR-T product, % CD4 é alto o suficiente para pseudobulk por paciente?

---

## Referências rápidas

- Dang *Cancer Cell* 2023 — GSE216571 / GSE217245  
- Deng *Nat Med* 2020 — GSE151511 / GSE150992  
- Haradhvala *Nat Med* 2022 — GSE197268  
- Premanufacture TSCM — GSE223655  
- Functional CAR-T atlas — Zenodo 17213452  
- tcellMIL — github.com/zinagoodlab/tcellMIL  
- ResisTec — NCT05945524 (dados futuros)
