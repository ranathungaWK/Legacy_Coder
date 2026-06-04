# LegacyCoder

The rebuilt source-aware Testing Agent, reference documents, retrieval design,
and rebuild/evaluation commands are documented in
[the Testing Agent guide](backend/agents/testing/README.md).

LegacyCoder is a production-grade AI modernization pipeline that transforms legacy codebase logic (such as COBOL) into modern, clean Python 3.12 code. 

The application utilizes a multi-agent AI architecture powered by `langchain-google-genai` and orchestrates a comprehensive end-to-end workflow: from code comprehension to transformation, automated test generation, and isolated sandbox verification.

## The Modernization Workflow

The pipeline consists of a sequential, four-stage orchestration process managed by the `ModernizationPipeline` in the backend. 

1. **User Input:** The user submits a snippet of legacy code (e.g., COBOL, C++) through the React frontend.
2. **Analysis:** The pipeline triggers the **Comprehension Agent** to deeply analyze the semantics of the legacy code.
3. **Rewrite:** The output of the comprehension stage is passed to the **Modernization Agent**, which produces a modern Python script.
4. **Test Generation:** The modernized Python code is then sent to the **Testing Agent**, which queries a RAG vector database for testing patterns and generates a comprehensive `pytest` file.
5. **Validation:** Finally, the **Verification Agent** spins up an isolated Docker Sandbox, installs any dependencies, runs the generated tests against the Python code, and captures the execution results.
6. **Result Display:** The frontend receives the finalized outputs from all agents and visualizes the insights, code diffs, and test metrics for the user.

## Multi-Agent Architecture

### 1. Comprehension Agent
- **Purpose:** Analyzes the legacy code semantics, identifying inputs, outputs, assumptions, side effects, and edge cases to build a deep understanding of the core business logic.
- **Technology Stack:**
  - `ChatGoogleGenerativeAI` (Gemini 2.5 Flash)
  - Langchain `ChatPromptTemplate`
  - Langchain `JsonOutputParser` mapped to Pydantic schemas to strictly enforce structured data output.

### 2. Code Transformation Agent (Modernization)
- **Purpose:** Generates a clean, idiomatic Python rewrite of the legacy code based on the insights gathered during the comprehension phase.
- **Technology Stack:**
  - `ChatGoogleGenerativeAI` (Gemini Pro/Flash)
  - Langchain `ChatPromptTemplate`
  - Outputs Pydantic-structured `RewriteOutput` containing the raw Python code, design notes, assumptions made, and compatibility notes.

### 3. Test Generation Agent
- **Purpose:** Generates a robust `pytest` suite covering normal cases, edge cases, and boundary conditions for the modernized Python code.
- **Technology Stack:**
  - **RAG System (Retrieval-Augmented Generation):** Uses focused, filtered searches over attributable COBOL/Fortran testing guides, ISTQB, pytest and numerical references, combining dense embeddings and lexical ranking.
  - Langchain `ChatPromptTemplate` injecting retrieved RAG context.
  - `ChatGoogleGenerativeAI` to construct the tests.
  - Source-aware prompts, cited retrieval evidence, and static validation of generated test scripts.

### 4. Verification Agent
- **Purpose:** Safely executes the modernized Python code against the generated test suite and ensures that syntax validation and runtime correctness are fully verified before deployment.
- **Technology Stack:**
  - **Docker Engine API:** Orchestrates ephemeral Docker containers.
  - **Docker-in-Docker (DooD):** Mounts the Docker socket to spin up sibling containers dynamically.
  - **Pytest:** Runs the test suites inside the sandboxed environments and captures stdout/stderr.
  - Custom size limiters and dependency parsers to ensure the sandbox doesn't crash from infinite loops or malicious inputs.

## Tech Stack Overview

- **Backend:** Python, FastAPI, Pydantic, Langchain, Pytest, Docker Engine API
- **Frontend:** React, Vite, TailwindCSS, Framer Motion, Lucide Icons
- **AI Models:** Gemini (Google Generative AI)

## How to Start the Web Server

### Prerequisites
- Docker Desktop installed and running.
- API Keys for Google Generative AI.

### Configuration
1. Navigate to the root directory of the project.
2. In the `backend` directory, create a `.env` file containing your Gemini API keys:
   ```env
   GOOGLE_GENAI_API_KEY=your_primary_api_key
   GOOGLE_GENAI_API_KEY_2=your_secondary_api_key_for_testing_agent
   ```

### Launching with Docker Compose
The entire application (backend and frontend) is containerized and managed by Docker Compose. To start both servers simultaneously:

1. Open your terminal at the root of the project (`c:\KR\work\LegacyCoder`).
2. Build and start the containers in detached mode:
   ```bash
   docker compose up --build -d
   ```
3. To view the logs of the running services:
   ```bash
   docker compose logs -f
   ```

### Accessing the Application
- **Frontend Web UI:** Open your browser and navigate to `http://localhost:5173`
- **Backend API Docs:** Open your browser and navigate to `http://localhost:8000/docs`

Once the web server is running, simply paste your legacy code into the web interface, select the source language, and hit "Start Modernization".
