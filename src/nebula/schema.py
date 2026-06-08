"""Shared schema constants for Nebula."""
from __future__ import annotations


DEFAULT_FEATURE_ID_COL = "ID"
DEFAULT_SAMPLE_ID_COL = "Run"

SUPPORTED_TABLE_SUFFIXES = {
    ".csv",
    ".xlsx",
    ".xls",
    ".txt",
    ".tsv",
}

TABULAR_TEXT_SUFFIXES = {
    ".txt",
    ".tsv",
}

EXCEL_SUFFIXES = {
    ".xlsx",
    ".xls",
}

DATABASE_ALIASES = {
    "chebi": "ChEBI",
    "cid": "PubChem.CID",
    "gnps": "GNPS",
    "hmdb": "HMDB",
    "inchi": "InChI",
    "inchikey": "InChIKey",
    "kegg": "KEGG",
    "keggcompound": "KEGG",
    "keggdrug": "KEGG",
    "lipidmaps": "LIPIDMAPS",
    "lm": "LIPIDMAPS",
    "massbank": "MassBank",
    "metlin": "METLIN",
    "pubchem": "PubChem.CID",
    "pubchemcid": "PubChem.CID",
    "smiles": "SMILES",
}
