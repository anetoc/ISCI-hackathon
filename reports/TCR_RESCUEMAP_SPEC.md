> **Status: forward research program (Paper 2 / multi-year experimental roadmap), NOT hackathon-submission scope.**
> The only computationally implementable Phase-0 item — the out-of-fold hardening of the M→M+C incremental test —
> has been executed this session; see `outputs/isci_oof_incremental.json` (OOF gain +0.305 [+0.131,+0.603], within-block perm p=0.002).
> All wet-lab phases (1–11: TCR–pMHC systems, paired CRISPR screens, imaging, organoids, safety) are future work.

---

# TCR-RescueMap v0.1
## Especificação científica e plano em fases para o Mapa de Controlabilidade Bidirecional TCR–Tumor

**Status:** especificação de desenvolvimento, pronta para virar `reports/TCR_RESCUEMAP_SPEC.md` no repositório.  
**Relação com ISCI:** o ISCI/CCI corrigido permanece como prior de controlabilidade intrínseca da célula T; o novo produto testa causalmente se uma engenharia da célula T consegue resgatar um mecanismo de resistência tumoral em um contexto TCR–peptídeo–HLA definido.  
**Nome público recomendado:** **TCR-RescueMap**.  
**Nome formal:** **Bidirectional TCR–Tumor Controllability Map**.

---

# 1. Decisão estratégica

O projeto não deve evoluir para um ranking maior de genes. Deve evoluir para um **mapa causal de interações entre dois lados da terapia**:

1. **lado efetor:** alterações na célula TCR-T que modulam reconhecimento, sinalização, persistência, sinapse, killing e resistência à supressão;
2. **lado tumoral:** alterações que geram escape por antígeno/peptídeo–HLA, apresentação, IFN, adesão, resistência à morte, metabolismo ou microambiente;
3. **interação:** se uma alteração na célula T resgata, não altera ou piora o fenótipo causado por uma alteração tumoral;
4. **contexto:** TCR, peptídeo, HLA, densidade de pMHC, linhagem tumoral, doador, pressão imune, microambiente e tempo;
5. **segurança:** se o resgate mantém especificidade, não aumenta reconhecimento de tecido normal e não introduz risco biológico desproporcional.

O produto final não será um super-score. Será uma **matriz adjudicada** que responde:

> Para cada mecanismo de resistência tumoral, qual engenharia da célula T consegue restaurar controle tumoral, em quais contextos, com qual mecanismo e com qual margem de segurança?

---

# 2. Claim central e limites

## 2.1 Claim-alvo

> Em sistemas TCR–peptídeo–HLA definidos, os efeitos de perturbações na célula T e no tumor não são apenas aditivos. Existem interações de resgate, antagonismo e não-resgatabilidade que podem ser medidas causalmente e usadas para escolher entre engenharia da célula T, restauração do tumor/APM, combinação farmacológica ou troca de modalidade terapêutica.

## 2.2 O que o programa não deve alegar antes da validação

- que existe um controlador universal de resposta;
- que um score transcricional prediz resposta clínica;
- que todo mecanismo de escape pode ser vencido pela engenharia da célula T;
- que um gene com bom efeito in vitro é um alvo terapêutico seguro;
- que CAR-T, TCE, TIL e TCR-T têm mecanismos de resistência intercambiáveis;
- que ausência de significância equivale a não-resgatabilidade;
- que correlação celular equivale a replicação biológica;
- que um resultado em um único TCR/HLA/antígeno generaliza para outros receptores.

---

# 3. Relação com o ISCI corrigido

O resultado `M → M+C` é o **anchor metodológico**, não o endpoint do novo programa.

## 3.1 Uso do ISCI no TCR-RescueMap

O ISCI fornece um prior para selecionar genes da célula T com:

- efeito detectável;
- especificidade por eixo;
- reprodutibilidade entre doadores;
- direção funcional anotada;
- risco/targetability separado do controllership.

No novo programa, esses genes entram como **candidatos**, mas só são promovidos a mecanismo de resgate após um teste pareado T-cell × tumor.

## 3.2 Hardening obrigatório do resultado incremental

Antes de utilizar `+0,357` como efeito confirmatório, implementar uma versão out-of-fold do teste:

- unidade de split = bloco de matching, não gene isolado;
- `model0 = label ~ M`;
- `model1 = label ~ M + S_resid + R_resid`;
- predições sempre out-of-fold;
- seleção de negativos, residualização, escalonamento e ajuste feitos apenas no training fold;
- bootstrap dos blocos completos, refazendo todo o procedimento;
- modelo fixo ou regularização fixada antes do teste;
- reportar AUPRC aparente, AUPRC OOF e optimism-corrected AUPRC separadamente.

**Gate:** o resultado atual pode permanecer como estimativa de desenvolvimento; o claim confirmatório usa a estimativa OOF.

---

# 4. Unidade causal e notação

