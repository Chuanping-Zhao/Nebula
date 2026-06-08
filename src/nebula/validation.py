"""Validation and normalization helpers for NebulaData objects."""
from __future__ import annotations

import pandas as pd

from nebula.data import NebulaData


def _normalize_label_value(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _normalize_labels(labels: pd.Index, label_name: str) -> pd.Index:
    """Convert labels to stripped strings and reject missing labels."""
    if isinstance(labels, pd.MultiIndex):
        raise ValueError(f"Nebula:{label_name} must not be a MultiIndex!")

    normalized = pd.Index(
        [_normalize_label_value(value) for value in labels],
        name=labels.name,
    )

    if (normalized == "").any():
        raise ValueError(f"Nebula:{label_name} must not contain missing or empty IDs!")

    return normalized


def _format_values(values: list[object], max_items: int = 5) -> str:
    shown = [repr(value) for value in values[:max_items]]
    if len(values) > max_items:
        shown.append("...")
    return ", ".join(shown)


def _duplicated_values(labels: pd.Index) -> list[object]:
    duplicated = labels[labels.duplicated(keep=False)]
    return duplicated.drop_duplicates().tolist()


def _require_unique(labels: pd.Index, label_name: str) -> None:
    duplicates = _duplicated_values(labels)
    if duplicates:
        raise ValueError(
            f"Nebula:{label_name} must contain unique IDs. "
            f"Duplicated values: {_format_values(duplicates)}"
        )


def _normalize_columns(table: pd.DataFrame, table_name: str) -> pd.DataFrame:
    normalized = table.copy()
    normalized.columns = _normalize_labels(normalized.columns, f"{table_name}.columns")
    _require_unique(normalized.columns, f"{table_name}.columns")
    return normalized


def _require_columns(
    table: pd.DataFrame,
    required_columns: list[str],
    table_name: str,
) -> None:
    missing = [column for column in required_columns if column not in table.columns]
    if missing:
        raise ValueError(
            f"Nebula:{table_name} is missing required columns: "
            f"{_format_values(missing)}"
        )


def _normalize_id_column(
    table: pd.DataFrame,
    column: str,
    label_name: str,
) -> None:
    table[column] = _normalize_labels(pd.Index(table[column]), label_name).to_list()
    _require_unique(pd.Index(table[column]), label_name)


def _missing_values(expected: pd.Index, actual: pd.Index) -> list[object]:
    actual_values = set(actual)
    return [value for value in expected if value not in actual_values]


def _extra_values(expected: pd.Index, actual: pd.Index) -> list[object]:
    expected_values = set(expected)
    return [value for value in actual if value not in expected_values]


def _validate_same_labels(
    expected: pd.Index,
    actual: pd.Index,
    *,
    actual_name: str,
    expected_name: str,
) -> None:
    missing = _missing_values(expected, actual)
    extra = _extra_values(expected, actual)

    if missing or extra:
        message_parts = [f"Nebula:{actual_name} must match {expected_name}."]
        if missing:
            message_parts.append(f"Missing: {_format_values(missing)}")
        if extra:
            message_parts.append(f"Extra: {_format_values(extra)}")
        raise ValueError(" ".join(message_parts))


def _ensure_dataframe(value: object, attr_name: str) -> pd.DataFrame:
    if not isinstance(value, pd.DataFrame):
        raise TypeError(f"Nebula:{attr_name} must be a pandas DataFrame!")
    return value.copy()


def _coerce_feature_values(features: pd.DataFrame) -> pd.DataFrame:
    numeric_features = features.apply(pd.to_numeric, errors="coerce")
    invalid_mask = features.notna() & numeric_features.isna()

    if invalid_mask.to_numpy().any():
        invalid_locations = invalid_mask.stack()[lambda mask: mask].index.tolist()
        formatted_locations = [
            f"(feature={feature!r}, sample={sample!r})"
            for feature, sample in invalid_locations[:5]
        ]
        if len(invalid_locations) > 5:
            formatted_locations.append("...")
        raise ValueError(
            "Nebula:data.features contains non-numeric intensity values at "
            f"{', '.join(formatted_locations)}"
        )

    return numeric_features


def _prepare_nebula_tables(
    features: pd.DataFrame,
    annotations: pd.DataFrame,
    metadata: pd.DataFrame,
    *,
    features_id_col: str,
    sample_id_col: str,
) -> NebulaData:
    """Normalize raw input tables into the NebulaData internal layout."""
    features_id_col = _normalize_label_value(features_id_col)
    sample_id_col = _normalize_label_value(sample_id_col)

    if not features_id_col:
        raise ValueError("Nebula:features_id_col must not be empty!")
    if not sample_id_col:
        raise ValueError("Nebula:sample_id_col must not be empty!")

    features = _normalize_columns(features, "features_file")
    annotations = _normalize_columns(annotations, "annotations_file")
    metadata = _normalize_columns(metadata, "metadata_file")

    _require_columns(features, [features_id_col], "features_file")
    _require_columns(annotations, [features_id_col], "annotations_file")
    _require_columns(metadata, [sample_id_col], "metadata_file")

    _normalize_id_column(features, features_id_col, f"features_file.{features_id_col}")
    _normalize_id_column(
        annotations,
        features_id_col,
        f"annotations_file.{features_id_col}",
    )
    _normalize_id_column(metadata, sample_id_col, f"metadata_file.{sample_id_col}")

    features = features.set_index(features_id_col)
    annotations = annotations.set_index(features_id_col)
    metadata = metadata.set_index(sample_id_col)

    data = NebulaData(features, annotations, metadata)
    validate_and_normalize_nebula(data)
    return data


def validate_and_normalize_nebula(data: NebulaData) -> None:
    """
    Validate and normalize a NebulaData object in place.

    This function checks whether the internal NebulaData structure is valid
    and standardizes table labels, table order, and feature intensity dtypes.
    It mutates ``data`` in place.

    Validation rules
    ----------------
    - data.features must be a pandas DataFrame.
    - data.annotations must be a pandas DataFrame.
    - data.metadata must be a pandas DataFrame.
    - data.features.index must contain unique feature identifiers.
    - data.features.columns must contain unique sample identifiers.
    - data.annotations.index must match data.features.index.
    - data.metadata.index must match data.features.columns.
    - all values in data.features must be numeric.

    Normalization rules
    -------------------
    - indexes and columns are converted to stripped strings.
    - annotation and metadata row order is aligned to the feature table.
    - feature intensity values are coerced to numeric dtype.

    Returns
    -------
    None
        The input NebulaData object is updated in place if validation passes.

    Raises
    ------
    TypeError
        If one of the core tables is not a pandas DataFrame.
    ValueError
        If duplicated IDs, missing IDs, inconsistent table alignment, or
        non-numeric feature intensity values are detected.
    """
    if not isinstance(data, NebulaData):
        raise TypeError("Nebula:data must be a NebulaData object!")

    features = _ensure_dataframe(data.features, "data.features")
    annotations = _ensure_dataframe(data.annotations, "data.annotations")
    metadata = _ensure_dataframe(data.metadata, "data.metadata")

    features.index = _normalize_labels(features.index, "data.features.index")
    features.columns = _normalize_labels(features.columns, "data.features.columns")
    annotations.index = _normalize_labels(
        annotations.index,
        "data.annotations.index",
    )
    annotations.columns = _normalize_labels(
        annotations.columns,
        "data.annotations.columns",
    )
    metadata.index = _normalize_labels(metadata.index, "data.metadata.index")
    metadata.columns = _normalize_labels(metadata.columns, "data.metadata.columns")

    _require_unique(features.index, "data.features.index")
    _require_unique(features.columns, "data.features.columns")
    _require_unique(annotations.index, "data.annotations.index")
    _require_unique(metadata.index, "data.metadata.index")

    _validate_same_labels(
        features.index,
        annotations.index,
        actual_name="data.annotations.index",
        expected_name="data.features.index",
    )
    _validate_same_labels(
        features.columns,
        metadata.index,
        actual_name="data.metadata.index",
        expected_name="data.features.columns",
    )

    data.features = _coerce_feature_values(features)
    data.annotations = annotations.reindex(features.index)
    data.metadata = metadata.reindex(features.columns)
