"""Annotation database naming helpers."""
from __future__ import annotations

import re

from nebula.schema import DATABASE_ALIASES


def _normalize_database_name(database: str | None) -> str | None:
    if database is None:
        return None

    cleaned = str(database).strip()
    if not cleaned:
        return None

    compact = re.sub(r"[\s_\-]+", "", cleaned).lower()
    return DATABASE_ALIASES.get(compact, cleaned)


def _infer_database_from_column(column: str) -> str | None:
    compact = re.sub(r"[\s_\-]+", "", str(column)).lower()

    if "kegg" in compact:
        return "KEGG"
    if "hmdb" in compact:
        return "HMDB"
    if "pubchem" in compact or compact in {"cid", "pubchemcid"}:
        return "PubChem.CID"
    if "chebi" in compact:
        return "ChEBI"
    if "lipidmaps" in compact or compact in {"lmid", "lm"}:
        return "LIPIDMAPS"
    if "metlin" in compact:
        return "METLIN"
    if "massbank" in compact:
        return "MassBank"
    if "gnps" in compact:
        return "GNPS"

    return None
