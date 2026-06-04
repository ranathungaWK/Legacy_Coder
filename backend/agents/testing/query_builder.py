"""Focused retrieval queries built from source evidence, without another LLM call."""
from __future__ import annotations
import ast
import json
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class RetrievalQuery:
    text: str
    categories: tuple[str, ...]
    language: str = "unknown"
    dialect: str = ""

def serialize_evidence(value) -> str:
    if value is None:
        return "Not supplied."
    if hasattr(value, "model_dump"):
        value = value.model_dump()
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)

class QueryBuilder:
    def build_queries(self, code: str, *, legacy_code: str = "", language: str = "unknown",
                      explanation=None, compiler_dialect: str = "",
                      available_dependencies: tuple[str, ...] = ("pytest",)) -> list[RetrievalQuery]:
        evidence = serialize_evidence(explanation)
        combined = (legacy_code + " " + code + " " + evidence).lower()
        patterns = {
            r"\bpic(?:ture)?\b": "PICTURE receiving field numeric limits",
            r"\bcomp-3\b": "COMP-3 packed decimal precision",
            r"\brounded\b": "ROUNDED rounding ties",
            r"\bsize\s+error\b": "ON SIZE ERROR overflow handling",
            r"\boccurs\b": "OCCURS table subscripts bounds",
            r"\bredefines\b": "REDEFINES overlapping storage",
            r"\b(decimal|quantize|interest|balance|currency|money)\b": "decimal monetary precision rounding",
            r"\b(real|double precision|float|real64|real32)\b": "floating point numerical tolerance",
            r"\b(dimension|allocatable|reshape|numpy|array)\b": "array shape bounds ordering",
            r"\b(read|write|open|close|file|database)\b": "file IO external dependency isolation",
            r"\bperform\b": "PERFORM loop termination",
            r"\bdo\b": "loop bounds iteration count",
        }
        topics = [topic for pattern, topic in patterns.items() if re.search(pattern, combined)]
        names = []
        try:
            tree = ast.parse(code)
            if any(isinstance(n, ast.Div) for n in ast.walk(tree)):
                topics.append("division zero denominator numerical precision")
            if any(isinstance(n, (ast.If, ast.IfExp, ast.Compare)) for n in ast.walk(tree)):
                topics.append("decision conditions branch thresholds")
            names = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
        except SyntaxError:
            pass
        topic = "; ".join(topics) or "normal inputs boundary conditions output behavior"
        behavior = re.sub(r"\s+", " ", evidence)[:220]
        make = lambda text, cats: RetrievalQuery(text, cats, language.lower(), compiler_dialect.lower())
        queries = [
            make(f"{topic}. Test design equivalence partitioning boundary value analysis decision tables branch coverage. {behavior}", ("test_design",)),
            make(f"{language} unit testing {topic}. Procedures {' '.join(names[:6])}. {behavior}", ("language_testing", "language_semantics")),
            make(f"pytest parametrization assertions expected results {topic}", ("python_testing",)),
        ]
        if any(word in combined for word in ("decimal", "rounded", "comp-3", "interest", "currency", "money")):
            queries.append(make(f"Python Decimal quantize rounding context precision monetary assertions. {topic}", ("numeric_testing",)))
        elif any(word in combined for word in ("float", "real", "numpy", "array", "dimension")):
            queries.append(make(f"numerical array assert_allclose shape absolute relative tolerance NaN. {topic}", ("numeric_testing",)))
        if "hypothesis" in available_dependencies:
            queries.append(make(f"Hypothesis strategies properties {topic}", ("property_testing",)))
        return queries

    def build_query(self, code: str, context: str = "") -> str:
        return self.build_queries(code, explanation=context)[0].text