## 4.1 Contexto experimental

Definir cada contexto como:

```text
c = {
  tcr_id,
  peptide_id,
  hla_allele,
  tumor_lineage,
  tumor_model,
  antigen_density,
  pmhc_density,
  t_cell_donor,
  cd4_cd8_composition,
  effector_target_ratio,
  tme_condition,
  challenge_round,
  timepoint,
  batch
}
```

## 4.2 Perturbações

- `gT`: perturbação na célula T;
- `gC`: perturbação na célula tumoral;
- `0`: controle não-targeting/safe-harbor apropriado;
- modalidade: KO, CRISPRi, CRISPRa, base editing, knock-in, intervenção farmacológica ou intervenção transitória de manufatura.

## 4.3 Outcome vetorial

Não colapsar tudo em um único score. Manter:

```text
Y = [
  tumor_control,
  time_to_first_kill,
  serial_killing,
  contact_to_kill_time,
  synapse_dwell_time,
  t_cell_expansion,
  t_cell_persistence,
  activation_induced_cell_death,
  cytokine_polyfunctionality,
  exhaustion_state,
  memory_state,
  tumor_regrowth,
  normal_tissue_killing,
  cross_reactivity
]
```

### Endpoint primário recomendado

`DurableTumorControl_AUC`: área sob a curva de células tumorais viáveis durante desafio inicial + desafios repetidos, normalizada para crescimento tumoral sem efetor e para controle TCR-T não perturbado.

### Endpoints coprimários mecanísticos

- serial killing por célula T;
- persistência/expansão após reexposição;
- tempo de contato até morte;
- escape clonal após múltiplos desafios.

---

# 5. Estimandos causais

## 5.1 Efeito intrínseco da célula T

```text
Tau_T(gT | c) = E[Y(gT, 0, c) - Y(0, 0, c)]
```

Pergunta: a engenharia melhora o fenótipo quando o tumor não contém o mecanismo de escape?

## 5.2 Efeito de escape tumoral

```text
Tau_C(gC | c) = E[Y(0, gC, c) - Y(0, 0, c)]
```

Pergunta: qual é o dano causado pela alteração tumoral sobre o controle mediado por TCR-T?

## 5.3 Interação bidirecional

```text
I(gT, gC | c) =
Y(gT, gC, c)
- Y(gT, 0, c)
- Y(0, gC, c)
+ Y(0, 0, c)
```

Interpretação:

- `I > 0`: resgate/sinergia;
- `I ≈ 0`: efeitos aproximadamente aditivos ou independentes;
- `I < 0`: antagonismo ou piora;
- o sinal deve ser definido de modo que valores maiores representem benefício.

## 5.4 Fração de resgate

Para um `gC` que reduz controle tumoral:

```text
RescueFraction(gT, gC | c) =
[Y(gT,gC,c) - Y(0,gC,c)] /
[Y(0,0,c) - Y(0,gC,c)]
```

- `0`: nenhum resgate;
- `1`: restauração ao nível do controle;
- `>1`: super-resgate;
- valores negativos: piora.

O threshold de resgate relevante deve ser definido após o piloto e congelado antes da tela confirmatória.

## 5.5 Resgatabilidade do mecanismo tumoral

```text
Rescuability(gC | C) = max_gT robust_lower_CI(RescueFraction)
```

Não usar apenas o maior point estimate. Usar limite inferior robusto em contextos de validação.

## 5.6 Robustez e fragilidade da engenharia T

```text
Robustness(gT) = proporção de contextos independentes com efeito benéfico
Fragility(gT)  = heterogeneidade entre TCR, HLA, densidade, doador e linhagem
```

## 5.7 Índice de troca de modalidade

Uma alteração tumoral recebe classe de **modality switch** quando:

- destrói reconhecimento por perda de antígeno/HLA/APM;
- nenhuma intervenção T-cell-intrinsic atinge o efeito mínimo relevante;
- a equivalência/upper bound exclui resgate relevante;
- restauração de antígeno/HLA ou troca de alvo resgata o fenótipo.

Isso aponta para TCR alternativo, CAR/TCE HLA-independente, restauração do APM ou combinação, não para “engenharia T mais forte”.

---

# 6. Ontologia dos mecanismos de resistência

| Classe | Mecanismo | Exemplos de leitura | Decisão potencial |
|---|---|---|---|
| R0 | ausência de reconhecimento | antígeno, HLA, B2M, TAP, pMHC | retargeting/restauração; possível troca de modalidade |
| R1 | contato/sinapse insuficiente | CD58, ICAM1, integrinas, dwell time | engenharia de adesão/costimulação |
| R2 | threshold de sinalização | baixa densidade pMHC, afinidade, CD8-dependência | ajuste fino de TCR/sinalização |
| R3 | resistência à execução de morte | FAS/TNF/TRAIL, apoptose, antiapoptóticos | combinação ou rota alternativa de killing |
| R4 | resposta adaptativa a citocinas | IFNGR/JAK/STAT, TNF/NF-κB | restaurar sensibilidade tumoral ou bypass |
| R5 | falha da célula T | exaustão, AICD, metabolismo, perda de memória | engenharia/manufatura T-cell-intrinsic |
| R6 | microambiente | TGFβ, adenosina, hipóxia, lactato, mieloides | resistência contextual/combinatória |
| R7 | heterogeneidade/evolução | subclones antigen-low/negative, escape temporal | multi-targeting e monitoramento evolutivo |

