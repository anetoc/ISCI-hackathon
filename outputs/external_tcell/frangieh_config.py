CONFIG = {
    "id": "frangieh_perturbcite",
    "label": "Frangieh 2021 Perturb-CITE-seq (melanoma + autologous TIL co-culture)",
    "system": "immune",
    "path": "/mnt/dados2/abel-tsc/data_public/external_perturb/FrangiehIzar2021_RNA.h5ad",
    "outdir": "/mnt/dados2/abel-tsc/repo/outputs/external_tcell",
    "target_col": "perturbation",
    "sample_col": "perturbation_2",        # 3 conditions (Control/IFNγ/Co-culture) = wells/replicates
    "control_label": "control",
    "singlets": True,
    # leave-marker-out immune-evasion axis = IFN-γ response in control cells (IFNγ - Control)
    "axis_condition_col": "perturbation_2",
    "axis_baseline": "Control",
    "axis_treatment": "IFNγ",
    # positives = CANONICAL IFN-γ-signaling + antigen-presentation regulators (external pathway
    # knowledge, NOT Frangieh's own discovery hits -> least-circular label set)
    "positives": ["B2M", "CD274", "HLA-A", "HLA-B", "HLA-C", "HLA-E",
                  "IFNGR1", "IFNGR2", "IRF3", "JAK1", "JAK2", "STAT1", "TAPBP"],
    "n_per_pos": 3,
    "min_pos": 5,
    "min_neg": 5,
}
