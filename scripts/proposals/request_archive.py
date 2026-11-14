#!/usr/bin/env python3
"""Ask Software Heritage to archive the public repositories a proposal pins.

usage: python3 -B scripts/proposals/request_archive.py docs/proposals/<slug> [--send]

A proposal refers to exact bytes in someone else's repository. If that repository is later deleted
or rewritten, the digests in SOURCE-PINS.json still say what the bytes were, but nobody can fetch
them. A save request to the Software Heritage archive keeps them retrievable. Without --send it only
prints the requests. A request that fails is reported and never fails the caller: archiving is a
courtesy, not a step the result depends on.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import proposal_lib as lib  # noqa: E402

HOST = 'archive.softwareheritage.org'
REPOSITORY_RE = re.compile(rf'^{lib.NAME}/{lib.NAME}$')


def requests_for(directory: Path) -> list[str]:
    pins = json.loads((directory / 'SOURCE-PINS.json').read_text(encoding='utf-8'))
    repositories = sorted({f['repository'] for f in pins.get('external_files', [])})
    for name in repositories:
        if not REPOSITORY_RE.match(name):
            raise lib.ProposalError(f'not a repository name: {name[:80]!r}')
    return [f'https://{HOST}/api/1/origin/save/git/url/https://github.com/{name}/' for name in repositories]


def send(url: str) -> str:
    request = urllib.request.Request(url, method='POST', headers={'User-Agent': 'wexp-interop-proposals'})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            answer = json.loads(response.read(65536))
        return f'{answer.get("save_request_status", "unknown")}, {answer.get("save_task_status", "unknown")}'
    except (urllib.error.URLError, OSError, ValueError) as error:
        return f'not sent: {str(error)[:120]}'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('directory', type=Path)
    ap.add_argument('--send', action='store_true')
    a = ap.parse_args()
    try:
        urls = requests_for(a.directory)
    except (lib.ProposalError, OSError, ValueError, KeyError) as error:
        print(f'refused: {error}', file=sys.stderr)
        return 2
    for url in urls:
        print(url, '->', send(url) if a.send else 'not sent (no --send)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
