# Recording script — slide by slide (T-CTRL hackathon video)

**Target length:** 2:50–3:10. **Voice:** first-person clinician-scientist, calm, unhurried.
**Spoken lines are in English** (match the deck + judges). **Directions in Portuguese are for you** —
they are not spoken. Every number here is verified against the locked artifacts.

**Before you hit record**
- Abra o deck em apresentação (tela cheia). Tenha `JUDGE_QA_REHEARSAL.md` aberto num segundo monitor/celular.
- Fale ~15% mais devagar do que o natural. As três "landings" marcadas ⏸ são pausas de ~2s.
- Se errar um número, **não corrija no meio** — termine a frase, respire, refaça a linha inteira. Corta limpo depois.
- Regra de ouro: **cada FAIL/NULL é dito com orgulho**, não como desculpa. É a tese.

---

## SLIDE 1 · Title (0:00–0:20)
**On screen:** "Which genes actually steer a T cell — and which just change the most?"

**SAY:**
> "I'm a hematologist. In my clinic, some patients respond beautifully to a T-cell therapy — and then,
> months later, the same disease comes back. ⏸ When that happens, we ask a question that sounds simple
> and isn't: which genes actually *steer* a T cell into the state we want — and which ones just happen
> to change the most when we perturb them?"

**COMO CONDUZIR:** Comece olhando para a câmera, não para o slide. Essa é a abertura emocional —
o paciente é real. Só avance quando terminar "change the most". Não leia o subtítulo em voz alta.

---

## SLIDE 2 · The clinical question (0:20–0:45)
**On screen:** três cartões — REACH / PRECISION / REPEATABILITY.

**SAY:**
> "Telling those two apart is the whole game — and most screens can't. A real controller has to answer
> three questions, not one. How much did the cell move? That's reach — the size of the abnormal result.
> Which state program actually moved? That's precision. And did independent donors agree? That's
> repeatability. ⏸ Magnitude alone — just the size — is necessary, but nowhere near sufficient."

**COMO CONDUZIR:** Aponte para cada cartão ao nomeá-lo (reach → precision → repeatability). O ritmo
aqui é de professor, listando. A landing é em "necessary, but nowhere near sufficient".

---

## SLIDE 3 · How a perturbation is read (0:45–1:10)
**On screen:** fluxo CRISPR → célula → Perturb-seq → comparação; abaixo, M / C₁ / C₂.

**SAY:**
> "Here's how we read one perturbation. We silence a single gene in a primary human T cell, read the
> whole transcriptome, and then compare where the cell went — across guides, donors and contexts. We
> measure three things: M, how far the profile moved; C-one, whether it moved along a specific state
> axis; and C-two, whether independent units agree. The key question is whether C adds anything *after*
> magnitude is already known."

**COMO CONDUZIR:** Acompanhe o fluxo da esquerda para a direita com o cursor. Ao dizer M / C₁ / C₂,
toque cada quadradinho colorido. Não se demore — é o slide "de mecânica", mantenha em ~25s.

---

## SLIDE 4 · Primary result (1:10–1:45)
**On screen:** três estimandos (+0.357 / +0.215 / 0.415→0.722) + figura central.

**SAY:**
> "And the answer is yes — it adds real signal. In the pre-specified test, adding direction and
> repeatability to a model that already knows magnitude improves how well we recover known regulators,
> by 0.357 in precision-recall. ⏸ Now — thirteen positives is a small set, so we re-ran the whole thing
> out-of-fold, refitting everything inside each training fold. The gain shrank to 0.215. And we *show*
> you that shrinkage — because hiding it would be the easy lie."

**COMO CONDUZIR:** Este é o slide mais importante. Vá devagar nos números. A landing é em "we show you
that shrinkage". NÃO diga "0.307" nem "0.722 é o resultado" — o 0.415→0.722 é uma visão descritiva
separada; se um juiz perguntar, use o card Q3 do ensaio. Enfatize a *honestidade* do encolhimento,
não o número maior.

---

## SLIDE 5 · Tests designed to break it (1:45–2:10)
**On screen:** forest plot do positive-set stress test (dois FAIL vermelhos).

**SAY:**
> "Here's the part I'm proudest of. We didn't stop at the win — we went looking for where it breaks.
> On a broad, independent set of functional regulators, it fails — cleanly, minus 0.281, with the whole
> interval below zero. And when we remove the four master transcription factors that define the axes,
> the gain collapses to essentially nothing. ⏸ So the honest claim is narrow: this holds for canonical,
> state-defining regulators in T cells."

