"""
Boolean query parser for PubMed-style queries.

Splits a boolean query into AND-fragments, then each fragment into OR-terms.
Strips field tags ([tiab], [MeSH Terms], etc.), wildcards, parentheses, quotes,
and filters empty / pure-operator tokens.
"""

import re
from typing import List

# PubMed field tags: [tiab], [MeSH Terms], [tw], [mp], etc.
_FIELD_TAG = re.compile(
    r'\[\s*(?:'
    r'ti|ab|tiab|tw|all\s+fields|mesh\s+terms?|major\s+mesh|mp|mh|sh|rn|nm|ot|'
    r'pt|la|jw|so|af|aud|cois|mf|px|rf|ro|rx|sb|si|subh|ec|ip|lr|od|pg|pl|vi|'
    r'au|corp|fau|gr|invt|ir|irad|cn|ed|fd|auid|book|series|pmid|tr|dn|ddt|isbn|'
    r'edat|pdat|mhda|crdt|entrez\s+date|publication\s+date|mesh\s+date|create\s+date'
    r')\s*(?::\w+)?\s*\]',
    re.IGNORECASE,
)

_STOP_WORDS = frozenset({'and', 'or', 'not', 'and not'})

# Sentinel to protect AND NOT from being split as AND
_ANDNOT_SENTINEL = '\x00ANDNOT\x00'


def _clean_term(raw: str) -> str:
    """Strip field tags, wildcards, brackets, quotes, leading NOT from a token."""
    term = _FIELD_TAG.sub('', raw)
    term = term.replace('*', '')
    term = term.replace('(', '').replace(')', '')
    # Straight and curly quotes
    term = term.replace('"', '').replace('\u201c', '').replace('\u201d', '')
    term = term.replace("'", '')
    # Strip leading NOT
    term = re.sub(r'^\s*NOT\s+', '', term, flags=re.IGNORECASE)
    return term.strip()


def parse_boolean_query(query: str) -> List[List[str]]:
    """
    Parse a boolean query into groups of keyword strings.

    Input:
        '("diabetes mellitus" OR insulin) AND ("heart attack" OR "myocardial infarction")'
    Output:
        [["diabetes mellitus", "insulin"], ["heart attack", "myocardial infarction"]]

    Rules:
    - Split on AND (case-insensitive), but skip AND NOT fragments (negative groups dropped)
    - Each AND-fragment is further split on OR
    - Field tags, wildcards, parentheses, quotes, and NOT prefixes are stripped
    - Empty tokens and bare boolean operators are filtered out
    - If no groups are detected, the query is returned as a single flat group
      (comma-separated tokens, or the whole string as one keyword)
    """
    if not query or not query.strip():
        return []

    # Protect AND NOT so it isn't split on AND
    work = re.sub(r'\bAND\s+NOT\b', _ANDNOT_SENTINEL, query, flags=re.IGNORECASE)

    # Split on AND
    and_fragments = re.split(r'\bAND\b', work, flags=re.IGNORECASE)

    groups: List[List[str]] = []
    for fragment in and_fragments:
        # Drop negative fragments
        if _ANDNOT_SENTINEL in fragment:
            continue

        # Split on OR
        raw_terms = re.split(r'\bOR\b', fragment, flags=re.IGNORECASE)

        terms: List[str] = []
        for raw in raw_terms:
            cleaned = _clean_term(raw)
            if cleaned and cleaned.lower() not in _STOP_WORDS:
                terms.append(cleaned)

        if terms:
            groups.append(terms)

    # Fallback: no boolean structure detected — try comma-separated or single group
    if not groups:
        if ',' in query:
            terms = [t.strip() for t in query.split(',') if t.strip()]
        else:
            terms = [query.strip()] if query.strip() else []
        if terms:
            groups = [terms]

    return groups
