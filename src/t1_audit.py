#!/usr/bin/env python3
"""Constructor TKH assignment, T1 audit only. Python stdlib. No trained/heuristic hierarchy.
Conservative observational snapshot policy:
 node.first_seen_year <= cutoff;
 edge.year <= cutoff AND edge.provenance.article_year <= cutoff;
 all incident nodes first_seen_year <= cutoff.
This choice is documented and is not an official Constructor-prescribed snapshot rule.
"""
import argparse
import collections
import csv
import io
import json
from pathlib import Path
from zipfile import ZipFile

SNAPSHOT_YEARS = [2020, 2022, 2024]

def parse_archive(path):
    with ZipFile(path) as z:
        names = set(z.namelist())
        required = ["data/tkh_collection10.json", "data/collection10_articles.csv", "data/questions.csv", "data/ground_truth.json"]
        missing = [name for name in required if name not in names]
        if missing:
            raise ValueError("Archive missing files: " + ", ".join(missing))
        graph = json.loads(z.read(required[0]))
        articles = list(csv.DictReader(io.StringIO(z.read(required[1]).decode('utf-8-sig'))))
        questions = list(csv.DictReader(io.StringIO(z.read(required[2]).decode('utf-8-sig')), delimiter=';'))
        ground_truth = json.loads(z.read(required[3]))
        return graph, articles, questions, ground_truth

def observe(graph, articles, questions, ground_truth, years):
    nodes = graph['nodes']
    edges = graph['hyperedges']
    node_ids = {n['id'] for n in nodes}
    if len(node_ids) != len(nodes):
        raise ValueError('Duplicate node IDs')
    if len({e['id'] for e in edges}) != len(edges):
        raise ValueError('Duplicate edge IDs')
    if any(not isinstance(n.get('first_seen_year'), int) for n in nodes):
        raise ValueError('Node missing integer first_seen_year')
    bad_references = []
    repeated_members = []
    future_edge_assertions = []
    for e in edges:
        if len(e['members']) != len(set(e['members'])):
            repeated_members.append(e['id'])
        for v in e['members']:
            if v not in node_ids:
                bad_references.append((e['id'], v))
        if e.get('provenance', {}).get('article_year', e['year']) > e['year']:
            future_edge_assertions.append(e['id'])
    if bad_references:
        raise ValueError('Broken node references: ' + str(bad_references[:10]))
    report = {
        'data_source': 'Constructor provided data.zip: data/tkh_collection10.json',
        'snapshot_policy': {'node': 'first_seen_year <= cutoff', 'edge': 'edge.year <= cutoff and provenance.article_year <= cutoff and all member first_seen_year <= cutoff', 'reason': 'Avoid asserting a fact before its corpus evidence/paper existed; origin_year is not evidence availability.'},
        'global': {
            'articles_csv_count': len(articles),
            'nodes': len(nodes), 'hyperedges': len(edges),
            'node_types': dict(sorted(collections.Counter(n['type'] for n in nodes).items())),
            'edge_relations': dict(sorted(collections.Counter(e['relation_type'] for e in edges).items())),
            'edge_arity_distribution': dict(sorted(collections.Counter(len(e['members']) for e in edges).items())),
            'edges_arity_at_least_three': sum(len(e['members']) >= 3 for e in edges),
            'nodes_origin_year_missing': sum(n.get('origin_year') is None for n in nodes),
            'nodes_year_before_first_seen': sum(n['year'] < n['first_seen_year'] for n in nodes),
            'edges_asserted_by_later_articles': len(future_edge_assertions),
            'edges_duplicate_members': len(repeated_members),
            'orphan_references': len(bad_references),
            'questions': len(questions),
            'questions_by_type': dict(collections.Counter(q['type'] for q in questions)),
            'ground_truth_entries': len(ground_truth),
        },
        'snapshots': {},
        'qa': {'later_assertion_edge_ids': future_edge_assertions, 'duplicate_members_edge_ids': repeated_members, 'time_ineligible_edge_ids_by_cutoff': {}}
    }
    snapshots = {}
    last_nodes = set()
    last_edges = set()
    for cutoff in years:
        node_list = [n for n in nodes if n['first_seen_year'] <= cutoff]
        subset = {n['id'] for n in node_list}
        eligible_date = [e for e in edges if e['year'] <= cutoff and e.get('provenance', {}).get('article_year', e['year']) <= cutoff]
        edge_list = [e for e in eligible_date if all(v in subset for v in e['members'])]
        excluded = [e['id'] for e in eligible_date if not all(v in subset for v in e['members'])]
        report['qa']['time_ineligible_edge_ids_by_cutoff'][str(cutoff)] = excluded
        edge_ids = {e['id'] for e in edge_list}
        involved = {v for e in edge_list for v in e['members']}
        key = str(cutoff)
        report['snapshots'][key] = {
            'nodes': len(node_list),
            'hyperedges': len(edge_list),
            'node_type_counts': dict(sorted(collections.Counter(n['type'] for n in node_list).items())),
            'edge_relation_counts': dict(sorted(collections.Counter(e['relation_type'] for e in edge_list).items())),
            'edge_arity_distribution': dict(sorted(collections.Counter(len(e['members']) for e in edge_list).items())),
            'edges_arity_at_least_three': sum(len(e['members']) >= 3 for e in edge_list),
            'isolated_nodes': len(subset - involved),
            'new_nodes_since_prior_snapshot': len(subset-last_nodes) if last_nodes else None,
            'new_hyperedges_since_prior_snapshot': len(edge_ids-last_edges) if last_edges else None,
            'edges_time_ineligible_due_to_members': len(excluded),
        }
        snapshots[key] = {'cutoff': cutoff, 'nodes': node_list, 'hyperedges': edge_list}
        last_nodes, last_edges = subset, edge_ids
    return report, snapshots

