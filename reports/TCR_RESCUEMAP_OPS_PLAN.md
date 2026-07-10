> **Status: operational flight-plan for the TCR-RescueMap research program (Paper 2). NOT hackathon-submission scope.**
> Companion to `reports/TCR_RESCUEMAP_SPEC.md`. Describes the 4-track execution model (comp/stats foundation, public-data
> harmonization, TCR–pMHC system selection, prospective bidirectional map), HPC/Slurm architecture, dataset/API registries,
> and a phased wave A–G roadmap. The ONLY compute-only Phase-0 item — OOF hardening of the M→M+C incremental test — is
> already done (`outputs/isci_oof_incremental.json`, OOF +0.215 [+0.074,+0.560]). Everything else requires a new repo,
> institutional HPC, and wet-lab reagents (TCR/pMHC systems, paired CRISPR screens); it is deliberately OUT of scope for
> the July 13 submission, which stays the frozen ISCI-v2 anchor.

---

# Plano operacional para executar o TCR-RescueMap

A execução deve ser organizada como **quatro trilhas paralelas, com dependências explícitas**:

1. **Fundação computacional e estatística**
2. **Aquisição e harmonização de dados públicos**
3. **Seleção dos sistemas TCR–peptídeo–HLA e preparação experimental**
4. **Geração prospectiva do mapa bidirecional**

O ponto mais importante é não tentar ca:

```text
ISCI endurecido
→ evidence graph
→ escolha TCR/pMHC
→ qualificação do ensaio
→ tela unilateral T
→ tela unilateral tumor
→ seleção de anchors
→ tela de interação
→ validação mecanística
→ segurança
→ validação translacional
```

Preparei um pacote operacional com playbook, registry de datasets, registry de APIs e perfis de compute:

* [Playbook de implementação](sandbox:/mnt/data/tcr_rescuemap_ops/TCR_RescueMap_Implementation_Playbook_v0.1.md)
* [Template do registry de datasets](sandbox:/mnt/data/tcr_rescuemap_ops/datasets_public_template.yaml)
* [Template do registry de APIs](sandbox:/mnt/data/tcr_rescuemap_ops/api_registry_template.yaml)
* [Template dos perfis de compute](sandbox:/mnt/data/tcr_rescuemap_ops/compute_profiles_template.yaml)
* [Pacote completo ZIP](sandbox:/mnt/data/TCR_RescueMap_Implementation_Bundle_v0.1.zip)

---

# 1. Primeira decisão: separar o novo programa do hackathon

O repositório `ISCI-hackathon` deve ser congelado como o anchor metodológico. O `result_lock` agora delimita corretamente o resultado a reguladores canônicos definidores de eixo e incorpora os resultados negativos do conjunto funcional externo.

Minha recomendação é:

```text
ISCI-hackathon
└── release/tag: isci-v2-anchor

TCR-RescueMap
├── código novo
├── workflows
├── registries
├── contratos de dados
├── análises bidirecionais
└── novo claim ledger
```

O novo repositório consome:

* o package do ISCI em uma versão pinada; ou
* o ranking e features congelados com checksum; ou
* uma release do Zenodo/GitHub.

Não copie todo o histórico do hackathon. Isso evitará misturar:

* índices depreciados;
* resultados históricos;
* diferentes manifests;
* claims antigos;
* código experimental com pipeline confirmatório.

---

# 2. P0 estatístico antes de usar o `+0,357` como confirmatório

A correção `M → M+C` resolve o problema do **estimando**: agora o teste pergunta corretamente quanto a controlabilidade acrescenta a um modelo que já conhece magnitude.

Há ainda um endurecimento técnico: no helper atual, quando são fornecidas `feature_cols`, a regressão logística é ajustada e pontuada nos mesmos elementos da amostra bootstrap. Isso gera uma estimativa aparente/in-sample, potencialmente otimista para 13 positivos e 20 negativos.

Isso não invalida o `+0,357`. Significa que ele deve ser rotulado temporariamente como:

> **incremental apparent/development estimate**

até rodarmos a versão out-of-fold.

## Implementação correta

Criar um `match_block_id` para:

```text
1 positivo
+ seus negativos expression/power-matched
```

Então usar grouped cross-validation:

