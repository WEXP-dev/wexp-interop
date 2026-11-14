#!/usr/bin/env python3
"""Result rows of proposals, and the two pages built from them.

usage: python3 -B scripts/proposals/result_table.py [--check]

Each proposal may carry RESULT-ROW.json: what was examined, who initiated the check and how that was
established, whether the author of the format agreed the row, what the author changed in their own
specification afterwards, and which readings of the Core-02 text the work left open. This script
validates every row and writes docs/proposals/RESULTS.md and docs/proposals/OPEN-READINGS.md.
With --check it writes nothing and fails if either page is not what the rows produce.

The counts in a row come from the committed evidence of the run, never from the row itself.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import proposal_lib as lib  # noqa: E402

SCHEMA = 'wexp-interop/proposal-result-row/1'
CHANNELS = ('interop-check', 'direct-correspondence', 'maintainer')
# Who initiated the check, relative to the format examined, and where that knowledge comes from.
RELATIONS = {
    'internet-draft-author': 'an author of Internet-Draft `{subject}`',
    'repository-owner': 'the owner of repository `{subject}`',
    'organization-public-member': 'a public member of the organization that owns `{subject}`',
    'repository-contributor': 'a contributor to repository `{subject}`',
    'maintainer': 'a maintainer of this repository',
    'not-established': 'a party with no established link to the format',
}
UNNAMED = {
    'internet-draft-author': 'an author of the Internet-Draft that describes the format',
    'repository-owner': 'the owner of a repository of the format',
    'organization-public-member': 'a public member of the organization behind the format',
    'repository-contributor': 'a contributor to a repository of the format',
    'maintainer': 'a maintainer of this repository',
    'not-established': 'no established link to the format',
}
ESTABLISHED = {
    'github-public-record': 'GitHub public record',
    'confirmed-with-the-person': 'confirmed with the person directly',
    'not-applicable': None,
    'not-established': None,
}
# An account name alone does not show who wrote a draft, so authorship is never taken from a form.
ALLOWED_BASIS = {
    'internet-draft-author': ('confirmed-with-the-person',),
    'repository-owner': ('github-public-record', 'confirmed-with-the-person'),
    'organization-public-member': ('github-public-record', 'confirmed-with-the-person'),
    'repository-contributor': ('github-public-record', 'confirmed-with-the-person'),
    'maintainer': ('not-applicable',),
    'not-established': ('not-established',),
}
STATUSES = ('draft', 'agreed')
REVIEWS = ('not-requested', 'requested', 'row-agreed', 'not-applicable')
# Why a row names nobody. Not having asked yet is a different fact from having been asked not to.
NOT_NAMED = {'asked-not-to-be-named': 'A party who asked not to be named',
             'naming-not-yet-agreed': 'Naming not yet agreed with the party'}
READING_STATUSES = ('open', 'answered')
SUBJECT_RE = re.compile(r'^(?:draft-[a-z0-9]+(?:-[a-z0-9]+)*-[0-9]{2}|' + lib.NAME + '/' + lib.NAME + ')$')
REFERENCE_RE = re.compile(r'^https://[A-Za-z0-9.-]+/[A-Za-z0-9._~/#?=&%+:@-]*$')
# Wording a row must not carry: a row reports what a run showed, not a verdict on the format.
BARRED = ('conform', 'certif', 'compatible', 'compliant', 'independent')
PAGES = {'results': 'RESULTS.md', 'readings': 'OPEN-READINGS.md'}


def line(value, what: str, limit: int = 300) -> str:
    if type(value) is not str or not value.strip() or len(value) > limit or any(c in value for c in '\r\n|`<>'):
        raise lib.ProposalError(f'{what} must be one plain line of at most {limit} characters')
    low = value.lower()
    for word in BARRED:
        if word in low:
            raise lib.ProposalError(f'{what} uses "{word}": a row reports what a run showed and says nothing '
                                    'about whether a format meets Core')
    return value.strip()


def template(title: str, issue: int | None, relation: str = 'not-established', subject: str | None = None,
             established_by: str | None = None) -> dict:
    row = {'schema': SCHEMA, 'examined': title, 'status': 'draft', 'author_review': 'not-requested',
           'summary': None,
           'initiation': {'channel': 'interop-check' if issue is not None else 'direct-correspondence',
                          'interop_check_issue': issue, 'named': False,
                          'not_named_because': 'naming-not-yet-agreed', 'initiated_by': None,
                          'relation': relation, 'relation_subject': subject,
                          'established_by': established_by or ALLOWED_BASIS[relation][0]},
           'author_spec_changes': [], 'open_readings': []}
    validate(row)
    return row


def validate(row: dict) -> dict:
    if type(row) is not dict or row.get('schema') != SCHEMA:
        raise lib.ProposalError(f'schema must be {SCHEMA}')
    line(row.get('examined'), 'examined', 120)
    if row.get('status') not in STATUSES or row.get('author_review') not in REVIEWS:
        raise lib.ProposalError(f'status is one of {STATUSES}; author_review is one of {REVIEWS}')
    if row.get('summary') is not None:
        line(row['summary'], 'summary')
    who = row.get('initiation')
    if type(who) is not dict:
        raise lib.ProposalError('initiation is required: who asked for the check and how that is known')
    relation, basis, subject = who.get('relation'), who.get('established_by'), who.get('relation_subject')
    if who.get('channel') not in CHANNELS or relation not in RELATIONS:
        raise lib.ProposalError(f'initiation.channel is one of {CHANNELS}; relation is one of {tuple(RELATIONS)}')
    if basis not in ALLOWED_BASIS[relation]:
        raise lib.ProposalError(f'relation {relation} can be established by {ALLOWED_BASIS[relation]}, not {basis!r}')
    issue = who.get('interop_check_issue')
    if (who['channel'] == 'interop-check') != (type(issue) is int and issue > 0) or (issue is not None and type(issue) is not int):
        raise lib.ProposalError('interop_check_issue is the number of the check when the channel is interop-check, else null')
    needs_subject = '{subject}' in RELATIONS[relation]
    if type(who.get('named')) is not bool:
        raise lib.ProposalError('initiation.named is true or false')
    if (who.get('not_named_because') in NOT_NAMED) == who['named'] or (
            who['named'] and who.get('not_named_because') is not None):
        raise lib.ProposalError(f'initiation.not_named_because is one of {tuple(NOT_NAMED)} when nobody is named, '
                                'and is absent when somebody is')
    if who['named']:
        line(who.get('initiated_by'), 'initiation.initiated_by', 80)
        if needs_subject != (type(subject) is str and bool(SUBJECT_RE.match(subject))) or (not needs_subject and subject is not None):
            raise lib.ProposalError('relation_subject is owner/repository or a draft name with its revision, '
                                    'and is given exactly when the relation refers to one')
    elif who.get('initiated_by') is not None or subject is not None:
        raise lib.ProposalError('a party who is not named has neither a name nor a named repository or draft in the row')
    if row['status'] == 'agreed':
        if who.get('not_named_because') == 'naming-not-yet-agreed':
            raise lib.ProposalError('a row is agreed only after the party has said whether to be named')
        if row['summary'] is None:
            raise lib.ProposalError('an agreed row has a summary')
        if row['author_review'] not in ('row-agreed', 'not-applicable') or (
                row['author_review'] == 'not-applicable' and relation != 'maintainer'):
            raise lib.ProposalError('a row is agreed only when the author of the format agreed it; '
                                    'not-applicable is for a check a maintainer initiated on no external format')
    for change in row.get('author_spec_changes', []):
        if type(change) is not dict or not REFERENCE_RE.match(str(change.get('reference'))):
            raise lib.ProposalError('each author_spec_changes entry has what and a public https reference')
        line(change.get('what'), 'author_spec_changes.what')
    seen = set()
    for reading in row.get('open_readings', []):
        if type(reading) is not dict or not lib.CASE_RE.match(str(reading.get('id'))) or reading['id'] in seen:
            raise lib.ProposalError('each open reading has a distinct id of letters, digits and hyphens')
        seen.add(reading['id'])
        line(reading.get('question'), 'open_readings.question', 400)
        lines_, cases = reading.get('core02_lines'), reading.get('cases', [])
        if type(lines_) is not list or not lines_ or any(type(n) is not int or n < 1 for n in lines_):
            raise lib.ProposalError('open_readings.core02_lines lists line numbers of the published Core-02 XML')
        if type(cases) is not list or any(not lib.CASE_RE.match(str(c)) for c in cases):
            raise lib.ProposalError('open_readings.cases lists case identifiers')
        if reading.get('status') not in READING_STATUSES:
            raise lib.ProposalError(f'open_readings.status is one of {READING_STATUSES}')
        if reading['status'] == 'answered' and not REFERENCE_RE.match(str(reading.get('answer_reference'))):
            raise lib.ProposalError('an answered reading names where it was answered')
    return row


def initiated_by(who: dict) -> str:
    basis = ESTABLISHED[who['established_by']]
    tail = f' ({basis})' if basis else ''
    if not who['named']:
        return f'{NOT_NAMED[who["not_named_because"]]}; {UNNAMED[who["relation"]]}{tail}'
    return f'{who["initiated_by"]}, {RELATIONS[who["relation"]].format(subject=who["relation_subject"])}{tail}'


def run_facts(directory: Path) -> str:
    path = directory / 'evidence' / 'comparison.json'
    if not path.is_file():
        return 'No run committed'
    # The check workflow replays only a proposal that has a freeze, so counts are published only
    # for one: a run with no freeze before it is not a result.
    if not (directory / lib.FREEZE).is_file():
        raise lib.ProposalError(f'{directory.name}: evidence is committed and there is no {lib.FREEZE}; '
                                'run counts are published only for a run on frozen inputs')
    cases = json.loads(path.read_text(encoding='utf-8'))['cases']
    verdicts = {}
    for case in cases.values():
        verdict = case.get('expected_verdict') if case.get('expected_verdict') in ('accept', 'downgrade', 'reject') else 'other'
        verdicts[verdict] = verdicts.get(verdict, 0) + 1
    equal = sum(1 for c in cases.values() if c['wexp_ref_equals_expected'] and c['wexp_check_equals_expected'])
    spread = ', '.join(f'{n} {v}' for v, n in sorted(verdicts.items()))
    return (f'{len(cases)} case(s); expected {spread}; {equal} of {len(cases)} equal the frozen expectation '
            'in both appraisers')


def load(root: Path) -> list[tuple[str, dict, Path]]:
    rows = []
    for path in sorted(root.glob(f'*/{lib.RESULT_ROW}')):
        try:
            row = validate(json.loads(path.read_text(encoding='utf-8')))
        except (ValueError, lib.ProposalError) as error:
            raise lib.ProposalError(f'{path.parent.name}/{lib.RESULT_ROW}: {error}')
        rows.append((path.parent.name, row, path.parent))
    return rows


def withheld(row: dict) -> bool:
    """A check asked for by a party with no established link to the format is not listed until
    the author of the format has agreed the row: anybody can ask about anybody's format."""
    return row['initiation']['relation'] == 'not-established' and row['author_review'] != 'row-agreed'


