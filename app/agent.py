# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


MODEL = "gemini-3.6-flash"


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


from app.tools_firestore import (
    get_coloring_page,
    list_coloring_pages,
    save_coloring_page,
)
from app.tools_image import generate_coloring_image
from app.tools_video import generate_coloring_video
from google.adk.code_executors import AgentEngineSandboxCodeExecutor

SANDBOX_RESOURCE_NAME = "projects/378718754451/locations/us-east1/reasoningEngines/3206367221618049024/sandboxEnvironments/3064215761309401088"
code_executor = AgentEngineSandboxCodeExecutor(
    sandbox_resource_name=SANDBOX_RESOURCE_NAME
)

from google.adk.agents.callback_context import CallbackContext
from google.adk.memory import VertexAiMemoryBankService
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

MEMORY_BANK_ID = "3206367221618049024"
PROJECT_ID = "qwiklabs-gcp-04-89bfd2aa8330"
LOCATION = "us-east1"


async def generate_memories_callback(callback_context: CallbackContext):
    """Saves session turns to Vertex AI Memory Bank for durable memory extraction."""
    try:
        await callback_context.add_session_to_memory()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Memory callback skipped: %s", e)
    return None


def memory_bank_service_builder():
    """Builds the VertexAiMemoryBankService for deployment on Agent Runtime."""
    return VertexAiMemoryBankService(
        project=PROJECT_ID,
        location=LOCATION,
        agent_engine_id=MEMORY_BANK_ID,
    )


from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from .a2ui_utils import a2ui_callback

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are ColorCraft AI, an assistant that helps parents and educators explore, "
        "customize, and design printable coloring book pages with color guides and smart palettes. "
        "You remember the user's stated preferences, children's ages, favorite themes, and past coloring pages across conversations. "
        "You have access to a catalog of coloring pages in Firestore (use list_coloring_pages, get_coloring_page, save_coloring_page). "
        "You can run Python code safely in a sandbox using your code execution capabilities. "
        "You can generate animated video clips for coloring book items using Google's Omni model (generate_coloring_video), which saves the video artifact and returns a public Cloud Storage https URL. "
        "IMPORTANT: Whenever the user asks to design, create, make, or generate a coloring page, scene, character, or illustration (such as from example prompts or user requests), you MUST ALWAYS call the generate_coloring_image tool to generate the coloring image and get its public https Cloud Storage URL. Never reply with just text descriptions of the page or color guide without calling generate_coloring_image."
    ),
    workflow_description="Whenever designing or creating a page, call generate_coloring_image first to get the image URL. When asked to generate a video or animation, call generate_coloring_video to get the video URL. Then return the structured A2UI Card containing the Image/media and details.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows and the Image. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "When you generate an image with generate_coloring_image, ALWAYS include the Image component in your A2UI card with the returned public https URL, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    code_executor=code_executor,
    tools=[
        PreloadMemoryTool(),
        list_coloring_pages,
        get_coloring_page,
        save_coloring_page,
        generate_coloring_image,
        generate_coloring_video,
        get_weather,
        get_current_time,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