---

# 7. Plano em fases

## Fase 0 — Lock científico, estatístico e de claims

### Objetivo
Criar uma base auditável antes de novos dados.

### Tarefas

1. Implementar `incremental_auprc_oof`.
2. Criar `match_block_id` para cada positivo + seus negativos pareados.
3. Fazer grouped leave-one-block-out ou repeated grouped CV.
4. Refazer matching/residualização dentro do fold.
5. Adicionar bootstrap hierárquico de blocos.
6. Criar permutation test dentro de blocos.
7. Congelar SAP v1 do TCR-RescueMap.
8. Criar um novo claim ledger separado do hackathon.
9. Criar release versionada do ISCI corrigido.
10. Remover do caminho crítico todos os stubs legados.

### Entregáveis

- `reports/TCR_RESCUEMAP_SAP.md`;
- `reports/ISCI_V2_RESULT_LOCK.md`;
- `outputs/isci_oof_incremental.json`;
- `tests/test_incremental_oof.py`;
- workflow CI em dados sintéticos;
- release + DOI/arquivo imutável.

### Gate

- nenhuma feature calculada usando informação do fold de teste;
- predições OOF para todos os genes;
- manifests e hashes reproduzíveis;
- claim diferencia claramente desenvolvimento, validação interna e validação externa.

---

## Fase 1 — Seleção formal dos sistemas TCR–pMHC

### Objetivo
Escolher modelos que permitam decompor mecanismos universais e contexto-específicos.

### Estratégia
Selecionar no mínimo:

1. **um sistema sólido clinicamente ancorado**, preferencialmente MAGE-A4/HLA-A*02;
2. **um sistema hematológico**, priorizando PRAME, WT1 ou HA-1 conforme acesso a TCR validado, HLA e modelos tumorais;
3. opcionalmente um sistema viral limpo, como HPV E7/HLA-A*02, para calibrar perda de HLA/APM.

### Scorecard de seleção

| Domínio | Critério |
|---|---|
| Reagente | TCR com sequência, afinidade, especificidade e manufacturing conhecidos |
| Biologia | antígeno endógeno e HLA definidos |
| Dinâmica | faixa ampla de pMHC/antígeno |
| Modelos | ≥2 linhas ou modelos tumorais por linhagem |
| Controle | antigen-null, HLA-null e peptide-pulse disponíveis |
| Segurança | painel normal e cross-reactivity factíveis |
| Escala | compatível com pooled/arrayed screen |
| Translação | doença e mecanismo clinicamente relevantes |

### Experimentos de qualificação

- dose-resposta por E:T;
- curva de densidade antigênica/pMHC;
- killing com antígeno endógeno;
- peptide pulse como bypass do processamento;
- bloqueio de HLA e TCR;
- TCR irrelevante;
- repeated challenge;
- painel mínimo de células normais.

### Entregáveis

- `config/tcr_systems.yaml`;
- `outputs/system_selection_matrix.csv`;
- SOP de geração do produto TCR-T;
- curvas de dynamic range;
- decisão go/no-go por sistema.

### Gate

O sistema avança somente se apresentar:

- killing antígeno/HLA-dependente;
- janela dinâmica que não esteja saturada;
- especificidade demonstrável;
- repetibilidade entre doadores;
- viabilidade para escalonamento.

---

## Fase 2 — Engenharia da plataforma experimental

### Objetivo
Construir uma plataforma que separe reconhecimento, contato, killing e persistência.

### Célula T

- inserção padronizada do TCR, idealmente no locus TRAC;
- controle da expressão e mispairing;
- CRISPRi/CRISPRa como modalidades primárias para rheostats/genes essenciais;
- KO reservado para genes seguros e hipóteses específicas;
- barcodes compatíveis com pooled readout;
- lotes de múltiplos doadores balanceados.

### Tumor

- Cas9/KRAB/VPR estáveis conforme modalidade;
- repórter nuclear fluorescente para contagem e morte;
- identidade clonal e barcode;
- medição de antígeno, HLA e pMHC;
- controles isogênicos.

### Formatos de ensaio

1. 2D de alto throughput;
2. repeated challenge;
3. 3D/organoide para validação;
4. live imaging para tempo de contato e serial killing;
5. flow/CITE-seq para estado T e tumoral.

### QC obrigatório

