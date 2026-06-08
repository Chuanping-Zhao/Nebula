"""Input/output helpers for creating NebulaData objects."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from nebula.data import NebulaData
from nebula.schema import (
    DEFAULT_FEATURE_ID_COL,
    DEFAULT_SAMPLE_ID_COL,
    EXCEL_SUFFIXES,
    SUPPORTED_TABLE_SUFFIXES,
    TABULAR_TEXT_SUFFIXES,
)
from nebula.validation import _prepare_nebula_tables


def _read_table(file_path: str, table_name: str) -> pd.DataFrame:
    """Read a supported tabular file into a DataFrame."""
    suffix = Path(file_path).suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(file_path)
    if suffix in EXCEL_SUFFIXES:
        return pd.read_excel(file_path)
    if suffix in TABULAR_TEXT_SUFFIXES:
        return pd.read_csv(file_path, sep="\t")

    supported_suffixes = ", ".join(sorted(SUPPORTED_TABLE_SUFFIXES))
    raise ValueError(
        f"Nebula:Unsupported file format for {table_name}: "
        f"{suffix or '<none>'}. Supported suffixes: {supported_suffixes}"
    )


def create_nebula(
    features_file: str,
    annotations_file: str,
    metadata_file: str,
    *,
    features_id_col: str = DEFAULT_FEATURE_ID_COL,
    sample_id_col: str = DEFAULT_SAMPLE_ID_COL,
) -> NebulaData:
    """
    Create a NebulaData object from feature, annotation, and metadata files.

    Parameters
    ----------
    features_file : str
        Path to the feature intensity table. Supported formats are csv, xlsx,
        xls, txt, and tsv.
    annotations_file : str
        Path to the feature annotation table.
    metadata_file : str
        Path to the sample metadata table.
    features_id_col : str, default="ID"
        Column containing unique feature IDs. This column becomes the
        ``features`` and ``annotations`` index.
    sample_id_col : str, default="Run"
        Column containing sample IDs. This column becomes the ``metadata``
        index and must match the feature intensity columns.

    Returns
    -------
    NebulaData
        A validated and normalized NebulaData object.
    """
    features = _read_table(features_file, "features_file")
    annotations = _read_table(annotations_file, "annotations_file")
    metadata = _read_table(metadata_file, "metadata_file")

    return _prepare_nebula_tables(
        features,
        annotations,
        metadata,
        features_id_col=features_id_col,
        sample_id_col=sample_id_col,
    )
