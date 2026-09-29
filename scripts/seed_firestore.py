# Copyright 2026 Google LLC
"""Seed script for ColorCraft AI coloring catalog in Firestore."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-89bfd2aa8330"
COLLECTION_NAME = "coloring_catalog"

SEED_ITEMS = [
    {
        "id": "dino-rex-volcano",
        "title": "Rex Near the Friendly Volcano",
        "theme": "dinosaurs",
        "target_age_group": "3-5 years",
        "edition": "Learning Edition",
        "story_text": "Rex the baby T-Rex waves happily beside the sleeping volcano as a friendly pterodactyl glides above.",
        "line_art_prompt": "Clean thick black-and-white coloring book outline of a cute smiling cartoon baby T-Rex standing on grassy hills with a gentle volcano and clouds in the background, high contrast, bold lines, no shading, white background.",
        "palette_suggestions": [
            {"item": "Baby T-Rex", "color": "Lime Green"},
            {"item": "Belly & Spots", "color": "Sunny Yellow"},
            {"item": "Volcano", "color": "Warm Brown"},
            {"item": "Clouds", "color": "Soft White"},
            {"item": "Sky", "color": "Light Sky Blue"},
        ],
        "difficulty": "easy",
        "created_at": "2026-09-29T09:00:00Z",
    },
    {
        "id": "space-rocket-luna",
        "title": "Rocket Luna's Cosmic Journey",
        "theme": "space",
        "target_age_group": "6-8 years",
        "edition": "Coloring Guide Edition",
        "story_text": "Rocket Luna zooms past Saturn's rings on her way to discover sparkling star constellations.",
        "line_art_prompt": "Coloring page line art of a retro-futuristic cartoon rocket ship zooming past planets, rings, and smiling stars, clean black outlines, print-friendly, open areas for coloring, pure white background.",
        "palette_suggestions": [
            {"item": "Rocket Hull", "color": "Cherry Red & Pearl White"},
            {"item": "Rocket Wings", "color": "Cobalt Blue"},
            {"item": "Engine Flame", "color": "Bright Orange & Yellow"},
            {"item": "Saturn Rings", "color": "Golden Yellow"},
            {"item": "Stars", "color": "Pale Yellow"},
        ],
        "difficulty": "medium",
        "created_at": "2026-09-29T09:05:00Z",
    },
    {
        "id": "underwater-coral-turtle",
        "title": "Tilly Turtle and the Coral Reef",
        "theme": "underwater",
        "target_age_group": "3-5 years",
        "edition": "Coloring Book Only",
        "story_text": "Tilly the sea turtle glides through a colorful coral garden greeting playful clownfish.",
        "line_art_prompt": "Simple bold outline coloring book illustration of a smiling sea turtle swimming among wavy seaweed and bubble trails, thick smooth contours, high contrast, child-friendly, no dark fills.",
        "palette_suggestions": [
            {"item": "Turtle Shell", "color": "Emerald Green & Teal"},
            {"item": "Turtle Skin", "color": "Light Sage"},
            {"item": "Coral", "color": "Coral Pink & Lavender"},
            {"item": "Seaweed", "color": "Ocean Green"},
            {"item": "Bubbles", "color": "Aqua Blue"},
        ],
        "difficulty": "easy",
        "created_at": "2026-09-29T09:55:00Z",
    },
]


def seed():
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    collection = db.collection(COLLECTION_NAME)

    for item in SEED_ITEMS:
        item_id = item["id"]
        data = {k: v for k, v in item.items() if k != "id"}
        collection.document(item_id).set(data)
        print(f"✅ Seeded: {item_id} -> '{item['title']}' ({item['edition']})")

    print("\n🎉 Seeding complete! All items uploaded to Firestore.")


if __name__ == "__main__":
    seed()
