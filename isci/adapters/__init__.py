"""Dataset adapters that translate external evidence into canonical ISCI tables."""

from isci.adapters.anndata_cells import (
    CellPreflightResult,
    CellPreflightStatus,
    preflight_anndata_cells,
)
from isci.adapters.anndata_effects import (
    AnnDataAdapterError,
    AnnDataInspectionResult,
    inspect_anndata_dataset,
    iter_anndata_effect_blocks,
    iter_anndata_group_effect_blocks,
)
from isci.adapters.tabular import (
    AdapterIssue,
    AdapterResult,
    DatasetInspection,
    IssueSeverity,
    RuntimeCapability,
    load_tabular_dataset,
)

__all__ = [
    "AnnDataAdapterError",
    "AnnDataInspectionResult",
    "AdapterIssue",
    "AdapterResult",
    "CellPreflightResult",
    "CellPreflightStatus",
    "DatasetInspection",
    "IssueSeverity",
    "RuntimeCapability",
    "inspect_anndata_dataset",
    "iter_anndata_effect_blocks",
    "iter_anndata_group_effect_blocks",
    "load_tabular_dataset",
    "preflight_anndata_cells",
]
