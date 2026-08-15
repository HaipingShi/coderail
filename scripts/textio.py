"""Repo-truth text writes: always LF, and skip the write when content is
already byte-identical.

WIN-RESIDUE-01: on Windows, ``Path.write_text`` translates ``\n`` to CRLF.
After a closeout stages and commits the LF-normalized blob, a same-content
CRLF rewrite leaves the Git index stat cache stale, and ``git status`` then
reports phantom "modified" residue without re-running the clean filter.
Writing LF and skipping no-op rewrites removes the whole bug class.
"""

from pathlib import Path


def write_text_lf(path, text: str) -> bool:
    """Write ``text`` with LF newlines; return False when nothing changed."""
    p = Path(path)
    try:
        if p.read_bytes() == text.encode("utf-8"):
            return False
    except OSError:
        pass
    p.write_text(text, encoding="utf-8", newline="\n")
    return True


def append_text_lf(path, text: str) -> None:
    """Append ``text`` with LF newlines so appended lines never turn CRLF."""
    with Path(path).open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
