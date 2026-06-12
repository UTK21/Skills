#!/usr/bin/env python3
"""Mechanical convention census for repo-consistency-checker.

Given one or more changed files, finds sibling files of the same kind,
extracts identifiers / imports / exports with line numbers, classifies
naming styles, and flags identifiers in the changed files whose casing
deviates from the sibling majority.

Stdlib only. Python files are parsed with `ast` (accurate); JS/TS/Java
are scanned with regex heuristics (good for declarations, not a full
parser). Output is JSON on stdout — treat it as leads to verify in the
actual code, not as a verdict.

Usage:
    python3 analyze_siblings.py CHANGED_FILE [CHANGED_FILE ...]
    python3 analyze_siblings.py --siblings a.py,b.py CHANGED_FILE
"""

import argparse
import ast
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

MAX_SIBLINGS = 4

# ---------------------------------------------------------------- casing

CASING_PATTERNS = [
    ("UPPER_SNAKE_CASE", re.compile(r"^[A-Z][A-Z0-9]*(_[A-Z0-9]+)+$|^[A-Z][A-Z0-9]+$")),
    ("snake_case", re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)+$")),
    ("PascalCase", re.compile(r"^[A-Z][a-z0-9]+([A-Z][a-z0-9]*)*$")),
    ("camelCase", re.compile(r"^[a-z][a-z0-9]*([A-Z][a-z0-9]*)+$")),
    ("lowercase", re.compile(r"^[a-z][a-z0-9]*$")),
    ("kebab-case", re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)+$")),
]


def classify_casing(name: str) -> str:
    if name.startswith("__") and name.endswith("__"):
        return "dunder"  # __init__ etc. — language convention, never an outlier
    name = name.strip("_")  # leading/trailing underscores are markers, not casing
    if not name:
        return "underscore-only"
    for label, pattern in CASING_PATTERNS:
        if pattern.match(name):
            return label
    return "mixed/other"


# ---------------------------------------------------------------- extraction

def extract_python(path: Path):
    """Identifiers + imports from a Python file via ast (accurate)."""
    out = {"identifiers": [], "imports": [], "exports": []}
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError as exc:
        out["error"] = f"syntax error: {exc}"
        return out
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out["identifiers"].append({"name": node.name, "kind": "function", "line": node.lineno})
            for arg in node.args.args + node.args.kwonlyargs:
                if arg.arg not in ("self", "cls"):
                    out["identifiers"].append({"name": arg.arg, "kind": "parameter", "line": arg.lineno})
        elif isinstance(node, ast.ClassDef):
            out["identifiers"].append({"name": node.name, "kind": "class", "line": node.lineno})
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    out["identifiers"].append({"name": target.id, "kind": "variable", "line": node.lineno})
                elif isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) \
                        and target.value.id == "self":
                    out["identifiers"].append({"name": target.attr, "kind": "attribute", "line": node.lineno})
        elif isinstance(node, ast.Import):
            for alias in node.names:
                out["imports"].append({"module": alias.name, "style": "absolute", "line": node.lineno})
        elif isinstance(node, ast.ImportFrom):
            style = "relative" if node.level else "absolute"
            out["imports"].append({"module": ("." * node.level) + (node.module or ""),
                                   "style": style, "line": node.lineno})
    return out


JS_DECL = re.compile(
    r"^\s*(?:export\s+)?(?:default\s+)?"
    r"(?:async\s+)?(?:function\s+(?P<fn>[A-Za-z_$][\w$]*)"
    r"|(?:const|let|var)\s+(?P<var>[A-Za-z_$][\w$]*)"
    r"|class\s+(?P<cls>[A-Za-z_$][\w$]*)"
    r"|(?:interface|type|enum)\s+(?P<type>[A-Za-z_$][\w$]*))"
)
JS_IMPORT = re.compile(r"^\s*import\b.*?from\s+['\"](?P<src>[^'\"]+)['\"]")
JS_EXPORT_DEFAULT = re.compile(r"^\s*export\s+default\b")
JS_EXPORT_NAMED = re.compile(r"^\s*export\s+(?!default)(?:const|let|var|function|class|interface|type|enum|\{)")