```text
Outer fold:
    deixa um ou mais matching blocks de fora

Training:
    escolhe negativos
    estima residualização S~M e R~M
    ajusta scaling
    ajusta model0 = label ~ M
    ajusta model1 = label ~ M + Sresid + Rresid

Test:
    aplica transformações do training
    gera predições model0 e model1

Final:
    concatena predições OOF
    calcula AUPRC0, AUPRC1 e ΔAUPRC
```

O bootstrap deve reamostrar **matching blocks completos** e refazer todo o processo.

## Entregáveis P0

```text
src/rescuemap/validation/incremental_oof.py
tests/test_incremental_oof.py
tests/test_no_leakage.py
outputs/isci_oof_incremental.json
reports/ISCI_V2_RESULT_LOCK.md
```

O resultado atual pode continuar no abstract enquanto estiver explicitamente identificado como aparente. Depois, o resultado OOF assume o headline.

---

# 3. Pré-requisitos reais

## 3.1 Pré-requisitos científicos e de reagentes

O maior bloqueador inicial não é computacional. É ter um sistema TCR–pMHC verdadeiramente utilizável.

Precisamos de:

* sequência completa do TCR α/β;
* direito acadêmico ou contratual de uso;
* afinidade e especificidade documentadas;
* HLA exato;
* antígeno endógeno no tumor;
* modelo antigen-null;
* modelo HLA-null ou `B2M`-null;
* tumor com faixa controlável de densidade antigênica;
* reagente ou método para medir pMHC;
* TCR irrelevante como controle;
* painel inicial de segurança.

**Não devemos assumir que a sequência do receptor de um produto comercial está disponível.** MAGE-A4/HLA-A*02 é um excelente modelo translacional, mas somente se houver:

* TCR acadêmico publicado e validado;
* colaboração formal;
* ou licença de uso.

VDJdb pode contribuir com registros curados contendo TCR, CDR3, V/J, epítopo, MHC e nível de confiança, mas os registros oncológicos continuam relativamente escassos.

## 3.2 Escolha de dois sistemas

### Sistema sólido

Preferência:

* MAGE-A4/HLA-A*02;
* HPV E7/HLA-A*02 como sistema de calibração;
* NY-ESO-1/HLA compatível, dependendo do TCR disponível.

### Sistema hematológico

Avaliar formalmente:

* PRAME;
* WT1;
* HA-1;
* outro minor histocompatibility antigen;
* neoantígeno recorrente, se houver modelo adequado.

O sistema hematológico deve ter pelo menos:

* uma linha de calibração;
* uma linha com antígeno endógeno;
* modelo adicional de validação;
* possibilidade de controlar HLA/APM.

## 3.3 Wet-lab mínimo

* BSL-2 e governança de vetores;
* electroporação ou plataforma de knock-in;
* CRISPR KO;
* preferencialmente CRISPRi e CRISPRa;
* células T primárias de pelo menos três doadores;
* geração de tumor reporter;
* flow cytometry;
* leitura de guide abundance;
* live-cell imaging;
* repeated challenge assay;
* possibilidade de fazer rescue constructs;
* armazenamento institucional para imagens e sequencing.

## 3.4 Time mínimo

| Papel                            | Entrega principal                      |
| -------------------------------- | -------------------------------------- |
| Lead científico TCR/hematologia  | sistema, relevância e claims           |
| Computational lead               | arquitetura e estimandos               |
| T-cell engineering               | TCR KI, CRISPR e manufacturing         |
| Tumor/screen scientist           | engenharia tumoral e screens           |
| Biostatístico                    | potência, interação e multiplicidade   |
| Workflow/bioinformatics engineer | HPC, ETL e provenance                  |
| Data steward                     | acesso, consentimento e segurança      |
| Imaging collaborator             | sinapse, killing e análise temporal    |
| Proteomics collaborator          | pMHC/phosphoproteomics, fase posterior |

No MVP, uma pessoa pode cobrir mais de uma função, mas cada responsabilidade deve ter dono explícito.

---

# 4. Arquitetura de compute

O compute institucional descrito no repositório já atende à fundação do programa:

* Linux;
* 128 GB RAM;
* GPU de 48 GB;
* acesso SSH;
* downloads públicos diretos.

O repositório estima que o Marson cell-level completo contém aproximadamente 1,7 TB e recomenda cerca de 2 TB de scratch; 256 GB seria mais confortável para certas análises cell-level, mas a máquina de 128 GB é suficiente para a maior parte do programa se forem usados processamento backed, sparse e chunked.

## 4.1 Três camadas

### Local — Mac 24 GB

