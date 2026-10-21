"""Validate the public skill graph and actual CLI help contracts without Hermes internals."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / 'skills'
EXPECTED = {'run-investigations', 'check-program-fit', 'discover-national-sources', 'research-healthcare',
            'research-care-services', 'research-medicaid', 'trace-federal-funds', 'resolve-entities',
            'analyze-payments', 'preserve-evidence', 'review-originality', 'challenge-findings', 'prepare-case-files'}
errors = []
found = {p.parent.name for p in SKILLS.glob('*/SKILL.md')}
if found != EXPECTED:
    errors.append('Skill inventory mismatch')
for name in sorted(EXPECTED):
    path = SKILLS / name / 'SKILL.md'
    text = path.read_text()
    if not text.startswith('---\n') or len(text.split('---', 2)) != 3:
        errors.append(name + ': invalid frontmatter')
    if not re.search(r'^name: ' + re.escape(name) + r'$', text, re.MULTILINE):
        errors.append(name + ': name mismatch')
    if not re.search(r'^description: [\"\x27]?Use when', text, re.MULTILINE):
        errors.append(name + ': missing trigger')
    for heading in ('## Reference loading', '## Completion contract'):
        if heading not in text:
            errors.append(name + ': missing ' + heading)
    for doc in sorted(path.parent.rglob('*')):
        if not doc.is_file():
            continue
        content = doc.read_text()
        if doc.suffix == '.json':
            json.loads(content)
        for target in re.findall(r'\]\(([^)#]+)', content):
            if '://' in target or target.startswith('#'):
                continue
            destination = (doc.parent / target).resolve()
            if not destination.is_relative_to(SKILLS.resolve()) or not destination.is_file():
                errors.append(name + ': broken/escaped reference ' + target)
    related = re.search(r'related_skills: \[([^\]]+)\]', text)
    if related:
        for dependency in related[1].split(','):
            if dependency.strip() not in EXPECTED:
                errors.append(name + ': unresolved related skill ' + dependency)
commands = [['--help'], ['case', '--help'], ['bulk', '--help'], ['inspect', '--help'],
            ['web-search', '--help'], ['web-extract', '--help']]
for args in commands:
    result = subprocess.run([sys.executable, '-m', 'fraudlab', *args], capture_output=True,
                            text=True, timeout=30, check=False)
    if result.returncode:
        errors.append('CLI help failed: ' + repr(args))
print(json.dumps({'passed': not errors, 'skills': len(found), 'cli_contracts': len(commands), 'errors': errors}, indent=2))
raise SystemExit(1 if errors else 0)
