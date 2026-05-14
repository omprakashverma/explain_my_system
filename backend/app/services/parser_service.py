import re
from typing import Any, Dict, List

from backend.app.utils.text_utils import (
    canonicalize_route_path,
    clean_route_path,
    line_number_from_offset,
)

PYTHON_ROUTE_RE = re.compile(
    r"@(?P<owner>[\w\.]+)\.(?P<method>get|post|put|patch|delete|options|head|trace)"
    r"\(\s*(?P<quote>['\"])(?P<path>.*?)(?P=quote)",
    re.IGNORECASE | re.DOTALL,
)
PYTHON_GENERIC_ROUTE_RE = re.compile(
    r"@(?P<owner>[\w\.]+)\.route"
    r"\(\s*(?P<quote>['\"])(?P<path>.*?)(?P=quote)(?P<rest>.*?)\)",
    re.IGNORECASE | re.DOTALL,
)
JS_ROUTE_RE = re.compile(
    r"\b(?P<owner>\w+)\.(?P<method>get|post|put|patch|delete|options|head|all)"
    r"\(\s*(?P<quote>['\"`])(?P<path>.*?)(?P=quote)",
    re.IGNORECASE | re.DOTALL,
)
METHODS_ARG_RE = re.compile(r"methods\s*=\s*\[(?P<methods>[^\]]+)\]", re.IGNORECASE | re.DOTALL)
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head", "trace"}


def parse_methods_from_rest(rest: str) -> List[str]:
    match = METHODS_ARG_RE.search(rest or "")
    if not match:
        return ["GET"]
    methods: List[str] = []
    for item in re.findall(r"['\"]([A-Za-z]+)['\"]", match.group("methods")):
        upper_item = item.upper()
        if upper_item == "ALL":
            methods.extend(["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
        elif item.lower() in HTTP_METHODS:
            methods.append(upper_item)
    return sorted(set(methods)) or ["GET"]


def expand_route_methods(method: str) -> List[str]:
    if method.lower() == "all":
        return ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
    return [method.upper()]


def extract_repository_operations(files: Dict[str, str]) -> List[Dict[str, Any]]:
    operations: List[Dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()

    for file_path, text in files.items():
        if file_path.endswith(".py"):
            for match in PYTHON_ROUTE_RE.finditer(text):
                method = match.group("method").upper()
                raw_path = clean_route_path(match.group("path"))
                line_no = line_number_from_offset(text, match.start())
                key = (method, raw_path, file_path, line_no)
                if key in seen:
                    continue
                seen.add(key)
                operations.append(
                    {
                        "method": method,
                        "path": raw_path,
                        "canonical_path": canonicalize_route_path(raw_path),
                        "file": file_path,
                        "line": line_no,
                        "framework": "python",
                    }
                )
            for match in PYTHON_GENERIC_ROUTE_RE.finditer(text):
                methods = parse_methods_from_rest(match.group("rest"))
                raw_path = clean_route_path(match.group("path"))
                line_no = line_number_from_offset(text, match.start())
                for method in methods:
                    key = (method, raw_path, file_path, line_no)
                    if key in seen:
                        continue
                    seen.add(key)
                    operations.append(
                        {
                            "method": method,
                            "path": raw_path,
                            "canonical_path": canonicalize_route_path(raw_path),
                            "file": file_path,
                            "line": line_no,
                            "framework": "python",
                        }
                    )
        elif file_path.endswith((".js", ".ts", ".tsx", ".jsx")):
            for match in JS_ROUTE_RE.finditer(text):
                methods = expand_route_methods(match.group("method"))
                raw_path = clean_route_path(match.group("path"))
                line_no = line_number_from_offset(text, match.start())
                for method in methods:
                    key = (method, raw_path, file_path, line_no)
                    if key in seen:
                        continue
                    seen.add(key)
                    operations.append(
                        {
                            "method": method,
                            "path": raw_path,
                            "canonical_path": canonicalize_route_path(raw_path),
                            "file": file_path,
                            "line": line_no,
                            "framework": "javascript",
                        }
                    )

    operations.sort(key=lambda item: (item["path"], item["method"], item["file"], item["line"]))
    return operations