Usar para:

* desenvolvimento;
* unit tests;
* API ETL;
* tabelas;
* pequenos slices;
* QC;
* figuras;
* documentação;
* criação do DAG;
* inspeção dos resultados.

### HPC institucional — principal

Usar para:

* downloads;
* harmonização h5ad;
* scVI/totalVI;
* CellxGene slices grandes;
* bootstraps hierárquicos;
* modelos mistos de interação;
* pMHC scanning;
* processamento de imagens;
* scRNA/CITE;
* multiome;
* job arrays por doador, dataset, HLA ou anchor.

O Slurm possui suporte a job arrays, gestão de CPU, recursos genéricos como GPUs e filas de high-throughput, que é exatamente o padrão necessário para paralelizar datasets, donors, anchors e bootstrap chunks. ([Slurm][1])

### Cloud burst — somente overflow

Usar para:

* dados públicos;
* jobs stateless;
* containers;
* grandes arrays independentes;
* processamento facilmente reiniciável.

AWS Batch pode provisionar e distribuir automaticamente jobs batch containerizados sobre recursos de compute gerenciados. ([Documentação AWS][2])

Não enviar para cloud pública:

* dados institucionais;
* dados controlados;
* dados de doadores;
* patient-level data;
* imagens prospectivas;

sem aprovação formal da TI, CEP/IRB e data-use agreement.

---

# 5. Matriz de recursos

Valores abaixo são **classes de planejamento**, a serem refinadas depois do piloto.

| Job                              |   CPU |          RAM |      GPU |    Scratch |
| -------------------------------- | ----: | -----------: | -------: | ---------: |
| APIs/evidence graph              |   2–8 |      8–32 GB |      não |    <100 GB |
| OOF ISCI + bootstrap             |  8–16 |     32–64 GB |      não |    <100 GB |
| Harmonização de screens públicos | 16–32 |    64–128 GB |      não |     0,5 TB |
| CELLxGENE slices                 |  8–16 |     32–64 GB |      não | 100–300 GB |
| Frangieh totalVI                 |    16 |       128 GB | 24–48 GB |     0,5 TB |
| CAR-T/scVI atlas                 |    16 |       128 GB | 24–48 GB |     0,5 TB |
| Marson cell-level                | 32–64 | 256 GB ideal |    48 GB |      ~2 TB |
| MHC/pMHC prediction              |  8–32 |     32–64 GB | opcional |     100 GB |
| Tela unilateral — análise        | 16–32 |    64–128 GB |      não |     0,5 TB |
| Interações T×tumor               | 32–64 |   128–256 GB |      não |   0,5–1 TB |
| Segmentação live imaging         | 16–32 |    64–128 GB | 24–48 GB |    2–10 TB |
| scRNA/CITE confirmatório         |    32 |   128–256 GB |    48 GB |     1–3 TB |
| Multiome                         | 32–64 |       256 GB |    48 GB |     2–5 TB |

## Storage recomendado

### Imediato

```text
2 TB scratch
1 TB curated/interim
```

### Quando começar imaging e sequencing prospectivo

```text
10–20 TB institucionais
```

Raw público pode ser rebaixado. Raw experimental precisa de duas cópias institucionais.

---

# 6. Como executar via SSH/Slurm

Não rodar análises canônicas em notebooks interativos.

## Fluxo

```text
Git commit
→ workflow gera DAG
→ submit via Slurm
→ job escreve logs + manifest
→ outputs vão para object storage/results
→ laptop recebe apenas artefatos pequenos
```

## Perfis

```text
profiles/
├── local/
├── slurm_cpu/
├── slurm_highmem/
└── slurm_gpu/
```

Exemplo de job GPU:

```bash
#SBATCH --job-name=rescuemap_totalvi
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --gres=gpu:1
#SBATCH --time=24:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err
```

Paralelizar por:

* dataset;
* doador;
* tumor anchor;
* HLA;
* antigen density;
* plate;
* bootstrap chunk;
* imaging field.

Não executar milhares de bootstraps em um único processo.

---

# 7. Workflow manager

Minha recomendação é **Snakemake** para o MVP porque:

* o projeto é Python-centric;
* a maior parte do código já existe como scripts Python;
* as unidades de execução são naturalmente files/rules;
* precisamos de profiles local e Slurm;
* recursos podem ser declarados por job.

Não introduzir simultaneamente Snakemake e Nextflow. Isso duplicaria manutenção.