- eficiência de edição por guide;
- expressão do TCR;
- viabilidade basal;
- crescimento tumoral sem T cells;
- composição CD4/CD8;
- eficiência de transdução;
- batch e donor tracking;
- HLA/antígeno/pMHC.

### Entregáveis

- SOPs;
- painéis de flow;
- pipeline de imagem;
- `contracts/assay_qc_schema.yaml`;
- controles positivos/negativos congelados.

### Gate

- Z-factor/dynamic range adequado no endpoint primário;
- concordância entre pelo menos dois readouts;
- estabilidade entre placas e doadores;
- ausência de saturação completa.

---

## Fase 3 — Atlas de evidência e desenho das bibliotecas

### Objetivo
Transformar literatura, ISCI e telas públicas em bibliotecas pequenas, mecanisticamente balanceadas e auditáveis.

### Biblioteca T-cell-side

Incluir famílias:

- threshold/sinalização TCR;
- checkpoints negativos;
- persistência/memória;
- exaustão/diferenciação;
- cromatina;
- RNA/splicing/decay;
- metabolismo e estresse;
- sinapse/citoesqueleto;
- apoptose/AICD;
- tráfego e resistência a TME.

Combinar:

- candidatos ISCI;
- hits funcionais externos;
- controles canônicos;
- genes “wrong-way”;
- genes perigosos apenas em modalidade titratável;
- negativos expression/power-matched.

### Biblioteca tumor-side

Incluir:

- antígeno e regulação de expressão;
- HLA/B2M/APM;
- IFNγ/JAK/STAT;
- TNF/NF-κB;
- adesão/sinapse;
- apoptose e resistência à morte;
- autofagia;
- metabolismo/estresse oxidativo;
- checkpoints/citocinas;
- epigenética;
- fitness controls.

### Regras

- ≥4 guides por gene na tela de descoberta, quando possível;
- guides independentes para validação;
- CRISPRi/CRISPRa para essencialidade e dose;
- exclusão explícita de genes sem dynamic range ou readout;
- provenance por gene.

### Entregáveis

- `inputs/tcell_candidate_library.csv`;
- `inputs/tumor_candidate_library.csv`;
- evidence cards por gene;
- rationale, modality e direção esperada;
- lista de controles de mecanismo.

### Gate

Nenhum gene entra sem:

- hipótese definida;
- direção esperada ou classificação “direction unknown”;
- modalidade apropriada;
- readout capaz de falsificar a hipótese;
- risco pré-anotado.

---

## Fase 4 — Tela unilateral da célula T

### Objetivo
Estimar `Tau_T(gT|c)` antes da interação pareada.

### Contextos mínimos

- ≥3 doadores;
- dois níveis de densidade de antígeno/pMHC;
- pelo menos um desafio agudo e um repeated challenge;
- dois modelos tumorais quando possível;
- TME basal e uma pressão supressora prioritária.

### Readouts

- tumor-control AUC;
- expansão e persistência;
- killing por célula;
- AICD;
- memória/exaustão;
- citocinas;
- viabilidade sem tumor.

### Análise

- modelo por guide e gene;
- donor/tumor/batch como efeitos aleatórios;
- separar benefício por expansão de benefício por eficiência de killing;
- estimar heterogeneidade por contexto;
- não selecionar apenas por média global.

### Critérios de hit

- efeito consistente entre guides;
- não explicado por proliferação basal isolada;
- replicação em ≥2 doadores;
- ausência de perda grave de viabilidade;
- benefício em contexto de baixa densidade ou repeated challenge;
- direção mecanisticamente coerente ou explicitamente inesperada.

### Entregáveis

- `results/tcell_main_effects.parquet`;
- mapa context-specific;
- shortlist por mecanismo;
- lista de toxicidade/fragilidade.

### Gate

Avançam para pairing:

- hits robustos;
- hits contextuais biologicamente informativos;
- controles positivos/negativos;
- alguns nulls necessários para calibrar a matriz.

---

## Fase 5 — Tela unilateral tumoral

### Objetivo
Estimar `Tau_C(gC|c)` e construir uma taxonomia de escape.

### Desenho

- tumor perturbado + TCR-T controle;
- baixa e alta pressão efetora;
- antígeno endógeno versus peptide pulse;
- com e sem IFNγ priming;
- crescimento tumoral sem T cells em paralelo;
- repeated challenge.

### Localização mecanística por bypass

| Resultado | Interpretação provável |
|---|---|
| escape com antígeno endógeno, resgate por peptide pulse | processamento/apresentação |
| escape persiste após peptide pulse | HLA, adesão, sinalização, morte ou T-cell interaction |
| resgate por HLA/antígeno re-expression | reconhecimento perdido |
| killing reduzido com dwell time curto | sinapse/adesão |
| contato normal, morte ausente | resistência à execução |

### Critérios de hit

