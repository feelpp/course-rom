"""Inventory the external teaching corpus; validate the saved catalog without it.

Extraction is lexical, not a TeX interpreter. Unresolved macro-dependent paths and
citations remain explicit review tasks. No external file is copied into Antora.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

REPO = Path(__file__).resolve().parents[1]
CATALOG = REPO / 'materials/catalog'
TOPICS = json.loads((CATALOG / 'topics.json').read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def topic_for(path):
    name = path.stem.lower()
    if any(word in name for word in ('macros', 'common', 'instructor', 'date-time', 'material', 'collaborator')):
        return 'source-support'
    if 'feelpp' in str(path).lower(): return 'feelpp'
    if 'kf' in name: return 'filtering'
    if name in ('rb-da', 'pbdw', 'demo') or '/DA/' in str(path): return 'assimilation'
    if 'non-affine' in name: return 'hyper-reduction'
    if 'scm' in name or 'mintheta' in name: return 'scm'
    if 'ncns' in name or 'femdual' in name: return 'primal-dual'
    if 'nonlinear' in name: return 'nonlinear'
    if 'parabolic' in name: return 'transient'
    if 'geotrans' in name: return 'geometry'
    if 'apriori' in name: return 'approximation'
    if 'pod' in name or 'svd' in name: return 'pod'
    if 'greedy' in name: return 'greedy'
    if 'error' in name or 'coercivity' in name or name == 'hypothesis': return 'certification'
    if 'notation' in name or 'inner-products' in name: return 'notation'
    if any(word in name for word in ('galerkin', 'formulation', 'approximation', 'decomposition', 'rbm-problem', 'problem-statement')):
        return 'galerkin'
    if any(word in name for word in ('example', 'lncmi', 'opus', 'heatshield', 'thermalblock', 'eye2brain')):
        return 'applications'
    if any(word in name for word in ('outline', 'motivation', 'definition', 'objective', 'deployed', 'methodolog')):
        return 'digital-twins'
    return 'foundations'


def references(text, command):
    return sorted(set(value.strip() for group in re.findall(
        r'\\(?:' + command + r')\*?(?:\[[^\]]*\])*\{([^{}]+)\}', text)
        for value in group.split(',') if value.strip()))


def inventory(root):
    paths = sorted(p for p in (root / 'Slides').rglob('*')
                   if p.is_file() and p.suffix.lower() == '.tex'
                   and 'auto' not in p.parts and not p.name.startswith(('#', '.')))
    # Only named lecture entry points outside Slides, never assessment/student trees.
    paths += sorted(root.glob('lecture*.tex'))
    paths = sorted(set(paths))
    bib_paths = sorted(set(root.glob('*.bib')) | set((root / 'biblio').rglob('*.bib'))
                       | set((root / 'Slides').rglob('*.bib')))
    bib_index = defaultdict(list)
    bibliographies = []
    for path in bib_paths:
        relative = path.relative_to(root).as_posix()
        keys = re.findall(r'@\w+\s*\{\s*([^,\s]+)\s*,', path.read_text(errors='replace'))
        bibliographies.append({'path': relative, 'sha256': digest(path), 'keys': sorted(set(keys))})
        for key in keys: bib_index[key].append(relative)

    def dependency(value, source, extensions):
        found = set()
        for directory in (root, source.parent, root / 'Figures', root / 'Slides'):
            for suffix in ('', *extensions):
                candidate = (directory / (value + suffix)).resolve()
                if candidate.is_relative_to(root) and candidate.is_file(): found.add(candidate)
        return {'reference': value, 'matches': [
            {'path': p.relative_to(root).as_posix(), 'sha256': digest(p)} for p in sorted(found)],
            'state': 'resolved' if len(found) == 1 else ('ambiguous' if found else 'unresolved')}

    entries = []
    for path in paths:
        relative = path.relative_to(root)
        text = re.sub(r'(?<!\\)%.*', '', path.read_text(errors='replace'))
        topic = topic_for(relative)
        selection = TOPICS[topic]
        entries.append({
            'source': relative.as_posix(), 'sha256': digest(path), 'topic': topic,
            'target': selection['target'], 'target_state': selection['state'],
            'course_sessions': selection['sessions'], 'priority': selection['priority'],
            'review_state': 'needs-editorial-and-mathematical-review',
            'publication': 'candidate-teaching-source',
            'figures': [dependency(v, path, ('.pdf', '.png', '.jpg', '.jpeg', '.svg', '.eps'))
                        for v in references(text, 'includegraphics')],
            'includes': [dependency(v, path, ('.tex',)) for v in references(text, 'input|include')],
            'references': [{'key': key, 'bibliographies': sorted(set(bib_index[key]))}
                           for key in references(text, r'cite[a-zA-Z]*')],
            'bibliography_commands': references(text, 'bibliography|addbibresource'),
            'overlap': {'topic_group': topic, 'identical_sources': []},
        })
    for entry in entries:
        entry['overlap']['identical_sources'] = [other['source'] for other in entries
            if other['sha256'] == entry['sha256'] and other['source'] != entry['source']]
    return {'schema_version': 1, 'source_collection': 'rbm',
        'scope': 'Slides/**/*.tex (case insensitive, excluding editor/auto files) and root lecture*.tex; bibliography dependencies only',
        'limitations': 'Lexical extraction; dynamic TeX paths, inherited graphics paths and nested macro arguments require manual review. Topic assignment is a provisional triage, not chapter completeness.',
        'excluded': [
            {'category': 'assessments-solutions-student-records', 'policy': 'Not scanned or copied. Review separately in a private workflow; never publish student records.'},
            {'category': 'notebooks-and-data', 'policy': 'Not included in the TeX inventory. Select student exercises explicitly; solutions stay outside Antora content roots.'},
            {'category': 'other-root-sources-and-assets', 'policy': 'Not part of the teaching allowlist; dependencies are recorded only when referenced. Expand the scope after manual classification.'}],
        'bibliographies': bibliographies, 'sources': entries}


def validate(data):
    assert data['schema_version'] == 1
    seen = set()
    for entry in data['sources']:
        source = entry['source']
        assert not Path(source).is_absolute() and '..' not in Path(source).parts
        assert source not in seen, source
        seen.add(source)
        assert re.fullmatch('[0-9a-f]{64}', entry['sha256'])
        topic = TOPICS[entry['topic']]
        for field, key in [('target', 'target'), ('target_state', 'state'), ('priority', 'priority'), ('course_sessions', 'sessions')]:
            assert entry[field] == topic[key], f'Stale topic mapping: {source}'
        if topic['state'] in ('partial', 'published'):
            assert (REPO / 'materials/modules/ROOT/pages' / topic['target'].split('::')[1]).is_file()
        assert entry['review_state'] == 'needs-editorial-and-mathematical-review'
        for other in entry['overlap']['identical_sources']:
            assert any(e['source'] == other and e['sha256'] == entry['sha256'] for e in data['sources'])
    for session in (2, 3):
        assert any(session in e['course_sessions'] and e['priority'] == 'P0' for e in data['sources'])
    print(f"Validated {len(seen)} teaching sources; priorities {dict(Counter(e['priority'] for e in data['sources']))}. No external source access required.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--source-root', type=Path, help='Refresh from an explicitly supplied rbm directory')
    mode.add_argument('--check', action='store_true', help='Validate only the committed inventory')
    args = parser.parse_args()
    destination = CATALOG / 'sources.json'
    if args.source_root:
        source_root = args.source_root.resolve()
        if not (source_root / 'Slides').is_dir(): parser.error('source root must contain Slides/')
        data = inventory(source_root)
        destination.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    else:
        data = json.loads(destination.read_text())
    validate(data)