## Alvos principais

```text
make bootstrap
make test
make data-manifest
make evidence-graph
make isci-oof
make systems
make libraries
make public-screens
make report
```

Internamente:

```text
Snakemake:
    download
    verify
    snapshot_api
    normalize
    harmonize
    analyze
    validate
    figure
    manifest
```

---

# 8. Ambientes e containers

Não usar um único environment gigante.

## Ambientes separados

```text
analytics
singlecell
screen
pmhc
imaging
rstats
workflow
```

### Analytics

* pandas;
* numpy;
* scipy;
* scikit-learn;
* statsmodels;
* pyarrow;
* pydantic/pandera;
* plotting.

### Single-cell

* anndata;
* scanpy;
* scvi-tools;
* torch;
* CUDA pinada.

### pMHC

* MHCflurry;
* pVACtools se houver neoantígenos;
* parsers IEDB/VDJdb/HLA.

MHCflurry fornece predição local de ligantes MHC-I e exige download explícito dos modelos/datasets. O repositório recomenda pin de versão e bundle; em vez de instalar indiscriminadamente `latest`, devemos congelar a versão e o checksum do modelo usado.

### Imaging

* stack de segmentação validado;
* OME-Zarr;
* tracking;
* feature extraction;
* QC visual amostral.

## Regras

* nada com tag `latest` em análise confirmatória;
* CUDA validada contra o driver;
* container por release;
* hash do container;
* hash dos modelos;
* Git SHA;
* config;
* seed;
* data hashes.

---

# 9. Plano de dados

## 9.1 Tier 0 — anchors existentes

Usar imediatamente:

| Dataset                  | Função                             |
| ------------------------ | ---------------------------------- |
| Marson CD4 DE/pseudobulk | prior T-side e ISCI                |
| Schmidt GSE190604        | CRISPRa T-cell                     |
| Frangieh Perturb-CITE    | tumor-side RNA/protein             |
| Belk                     | cromatina e persistência           |
| THP-1 GSE221321          | sinal imune não-T                  |
| CAR-T atlas              | estado/estrutura; não valida TCR-T |
| GSE208052/GSE223655      | direção memory/stem                |

Os dados públicos devem ser baixados diretamente pelo servidor, e não copiados a partir do laptop. O próprio plano de infraestrutura já adota essa estratégia para S3, GEO e Zenodo.

## 9.2 Tier 1 — TCR–pMHC

### IEDB

Usar para:

* epítopos;
* HLA;
* ensaios de binding;
* ensaios T-cell;
* TCRs quando disponíveis.

A Query API do IEDB deve ser tratada como snapshot versionado, não como chamada live.

### VDJdb

Usar para:

* CDR3 α/β;
* V/J;
* epítopo;
* MHC;
* referência;
* confidence.

### IPD-IMGT/HLA

Usar para:

* nomenclatura;
* sequências;
* alinhamentos;
* aliases.

Os dados são disponibilizados por FTP e GitHub, com branches/releases; a licença informada é Creative Commons Attribution-NoDerivs, portanto a versão e os termos devem entrar no manifest. ([EMBL-EBI][3])

### MHCflurry

Usar para:

* predição de apresentação MHC-I;
* comparação entre HLAs;
* antigen-density/presentation priors;
* candidatos de off-target peptide similarity.

Não usar predição in silico como substituto de immunopeptidomics ou pMHC measurement.

## 9.3 Tier 2 — seleção do tumor

### DepMap/CCLE

Usar para:

* expressão de antígeno;
* HLA/APM;
* dependências;
* escolha de linhas;
* fitness de genes.

O portal recomenda bulk downloads em vez de scraping. ([depmap.org][4])

### GDC

Usar para:

* prevalência de antígeno;
* HLA/APM;
* mutações;
* CNV;
* expressão;
* contexto de doença.

A GDC API oferece endpoints para projetos, casos, arquivos, annotations e download, usando tokens nos dados controlados. ([docs.gdc.cancer.gov][5])

### cBioPortal

Usar para:

* coortes;
* mutações;
* copy number;
* molecular profiles;
* dados clínicos disponíveis.

O cBioPortal oferece REST API e clientes Python/R; devemos congelar `study_id`, molecular profiles e sample lists em cada snapshot. ([cBioPortal Docs][6])

### CELLxGENE Census

Usar para:

* expressão normal;
* referências de cell type;
* eixos;
* avaliação de possíveis tecidos off-target;
* slices maiores que a memória.

