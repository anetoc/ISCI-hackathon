# Protein targetability matrix — interpretation contract

`protein_targetability_matrix.csv` is a standard header-first CSV. It is a hypothesis-generating
triage overlay and does not validate the ISCI/T-REMAP core or recommend clinical intervention.

It annotates the locked candidate list with protein/druggability metadata to prioritize follow-up
experiments such as probes, arrays and CRISPRi/a titration. Direction and class fields are
computational hypotheses requiring wet-lab validation.

Sources used by the historical run:

- MyGene for identifier mapping;
- UniProt for families, keywords and localization;
- Human Protein Atlas 25.1 for protein class, subcellular location and immune expression; and
- ChEMBL for target existence and approved/clinical mechanism-of-action drugs.

Open Targets tractability was unavailable during that run because of sustained upstream rate
limiting. `druggability_tier` is therefore ChEMBL/HPA-derived.

`translation_triage_score` combined normalized `ISCI_orthogonal`, druggability,
small-molecule ligandability and a reverser prior, then subtracted predeclared signaling,
essentiality and oncogenic-risk penalties. Higher values indicate experimental follow-up priority,
not a stronger drug target.