def extract_js(path: Path):
    """Declarations + imports/exports from JS/TS/TSX via regex (heuristic)."""
    out = {"identifiers": [], "imports": [], "exports": []}
    kind_map = {"fn": "function", "var": "variable", "cls": "class", "type": "type"}
    for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        m = JS_DECL.match(line)
        if m:
            for group, kind in kind_map.items():
                if m.group(group):
                    out["identifiers"].append({"name": m.group(group), "kind": kind, "line": lineno})
        m = JS_IMPORT.match(line)
        if m:
            src = m.group("src")
            style = ("relative" if src.startswith(".")
                     else "aliased" if src.startswith(("@/", "~/", "#"))
                     else "package")
            out["imports"].append({"module": src, "style": style, "line": lineno})
        if JS_EXPORT_DEFAULT.match(line):
            out["exports"].append({"style": "default", "line": lineno})
        elif JS_EXPORT_NAMED.match(line):
            out["exports"].append({"style": "named", "line": lineno})
    return out


JAVA_METHOD = re.compile(
    r"^\s*(?:public|protected|private)\s+(?:static\s+|final\s+|abstract\s+|synchronized\s+)*"
    r"[\w<>\[\],\s]+?\s+(?P<name>[A-Za-z_$][\w$]*)\s*\("
)
JAVA_CLASS = re.compile(r"^\s*(?:public\s+|final\s+|abstract\s+)*(?:class|interface|enum|record)\s+(?P<name>[A-Za-z_$][\w$]*)")
JAVA_FIELD = re.compile(
    r"^\s*(?:public|protected|private)\s+(?:static\s+|final\s+)*[\w<>\[\],\s]+?\s+(?P<name>[A-Za-z_$][\w$]*)\s*[=;]"
)
JAVA_IMPORT = re.compile(r"^\s*import\s+(?:static\s+)?(?P<module>[\w.]+\*?)\s*;")
JAVA_PARAMS = re.compile(r"\(([^)]*)\)")


def extract_java(path: Path):
    out = {"identifiers": [], "imports": [], "exports": []}
    for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        m = JAVA_CLASS.match(line)
        if m:
            out["identifiers"].append({"name": m.group("name"), "kind": "class", "line": lineno})
            continue
        m = JAVA_METHOD.match(line)
        if m and m.group("name") not in ("if", "for", "while", "switch", "catch", "return", "new"):
            out["identifiers"].append({"name": m.group("name"), "kind": "method", "line": lineno})
            pm = JAVA_PARAMS.search(line)
            if pm:
                for param in pm.group(1).split(","):
                    parts = param.strip().rsplit(" ", 1)
                    if len(parts) == 2 and re.match(r"^[A-Za-z_$][\w$]*$", parts[1]):
                        out["identifiers"].append({"name": parts[1], "kind": "parameter", "line": lineno})
            continue
        m = JAVA_FIELD.match(line)
        if m:
            out["identifiers"].append({"name": m.group("name"), "kind": "field", "line": lineno})
        m = JAVA_IMPORT.match(line)
        if m:
            style = "wildcard" if m.group("module").endswith("*") else "explicit"
            out["imports"].append({"module": m.group("module"), "style": style, "line": lineno})
    return out


EXTRACTORS = {
    ".py": extract_python,
    ".js": extract_js, ".jsx": extract_js, ".ts": extract_js, ".tsx": extract_js,
    ".java": extract_java,
}


# ---------------------------------------------------------------- siblings

def git_last_commit_ts(path: Path) -> int:
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%ct", "--", str(path)],
                             capture_output=True, text=True, timeout=10)
        return int(out.stdout.strip() or 0)
    except Exception:
        return 0


