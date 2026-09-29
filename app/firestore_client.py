# Copyright 2026 Google LLC
"""Firestore client and data layer for ColorCraft AI."""

from google.cloud import firestore

# Hardcoded project ID as string to avoid project number issues on Agent Platform
PROJECT_ID = "qwiklabs-gcp-04-89bfd2aa8330"

_db = None


def get_firestore_client() -> firestore.Client:
    """Returns a singleton Firestore client explicitly initialized with project ID."""
    global _db
    if _db is None:
        _db = firestore.Client(project=PROJECT_ID)
    return _db
