#!/usr/bin/env python3
"""Add the version switcher to documentation built from an older tag."""

from __future__ import annotations

import argparse
from html import escape
from pathlib import Path


MARKER = 'name="edrixs-doc-version"'


def inject(html_dir: Path, version: str, site_root: str) -> int:
    """Inject shared switcher assets into HTML files that lack the marker."""
    site_root = f"/{site_root.strip('/')}/"
    snippet = f"""
    <meta name="edrixs-doc-version" content="{escape(version, quote=True)}">
    <meta name="edrixs-doc-site-root" content="{escape(site_root, quote=True)}">
    <link rel="stylesheet" href="{site_root}_versioning/version-switcher.css">
    <script defer src="{site_root}_versioning/version-switcher.js"></script>
"""
    changed = 0
    for path in html_dir.rglob("*.html"):
        contents = path.read_text(encoding="utf-8")
        if MARKER in contents:
            continue
        if "</head>" not in contents:
            raise RuntimeError(f"Cannot find </head> in {path}")
        path.write_text(
            contents.replace("</head>", f"{snippet}  </head>", 1),
            encoding="utf-8",
        )
        changed += 1
    return changed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("html_dir", type=Path)
    parser.add_argument("version")
    parser.add_argument("--site-root", default="/edrixs/")
    args = parser.parse_args()

    if not args.html_dir.is_dir():
        parser.error(f"HTML directory does not exist: {args.html_dir}")
    changed = inject(args.html_dir, args.version, args.site_root)
    print(f"Injected the documentation version into {changed} HTML files.")


if __name__ == "__main__":
    main()
