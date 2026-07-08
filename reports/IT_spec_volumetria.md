# Especificação de infraestrutura — projeto ISCI (Perturb-seq / imunologia computacional)

**Para:** equipe de TI / infraestrutura
**De:** Abel Costa (IDOR) — projeto de análise de dados de perturbação single-cell
**Pedido:** acesso a uma máquina (servidor/HPC ou VM) para processar datasets que
não cabem no laptop atual (Mac, 24 GB RAM). Abaixo, o que precisamos e por quê.

---

## 1. Resumo em uma linha

Preciso de acesso SSH a uma máquina Linux com **≥128 GB de RAM, GPU e disco de
trabalho**, com saída de internet para repositórios públicos (AWS S3, GEO, Zenodo).
Uso intermitente (rodadas de horas a poucos dias), não 24/7.

> **A máquina disponível (128 GB RAM + GPU 48 GB) atende bem.** Não é treino de IA —
> é processamento/análise de dados single-cell.

## 1a. Sobre transferência de dados — NÃO há upload do meu notebook

O ponto mais importante para o dimensionamento: **os dados não são transferidos da
minha máquina para o servidor.** Eles são baixados **diretamente dos repositórios
públicos** (AWS S3, GEO/NCBI, Zenodo) pela própria máquina, via internet. Ou seja:

- Não existe transferência de TBs saindo do meu notebook (o gargalo de "3 dias" não se aplica).
- O servidor puxa os arquivos direto da fonte pública; dentro de um datacenter com boa
  banda isso é rápido.
- O volume de trabalho imediato é pequeno (~17 GB + ~44 GB). Só a resolução
  célula-a-célula completa chega a ~1,7 TB — e mesmo essa vem do S3 público direto para o servidor.

## 2. Por que o laptop não basta

A análise principal já roda localmente porque uso uma forma **resumida** dos dados
(estatísticas por perturbação, ~17 GB). Mas os dados **em nível de célula única**
— necessários para as análises de expansão — são muito maiores:

| Conjunto de dados | Tamanho por arquivo | Total | Cabe em 24 GB? |
|---|---|---|---|
| Marson CD4+ (nível de célula, 12 arquivos) | **118,6 – 172,8 GB cada** | **~1,7 TB** | Não |
| Perturb-seq genome-wide (K562/RPE1) | ~8,8 GB (nível de célula) | — | No limite / não |
| Atlas CAR-T completo | ~15,5 GB | — | Parcial |

Ler e normalizar um arquivo de 150 GB exige memória de trabalho de várias vezes o
seu tamanho em disco — daí o pedido de 128–256 GB de RAM.

## 3. Especificação mínima vs recomendada

| Recurso | Mínimo funcional | Máquina disponível (128 GB + GPU 48 GB) | Motivo |
|---|---|---|---|
| **RAM** | 128 GB | **128 GB ✓ atende** | Carregar/normalizar matrizes single-cell |
| **CPU** | 16 núcleos | (confirmar nº de cores) | Leitura de h5ad e inferência de rede são multi-thread |
| **GPU** | 1× (24 GB VRAM) | **48 GB ✓ folgado** | scVI / SCENIC+ / modelos de perturbação |
| **Disco scratch** | 500 GB–1 TB | (confirmar espaço livre) | Trabalho imediato ~60 GB; célula-a-célula completa ~1,7 TB (opcional) |
| **Rede** | saída HTTPS/S3 | (confirmar allowlist) | **Baixar dos repos públicos — não upload do notebook** |
| **SO** | Linux x86-64 | (confirmar) | Compatibilidade com conda/Python |

## 4. Software (eu instalo, não precisa de licença)

- **Conda/Miniconda** (ambiente Python 3.12) — eu gerencio meus próprios ambientes.
- Bibliotecas open-source: scanpy, anndata, scvi-tools, numpy/scipy, pytorch (para GPU).
- Nenhum software proprietário ou licenciado é necessário.
- Idealmente: acesso SSH (e, se possível, um agendador tipo SLURM se for um cluster
  compartilhado — mas uma VM dedicada com SSH também serve).

## 5. Rede — domínios de saída necessários

Se houver firewall/allowlist, preciso de saída para:
- `*.s3.amazonaws.com` (dados públicos da CZI/Marson)
- `ftp.ncbi.nlm.nih.gov` / `www.ncbi.nlm.nih.gov` (GEO)
- `zenodo.org` (datasets harmonizados)
- `conda.anaconda.org` / `pypi.org` (instalação de bibliotecas)

Nenhum dado de paciente sai da instituição — todos os conjuntos são **públicos e
de-identificados** (screens de perturbação em linhagens/células primárias de doadores
anônimos).

## 6. Padrão de uso e segurança

- **Uso intermitente:** rodadas de processamento de algumas horas a poucos dias,
  não uso contínuo. Uma VM que eu possa ligar sob demanda é ideal.
- **Sem dados sensíveis:** trabalho apenas com dados públicos de repositórios
  científicos; nenhum prontuário ou dado identificável é usado ou armazenado.
- **Isolamento:** um ambiente conda/usuário próprio é suficiente; não preciso de root
  além de instalar meus ambientes no meu home.

## 7. O que isso habilita (justificativa científica)

Com essa máquina eu consigo: (a) processar os 22 milhões de células do screen
Marson em resolução de célula única; (b) rodar inferência de rede regulatória em
escala; (c) aplicar modelos de fundação de perturbação com GPU; (d) validar se as
assinaturas de RNA viram fenótipo de proteína (CITE-seq/CyTOF). Sem ela, fico
limitado às formas resumidas dos dados.

---

**Pergunta objetiva para a TI:** vocês conseguem me dar acesso a uma máquina com
~128–256 GB RAM, 16+ cores, 1 GPU e ~2 TB de scratch, com SSH e saída de rede para
os domínios acima? Uso intermitente, só dados públicos.
