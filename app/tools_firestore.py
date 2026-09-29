# Copyright 2026 Google LLC
"""Firestore function tools for ColorCraft AI."""

import datetime
from typing import Any, Dict, List, Optional
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-89bfd2aa8330"
COLLECTION_NAME = "coloring_catalog"


def _get_db() -> firestore.Client:
    return firestore.Client(project=PROJECT_ID)


def list_coloring_pages(
    theme: Optional[str] = None,
    edition: Optional[str] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Lists coloring book pages from the catalog with optional filtering.

    Args:
        theme: Filter by theme (e.g. 'dinosaurs', 'space', 'underwater', 'animals').
        edition: Filter by edition ('Coloring Book Only', 'Coloring Guide Edition', 'Learning Edition').
        limit: Maximum number of pages to return (default 10).

    Returns:
        A list of dictionaries representing coloring page entries in the catalog.
    """
    db = _get_db()
    query = db.collection(COLLECTION_NAME)

    if theme:
        query = query.where("theme", "==", theme.strip().lower())
    if edition:
        query = query.where("edition", "==", edition.strip())

    docs = query.limit(limit).stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return results


def get_coloring_page(page_id: str) -> Dict[str, Any]:
    """Gets details of a single coloring page by its page ID.

    Args:
        page_id: The document ID of the coloring page (e.g. 'dino-safari-01').

    Returns:
        The coloring page details including title, prompt, palette, and edition.
    """
    db = _get_db()
    doc_ref = db.collection(COLLECTION_NAME).document(page_id)
    doc = doc_ref.get()
    if not doc.exists:
        return {"error": f"Coloring page '{page_id}' not found."}
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def save_coloring_page(
    page_id: str,
    title: str,
    theme: str,
    target_age_group: str,
    edition: str,
    story_text: str,
    line_art_prompt: str,
    palette_suggestions: List[Dict[str, str]],
    difficulty: str = "easy",
) -> Dict[str, Any]:
    """Saves a new or updated coloring page entry to the catalog.

    Args:
        page_id: Unique slug for the page (e.g., 'cosmic-rocket-02').
        title: Title of the coloring page (e.g., 'Rex Explores the Jungle').
        theme: Theme of the scene (e.g., 'dinosaurs', 'space', 'fantasy').
        target_age_group: Intended age range (e.g., '3-5 years', '6-8 years').
        edition: Edition type ('Coloring Book Only', 'Coloring Guide Edition', 'Learning Edition').
        story_text: Accompanying story sentence printed on the page.
        line_art_prompt: Detailed prompt describing the line art scene.
        palette_suggestions: List of color recommendations (e.g., [{'item': 'Dinosaur', 'color': 'Forest Green'}]).
        difficulty: Difficulty level ('easy', 'medium', 'advanced').

    Returns:
        A dictionary confirming creation and returning the saved document data.
    """
    db = _get_db()
    doc_ref = db.collection(COLLECTION_NAME).document(page_id)
    data = {
        "title": title,
        "theme": theme.strip().lower(),
        "target_age_group": target_age_group,
        "edition": edition,
        "story_text": story_text,
        "line_art_prompt": line_art_prompt,
        "palette_suggestions": palette_suggestions,
        "difficulty": difficulty,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    doc_ref.set(data)
    data["id"] = page_id
    return {"status": "success", "page": data}