- efeito de escape/sensibilização além do crescimento basal;
- guides concordantes;
- reversão por rescue construct quando aplicável;
- mecanismo atribuível a uma classe R0–R7;
- replicação em modelo adicional para hits centrais.

### Entregáveis

- `results/tumor_escape_effects.parquet`;
- `results/escape_mechanism_classes.csv`;
- shortlist de anchors tumorais;
- mecanismos não avaliáveis.

### Gate

Selecionar anchors que cubram diferentes mecanismos, não apenas os hits de maior efeito.

---

## Fase 6 — Tela de interação bidirecional

### Objetivo
Estimar `I(gT,gC|c)` e `RescueFraction`.

## 6A. Estratégia anchor-by-library

### Forward screen

- tumor perturbation como anchor arrayed por poço;
- biblioteca pooled de perturbações em TCR-T;
- tumor genotype conhecido pelo poço;
- T-cell guide identificado por sequencing;
- readout de tumor sobrevivente e expansão T.

### Reciprocal screen

- T-cell perturbation como anchor arrayed;
- biblioteca pooled tumoral;
- guide tumoral identificado por sequencing.

Essa arquitetura é mais factível e auditável que tentar parear simultaneamente duas bibliotecas totalmente pooled sem identidade física confiável.

## 6B. Matriz arrayed confirmatória

Para pares prioritários:

- perturbadores independentes;
- múltiplos doadores;
- múltiplos modelos;
- live imaging;
- repeated challenge;
- rescue genético.

## 6C. Escalas de programa

- **Mínimo viável:** matriz reduzida de mecanismos representativos;
- **Padrão:** dezenas de anchors de cada lado e milhares de pares;
- **Flagship:** centenas de genes e optical/spatial pooled readout.

A escala final deve ser definida por simulação de potência com variância do piloto, não por conveniência.

### Modelo primário

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

### Gate de “resgate”

Um par só é chamado de resgate se:

1. interação positiva com FDR controlado;
2. RescueFraction acima do mínimo pré-especificado;
3. replicação em guides independentes;
4. replicação em doadores;
5. não ser explicada apenas por crescimento/viabilidade basal;
6. manter especificidade antígeno/HLA;
7. não apresentar sinal de segurança impeditivo.

### Gate de “não-resgatável”

Usar equivalência, não ausência de significância:

- upper CI abaixo do efeito mínimo relevante;
- múltiplas classes de engenharia T testadas;
- validação com bypass de antígeno/APM;
- consistência entre modelos/contextos.

### Entregáveis

- `results/pair_interactions.parquet`;
- `results/rescue_fraction.parquet`;
- matriz de heatmaps por contexto;
- classes universal/contextual/non-rescuable/antagonistic;
- preregistered confirmatory pair list.

---

## Fase 7 — Decomposição mecanística multimodal

### Objetivo
Explicar por que os pares funcionam ou falham.

### Seleção

- resgates robustos;
- resgates contextuais;
- antagonismos;
- mecanismos não-resgatáveis;
- hits novos do ISCI;
- controles canônicos.

### Readouts

1. **Reconhecimento:** pMHC quantitativo, HLA, antígeno, immunopeptidomics.
2. **Sinapse:** dwell time, área de contato, MTOC, F-actin, CD2/CD58, LFA-1/ICAM1.
3. **Sinalização:** pCD3ζ, pZAP70, pLAT, pERK, pAKT, pS6, NFAT/NF-κB/AP-1.
4. **Execução:** granzimas, perforina, FAS/TNF/TRAIL, caspases.
5. **Estado T:** scRNA, CITE, scATAC, TCR clonotype, memória/exaustão.
6. **Estado tumoral:** IFN response, APM, stress, death pathways.
7. **Tempo:** early signaling, first kill, repeated challenge, escape tardio.

### Causal mediation

Testar se o efeito do par é mediado por:

- aumento de reconhecimento;
- aumento da duração de contato;
- redução do threshold;
- aumento de persistência;
- bypass de resistência à morte;
- prevenção de adaptação tumoral.

### Entregáveis

- mechanism cards por par;
- DAG causal;
- validação por rescue/epistasis;
- manuscrito mecanístico candidato.

### Gate

Nenhum “mecanismo” é declarado apenas por enriquecimento transcricional; exigir perturbação/rescue ou readout funcional direto.

---

## Fase 8 — Segurança e especificidade

### Objetivo
Impedir que um grande resgate seja promovido se aumentar toxicidade ou risco de transformação.

### TCR safety

- painel de peptídeos semelhantes;
- normal tissue cell panel;
- HLA alleles relevantes;
- antigen-low normal cells;
- alloreactivity;
- cross-reactivity proteome-wide quando aplicável.

### Edit safety

- viabilidade e expansão sem antígeno;
- autonomia/proliferação excessiva;
- resistência à apoptose;
- instabilidade genômica;
- transformação/oncogenic-risk;
- off-target editing;
- cytokine excess;
- resposta em TCR irrelevante.