O Census suporta slicing por metadata/gene, acesso cloud e criação de AnnData, inclusive para dados maiores que a memória. Deve-se pinçar uma release LTS, não usar a release semanal flutuante. ([Chan Zuckerberg Initiative][7])

## 9.4 Tier 3 — controlled

* dbGaP;
* EGA;
* Synapse;
* dados institucionais;
* patient-derived data;
* prospective clinical samples.

dbGaP separa acesso aberto e controlado; dados individuais requerem autorização do Data Access Committee e Data Use Certification compatível com o consentimento. ([NCBI][8])

Synapse pode ser usado para files, tables, datasets, access control e provenance por IDs versionados. ([python-docs.synapse.org][9])

## Limitação central

Entre os datasets atualmente mapeados:

* Marson perturba o lado T;
* Frangieh perturba o lado tumoral com co-cultura;
* os cohorts clínicos são observacionais;
* as telas tumorais são unilaterais.

Portanto, **os dados públicos podem construir priors e selecionar a biblioteca, mas não substituem a geração prospectiva da matriz T-cell perturbation × tumor perturbation**.

---

# 10. Registry de datasets

Toda entrada precisa ter:

```yaml
id:
title:
source_type:
accession:
source_url:
access:
controlled:
license:
expected_bytes:
checksum:
raw_format:
adapter:
unit_of_inference:
primary_use:
limitations:
status:
```

Exemplo:

```yaml
- id: schmidt_gse190604
  source_type: geo_sra
  accession: GSE190604
  controlled: false
  raw_format: matrix_or_fastq
  adapter: schmidt
  unit_of_inference: target_well_condition
  primary_use: T-side modality transfer
  limitations: targeted screen; limited positives
  status: available
```

Separar:

```text
datasets_public.yaml
datasets_controlled.yaml
```

O segundo fica no enclave institucional e não entra no Git público.

---

# 11. APIs

## Princípio

Nunca consultar APIs live durante o teste confirmatório.

Usar:

```text
API
→ raw JSON snapshot
→ normalized Parquet
→ analysis
```

Salvar:

* query;
* body;
* endpoint;
* data de recuperação;
* headers;
* paginação;
* checksum;
* schema version;
* erro/retry log.

## APIs prioritárias

| API              | Uso                                  |
| ---------------- | ------------------------------------ |
| NCBI E-utilities | GEO/SRA/PubMed discovery             |
| Zenodo           | records, files e releases            |
| CELLxGENE        | referências single-cell              |
| Open Targets     | tractability e evidência alvo–doença |
| ChEMBL           | compounds, targets, MOA e activity   |
| IEDB             | epítopos, HLA e TCR assays           |
| GDC              | contexto tumoral                     |
| cBioPortal       | cohorts moleculares                  |
| Synapse          | datasets e provenance                |
| VDJdb Git        | TCR specificity                      |
| IMGT/HLA Git/FTP | nomenclatura e sequência             |

NCBI E-utilities fornece uma interface estruturada e estável para busca e recuperação em bancos Entrez. ([NCBI][10])

Zenodo REST suporta busca de records, manipulação de files e depósito/publicação de research outputs; publicação exige token. ([developers.zenodo.org][11])

Open Targets oferece GraphQL para targets individuais, mas recomenda bulk downloads ou BigQuery para consultas sistemáticas de múltiplos alvos. ([Open Targets Platform][12])

ChEMBL mantém web services documentados para dados e ferramentas cheminformáticas. ([ChEMBL][13])

## Estrutura

```text
src/rescuemap/apis/
├── base.py
├── ncbi.py
├── zenodo.py
├── cellxgene.py
├── opentargets.py
├── chembl.py
├── iedb.py
├── hla.py
├── vdjdb.py
├── gdc.py
├── cbioportal.py
└── synapse.py
```

Interface:

```python
class DataSourceClient:
    def fetch_raw(self, request): ...
    def normalize(self, raw): ...
    def validate(self, table): ...
    def write_snapshot(self, raw, metadata): ...
```

Tokens:

```text
NCBI_API_KEY
ZENODO_TOKEN
GDC_TOKEN_FILE
SYNAPSE_AUTH_TOKEN
CBIOPORTAL_TOKEN
```

Nunca em Git ou notebook.

---

# 12. Novo repositório

