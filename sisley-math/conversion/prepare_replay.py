"""Make an isolated replay folder without overwriting the preserved textbook."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('destination', type=Path, help='A new, nonexistent directory')
args = parser.parse_args()
conversion = Path(__file__).resolve().parent
project = conversion.parent
destination = args.destination.resolve()
if destination.exists():
    parser.error('Destination already exists; choose a new directory.')
if destination.is_relative_to(project):
    parser.error('Choose a directory outside the preserved project to avoid recursive copies.')
inventory = json.loads((conversion / 'inventory.json').read_text())
for item in inventory['scripts'] + inventory['checkpoints']:
    file = conversion / item['file']
    expected = item.get('preserved_sha256', item.get('sha256'))
    if hashlib.sha256(file.read_bytes()).hexdigest() != expected:
        parser.error(f'Checkpoint or script differs from inventory: {item["file"]}')
destination.mkdir(parents=True)
for name in ['gat-1-20', 'source', 'scripts']:
    shutil.copytree(project / name, destination / name)
for name in ['package.json', 'package-lock.json']:
    shutil.copy2(project / name, destination / name)
shutil.copytree(conversion / 'checkpoints', destination / '.conversion-work')
shutil.copytree(conversion / 'scripts', destination / 'conversion/scripts')
for name in ['package.json', 'package-lock.json', 'requirements.txt']:
    if (conversion / name).exists():
        shutil.copy2(conversion / name, destination / 'conversion' / name)
print(f'Replay folder prepared: {destination}')
print('Run the recovery scripts from that directory, following conversion/README.md in the preserved project.')