### Regra

Segurança funciona como override, não como componente ponderado de score.

### Entregáveis

- `results/safety_matrix.parquet`;
- flags de contraindicação;
- categorias: manufacturing-only, transient-only, permanent-edit-eligible, avoid.

### Gate

Somente pares com janela terapêutica demonstrável avançam.

---

## Fase 9 — Validação translacional

### Objetivo
Testar se a interação sobrevive em sistemas mais próximos de doença humana.

### Modelos

- organoides/patient-derived tumor cells;
- marrow co-culture para doenças hematológicas;
- modelos 3D e matriz extracelular;
- componentes mieloides/Tregs quando relevantes;
- PDX/humanized models apenas após validação in vitro robusta;
- amostras pareadas pré/pós-terapia, quando disponíveis.

### Estratificação biológica

Medir em cada amostra:

- antígeno;
- HLA e LOH;
- APM;
- IFN pathway;
- CD58/ICAM1;
- death pathways;
- composição do produto T;
- TCR abundance/persistence;
- microambiente.

### Objetivo clínico inicial

Não criar imediatamente um biomarcador binário. Criar uma **classificação mecanística de resistência** e verificar se a regra de resgate prevista é observada ex vivo.

### Entregáveis

- validação de pares em material independente;
- mapa de mecanismos por paciente/modelo;
- estimativa de transportabilidade;
- critérios para estudo prospectivo.

### Gate

- replicação em material biologicamente independente;
- efeito funcional, não apenas transcricional;
- contexto e limitação explicitamente documentados.

---

## Fase 10 — Produto: mapa e motor decisório

### Objetivo
Transformar resultados em recurso navegável e não em target list.

## Taxonomia final

| Classe | Significado |
|---|---|
| A | resgate robusto em múltiplos contextos |
| B | resgate contexto-específico |
| C | sensibilização tumoral; requer intervenção no tumor/combinação |
| D | não-resgatável por engenharia T testada; considerar troca de alvo/modalidade |
| E | antagonismo/wrong-way |
| F | benefício aparente, segurança impeditiva |
| G | probe-only/insuficiente |
| H | não avaliável |

### Interface

Para cada par `gT × gC` mostrar:

- main effects;
- interação;
- RescueFraction;
- IC e FDR;
- contextos testados;
- mecanismo;
- segurança;
- evidência externa;
- resultado de holdout;
- melhor próximo experimento;
- claims proibidos.

### Entregáveis

- dashboard;
- API/tabelas abertas;
- DOI/versionamento;
- evidence ledger;
- notebooks reproduzíveis;
- release de dados agregados.

---

## Fase 11 — Confirmação independente e publicação

### Objetivo
Separar descoberta de confirmação.

### Desenho

- congelar os pares antes do experimento;
- novos doadores;
- novo lote de produto;
- modelo tumoral não usado na descoberta;
- guides independentes;
- analista cego ao par quando factível;
- endpoint e efeito mínimo pré-especificados;
- laboratório independente para pelo menos um resultado central.

### Pacotes de publicação

1. **Paper de método/recurso:** mapa bidirecional, estimandos, interação e classes de resgate.
2. **Paper mecanístico:** um par novo e causalmente resolvido.
3. **Paper translacional:** classificação de resistência + validação em material de pacientes.

### Gate de sucesso científico

O programa atinge descoberta forte se demonstrar pelo menos um dos seguintes:

- um resgate robusto não previsível pelos main effects isolados;
- um mecanismo de escape formalmente não-resgatável por engenharia T-cell-intrinsic;
- uma interação dependente de pMHC/afinidade que muda a decisão terapêutica;
- uma regra reproduzível de troca entre engenharia T, combinação tumoral e modalidade HLA-independente.

---

# 8. Especificação estatística transversal

## 8.1 Unidade de inferência

- donor, tumor model, experimental run e patient-derived model;
- nunca tratar células individuais como replicatas biológicas independentes;
- single-cell entra como readout, com inferência pseudobulk/multinível.

## 8.2 Randomização e bloqueio

- randomizar posição de guides/anchors;
- bloquear por doador, tumor, E:T e lote;
- balancear controles em todas as placas;
- registrar batch antes do unblinding.

## 8.3 Multiplicidade

Estrutura hierárquica:

1. mecanismo/família;
2. gene main effect;
3. interação gene×gene;
4. contexto.

Usar FDR hierárquico e reservar a lista confirmatória antes da validação.

## 8.4 Validação

- holdout por doador;
- holdout por tumor model;
- holdout por TCR;
- holdout por densidade de antígeno;
- validação cruzada nunca dividindo poços/células do mesmo bloco entre treino e teste.

## 8.5 Heterogeneidade

Reportar:

- efeito médio;
- efeito por contexto;
- intervalos;
- `I²` ou variância entre contextos;
- proporção de contextos com direção correta;
- prediction interval para novo contexto.

