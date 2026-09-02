#!/usr/bin/env python3
"""Validate repository syntax, references and public-artifact boundaries.

The scan is intentionally split in two. Actual media-like files are prohibited
across the whole repository. Scoped string-content checks cover current machine
facts, generated reviews, runtime artifacts, validation records, current
task/state documents and the newly migrated Succession ledger. The original 30
immutable legacy Markdown ledgers are reported as an explicit excluded
provenance scope and are validated only through their conservative canonical
conversion; test fixtures and validator source are excluded because they
intentionally contain rejected examples.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence
from urllib.parse import unquote


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPOSITORY_ROOT = SKILL_ROOT.parents[1]

PROHIBITED_FILE_SUFFIXES = {
    ".mp4", ".mkv", ".mov", ".avi", ".m4v", ".webm",
    ".wav", ".mp3", ".flac", ".aac", ".m4a", ".ogg",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".heic", ".tif", ".tiff", ".bmp",
    ".srt", ".ass", ".ssa", ".vtt", ".pdf",
}

STRING_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "PRIVATE-ABSOLUTE-PATH",
        re.compile(
            r"(?i)(?:file://|/Users/|/Volumes/|/private/|/tmp/|/var/|/home/|~/|[A-Za-z]:\\)"
        ),
    ),
    (
        "MEDIA-OR-SUBTITLE-FILENAME",
        re.compile(
            r"(?i)\.(?:mp4|mkv|mov|avi|m4v|webm|wav|mp3|flac|aac|m4a|ogg|png|jpe?g|gif|webp|heic|tiff?|bmp|srt|ass|ssa|vtt|pdf)\b"
        ),
    ),
    (
        "SIGNED-URL-LIKE",
        re.compile(
            r"(?i)https?://[^\s\"']+\?(?:[^\s\"']*&)*(?:signature|sig|token|expires|credential)="
        ),
    ),
    (
        "CREDENTIAL-LIKE-MATERIAL",
        re.compile(
            r"(?:-----BEGIN [A-Z ]*PRIVATE KEY-----|\bsk-[A-Za-z0-9_-]{20,}\b|"
            r"\bgh[pousr]_[A-Za-z0-9]{20,}\b|\bAKIA[0-9A-Z]{16}\b|"
            r"\bBearer\s+[A-Za-z0-9._~-]{20,})"
        ),
    ),
    (
        "MEDIA-FINGERPRINT-TOKEN",
        re.compile(r"(?<![A-Za-z0-9])[A-Fa-f0-9]{40,}(?![A-Za-z0-9])"),
    ),
)

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def repository_files(root: Path = REPOSITORY_ROOT) -> list[Path]:
    return sorted(
        (
            path
            for path in root.rglob("*")
            if path.is_file()
            and ".git" not in path.parts
            and "__pycache__" not in path.parts
        ),
        key=lambda path: path.as_posix(),
    )


def public_artifact_files(root: Path = REPOSITORY_ROOT) -> list[Path]:
    paths: set[Path] = set()
    evidence_root = root / "research" / "evidence"
    paths.update(evidence_root.rglob("*.scene-evidence.json"))
    paths.update(evidence_root.rglob("*.scene-evidence.generated.md"))
    paths.add(
        evidence_root
        / "succession"
        / "SUCCESSION_S01E06_BOARD_VOTE_EVIDENCE_V0.1.md"
    )
    for relative in (
        "research/grammar",
        "research/validation",
        "examples/forward-tests",
        "context",
        "skills/drama-director-compiler/references",
    ):
        artifact_root = root / relative
        if artifact_root.exists():
            paths.update(path for path in artifact_root.rglob("*") if path.is_file())
    paths.add(root / "skills" / "drama-director-compiler" / "SKILL.md")
    return sorted(
        (path for path in paths if path.is_file()),
        key=lambda path: path.as_posix(),
    )


def historical_legacy_markdown_files(root: Path = REPOSITORY_ROOT) -> list[Path]:
    evidence_root = root / "research" / "evidence"
    succession = (
        evidence_root
        / "succession"
        / "SUCCESSION_S01E06_BOARD_VOTE_EVIDENCE_V0.1.md"
    )
    return sorted(
        (
            path
            for path in evidence_root.rglob("*.md")
            if not path.name.endswith(".scene-evidence.generated.md")
            and path != succession
            and path.with_suffix(".scene-evidence.json").is_file()
        ),
        key=lambda path: path.as_posix(),
    )


def _relative(path: Path, root: Path = REPOSITORY_ROOT) -> str:
    return path.relative_to(root).as_posix()


def _issue(
    issues: list[dict[str, str]],
    code: str,
    path: Path,
    root: Path = REPOSITORY_ROOT,
) -> None:
    issues.append({"code": code, "path": _relative(path, root)})


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def validate_markdown_links(
    files: Iterable[Path],
    issues: list[dict[str, str]],
    root: Path = REPOSITORY_ROOT,
) -> int:
    checked = 0
    for path in files:
        if path.suffix.lower() != ".md":
            continue
        text = _read_text(path)
        if text is None:
            continue
        for raw_target in MARKDOWN_LINK_RE.findall(text):
            target = raw_target.strip().strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            target = unquote(target.split("#", 1)[0])
            checked += 1
            candidate = (path.parent / target).resolve()
            try:
                candidate.relative_to(root.resolve())
            except ValueError:
                _issue(issues, "MARKDOWN-LINK-ESCAPES-REPOSITORY", path, root)
                continue
            if not candidate.exists():
                _issue(issues, "BROKEN-MARKDOWN-LINK", path, root)
    return checked


def _has_media_signature(path: Path) -> bool:
    try:
        prefix = path.read_bytes()[:16]
    except OSError:
        return False
    return any(
        (
            prefix.startswith(b"\x89PNG\r\n\x1a\n"),
            prefix.startswith(b"\xff\xd8\xff"),
            prefix.startswith((b"GIF87a", b"GIF89a")),
            prefix.startswith(b"RIFF"),
            prefix.startswith(b"\x1aE\xdf\xa3"),
            prefix.startswith(b"ID3"),
            prefix.startswith(b"fLaC"),
            prefix.startswith(b"%PDF-"),
            len(prefix) >= 12 and prefix[4:8] == b"ftyp",
        )
    )


def validate_repository(root: Path = REPOSITORY_ROOT) -> dict[str, Any]:
    root = root.resolve()
    all_files = repository_files(root)
    public_files = public_artifact_files(root)
    excluded_legacy_files = historical_legacy_markdown_files(root)
    issues: list[dict[str, str]] = []

    symlinks = sorted(
        (path for path in root.rglob("*") if path.is_symlink()),
        key=lambda path: path.as_posix(),
    )
    symlink_escape_count = 0
    for path in symlinks:
        try:
            path.resolve().relative_to(root)
        except (OSError, ValueError):
            _issue(issues, "SYMLINK-ESCAPES-REPOSITORY", path, root)
            symlink_escape_count += 1

    media_files = sorted(
        {
            path
            for path in all_files
            if path.suffix.lower() in PROHIBITED_FILE_SUFFIXES
            or _has_media_signature(path)
        },
        key=lambda path: path.as_posix(),
    )
    for path in media_files:
        _issue(issues, "PROHIBITED-REPOSITORY-FILE", path, root)

    json_files = [path for path in all_files if path.suffix.lower() == ".json"]
    for path in json_files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            _issue(issues, "INVALID-JSON", path, root)

    python_files = [path for path in all_files if path.suffix.lower() == ".py"]
    for path in python_files:
        try:
            source = path.read_text(encoding="utf-8")
            compile(source, _relative(path, root), "exec")
        except (OSError, UnicodeDecodeError, SyntaxError):
            _issue(issues, "INVALID-PYTHON", path, root)

    whitespace_issue_count = 0
    text_suffixes = {".md", ".json", ".py", ".yml", ".yaml", ".toml"}
    for path in (item for item in all_files if item.suffix.lower() in text_suffixes):
        text = _read_text(path)
        if text is None:
            continue
        if text and not text.endswith("\n"):
            _issue(issues, "MISSING-FINAL-NEWLINE", path, root)
            whitespace_issue_count += 1
        if any(line.endswith((" ", "\t")) for line in text.splitlines()):
            _issue(issues, "TRAILING-WHITESPACE", path, root)
            whitespace_issue_count += 1

    scoped_string_issue_count = 0
    for path in public_files:
        text = _read_text(path)
        if text is None:
            _issue(issues, "NON-TEXT-PUBLIC-ARTIFACT", path, root)
            continue
        for code, pattern in STRING_PATTERNS:
            if pattern.search(text):
                _issue(issues, code, path, root)
                scoped_string_issue_count += 1

    markdown_link_count = validate_markdown_links(all_files, issues, root)
    issues.sort(key=lambda item: (item["path"], item["code"]))
    broken_reference_count = sum(
        item["code"] in {"BROKEN-MARKDOWN-LINK", "MARKDOWN-LINK-ESCAPES-REPOSITORY"}
        for item in issues
    )

    return {
        "schema_version": "repository-boundary-validation/0.1",
        "status": "PASS" if not issues else "FAIL",
        "error_count": len(issues),
        "repository_file_count": len(all_files),
        "json_file_count": len(json_files),
        "python_file_count": len(python_files),
        "public_artifact_count": len(public_files),
        "markdown_link_count": markdown_link_count,
        "broken_reference_count": broken_reference_count,
        "prohibited_repository_file_count": len(media_files),
        "scoped_public_string_issue_count": scoped_string_issue_count,
        "public_string_scan_scope": "CURRENT_MACHINE_AND_RUNTIME_ARTIFACTS_ONLY",
        "excluded_historical_legacy_markdown_count": len(excluded_legacy_files),
        "whitespace_issue_count": whitespace_issue_count,
        "symlink_escape_count": symlink_escape_count,
        "historical_legacy_markdown_scope": "EXCLUDED_IMMUTABLE_PROVENANCE_CONVERTED_OUTPUTS_VALIDATED",
        "issues": issues,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    report = validate_repository()
    content = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(content, encoding="utf-8")
    if not args.quiet:
        print(content, end="")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
