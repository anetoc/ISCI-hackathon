# What we are delivering

ISCI is not a single Python script and it is not a therapeutic-target list. It is an integrated,
auditable research package that connects a biological question to deterministic analysis, frozen
evidence and a judge-facing explanation.

## The package in plain language

1. **Scientific contracts** define the functional T-cell axes, claims, gates and overclaim
   boundaries before the public result is presented.
2. **Python code** reads the public Perturb-seq evidence, applies leakage controls, computes the
   metrics and reproduces the figures. Python is the engine, not the whole product.
3. **Versioned evidence** stores the verdicts, tables, figures, commands and Git/data/axes hashes
   required to audit what was shown.
4. **Presentation artifacts** translate the result for a mixed medical and scientific audience:
   the PowerPoint deck, deterministic offline demo, Full-HD fallback video and judge Q&A.
5. **Release gates** verify that the four verdicts remain frozen, the evidence and media agree,
   public surfaces contain no local paths or prohibited raw files, and human approval is still
   required before submission.

## Start here

- **Medical-language deck:** `outputs/isci_hackathon_medical_deck.pptx`
- **Live/offline demo:** `docs/hackathon_judge_demo.html`
- **2:30 video fallback:** `demo_assets/hackathon/hackathon_fallback_2m30.mp4`
- **Submission copy:** `SUBMISSION.md`
- **Locked scientific result:** `reports/result_lock.md`
- **Claim-by-claim evidence:** `reports/CLAIM_LEDGER.md`
- **Machine-readable verdicts:** `outputs/hackathon/claim_manifest.json`
- **Automated release status:** `outputs/hackathon/readiness_report.json`
- **Rebuild and verify the stage package:** `make hackathon-package`

## What it does not claim

- It is not a validated clinical biomarker.
- It does not recommend treatment or declare a gene ready for engineering.
- It does not generalize to every functional regulator or every cellular system.
- It does not convert missing data into a negative result.
- It does not commit raw H5AD/H5MU datasets or clinical information.

The scientific contribution is the auditable judgment workflow: it separates perturbation size
from directional, donor-reproducible state control and preserves PASS, FAIL, NULL and
NOT-EVALUABLE as legitimate outcomes.