## 8.6 Ausência de efeito

Usar equivalência/non-inferiority bounds para chamar não-resgate. “p>0,05” sozinho não autoriza a classe D.

## 8.7 Direcionalidade

Testes unilaterais somente quando:

- direção foi preregistrada;
- intervenção e endpoint têm sinal inequívoco;
- resultado oposto é classificado como falha/antagonismo.

---

# 9. Contratos de dados

## `contexts.parquet`

```text
context_id
tcr_id
peptide_id
hla_allele
tumor_lineage
tumor_model
antigen_density
pmhc_density
donor_id
cd4_fraction
cd8_fraction
effector_target_ratio
tme_condition
challenge_round
timepoint
batch_id
```

## `perturbations.parquet`

```text
perturbation_id
cell_side            # T or tumor
gene
modality             # KO/CRISPRi/CRISPRa/KI/drug
guide_id
dose
editing_efficiency
expression_change
essentiality_flag
safety_flag
```

## `outcomes.parquet`

```text
experiment_id
context_id
t_perturbation_id
tumor_perturbation_id
timepoint
tumor_live_count
t_cell_count
killing_rate
serial_kills
contact_to_kill
synapse_dwell
cytokines
memory_score
exhaustion_score
aicd
normal_cell_killing
```

## `interaction_results.parquet`

```text
gene_T
gene_C
context_scope
tau_T
tau_C
interaction
interaction_ci_low
interaction_ci_high
interaction_q
rescue_fraction
rescue_ci_low
rescue_ci_high
heterogeneity
replicated_donors
replicated_models
mechanism_class
safety_class
decision_class
```

## `evidence_ledger.yaml`

Para cada claim:

- claim;
- status;
- discovery evidence;
- confirmatory evidence;
- negative evidence;
- external evidence;
- not claimed;
- next falsification test.

---

# 10. Arquitetura de software recomendada

```text
TCR-RescueMap/
├── README.md
├── pyproject.toml
├── uv.lock
├── Makefile
├── config/
│   ├── tcr_systems.yaml
│   ├── contexts.yaml
│   ├── libraries.yaml
│   ├── endpoints.yaml
│   └── preregistration.yaml
├── contracts/
│   ├── context_schema.yaml
│   ├── perturbation_schema.yaml
│   ├── outcome_schema.yaml
│   ├── interaction_schema.yaml
│   └── claim_schema.yaml
├── src/rescuemap/
│   ├── io.py
│   ├── qc.py
│   ├── matching.py
│   ├── main_effects.py
│   ├── interactions.py
│   ├── rescue.py
│   ├── longitudinal.py
│   ├── imaging.py
│   ├── singlecell.py
│   ├── pmhc.py
│   ├── safety.py
│   ├── heterogeneity.py
│   ├── decision_tree.py
│   └── reports.py
├── workflows/
│   ├── Snakefile
│   └── profiles/
├── tests/
│   ├── fixtures/
│   ├── test_oof_incremental.py
│   ├── test_interaction_estimand.py
│   ├── test_no_leakage.py
│   ├── test_schema.py
│   └── test_reproducibility.py
├── reports/
├── results/
├── figures/
└── docs/
```

## Regras de engenharia

- sem caminhos absolutos;
- dependências pinadas;
- container reproduzível;
- checksums de dados;
- mini-dataset sintético no CI;
- heavy data fora do Git, com registry e downloader;
- cada resultado contém código, config, seed, data hash e git SHA;
- nenhuma figura manualmente editada sem script de origem;
- outputs canônicos imutáveis por release.

---

# 11. Riscos e mitigação

| Risco | Consequência | Mitigação |
|---|---|---|
| pMHC não quantificado | confunde reconhecimento com downstream killing | peptide pulse, pMHC assay, immunopeptidomics |
| tela saturada | perde interações | baixa/alta densidade e E:T calibrado |
| gene essencial | falso benefício/escape por fitness | CRISPRi titratável + growth-only arm |
| pseudorreplicação | ICs falsamente estreitos | donor/model como unidade; modelos multinível |
| library bottleneck | perda de guides | cobertura e tracking por etapa |
| TCR mispairing | ruído/segurança | TRAC-targeted KI ou controle do endogenous TCR |
| generalização falsa | resultado específico de um TCR | holdout por TCR/pMHC |
| resgate por expansão apenas | não melhora eficiência funcional | killing por célula e imaging |
| normal tissue toxicity | inviabiliza candidato | safety override precoce |
| ausência de resposta chamada “não-resgate” | conclusão falsa | equivalence bounds |
| main effects dominam interação | matriz pouco informativa | seleção de anchors com mecanismos distintos e faixa não saturada |
| custo combinatorial | programa impraticável | single-sided → anchor-by-library → matrix confirmatória |

---

# 12. Três níveis de execução

