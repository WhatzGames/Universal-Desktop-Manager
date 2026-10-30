"""Load the newest successful tooling image, refusing drift from a reviewed VM."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

WORKFLOW = '.github/workflows/vm-tooling-image.yml'
IMAGE = 'udm-vm-tooling:artifact'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def validate(metadata, run, repository, dockerfile_sha, reviewed=None):
    if (run.get('conclusion') != 'success' or run.get('path') != WORKFLOW or
            run.get('event') not in ('push', 'workflow_dispatch') or
            run.get('head_repository', {}).get('full_name') != repository):
        raise ValueError('Untrusted or unsuccessful tooling build')
    expected = dict(schema_version=1, run_id=run['id'], run_attempt=run['run_attempt'],
                    source_revision=run['head_sha'], platform='linux/amd64',
                    dockerfile_sha256=dockerfile_sha)
    if any(metadata.get(key) != value for key, value in expected.items()):
        raise ValueError('Tooling provenance or Dockerfile differs; build a fresh image')
    if not isinstance(metadata.get('image_id'), str) or not isinstance(metadata.get('archive_sha256'), str):
        raise ValueError('Invalid tooling image hashes')
    if not re.fullmatch(r'sha256:[0-9a-f]{64}', metadata['image_id']) or not re.fullmatch(r'[0-9a-f]{64}', metadata['archive_sha256']):
        raise ValueError('Invalid tooling image hashes')
    if reviewed is not None and metadata != reviewed.get('tooling_image'):
        raise ValueError('Latest tooling image changed since review; prepare and approve a fresh snapshot')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--review-sha256')
    args = parser.parse_args()
    repository = os.environ['GITHUB_REPOSITORY']
    result = subprocess.check_output(['gh', 'api', f'repos/{repository}/actions/workflows/vm-tooling-image.yml/runs?status=success&per_page=1'], text=True)
    runs = json.loads(result)['workflow_runs']
    if not runs:
        raise ValueError('No successful tooling image build; run Build fresh VM tooling image first')
    run = runs[0]
    args.state.mkdir(exist_ok=True)
    directory = args.state / 'tooling'
    directory.mkdir()
    def download(name, destination):
        subprocess.run(['gh', 'run', 'download', str(run['id']), '--repo', repository,
                        '--name', f'{name}-{run["run_attempt"]}', '--dir', str(destination)], check=True)
    download('udm-vm-tooling-metadata', directory / 'metadata')
    metadata = json.loads((directory / 'metadata/metadata.json').read_text())
    reviewed = None
    if args.review_sha256:
        if sha(args.state / 'review.json') != args.review_sha256:
            raise ValueError('Reviewed manifest hash differs')
        reviewed = json.loads((args.state / 'review.json').read_text())
    validate(metadata, run, repository, sha('tests/vm/Dockerfile'), reviewed)
    download('udm-vm-tooling-image', directory / 'image')
    archive = directory / 'image/udm-vm-tooling.tar.gz'
    if sha(archive) != metadata['archive_sha256']:
        raise ValueError('Tooling image archive hash differs')
    subprocess.run(['docker', 'image', 'load', '--input', str(archive)], check=True)
    image_id = subprocess.check_output(['docker', 'image', 'inspect', '--format', '{{.Id}}', IMAGE], text=True).strip()
    if image_id != metadata['image_id']:
        raise ValueError('Loaded tooling image identity differs')
    subprocess.run(['docker', 'tag', IMAGE, 'udm-vm-tooling'], check=True)
    (args.state / 'tooling-image.json').write_text(json.dumps(metadata, indent=2) + '\n')
    # The loaded image is in Docker; avoid retaining another large archive with the guest.
    archive.unlink()
    print(json.dumps(metadata), flush=True)


if __name__ == '__main__':
    main()
