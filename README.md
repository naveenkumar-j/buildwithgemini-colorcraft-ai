# ColorCraft AI

**ColorCraft AI** is an intelligent assistant built on Google's Agent Development Kit (ADK) that helps parents and educators explore, customize, and design printable coloring book pages with color guides and smart palettes.

---

## What ColorCraft AI Does

ColorCraft AI pairs conversational design workflows with Google Cloud services to generate child-friendly coloring book materials:

- **Stateful Memory & User Preferences**: Uses **Vertex AI Memory Bank** to remember user preferences across sessions (such as children's ages, favorite themes, and past coloring pages) via `PreloadMemoryTool` and callback-driven extraction.
- **Coloring Catalog Storage**: Backed by **Google Cloud Firestore** to query and persist coloring page designs:
  - `list_coloring_pages`: Query catalog pages filtered by theme or edition.
  - `get_coloring_page`: Retrieve detailed metadata, story text, and color palettes by page ID.
  - `save_coloring_page`: Persist new or updated coloring page designs to Firestore.
- **Image Generation & Publishing**: Uses `gemini-3.1-flash-lite-image` in the `global` region to generate clean coloring book line art:
  - `generate_coloring_image`: Creates line art illustrations, saves each image as a session artifact (viewable in ADK Playground), uploads the image directly to **Google Cloud Storage**, and provides a public HTTPS URL.
- **Omni Video Generation**: Generates short animated preview clips using Google's Omni model:
  - `generate_coloring_video`: Uses `gemini-omni-flash-preview` in the `global` region via the Google GenAI Interactions API. Saves the clip as an ADK session artifact and uploads the `.mp4` file directly to **Google Cloud Storage**, returning its public HTTPS URL.
- **A2UI Interactive Surfaces**: Formats structured responses using **A2UI (v0.8)** schemas and the Basic Catalog, presenting responsive cards with titles, story descriptions, embedded images, and color guide palettes.
- **Agent Engine Sandbox Code Execution**: Evaluates code safely in a dedicated **Vertex AI Agent Engine Sandbox Environment** (`AgentEngineSandboxCodeExecutor`).

---

## Project Structure

```
colorcraft-ai/
├── app/
│   ├── agent.py               # Core ADK agent configuration, prompt, memory, and tools
│   ├── fast_api_app.py        # FastAPI server running the ADK runner and A2A endpoints
│   ├── tools_firestore.py     # Firestore catalog tools (list, get, save)
│   ├── tools_image.py         # Image generation via gemini-3.1-flash-lite-image & GCS upload
│   ├── tools_video.py         # Video generation via gemini-omni-flash-preview & GCS upload
│   ├── firestore_client.py    # Firestore client initializer
│   ├── a2ui_utils.py          # A2UI response formatting callback
│   └── app_utils/             # Service registry (Session, Artifact, Memory services)
├── frontend/                  # Lightweight FastAPI chat UI proxy and web client
│   ├── main.py                # Chat API proxying to Agent Engine
│   └── static/
│       └── index.html         # Responsive chat UI rendering A2UI cards and images
├── tests/                     # Unit and integration tests
├── pyproject.toml             # Python dependencies and project metadata
└── agents-cli-manifest.yaml   # Agents CLI configuration
```

---

## Implementation Status

### Implemented & Wired:
- [x] **Vertex AI Memory Bank**: Configured with `PreloadMemoryTool` and `generate_memories_callback`.
- [x] **Firestore Catalog**: Fully integrated (`list_coloring_pages`, `get_coloring_page`, `save_coloring_page`).
- [x] **Cloud Storage Publishing**: Direct byte uploads for generated images and videos.
- [x] **Gemini Image Generation**: `gemini-3.1-flash-lite-image` generating coloring book line art.
- [x] **Omni Video Generation**: `gemini-omni-flash-preview` producing short animated coloring clips.
- [x] **A2UI Surface Rendering**: Adaptive cards with responsive layouts, headings, body text, and images.
- [x] **Web Chat UI**: Dedicated frontend with custom branding, clickable prompt chips, and A2UI renderer.
- [x] **Agent-to-Agent (A2A)**: Full compliance with the A2A protocol and standard agent card.

### Planned, Not Yet Implemented:
- [ ] **Automated PDF Compilation**: Dynamic multi-page PDF generation and assembly using ReportLab.
- [ ] **Interactive Digital Coloring Canvas**: In-browser digital coloring canvas for tablet devices.

---

## Setup and Running Locally

### Prerequisites

1. **Python 3.11+** and **uv** package manager:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
2. **Google Cloud SDK**:
   ```bash
   gcloud auth application-default login
   gcloud config set project <YOUR_PROJECT_ID>
   ```
3. **Agents CLI**:
   ```bash
   uv tool install google-agents-cli
   ```

### 1. Install Dependencies

From the project root:
```bash
agents-cli install
```

### 2. Run the Agent Playground

Start the local development server with the ADK playground:
```bash
agents-cli playground
```

Or run the agent directly using ADK Web with Memory Bank support:
```bash
uv run adk web --memory_service_uri=agentengine://<MEMORY_BANK_ID>
```

### 3. Run the Frontend Locally

In a separate terminal, start the web interface:
```bash
cd frontend
export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_NUMBER>/locations/<LOCATION>/reasoningEngines/<ENGINE_ID>"
export AGENT_DIRECTORY="app"
uv run uvicorn main:app --host 0.0.0.0 --port 8080
```
Open a browser and navigate to the local host address.

---

## Deployment

To deploy the agent to Google Cloud Agent Runtime:

```bash
agents-cli deploy -d agent_runtime
```
