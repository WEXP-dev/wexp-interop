"""Copy four reviewed public CI archives to a NEW evidence branch; never update a ref."""
import base64
import hashlib
import io
import json
import os
from pathlib import PurePosixPath
import urllib.error
import urllib.parse
import urllib.request
import zipfile

REPO = 'WEXP-dev/wexp-interop'
REPO_ID = '1342067237'
SOURCE = '70d6c5d1fca0843859008c98fd6a57e265ff3f68'
BASE_TREE = 'd88cdc985ccd82b50ae98fe2394860f85d87953a'
BRANCH = 'evidence/wimse-core02-70d6c5d-run001'
PREFIX = 'docs/proposals/wimse-core02-replay-001/evidence/run-001'
OBSERVED = '882cb96cef3fb00192988396ac0ebe4f742070b1d55c2141afe7aebabcb390ae'
INPUTS = [
 ('push-python312.zip', 40604969823, 12780681745, 252140, 'f42aabcfd3a4060947371790e0cc8f2952dd9d31ba2c8518ca48d4ef1328b895'),
 ('push-python313.zip', 40604969823, 12779768279, 252141, '924ca402b560ba40dc73f3f6e672c15231b989638e6f3be31a2475e1f014617d'),
 ('pr-python312.zip', 40604995949, 12779903227, 252140, '260869efee594aa876f347ebcedaae147878847f3a96409f4c40902cdf8d5c06'),
 ('pr-python313.zip', 40604995949, 12780976038, 252143, '815b8d5b181462b4aff9d04a584a9dbe3518efb9e7ffcbfe76c967fb584cfe40'),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check_archive(data, expected):
    if sha(data) != expected:
        raise ValueError('archive identity mismatch')
    names = {'source-commit.txt'} | {mode + '/' + name for mode in ('normal', 'optimized')
        for name in ('START.json', 'SUMMARY.json', 'errors.json', 'observed.json',
                     'processes.json', 'recipient-distribution.json')}
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if len(z.namelist()) != 13 or set(z.namelist()) != names or z.testzip() is not None:
            raise ValueError('archive member set or CRC mismatch')
        if sum(i.file_size for i in z.infolist()) > 8_000_000:
            raise ValueError('unexpected expansion size')
        if z.read('source-commit.txt').decode().strip() != SOURCE:
            raise ValueError('wrong source commit')
        for mode in ('normal', 'optimized'):
            result = json.loads(z.read(mode + '/SUMMARY.json'))
            if (result['status'], result['cases'], result['completed'], result['passed'],
                result['mapped'], result['errors'], result['observed_sha256']) != (
                'PASS_BOUNDED_MIGRATION', 130, 130, 130, 35, 0, OBSERVED):
                raise ValueError('unexpected summary')
            if sha(z.read(mode + '/observed.json')) != OBSERVED:
                raise ValueError('observed result digest mismatch')
            if json.loads(z.read(mode + '/errors.json')) != []:
                raise ValueError('error record is nonempty')
        if z.read('normal/observed.json') != z.read('optimized/observed.json'):
            raise ValueError('mode comparison mismatch')


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def main():
    if os.environ.get('GITHUB_REPOSITORY') != REPO or os.environ.get('GITHUB_REPOSITORY_ID') != REPO_ID:
        raise SystemExit('wrong repository')
    if os.environ.get('GITHUB_REF') != 'refs/heads/preservation/wimse-core02-run001-20261028':
        raise SystemExit('wrong preservation branch')
    token = os.environ['GH_TOKEN']
    opener = urllib.request.build_opener(NoRedirect)
    api = 'https://api.github.com/repos/' + REPO
    def request(path, payload=None):
        method = 'GET' if payload is None else 'POST'
        data = None if payload is None else json.dumps(payload).encode()
        req = urllib.request.Request(api + path, data=data, method=method, headers={
            'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'wexp-exact-evidence-copy'})
        with opener.open(req, timeout=60) as response:
            return json.load(response)
    # Ref creation only. A previously existing branch is never replaced.
    try:
        request('/git/ref/heads/' + BRANCH)
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    else:
        raise SystemExit('evidence branch already exists; no write performed')
    files = []; entries = []
    for name, run, artifact, size, digest in INPUTS:
        meta = request('/actions/artifacts/' + str(artifact))
        if meta.get('expired') or meta['workflow_run']['head_sha'] != SOURCE or meta['workflow_run']['id'] != run:
            raise ValueError('artifact provenance mismatch')
        if meta.get('digest') != 'sha256:' + digest or meta['size_in_bytes'] != size:
            raise ValueError('artifact metadata identity mismatch')
        endpoint = api + '/actions/artifacts/' + str(artifact) + '/zip'
        req = urllib.request.Request(endpoint, headers={'Authorization': 'Bearer ' + token,
            'User-Agent': 'wexp-exact-evidence-copy'})
        try:
            with opener.open(req, timeout=60) as response:
                data = response.read(size + 1)
        except urllib.error.HTTPError as e:
            if e.code not in (301, 302, 303, 307, 308):
                raise
            location = e.headers['Location']
            parsed = urllib.parse.urlsplit(location)
            allowed = ('.blob.core.windows.net', '.actions.githubusercontent.com', '.githubusercontent.com')
            if parsed.scheme != 'https' or not parsed.hostname or not parsed.hostname.endswith(allowed):
                raise ValueError('unexpected artifact download host')
            # Never forward the GitHub authorization header to blob storage.
            with urllib.request.urlopen(location, timeout=60) as response:
                data = response.read(size + 1)
        if len(data) != size:
            raise ValueError('archive size mismatch')
        check_archive(data, digest)
        blob = request('/git/blobs', {'encoding': 'base64', 'content': base64.b64encode(data).decode('ascii')})
        expected_blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if blob['sha'] != expected_blob:
            raise ValueError('uploaded blob differs')
        entries.append({'path': PREFIX + '/' + name, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
        files.append({'path': name, 'run_id': run, 'artifact_id': artifact, 'bytes': size,
            'sha256': digest, 'git_blob': blob['sha'], 'original_archive_bytes_preserved': True})
    record = {'schema': 'wexp-bounded-migration-evidence/1', 'source_commit': SOURCE,
        'preservation_workflow_commit': os.environ['GITHUB_SHA'], 'archives': files,
        'observed_sha256_all_eight_mode_runs': OBSERVED, 'cases_per_run': 130,
        'mapped_per_run': 35, 'unmapped_per_run': 95, 'external_independent_reproduction': False,
        'new_two_world_operations': False, 'coverage_evaluation': False, 'aac_execution': False,
        'scope': 'Exact four public Actions ZIP archives. Same-project bounded replay, not full conformance or deployment validation.'}
    text = json.dumps(record, sort_keys=True, indent=2) + '\n'
    entries.append({'path': PREFIX + '/RECORD.json', 'mode': '100644', 'type': 'blob', 'content': text})
    tree = request('/git/trees', {'base_tree': BASE_TREE, 'tree': entries})
    commit = request('/git/commits', {'message': 'Preserve exact WIMSE/Core-02 first-run archives without changing trial inputs',
        'tree': tree['sha'], 'parents': [SOURCE]})
    request('/git/refs', {'ref': 'refs/heads/' + BRANCH, 'sha': commit['sha']})
    print(json.dumps({'status': 'EXACT_ARCHIVES_COPIED_TO_NEW_BRANCH', 'branch': BRANCH,
                      'commit': commit['sha'], 'archives': files, 'record_sha256': sha(text.encode())}, sort_keys=True))


if __name__ == '__main__':
    main()
