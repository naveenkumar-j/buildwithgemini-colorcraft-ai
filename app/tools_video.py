# Copyright 2026 Google LLC
"""Video generation and Cloud Storage publishing tool for ColorCraft AI using Google's Omni model."""

import base64
import uuid
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

PROJECT_ID = "qwiklabs-gcp-04-89bfd2aa8330"
BUCKET_NAME = "bwg3-qwiklabs-gcp-04-89bfd2aa8330"
MODEL_NAME = "gemini-omni-flash-preview"
LOCATION = "global"


async def generate_coloring_video(
    prompt: str,
    tool_context: ToolContext,
    video_name: str | None = None,
) -> str:
    """Generates a short animated video or preview clip for a coloring book item using Google's Omni model (gemini-omni-flash-preview) in the global region.

    Saves the video as an ADK session artifact (visible in the Playground's Artifacts panel)
    and uploads the video bytes directly to the public Cloud Storage bucket, returning the public HTTPS URL.

    Args:
        prompt: Descriptive prompt for the animated coloring scene (e.g., 'A cute baby dinosaur blinking and turning into line art, short 3-5 second clip').
        tool_context: ADK ToolContext for managing session artifacts.
        video_name: Optional prefix or identifier for the artifact and object name.

    Returns:
        The public HTTPS URL of the uploaded video (https://storage.googleapis.com/<bucket>/<object>).
    """
    # 1. Generate video using gemini-omni-flash-preview via the Interactions API in the global region
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    interaction = client.interactions.create(
        model=MODEL_NAME,
        input=prompt,
        response_format={"type": "video"},
    )

    # 2. Extract video bytes from the interaction output
    video_bytes = None
    mime_type = "video/mp4"

    # Search interaction steps for video content
    if hasattr(interaction, "steps") and interaction.steps:
        for step in interaction.steps:
            step_dict = step.model_dump() if hasattr(step, "model_dump") else {}
            content_items = step_dict.get("content") or []
            for item in content_items:
                if item.get("type") == "video" and item.get("data"):
                    video_bytes = base64.b64decode(item["data"])
                    mime_type = item.get("mime_type") or "video/mp4"
                    break
            if video_bytes:
                break

    # Fallback to output_video attribute if present
    if not video_bytes and hasattr(interaction, "output_video") and interaction.output_video:
        data = getattr(interaction.output_video, "data", None)
        if data:
            video_bytes = base64.b64decode(data) if isinstance(data, str) else data

    if not video_bytes:
        raise ValueError("Failed to retrieve video bytes from gemini-omni-flash-preview interaction response.")

    # 3. Determine file name
    safe_name = video_name.replace(" ", "_").lower() if video_name else "coloring_video"
    unique_suffix = uuid.uuid4().hex[:8]
    filename = f"{safe_name}_{unique_suffix}.mp4"

    # 4. Save as ADK session artifact (visible in Playground's Artifacts panel)
    artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
    await tool_context.save_artifact(
        filename=filename,
        artifact=artifact_part,
    )

    # 5. Upload bytes directly to the public Cloud Storage bucket without writing to local disk
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    object_path = f"coloring_videos/{filename}"
    blob = bucket.blob(object_path)
    blob.upload_from_string(video_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{object_path}"
    return public_url