def build(root: Path = lib.PROPOSALS) -> dict[str, str]:
    every = load(root)
    rows = [entry for entry in every if not withheld(entry[1])]
    held = len(every) - len(rows)
    out = ['# Results of proposals', '',
           '<!-- Generated by scripts/proposals/result_table.py from each proposal\'s RESULT-ROW.json. Do not edit. -->', '',
           'One row per proposal that carries a result row. A row says what a run on frozen inputs showed. '
           'It does not say whether a format meets Core, and both appraisers are operated by one person. '
           'Each row states who initiated the check and how that is known; a row marked draft has not been '
           'agreed with the author of the format.', '',
           '| Proposal | Examined | Initiated by | Run | Summary | Row |', '|---|---|---|---|---|---|']
    for slug, row, directory in rows:
        who = row['initiation']
        origin = initiated_by(who)
        if who['interop_check_issue'] is not None:
            n = who['interop_check_issue']
            origin += f'; [check {n}](https://github.com/WEXP-dev/interop-test-lab/issues/{n})'
        state = 'agreed with the author' if row['author_review'] == 'row-agreed' else (
            'agreed' if row['status'] == 'agreed' else 'draft')
        out.append(f'| [{slug}]({slug}/README.md) | {row["examined"]} | {origin} | {run_facts(directory)} | '
                   f'{row["summary"] or "Not written yet"} | {state} |')
    if not rows:
        out.append('| _none yet_ | | | | | |')
    if held:
        out += ['', f'{held} proposal(s) not listed: the check was asked for by a party with no established link '
                'to the format, and the author of the format has not agreed the row.']
    changes = [(slug, c) for slug, row, _ in rows for c in row.get('author_spec_changes', [])]
    out += ['', '## Changes authors made to their own specifications after a check', '']
    out += [f'- [{slug}]({slug}/README.md): {c["what"]} ([reference]({c["reference"]}))' for slug, c in changes] or ['None recorded yet.']
    readings = ['# Open readings of the Core-02 text', '',
                '<!-- Generated by scripts/proposals/result_table.py from each proposal\'s RESULT-ROW.json. Do not edit. -->', '',
                'Places where mapping a real format showed that the text of draft-sergeev-wexp-core-02 allows two '
                'readings, or does not say. Line numbers refer to the published XML (SHA-256 '
                f'`{lib.CORE02_XML_SHA256}`). These are input to the next revision of the draft, not errata.', '',
                '| Reading | Question | Core-02 lines | Proposal and cases | Status |', '|---|---|---|---|---|']
    found = False
    for slug, row, _ in rows:
        for r in row.get('open_readings', []):
            found = True
            status = 'open' if r['status'] == 'open' else f'[answered]({r["answer_reference"]})'
            cases = ', '.join(f'`{c}`' for c in r.get('cases', [])) or 'none'
            readings.append(f'| `{slug}/{r["id"]}` | {r["question"]} | {", ".join(str(n) for n in r["core02_lines"])} | '
                            f'[{slug}]({slug}/README.md): {cases} | {status} |')
    if not found:
        readings.append('| _none recorded yet_ | | | | |')
    return {PAGES['results']: '\n'.join(out) + '\n', PAGES['readings']: '\n'.join(readings) + '\n'}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--publishable', action='store_true',
                    help='also refuse when a row is withheld from the pages (used before a merge)')
    ap.add_argument('--root', type=Path, default=lib.PROPOSALS)
    a = ap.parse_args()
    try:
        pages = build(a.root)
    except (lib.ProposalError, OSError, KeyError) as error:
        print(f'refused: {error}', file=sys.stderr)
        return 2
    if a.publishable:
        held = [slug for slug, row, _ in load(a.root) if withheld(row)]
        if held:
            print(f'refused: {", ".join(held)}: asked for by a party with no established link to the format, and '
                  'its author has not agreed the row; it is not merged in this state', file=sys.stderr)
            return 2
    stale = []
    for name, text in pages.items():
        path = a.root / name
        if a.check:
            if not path.is_file() or path.read_text(encoding='utf-8') != text:
                stale.append(name)
        else:
            path.write_text(text, encoding='utf-8')
    if stale:
        print(f'refused: {", ".join(stale)} is not what the result rows produce; run result_table.py', file=sys.stderr)
        return 3
    print('pages match the result rows' if a.check else 'wrote ' + ', '.join(pages))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