def find_siblings(changed: Path, all_changed: set) -> list:
    """Same-directory, same-extension files not in the diff, newest-touched first."""
    candidates = [p for p in changed.parent.glob(f"*{changed.suffix}")
                  if p.resolve() != changed.resolve()
                  and p.resolve() not in all_changed
                  and not p.name.startswith(".")]
    candidates.sort(key=git_last_commit_ts, reverse=True)
    return candidates[:MAX_SIBLINGS]


# ---------------------------------------------------------------- analysis

def summarize(extracted: dict) -> dict:
    casing = Counter(classify_casing(i["name"]) for i in extracted["identifiers"])
    imports = Counter(i["style"] for i in extracted["imports"])
    exports = Counter(e["style"] for e in extracted["exports"])
    return {"casing": dict(casing), "import_styles": dict(imports), "export_styles": dict(exports)}


def dominant(counter: Counter):
    if not counter:
        return None
    return counter.most_common(1)[0][0]


def analyze(changed_path: Path, siblings: list) -> dict:
    extractor = EXTRACTORS[changed_path.suffix]
    changed_data = extractor(changed_path)

    sibling_reports, baseline_casing, baseline_imports, baseline_exports = [], Counter(), Counter(), Counter()
    for sib in siblings:
        data = extractor(sib)
        baseline_casing.update(classify_casing(i["name"]) for i in data["identifiers"])
        baseline_imports.update(i["style"] for i in data["imports"])
        baseline_exports.update(e["style"] for e in data["exports"])
        sibling_reports.append({"file": str(sib), "summary": summarize(data)})

    # ignore styles that are inherently fine alongside the dominant one
    benign = {"UPPER_SNAKE_CASE", "lowercase", "underscore-only", "dunder"}
    dom_casing = dominant(Counter({k: v for k, v in baseline_casing.items()
                                   if k not in benign and k != "PascalCase"}))
    outliers = []
    if dom_casing:
        for ident in changed_data["identifiers"]:
            style = classify_casing(ident["name"])
            if ident["kind"] in ("class", "type"):
                continue  # classes/types are PascalCase in all three stacks
            if style not in benign and style != dom_casing and style != "PascalCase":
                outliers.append({**ident, "casing": style,
                                 "expected": dom_casing,
                                 "note": f"sibling majority for functions/variables is {dom_casing}"})
            elif style == "PascalCase":
                outliers.append({**ident, "casing": style, "expected": dom_casing,
                                 "note": "PascalCase on a non-class identifier; verify against siblings"})

    dom_import = dominant(baseline_imports)
    import_outliers = [i for i in changed_data["imports"]
                       if dom_import and i["style"] != dom_import and i["style"] != "package"]
    dom_export = dominant(baseline_exports)
    export_outliers = [e for e in changed_data["exports"] if dom_export and e["style"] != dom_export]

    return {
        "changed_file": str(changed_path),
        "siblings_used": [str(s) for s in siblings],
        "changed_summary": summarize(changed_data),
        "sibling_summaries": sibling_reports,
        "baseline_dominant": {"casing": dom_casing, "import_style": dom_import, "export_style": dom_export},
        "naming_outliers": outliers,
        "import_style_outliers": import_outliers,
        "export_style_outliers": export_outliers,
        "identifiers_in_changed_file": changed_data["identifiers"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", help="changed files to analyze")
    parser.add_argument("--siblings", help="comma-separated sibling files to use instead of auto-discovery")
    args = parser.parse_args()

    all_changed = {Path(f).resolve() for f in args.files}
    results, skipped = [], []
    for f in args.files:
        path = Path(f)
        if not path.exists():
            skipped.append({"file": f, "reason": "not found"})
            continue
        if path.suffix not in EXTRACTORS:
            skipped.append({"file": f, "reason": f"unsupported extension {path.suffix}"})
            continue
        siblings = ([Path(s.strip()) for s in args.siblings.split(",")] if args.siblings
                    else find_siblings(path, all_changed))
        siblings = [s for s in siblings if s.exists() and s.suffix in EXTRACTORS]
        results.append(analyze(path, siblings))

    json.dump({"results": results, "skipped": skipped,
               "note": "Heuristic census — verify every outlier against the actual lines before reporting it."},
              sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
