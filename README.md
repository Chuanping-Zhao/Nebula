# Nebula: an open-source metabolomics data analysis tool

## What's Nebula?

Nebula is an open-source metabolomics data analysis platform for end-to-end workflows from raw mass spectrometry data processing to downstream biological interpretation.

##  Overview

Nebula aims to provide an integrated metabolomics workflow including:
- Raw LC-MS/MS data processing
- Feature detection
- Peak alignment
- Metabolite annotation
- Statistical analysis
- Visualization
- Biological interpretation
- Machine learning for biomarkers

## Data Input and Internal Storage

Nebula currently builds its core data object with `create_nebula()`. Users
provide three tabular files:

- `features_file`: feature intensity table. Each row is a metabolomics feature,
  and each sample is stored in one intensity column. The feature ID column is
  `ID` by default.
- `annotations_file`: feature annotation table. It must contain the same
  feature ID column as `features_file`.
- `metadata_file`: sample metadata table. The sample ID column is `Run` by
  default and must match the sample columns in `features_file`.

Supported table formats are `.csv`, `.xlsx`, `.xls`, `.txt`, and `.tsv`.

Example:

```python
from nebula.io import create_nebula

data = create_nebula(
    features_file="demodata/inputfile_format/feature_intensity.csv",
    annotations_file="demodata/inputfile_format/annoations.csv",
    metadata_file="demodata/inputfile_format/sampleInfo_metadata.csv",
    features_id_col="ID",
    sample_id_col="Run",
)
```

When the files are loaded, Nebula validates and normalizes them before returning
the `NebulaData` object:

1. Read the three input files into pandas `DataFrame` objects.
2. Normalize column names and IDs by converting them to strings and stripping
   leading or trailing spaces.
3. Check that required ID columns exist.
4. Check that feature IDs and sample IDs are unique.
5. Set `features_id_col` as the index of `features` and `annotations`.
6. Set `sample_id_col` as the index of `metadata`.
7. Check that `annotations.index` matches `features.index`.
8. Check that `metadata.index` matches `features.columns`.
9. Convert feature intensity values to numeric dtype.
10. Reorder `annotations` and `metadata` so their rows are aligned with
    `features`.

After this process, data is stored inside `NebulaData` as:

- `data.features`: a numeric feature-by-sample intensity matrix. Rows are
  feature IDs, columns are sample IDs.
- `data.annotations`: feature annotation metadata. Rows are feature IDs and are
  aligned to `data.features.index`.
- `data.metadata`: sample metadata. Rows are sample IDs and are aligned to
  `data.features.columns`.

This means downstream analysis can rely on a consistent internal layout:

```text
data.features.index      == data.annotations.index
data.features.columns    == data.metadata.index
data.features values     are numeric
```

## Development Status
Current version: v0.0.1
Implemented:

- [x] Project initialization
- [x] GitHub repository
- [ ] Data preprocessing