## Nível 1 — Minimum Viable Discovery

- um TCR/pMHC;
- três doadores;
- um modelo tumoral principal + um de validação;
- bibliotecas focadas;
- single-sided screens;
- matriz reduzida de interações;
- live imaging para pares principais;
- claim limitado a um contexto.

## Nível 2 — Programa publicável robusto

- sistema sólido + hematológico;
- densidade pMHC baixa/alta;
- múltiplos modelos;
- TME prioritário;
- telas recíprocas anchor-by-library;
- multiômica dos pares;
- validação independente.

## Nível 3 — Atlas flagship

- múltiplos TCRs/HLAs/antígenos;
- optical/spatial pooled screening;
- patient-derived models;
- immunopeptidomics quantitativa;
- regras de modalidade;
- recurso público versionado.

---

# 13. Backlog inicial pronto para issues

## P0 — imediatamente

1. `Implement grouped out-of-fold M→M+C evaluation`  
   **Aceite:** predições OOF, sem leakage, bootstrap por match-block.

2. `Create TCR-RescueMap scientific analysis plan`  
   **Aceite:** estimandos, endpoints, multiplicidade, stop rules e claims congelados.

3. `Create data contracts for context, perturbation, outcome and interaction`  
   **Aceite:** validação automática de schemas.

4. `Create system-selection scorecard`  
   **Aceite:** comparação formal dos sistemas MAGE-A4, hematológico e calibration model.

5. `Build literature/evidence graph for both cell sides`  
   **Aceite:** cada gene com mecanismo, modalidade, direção e evidência.

6. `Remove absolute paths and pin environment`  
   **Aceite:** CI roda mini-workflow em checkout limpo.

## P1 — antes da tela

7. `Qualify endogenous-antigen vs peptide-pulse assay`.
8. `Qualify repeated-challenge tumor-control endpoint`.
9. `Validate editing modalities in TCR-T and tumor cells`.
10. `Run pilot variance/power simulation`.
11. `Freeze focused libraries and control set`.
12. `Pre-register single-sided screen criteria`.

## P2 — após single-sided screens

13. `Select mechanistically diverse tumor anchors`.
14. `Select robust and contextual T-cell candidates`.
15. `Run forward anchor-by-library interaction screen`.
16. `Run reciprocal interaction screen`.
17. `Fit hierarchical interaction model`.
18. `Pre-register confirmatory pair matrix`.

## P3 — descoberta e translação

19. `Mechanistic imaging and phospho validation`.
20. `Genetic rescue/epistasis validation`.
21. `Normal-tissue and cross-reactivity safety panel`.
22. `Patient-derived validation`.
23. `Independent-lab replication`.
24. `Release TCR-RescueMap v1 with claim ledger`.

---

# 14. Critérios de sucesso do programa

## Sucesso metodológico

- interação estimada sem leakage;
- main effects separados de interaction effects;
- validação por contexto holdout;
- equivalência usada para não-resgate;
- reproducibilidade end-to-end.

## Sucesso biológico

- pelo menos um par de resgate causal e reproduzível;
- mecanismo localizado em reconhecimento, sinapse, sinalização, killing ou persistência;
- pelo menos uma classe de escape não-resgatável ou contextualmente resgatável;
- demonstração de dependência de pMHC/TCR quando relevante.

## Sucesso translacional

- decisão clara entre engenharia T, intervenção tumoral, combinação ou troca de modalidade;
- segurança suficiente para justificar desenvolvimento adicional;
- validação em sistema independente/patient-derived;
- claim útil mesmo quando o resultado é FAIL ou non-rescuable.

---

# 15. Frase de posicionamento

> **TCR-RescueMap não pergunta apenas quais genes tornam uma célula T mais forte ou um tumor mais resistente. Ele mede quais engenharias da célula T resgatam cada mecanismo tumoral de escape, identifica os mecanismos que não podem ser resgatados sem restaurar peptide–HLA ou trocar de modalidade e transforma essa interação causal em uma regra experimental e translacional auditável.**

---

# 16. Âncoras científicas para o desenho

O desenho deve ser explicitamente informado por quatro fatos estabelecidos:

1. TCR-T já possui validação clínica em tumores sólidos, tornando MAGE-A4/HLA-A*02 um sistema de referência translacional.
2. Resistência clínica a TCR-T pode ocorrer por perda de HLA/apresentação e por defeitos na resposta a IFNγ.
3. Telas tumorais identificam módulos de IFNγ, TNF, autofagia, CD58 e adesão/sinapse como determinantes de sensibilidade a killing por T cells.
4. Telas T-cell-intrinsic identificam programas de sinalização, cromatina, diferenciação, persistência e exaustão, mas main effects isolados não informam se uma intervenção resgata um mecanismo tumoral específico.

O gap do programa é a **interação bidirecional e a resgatabilidade**, não uma nova lista unilateral de hits.
