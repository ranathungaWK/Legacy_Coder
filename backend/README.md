# **LegacyCoder** – Modernizing Legacy Source Code with LLM‑powered Agents

> The Testing Agent has been rebuilt. See [its current guide](agents/testing/README.md)
> for the reference corpus, hybrid retrieval, source-aware prompts, and setup commands.
> The older FAISS knowledge-base description below is historical.

**Summary**
LegacyCoder is a **FastAPI** service that receives legacy source code and returns a clean, idiomatic Python implementation.  It orchestrates four LLM‑driven agents:
1️⃣ **ComprehensionAgent** – parses the legacy snippet and produces a detailed JSON description.
2️⃣ **ModernizationAgent** – rewrites the code into Python using the description.
3️⃣ **TestingAgent** – generates pytest test suites by retrieving relevant patterns from a FAISS vector store.
4️⃣ **VerificationAgent** – runs the generated tests in an isolated Docker sandbox and reports the result.

**Structure**
```
LegacyCoder/
│
├─ app/                     # FastAPI entry point & Pydantic schemas
│   ├─ main.py
│   ├─ api/v1/
│   │   ├─ modernize.py      # /modernize router – orchestrates agents
│   │   └─ health.py         # health‑check endpoint
│   └─ schemas/
│       ├─ input.py          # LegacyCodeInput model
│       ├─ explanation.py   # ExplanationOutput model
│       ├─ rewrite.py        # RewriteOutput model
│       ├─ testOutcome.py    # TestExecutionOutput model
│       ├─ verifyExecution.py# ExecutionResult dataclass
│       └─ pipelineEvent.py   # optional event model for pipelines
│
├─ agents/
│   ├─ comprehension/       # Gemini‑based analysis
│   ├─ modernization/        # Gemini‑based rewrite
│   ├─ testing/              # Google GenAI test generation + FAISS retrieval
│   └─ verification/         # Docker sandbox executor
│
├─ execution/               # sandbox runner (Docker + pytest)
├─ rag/                      # placeholder for future RAG logic
├─ orchestration/            # stubs for async pipelines
├─ config/                   # environment & logging hooks (currently empty)
├─ scripts/                  # utility scripts (e.g., build index)
├─ tests/                    # sanity‑check scripts for each agent
├─ pyproject.toml
└─ README.md                 # **THIS FILE**
```

**Contracts**
| Model | Location | Purpose |
|-------|----------|---------|
| **LegacyCodeInput** | `app/schemas/input.py` | API request – `code`, `language`, optional `job_id` |
| **ExplanationOutput** | `app/schemas/explanation.py` | Output of **ComprehensionAgent** – purpose, I/O, assumptions, edge cases, confidence |
| **RewriteOutput** | `app/schemas/rewrite.py` | Output of **ModernizationAgent** – Python code + design notes |
| **ExecutionResult** | `app/schemas/verifyExecution.py` | Docker sandbox outcome – success, exit code, stdout, stderr, timeout |
| **TestExecutionOutput** | `app/schemas/testOutcome.py` | Test code paired with its execution result |
| **PipelineEvent** | `app/schemas/pipelineEvent.py` | Optional event model for a multi‑step orchestration pipeline |

**Agents**
| Agent | Module | Model | Core Logic |
|-------|--------|-------|------------|
| **ComprehensionAgent** | `agents/comprehension/agent.py` | Gemini `gemini-2.5-flash` | Formats system/user prompts, invokes Gemini, parses JSON to `ExplanationOutput` |
| **ModernizationAgent** | `agents/modernization/agent.py` | Gemini `gemini-2.5-flash` | Receives legacy code + explanation, prompts Gemini to emit Python + notes, validates with `RewriteOutput` |
| **TestingAgent** | `agents/testing/agent.py` | Gemini `gemini-2.5-flash` | Builds a retrieval query, fetches up to 5 relevant knowledge‑base chunks (FAISS), builds a QA prompt, invokes LLM, strips markdown fences |
| **VerificationAgent** | `agents/verification/agent.py` | – (no LLM) | Writes solution & test files to a temporary folder, runs `docker run … pytest` inside the sandbox, returns `ExecutionResult` |

**Knowledge Base (TestingAgent)**
The folder `agents/testing/knowledge_base/` holds plain‑text files grouped by:
- **migrations** – concrete legacy‑to‑Python patterns (e.g., `c_to_python.txt`).
- **patterns** – reusable algorithmic or I/O patterns.
- **core** – generic edge‑case collections.
- **language_independent** – type‑agnostic corner cases.
Running `python agents/testing/build_index.py`:
1. Walks the directory, reads every `.txt`.
2. Splits each file into 500‑char chunks (50‑char overlap).
3. Computes embeddings with `sentence‑transformers/all‑MiniLM‑L6‑v2`.
4. Persists a FAISS index under `agents/testing/vectorstore/faiss_index`.
A pre‑built index (`index.pkl`/`index.faiss`) ships with the repo; rebuild only after adding new files.