```text
TCR-RescueMap/
├── README.md
├── pyproject.toml
├── uv.lock
├── Makefile
├── Snakefile
├── config/
│   ├── datasets_public.yaml
│   ├── systems.yaml
│   ├── libraries.yaml
│   ├── endpoints.yaml
│   └── preregistration.yaml
├── contracts/
│   ├── context_schema.yaml
│   ├── perturbation_schema.yaml
│   ├── outcome_schema.yaml
│   ├── interaction_schema.yaml
│   └── claim_schema.yaml
├── profiles/
│   ├── local/
│   ├── slurm_cpu/
│   ├── slurm_highmem/
│   └── slurm_gpu/
├── envs/
├── containers/
├── src/rescuemap/
│   ├── apis/
│   ├── io/
│   ├── isci/
│   ├── screens/
│   ├── interactions/
│   ├── pmhc/
│   ├── singlecell/
│   ├── imaging/
│   ├── safety/
│   ├── statistics/
│   └── reports/
├── tests/
├── reports/
├── results/
└── figures/
```

---

# 13. Roadmap de execução

## Wave A — fundação

### Entregas

* tag/release do ISCI;
* novo repositório;
* OOF `M→M+C`;
* schemas;
* registry;
* API clients;
* environments;
* containers;
* Slurm smoke test;
* synthetic pipeline;
* claim ledger.

### Gate

```text
pipeline reproduzível
sem leakage
manifests válidos
HPC validado
```

## Wave B — discovery in silico

Executar em paralelo:

### Track T-side

* ISCI candidates;
* external functional hits;
* controls;
* modalidade apropriada;
* direction;
* essentiality;
* safety flags.

### Track tumor-side

* screens públicos;
* APM;
* IFN;
* death;
* adhesion;
* autophagy;
* tumor-expression context.

### Track TCR/pMHC

* IEDB;
* VDJdb;
* IMGT/HLA;
* MHCflurry;
* literatura;
* IP/reagent access.

### Saída

```text
systems_selection_matrix.csv
tcell_library_v0.csv
tumor_library_v0.csv
control_set.csv
power_simulation.json
```

## Wave C — qualificação do ensaio

Antes de qualquer screen:

1. TCR expression/KI;
2. antigen dependency;
3. HLA dependency;
4. curva E:T;
5. curva de pMHC;
6. antigen-null;
7. HLA/B2M-null;
8. peptide-pulse bypass;
9. repeated challenge;
10. live imaging;
11. editing efficiency;
12. estimativa de variância.

### Gate

O ensaio precisa ter:

* dynamic range;
* baixa saturação;
* reproducibilidade por doador;
* controle de crescimento tumoral;
* resposta HLA/antígeno-dependente;
* endpoint funcional robusto.

## Wave D — telas unilaterais

### T-side

Estimar:

[
\tau_T(g_T|c)
]

### Tumor-side

Estimar:

[
\tau_C(g_C|c)
]

Selecionar anchors por diversidade mecanística, não apenas pelos maiores efeitos.

## Wave E — interação

### Piloto recomendado

Não iniciar genome-wide.

Começar com algo como:

```text
8–12 T-cell perturbations
×
8–12 tumor perturbations
```

Incluindo:

* controles positivos;
* nulls;
* um mecanismo APM;
* IFN;
* adesão;
* morte;
* exaustão/persistência;
* rheostat TCR;
* candidato novo.

Depois escalar via anchor-by-library.

### Análise

```text
Y ~ gT + gC + gT:gC
  + antigen_density
  + TME
  + challenge_round
  + time
  + (1|donor)
  + (1|tumor_model)
  + (1|batch)
  + (1|guide_T)
  + (1|guide_C)
```

## Wave F — mecanismo e segurança

* guides independentes;
* rescue constructs;
* live imaging;
* phospho-flow;
* scRNA/CITE;
* ATAC/SLAM-seq conforme candidato;
* normal tissue panel;
* peptide similarity;
* alloreactivity;
* transformation/AICD risk.

## Wave G — tradução

* patient-derived tumor;
* organoides;
* marrow models;
* co-cultura mieloide;
* validação ex vivo;
* laboratório independente;
* release pública.

---

# 14. Primeiro sprint concreto

O primeiro sprint deve terminar com execução real, não apenas documentação.

