"""Validate one explicit signed push approval before scheduling any VM work."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

BRANCH = 'refs/heads/ci/debian13-install-approved'
APPROVAL = '.ci/debian13-approval.json'
FIELDS = {'approved', 'source_revision', 'review_run', 'review_sha256', 'plan_digest', 'software_only'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def hex_value(value, length):
    return isinstance(value, str) and re.fullmatch(f'[0-9a-f]{{{length}}}', value) is not None


def validate(event, record, commit, parent, changes, previous, actor, owner, attempt):
    require(event.get('ref') == BRANCH, 'Not the dedicated approval branch')
    require(attempt == '1', 'Workflow reruns cannot repeat installation approval')
    require(not any(event.get(key) for key in ('created', 'deleted', 'forced')), 'Creation/deletion/force pushes are not approval')
    require(hex_value(event.get('before'), 40) and event['before'] != '0' * 40, 'Missing existing branch state')
    require(hex_value(event.get('after'), 40), 'Missing approval commit')
    require(parent == event['before'], 'Approval must be one non-merge commit')
    require(changes in (f'A\t{APPROVAL}', f'M\t{APPROVAL}'), 'Only the approval file may change')
    require(isinstance(record, dict) and set(record) == FIELDS, 'Unexpected approval fields')
    require(record['approved'] is True, 'Transaction is not explicitly approved')
    require(hex_value(record['source_revision'], 40), 'Invalid reviewed source')
    require(type(record['review_run']) is int and record['review_run'] > 0, 'Invalid preparation run')
    require(hex_value(record['review_sha256'], 64) and hex_value(record['plan_digest'], 64), 'Invalid exact review digests')
    require(type(record['software_only']) is bool, 'Invalid acceleration selection')
    require(actor == owner == event.get('sender', {}).get('login'), 'Only the repository owner may publish approval')
    require(commit.get('sha') == event['after'] and commit.get('author', {}).get('login') == owner and commit.get('committer', {}).get('login') == owner, 'Approval author does not match owner')
    require(commit.get('commit', {}).get('verification', {}).get('verified') is True, 'Approval commit must be GitHub Verified')
    title = commit['commit'].get('message', '').splitlines()
    require(title and title[0] == f"Approve Debian 13 VM {record['review_sha256']}", 'Missing exact approval commit title')
    if isinstance(previous, dict) and previous.get('approved') is True:
        require(any(previous.get(key) != record[key] for key in FIELDS - {'approved'}), 'This exact record was already approved')
    return dict(source_revision=record['source_revision'], review_run=str(record['review_run']),
                review_sha256=record['review_sha256'], plan_digest=record['plan_digest'],
                software_only=str(record['software_only']).lower(), approval_commit=event['after'])


def check_review(record, run, manifest_bytes, repository):
    require(run.get('conclusion') == 'success', 'Preparation did not succeed')
    require(run.get('head_sha') == record['source_revision'], 'Preparation source differs')
    require(run.get('head_repository', {}).get('full_name') == repository, 'Preparation repository differs')
    require(run.get('event') == 'workflow_dispatch' or
            (run.get('event') == 'push' and run.get('head_branch') == 'ci/debian13-snapshot-vm'), 'Unexpected preparation trigger')
    require(run.get('path') in ('.github/workflows/ci.yml', '.github/workflows/debian-vm.yml',
                               '.github/workflows/debian-vm-tcg.yml'), 'Unexpected preparation workflow')
    require(hashlib.sha256(manifest_bytes).hexdigest() == record['review_sha256'], 'Review manifest differs')
    manifest = json.loads(manifest_bytes)
    require(manifest.get('source_revision') == record['source_revision'], 'Manifest source differs')
    require(manifest.get('plan_digest') == record['plan_digest'], 'Manifest transaction differs')
    require(manifest.get('snapshot_restore_verified') is True, 'Snapshot restoration was not verified')
    require(manifest.get('acceleration') == ('tcg' if record['software_only'] else 'kvm'), 'Snapshot acceleration differs')


def main():
    require(os.environ.get('GITHUB_EVENT_NAME') == 'push', 'Only a push can carry approval')
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    require(event.get('repository', {}).get('full_name') == os.environ['GITHUB_REPOSITORY'], 'Repository differs')
    before, after = event.get('before'), event.get('after')
    require(hex_value(before, 40) and hex_value(after, 40), 'Invalid push commits')
    require(subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() == after, 'Checkout differs from push')
    parents = subprocess.check_output(['git', 'rev-list', '--parents', '-n', '1', 'HEAD'], text=True).split()
    parent = parents[1] if len(parents) == 2 else None
    changes = subprocess.check_output(['git', 'diff', '--no-renames', '--name-status', before, after], text=True).strip()
    prior = subprocess.run(['git', 'show', f'{before}:{APPROVAL}'], text=True, capture_output=True, check=False)
    try:
        previous = json.loads(prior.stdout) if prior.returncode == 0 else None
    except ValueError:
        previous = None
    commit = json.loads(subprocess.check_output(['gh', 'api', f"repos/{os.environ['GITHUB_REPOSITORY']}/commits/{after}"], text=True))
    record = json.loads(Path(APPROVAL).read_text())
    outputs = validate(event, record, commit, parent, changes, previous,
                       os.environ['GITHUB_ACTOR'], os.environ['GITHUB_REPOSITORY_OWNER'], os.environ['GITHUB_RUN_ATTEMPT'])
    repository = os.environ['GITHUB_REPOSITORY']
    run = json.loads(subprocess.check_output(['gh', 'api', f"repos/{repository}/actions/runs/{record['review_run']}"], text=True))
    with tempfile.TemporaryDirectory() as directory:
        subprocess.run(['gh', 'run', 'download', str(record['review_run']), '--repo', repository,
                        '--name', 'debian13-vm-evidence-prepare', '--dir', directory], check=True)
        check_review(record, run, (Path(directory) / 'review.json').read_bytes(), repository)
    with open(os.environ['GITHUB_OUTPUT'], 'a') as stream:
        stream.write(''.join(f'{key}={value}\n' for key, value in outputs.items()))
    print('Exact signed approval validated; installation still revalidates source, snapshot and guest transaction.')


if __name__ == '__main__':
    main()