**Sandbox (VerificationAgent)**
`execution/sandbox.py` creates a temporary directory, writes `solution.py` and `test_solution.py`, mounts the folder into a Docker container (default image `sandbox-python:3.11`), optionally installs a mounted `requirements.txt`, runs `pytest -vv`, and captures stdout, stderr, exit code, and timeout. The container must contain Python 3.11 and `pytest`.

**Running the Service**
**Prerequisites**
| Requirement | How to satisfy |
|------------|----------------|
| Python 3.9+ | `pyenv install 3.11 && pyenv local 3.11` |
| FastAPI & dependencies | `pip install -r requirements.txt` |
| Google Gemini API key | Add `GOOGLE_API_KEY=YOUR_KEY` to a `.env` file at the repo root |
| Optional testing-agent key | Add `GOOGLE_GENAI_API_KEY_2=YOUR_KEY` to route only `TestingAgent` to a separate Gemini quota |
| Docker (for verification) | Install Docker Engine; ensure you can run `docker` without sudo |
| FAISS vector store | Already present; rebuild with `python agents/testing/build_index.py` if needed |

Start the API:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The service will be reachable at `http://localhost:8000`.

**Example Request**
```bash
curl -X POST http://localhost:8000/api/v1/modernize/ \
  -H "Content-Type: application/json" \
  -d '{"code": "function add(a,b){ return a+b; }", "language": "javascript", "job_id": "demo-001"}'
```
Response (formatted):
```json
{
  "python_code": "def add(a, b):\n    return a + b",
  "design_notes": ["Preserved JavaScript '+' semantics for both numbers and strings."],
  "assumptions_made": ["Input types are compatible with Python '+' operator."],
  "compatibility_notes": ["String concatenation behaviour matches JavaScript when both operands are strings."]
}
```

**Generating & Verifying Tests (Programmatic)**
```python
from agents.testing.agent import TestingAgent
from agents.verification.agent import VerificationAgent

rewritten = """
def add(a, b):
    return a + b
"""

# Generate pytest suite
test_agent = TestingAgent()
test_code = await test_agent.generate_tests(rewritten_code=rewritten)
print("Generated tests:\n", test_code)

# Verify inside Docker
verif_agent = VerificationAgent()
result = verif_agent.verify(rewritten_code=rewritten, test_code=test_code)
print("Verification result:", result)
```
Typical `ExecutionResult` output:
```
ExecutionResult(success=True, exit_code=0, stdout='... 1 passed in 0.04s ...', stderr='', timed_out=False)
```

**Development & Testing**
- Run unit tests: `pytest -vv`
- Add new migration patterns: drop a `.txt` into `agents/testing/knowledge_base/` and re‑run the index builder.
- Future work: a full async orchestration pipeline (`orchestration/`), richer RAG integration (`rag/`), structured logging, and hardened sandbox security.

**Config & Secrets**
Environment variables are loaded via `python‑dotenv`. Typical `.env` entries:
```dotenv
GOOGLE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
GOOGLE_GENAI_API_KEY_2=sk-yyyyyyyyyyyyyyyyyyyy
SANDBOX_IMAGE=sandbox-python:3.11  # optional override
```
Typed settings can be added to `config/settings.py` for automatic validation.

**Limits & Future Work**
| Area | Current | Planned |
|------|---------|--------|
| Orchestration | Stub files only | Async pipeline with `PipelineEvent` and background jobs |
| RAG | Empty package | Integrate LangChain `RetrievalQA` using the same FAISS store |
| Docker image | Assumes pre‑built `sandbox-python:3.11` | Provide Dockerfile and publish to Docker Hub |
| Index ingestion | Hard‑coded path | CLI with configurable source directory |
| Logging | Empty `config/logging.py` | Add `loguru`/`structlog` for JSON logs |
| LLM model flexibility | Fixed to Gemini | Configurable model selection |
| Security | Minimal sandbox | Add static analysis (`restrictedpython`), rate limiting, prompt‑injection guards |

**Contribute**
1. Fork the repo and create a feature branch.
2. Ensure all tests pass (`pytest -q`). Add tests for new functionality.
3. Follow the single‑responsibility style; keep functions small and type‑annotated.
4. Submit a PR – CI will run the test suite and lint checks.

---
*LegacyCoder is released under the MIT License.*

**Agent Interaction Diagram**
```mermaid
graph LR
    subgraph API
        ModernizeEndpoint[POST /api/v1/modernize] --> Comprehension
    end
    Comprehension[ComprehensionAgent] -->|ExplanationOutput| Modernization[ModernizationAgent]
    Modernization -->|RewriteOutput| Testing[TestingAgent]
    Testing -->|Generated pytest| Verification[VerificationAgent]
    Verification -->|ExecutionResult| Response[API Response]

    Testing -->|FAISS retrieval| VectorStore[FAISS Vector Store]
    Verification -->|Docker sandbox| Docker[Docker (sandbox-python:3.11)]
```