| Item             | Done quando                              |
| ---------------- | ---------------------------------------- |
| Congelar ISCI    | tag + manifest + checksums               |
| Criar novo repo  | estrutura mínima e proteção de branch    |
| Configurar HPC   | CPU/GPU/scratch confirmados              |
| Criar containers | smoke tests local/HPC                    |
| Dataset registry | 100% dos anchors registrados             |
| API registry     | clients básicos funcionando              |
| OOF incremental  | predições OOF e bootstrap por blocos     |
| System matrix    | 2–3 sistemas comparados                  |
| Reagent gap list | sequência, HLA, tumor e IP identificados |
| Evidence graph   | T-side e tumor-side                      |
| Library v0       | genes, modalidade, controles e direção   |
| Pilot power plan | tamanho baseado em variância prevista    |

## Critério de saída

O sprint produz um relatório respondendo:

1. Qual TCR podemos realmente usar?
2. Qual HLA e tumor?
3. Qual antígeno endógeno?
4. Quais reagentes faltam?
5. Qual compute está operacional?
6. Quais dados foram baixados e verificados?
7. Quais genes entram no piloto?
8. Qual o tamanho do primeiro experimento?
9. Qual é o endpoint primário?
10. Qual efeito mínimo será considerado resgate?

---

# 15. O que pode começar apenas com compute

Sem wet-lab, já podemos executar:

* OOF ISCI;
* registry completo;
* evidence graph;
* API snapshots;
* harmonização dos screens públicos;
* taxonomia tumoral R0–R7;
* seleção das linhas tumorais;
* seleção de TCR/HLA;
* bibliotecas v0;
* power simulations;
* interaction-model simulation;
* dashboards sintéticos;
* pipeline de provenance;
* preregistration/SAP.

Isso cria todo o plano de voo.

Mas a descoberta central — **resgate bidirecional** — exige dados prospectivos, porque os datasets públicos atualmente mapeados não contêm a matriz pareada `gT × gC` com TCR/pMHC definido e endpoints funcionais repetidos.

---

# 16. Sequência de investimento

## Primeiro investir em

1. reagente TCR/pMHC;
2. qualificação do ensaio;
3. repeated challenge;
4. live imaging;
5. CRISPRi/a;
6. storage;
7. pipeline e estatística;
8. tela unilateral.

## Não investir primeiro em

* foundation model grande;
* Marson cell-level completo;
* dual-genome-wide screen;
* scRNA de todos os pares;
* multiome de descoberta;
* grande cohort clínico heterogêneo;
* dashboard sofisticado antes do piloto.

A máquina de 128 GB/48 GB é suficiente para iniciar. O primeiro gargalo é **biológico e operacional**, não computacional. O compute maior se torna decisivo quando entrarem:

* imagem em escala;
* scRNA/CITE dos pares;
* multiome;
* Marson cell-level;
* análise prospectiva de pacientes.

O próximo marco objetivo deve ser um **Readiness Report v1** contendo o OOF ISCI, o sistema TCR/pMHC escolhido, o registry verificado, a biblioteca piloto, a simulação de potência e o protocolo do primeiro ensaio bidirecional.

[1]: https://slurm.schedmd.com/documentation.html "Slurm Workload Manager - Documentation"
[2]: https://docs.aws.amazon.com/batch/latest/userguide/what-is-batch.html "What is AWS Batch? - AWS Batch"
[3]: https://www.ebi.ac.uk/ipd/imgt/hla/download/ "IPD-IMGT/HLA Database"
[4]: https://depmap.org/portal/download/ "DepMap — Verification"
[5]: https://docs.gdc.cancer.gov/API/Users_Guide/Getting_Started/ "Getting Started - GDC Docs"
[6]: https://docs.cbioportal.org/web-api-and-clients/ "API and API Clients"
[7]: https://chanzuckerberg.github.io/cellxgene-census/ "CZ CELLxGENE Discover Census — cellxgene-census  documentation"
[8]: https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/about.html "www.ncbi.nlm.nih.gov"
[9]: https://python-docs.synapse.org/ "Home - Synapse Python/Command Line Client Documentation"
[10]: https://www.ncbi.nlm.nih.gov/books/NBK25501/ "Entrez® Programming Utilities Help - NCBI Bookshelf"
[11]: https://developers.zenodo.org/ "Developers | Zenodo"
[12]: https://platform-docs.opentargets.org/data-access/graphql-api "GraphQL API | Open Targets Platform Documentation"
[13]: https://chembl.gitbook.io/chembl-interface-documentation/web-services "Web Services | ChEMBL Interface Documentation"