def write_outputs(report, snapshots, out):
    out.mkdir(parents=True, exist_ok=True)
    (out/'eda_summary.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    for k,snapshot in snapshots.items():
        (out/('snapshot_'+k+'.json')).write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding='utf-8')
    lines = ['# T1 Data Audit — Constructor provided TKH', '', 'These are actual audited dataset observations, not trained method outputs.', '', '## Conservative temporal slicing', report['snapshot_policy']['node'], report['snapshot_policy']['edge'], '', '| Cutoff | Nodes | Hyperedges | Arity >= 3 | Isolated | Edges excluded for unavailable nodes |', '|---|---:|---:|---:|---:|---:|']
    for k,x in report['snapshots'].items():
        lines.append('| '+k+' | '+str(x['nodes'])+' | '+str(x['hyperedges'])+' | '+str(x['edges_arity_at_least_three'])+' | '+str(x['isolated_nodes'])+' | '+str(x['edges_time_ineligible_due_to_members'])+' |')
    gl = report['global']
    lines += ['', '## Original archive', f"- Article records: {gl['articles_csv_count']}", f"- Nodes: {gl['nodes']}", f"- Hyperedges: {gl['hyperedges']}", f"- Hyperedges with >=3 members: {gl['edges_arity_at_least_three']}", f"- Missing origin_year: {gl['nodes_origin_year_missing']}", f"- Node year before first_seen_year: {gl['nodes_year_before_first_seen']}", f"- Edge asserted by later-dated paper: {gl['edges_asserted_by_later_articles']}", f"- Questions: {gl['questions']} ({gl['questions_by_type']})", '', '## Scientific caveats', '- A node origin year is not proof that this dataset contained the claim then. We use first_seen_year.', '- We require the asserting article year to be no later than the snapshot cutoff, in addition to edge year.', '- Questions/ground_truth are held out for T6 extrinsic evaluation; no model fit or label generation on gold answers.', '- The 2026 entries have years but not always precise months; do not use all 2026 entries as if available by Feb 2026.', '- This starter implements T1 ONLY. T2–T7 and robust evaluation are NOT completed.', '']
    (out/'T1_DATA_AUDIT.md').write_text('\n'.join(lines),encoding='utf-8')
    return lines

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--zip',dest='zip_path',default='data.zip')
    p.add_argument('--out',default='outputs')
    args=p.parse_args()
    graph,articles,questions,gt=parse_archive(args.zip_path)
    report,snapshots=observe(graph,articles,questions,gt,SNAPSHOT_YEARS)
    write_outputs(report,snapshots,Path(args.out))
    print('T1 completed using actual Constructor input:',args.zip_path)
    print('Total:',report['global']['nodes'],'nodes,',report['global']['hyperedges'],'hyperedges,',report['global']['questions'],'questions')
    for yr,info in report['snapshots'].items():
        print('Snapshot',yr,':',info['nodes'],'nodes;',info['hyperedges'],'hyperedges; arity >= 3:',info['edges_arity_at_least_three'])
    print('Outputs:',str(Path(args.out).resolve()))
    print('NOTICE: This is T1 only. No hierarchy, temporal event alignment, or evaluation T6 yet.')

if __name__ == '__main__':
    main()
