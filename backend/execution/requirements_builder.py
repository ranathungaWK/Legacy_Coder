import ast
import sys
from typing import Iterable, Set


def _iter_import_modules(code: str) -> Iterable[str]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                yield n.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                yield node.module.split(".")[0]


def build_requirements_from_sources(sources: Iterable[str]) -> str:
    """Return a minimal requirements.txt content inferred from import statements.

    This does a best-effort extraction: it collects top-level import module names,
    filters out standard-library modules using sys.stdlib_module_names when available,
    and returns newline-separated package names. No versions are inferred.
    """

    stdlib: Set[str] = set()
    if hasattr(sys, "stdlib_module_names"):
        stdlib = set(sys.stdlib_module_names)  # Python 3.10+

    pkgs: Set[str] = set()
    for src in sources:
        for mod in _iter_import_modules(src or ""):
            if not mod:
                continue
            if mod in stdlib:
                continue
            # skip relative imports like "." or empty
            if mod.startswith("_"):
                continue
            pkgs.add(mod)

    # Heuristic: drop obvious non-package names
    drops = {"typing", "builtins", "pytest"}  # we may still include pytest if tests need it
    pkgs = {p for p in pkgs if p not in drops}

    if not pkgs:
        return ""

    return "\n".join(sorted(pkgs)) + "\n"


def detect_heavy_packages(requirements_text: str, size_threshold_bytes: int | None = None, timeout: float = 5.0) -> list:
    """Return a list of heavy or hardware-bound packages found in the provided
    requirements text. This list is a conservative heuristic — packages here are
    considered heavy to install in ephemeral sandboxes (large wheels, native
    extensions, or GPU/accelerator drivers).
    """
    if not requirements_text:
        return []

    # Curated fallback set of heavy packages (numpy intentionally excluded)
    curated_heavy = {
        "pandas",
        "scipy",
        "torch",
        "tensorflow",
        "mxnet",
        "opencv-python",
        "opencv_contrib_python",
        "dlib",
        "faiss",
        "faiss-cpu",
        "faiss-gpu",
        "torchvision",
        "torchaudio",
        "pytorch",
    }

    found = []
    pkgs = [line.strip().split("==")[0].split("<=")[0].split(">=")[0].lower().split("[")[0]
            for line in requirements_text.splitlines() if line.strip()]

    # If a size threshold is provided, attempt to query PyPI for release file sizes.
    # Mark a package as heavy if any distribution file for the latest release exceeds the threshold.
    sizes_map = {}
    if size_threshold_bytes is not None and pkgs:
        import urllib.request
        import json

        for name in pkgs:
            try:
                url = f"https://pypi.org/pypi/{name}/json"
                with urllib.request.urlopen(url, timeout=timeout) as resp:
                    if resp.status != 200:
                        continue
                    data = json.load(resp)
                    urls = data.get("urls", [])
                    max_size = 0
                    for entry in urls:
                        size = entry.get("size") or 0
                        if isinstance(size, int) and size > max_size:
                            max_size = size
                    sizes_map[name] = max_size
            except Exception:
                # network error or package not found — leave sizes_map without this package
                continue

    for name in pkgs:
        if not name:
            continue

        # If we have a size threshold and a discovered size, use it
        if size_threshold_bytes is not None and name in sizes_map:
            if sizes_map[name] >= size_threshold_bytes:
                found.append(name)
            continue

        # otherwise fall back to curated list
        if name in curated_heavy:
            found.append(name)

    return sorted(set(found))
