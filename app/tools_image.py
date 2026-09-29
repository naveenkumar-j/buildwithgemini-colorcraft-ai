# Copyright 2026 Google LLC
"""Image generation and Cloud Storage publishing tool for ColorCraft AI."""

import uuid
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

PROJECT_ID = "qwiklabs-gcp-04-89bfd2aa8330"
BUCKET_NAME = "bwg3-qwiklabs-gcp-04-89bfd2aa8330"
MODEL_NAME = "gemini-3.1-flash-lite-image"
LOCATION = "global"


async def generate_coloring_image(
    prompt: str,
    tool_context: ToolContext,
    image_name: str | None = None,
) -> str:
    """Generates an illustration or coloring page using gemini-3.1-flash-lite-image in the global region.

    Saves the image as an ADK session artifact (visible in Playground's Artifacts panel)
    and uploads the image bytes directly to Cloud Storage, returning the public HTTPS URL.

    Args:
        prompt: Descriptive prompt for the image (e.g. 'Clean black-and-white coloring book outline of a baby T-Rex...').
        tool_context: ADK ToolContext for managing session artifacts.
        image_name: Optional prefix or identifier for the artifact and object name.

    Returns:
        The public HTTPS URL of the uploaded image (https://storage.googleapis.com/<bucket>/<object>).
    """
    # 1. Generate image using gemini-3.1-flash-lite-image in global region
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    image_bytes = None
    mime_type = "image/jpeg"

    for candidate in response.candidates:
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/jpeg"
                    break
        if image_bytes:
            break

    if not image_bytes:
        raise ValueError("Failed to retrieve image bytes from model response.")

    # 2. Determine file extension and filename
    ext = "jpg" if "jpeg" in mime_type or "jpg" in mime_type else "png"
    safe_name = image_name.replace(" ", "_").lower() if image_name else "coloring_page"
    unique_suffix = uuid.uuid4().hex[:8]
    filename = f"{safe_name}_{unique_suffix}.{ext}"

    # 3. Save as ADK session artifact (visible in Playground Artifacts panel)
    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    await tool_context.save_artifact(
        filename=filename,
        artifact=artifact_part,
    )

    # 4. Upload bytes directly to the public Cloud Storage bucket without writing to local disk
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    object_path = f"coloring_pages/{filename}"
    blob = bucket.blob(object_path)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{object_path}"
    return public_url
