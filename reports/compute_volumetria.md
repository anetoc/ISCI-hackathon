# Compute volumetria — o que uma máquina institucional habilita

**Objetivo:** subsídio para a discussão de acesso ao HPC/servidor da instituição.
Hoje toda a análise roda CPU-local (Mac M4 Pro, 24 GB). O core ISCI_orthogonal e
toda a expansão T-REMAP cabem nisso porque operam sobre o **pseudobulk DE_stats**
(16.8 GB, 33.983 perturbação×condição × 10.282 genes). O que NÃO cabe — e o que
uma máquina maior habilita — está abaixo.

## O que fica bloqueado sem mais compute

| Tarefa | Dado | Requisito | Ganho científico |
|---|---|---|---|
| Marson **cell-level** (22M células) | 12 arquivos `assigned_guide.h5ad`, **118.6–172.8 GB cada** (~1.7 TB total) | 256 GB RAM (ou leitura backed/chunked) + ~2 TB scratch; GPU p/ scVI | Re-derivar coerência/especificidade por célula, testar heterogeneidade intra-perturbação, refinar módulos |
| **GRN em escala** (pySCENIC/SCENIC+) | matriz de expressão célula×gene | ≥16 cores, 1 GPU, ~1 TB scratch | Inferência de regulon adequada (o teste atual com decoupler é aproximação) |
| **Atlas CAR-T completo** | scVI_hub_adata.h5ad (15.5 GB) | 64–128 GB RAM | Cinética clonal (scTCR), concordância proteica (CITE/CyTOF), trajetória temporal |
| **CITE/CyTOF** concordância (ex. GSE273170) | matrizes multi-modais | 64 GB RAM | Validar se módulos de RNA viram fenótipo de proteína de superfície |
| **Foundation models de perturbação** (scGPT/Geneformer/STATE) | embeddings + fine-tune | 1 GPU (24–40 GB VRAM) | Componente A (concordância in-silico) com modelo, não só pseudobulk |

## Pedido mínimo recomendado à instituição

- **RAM:** 128 GB (mínimo funcional) — 256 GB (confortável para cell-level completo).
- **CPU:** ≥16 cores (GRN e leitura de h5ad grande são multi-thread).
- **GPU:** 1× (≥24 GB VRAM) — scVI, SCENIC+, foundation models.
- **Scratch:** ~2 TB (o Marson cell-level completo é ~1.7 TB; atlas + intermediários somam mais).
- **Rede:** saída para S3 público (CZI bucket) e GEO/Zenodo.

## Como isso se conecta ao Claude Science

Quando a máquina estiver disponível, ela entra como alvo de **compute remoto**
(painel Compute → SSH). O fluxo: preparo o script e os inputs aqui, despacho o
passo pesado para a máquina, e os resultados voltam como artefatos. Os passos
candidatos a remoto são exatamente os da tabela acima; tudo que é leve
(parsing, plotagem, os scores ISCI/T-REMAP) permanece local.

## Prioridade honesta

Nada disso é necessário para a **submissão** (core + T-REMAP + validação externa
já rodam local). É o caminho de **expansão pós-hackathon** para transformar o
framework num mapa multiômico em escala real — e é onde a máquina institucional
muda a fronteira do viável.