**COMO CONDUZIR:** Diga os FAILs com firmeza e até com um leve orgulho — é o oposto de esconder.
Aponte para o ponto vermelho "External screen" no gráfico. A landing é "canonical, state-defining
regulators in T cells". Não acelere para economizar tempo — se precisar cortar, corte do slide 3.

---

## SLIDE 6 · Boundary across systems (2:10–2:30)
**On screen:** CCI 4-sistemas + tabela PASS / NEAR-MISS / FAIL.

**SAY:**
> "And that boundary is graded, not binary. In immune T cells it passes. In a myeloid immune line it's
> a near-miss. In non-immune cells — K562, RPE1 — it fails. That's a scope map: it tells you exactly
> where the property lives. Which is why we never call it an *invariant*."

**COMO CONDUZIR:** Percorra a tabela de cima para baixo (verde → âmbar → vermelho). A palavra
"invariant" é dita com uma leve ênfase negativa — mostra disciplina. ~20s, ritmo firme.

---

## SLIDE 7 · Translation limits (2:30–2:45)
**On screen:** quadrante controller × convergence; IRF1 destacado.

**SAY:**
> "One more honesty check. A controller is not automatically a drug target. Our number-one controller,
> IRF1, actually points the wrong way for intervention. And as a predictor of who responds to CAR-T
> across studies, the whole approach is a null — a simple CD8 fraction does better. We report that,
> plainly."

**COMO CONDUZIR:** Este é o slide que um hematologista-juiz vai olhar com atenção. Diga o NULL sem
hesitar. Se perguntarem "então não serve para a clínica?", use o card R1/Q9 do ensaio — a resposta é
que o valor é o framework de adjudicação, não uma promessa clínica. ~15s.

---

## SLIDE 8 · The innovation is judgment (2:45–2:58)
**On screen:** taxonomia PASS / FAIL / NULL / NOT-EVALUABLE.

**SAY:**
> "So what's the actual innovation? It's judgment. Every one of those boundaries — every FAIL, every
> null — came out of a correction loop, where Claude challenged our own headline, found a leak in how
> we chose controls, and forced the stricter test. The deterministic code owns the numbers. The
> skepticism is the science."

**COMO CONDUZIR:** Aqui o tom sobe um pouco — é o clímax intelectual. "The skepticism is the science"
é dito com convicção, olhando para a câmera. Não corra.

---

## SLIDE 9 · Gladstone bridge (2:58–3:05) — *opcional, se o tempo permitir*
**On screen:** design donor-resolved + falsificação + stop-before-synthesis.

**SAY:**
> "And it points to a concrete next experiment: a pre-declared donor-resolved panel that can *falsify*
> the next claim — with the safety checkpoints stated before any synthesis."

**COMO CONDUZIR:** Se o vídeo tiver limite de 3 min rígido, este slide pode virar apenas visual
(mostra 2s sem narração) ou ser cortado. É o "e o que vem depois" — bom para o prêmio Gladstone, mas
não essencial para a mensagem central.

---

## SLIDE 10 · Open-source delivery + close (3:05–3:15)
**On screen:** 4 camadas + comando + 21/21 gates.

**SAY:**
> "Everything is open-source and reproducible — clone it, run one command, and 21 of 21 release gates
> pass. What you're left with isn't a target list. It's a tested scope map — with every PASS, FAIL and
> null written down. ⏸ Because a good scientific agent doesn't just find an answer. It knows when *not*
> to call PASS."

**COMO CONDUZIR:** A última frase é a assinatura do projeto inteiro. Pausa antes de "It knows when not
to call PASS", e diga devagar, olhando para a câmera. Deixe 1–2s de silêncio antes de cortar a
gravação — dá peso ao fecho.

---

## Checklist pós-gravação
1. Confira áudio (sem estouro nas landings).
2. Duração ≤ limite do formulário (confirme se é 3 min).
3. Exporte MP4 1080p. Um fallback de 2:30 já existe em `demo_assets/hackathon/`.
4. Suba o vídeo (YouTube unlisted ou o que o formulário pedir) e pegue o link.
5. Torne o repo público → cole link do repo + link do vídeo + summary no formulário.

## Se travar / esquecer uma linha
- Números na ponta da língua: **0.357** (pre-specified), **0.215** (out-of-fold), **−0.281** (external FAIL),
  **0.533** (CAR-T study-out), **0.585** (CD8 baseline). Tudo está na ficha de `JUDGE_QA_REHEARSAL.md`.
- Nunca improvise um número. Se não lembrar, diga "it's in the claim ledger" e siga.
