# Source-aware test generation with RAG

The testing agent receives the original code, source language/compiler details,
comprehension output, Python rewrite and any user-supplied verified examples.
It builds separate searches for test design, source-language testing/semantics,
pytest implementation, and (when relevant) numerical assertions. Hypothesis
retrieval is enabled only when Hypothesis is declared available.

Retrieval uses normalized MiniLM embeddings plus BM25-style lexical ranking,
reciprocal-rank fusion, language/category/dialect filters, round-robin selection,
deduplication and a bounded context budget. Results carry document URLs, versions,
chunk IDs and content-kind labels. Both tests and API outcomes preserve provenance.
No magic words trigger RAG: `generate_with_evidence` explicitly retrieves first.

## References

`references/sources.json` is the source registry. `references/snapshots/*.json`
contains locally extracted reference text with attribution, retrieval date and hash after synchronization.
`references/raw/` retains the downloaded originals, including the PDF documents.
The source registry covers:

- COBOL Check README, wiki, worked examples, patterns, mocks and test syntax.
- IBM ZUnit and Enterprise COBOL TRUNC scope notes (see availability below).
- CIME and Met Office LFRic Fortran unit-testing guides, test-drive and pFUnit.
- ISTQB CTFL 4.0.1 (only the test-design chapter is indexed).
- pytest assertions, parametrization, fixtures and monkeypatching.
- Python 3.11 Decimal, NumPy numerical assertions and Hypothesis strategies.
- GnuCOBOL language semantics and the COBOL-to-Java testing research paper.

IBM returned HTTP 403. The two IBM entries are explicitly labeled **curated
reference notes**, not full original manuals. The TRUNC note does not invent
compiler-specific arithmetic rules. Replace it with licensed/accessible official
text before relying on detailed TRUNC semantics. COBOL Check is archived and its
patterns are used as historical reference. Snapshots retain publishers' ownership;
check their terms before redistributing the corpus publicly.

Moving `stable`/`latest` documentation is frozen at synchronization time; the
snapshot version and date are shown to the generator. They are not guaranteed to
match your installed framework versions. Source-language semantics are retrieved
only when the compiler dialect is known; compiler details are optional API fields.

The previous 14 custom text documents and FAISS/pickle index are preserved but are
not used by the rebuilt agent. The new index is JSON plus NumPy arrays loaded with
`allow_pickle=False`. Source text changes invalidate the index until rebuilt. Downloaded originals, extracted full-text snapshots and the derived index are local build artifacts excluded from Git. The two attributed IBM scope notes are committed. Run source synchronization and index building after cloning; do not redistribute downloaded documents without checking publisher terms.

## Refresh and build

Install backend requirements, then run from `backend/`:

```powershell
python -m agents.testing.references.sync_sources
python -m agents.testing.build_index
python -m pytest tests/test_testing_rag.py -q
python scripts/evaluate_testing_rag.py
```

Source sync reports inaccessible pages and exits nonzero on partial failure. It
does not fabricate source text or delete existing snapshots. Review its report;
indexing uses the snapshots actually present. Network access is used only during
source sync, initial model download and LLM generation. The index/model can be
built and retrieved offline once cached. Paths are relative to the module rather
than the shell's current directory.

Optional model smoke check (uses configured API quota; does not execute generated code):

```powershell
python scripts/evaluate_testing_rag.py --live
```

`artifacts/testing_rag_evaluation.json` records retrieval checks. These are relevance
smoke checks, not evidence of improved defect detection. Evaluate generated suites
against independently verified originals and injected migration defects before
claiming quality improvements.

## Programmatic usage

```python
generated = await TestingAgent().generate_with_evidence(
    rewritten_code=python_code,
    legacy_code=original_code,
    language="cobol",
    compiler_dialect="gnucobol",
    explanation=analysis,
    verified_examples=reference_examples,
    available_dependencies=("pytest",),
)
test_code = generated.test_code
references = generated.evidence.references
```

`generate_tests(rewritten_code, **kwargs)` remains a code-only compatibility API.
With no original source the prompt explicitly limits the suite's migration
assurance. Model selection is configurable through `TESTING_MODEL`. API keys are
resolved in order: `GOOGLE_GENAI_API_KEY_2`, `GOOGLE_GENAI_API_KEY`, `GOOGLE_API_KEY`.

The default sandbox uses Python 3.11, pytest and standard library. Declaring NumPy
or Hypothesis available does not install it; provision it in your sandbox first.
The generator must not treat tests based on the rewrite as independent expected
outputs. Retrieval/index failures are explicit, never silently downgraded to
generation without references. Static validation rejects malformed code,
unavailable imports, missing solution imports, placeholders, and skip/xfail.
It is a quality gate, not a security boundary or a proof of test adequacy; execute
generated code only in the sandbox.
