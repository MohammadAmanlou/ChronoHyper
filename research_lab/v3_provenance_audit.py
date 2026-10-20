"""Full-membership, dated provenance audit of ALL 180 developmental V3 labels.

A structural/lexical assertion checker, not an independent semantic or paper-text
faithfulness evaluator. Reads original ZIP but never opens any benchmark gold.
All reported evidence stays under ignored local_only/.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

from src.t1_audit import parse_archive
from research_lab.label_v2 import EXCLUDED_TYPES, phrases, _provenance_articles
from research_lab.label_v3 import YEARS, improve_case

def _read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def _require(condition, message):
    if not condition:
        raise ValueError(message)

def _bykey(records):
    result = {}
    for x in records:
        key = (int(x['level']), str(x['stable_id']))
        _require(key not in result, 'Duplicate level/stable_id: '+repr(key))
        result[key] = x
    return result

def audit(project='.', out='local_only/label_v3_dev/provenance_audit.json',
          years=YEARS, expected_per_year=60):
    root = Path(project)
    graph, articles, _, _ = parse_archive(root/'inputs/data.zip')
    nodes = {str(n['id']): n for n in graph['nodes']}
    byarticle = {str(a['id']): a for a in articles}
    seen = set()
    statuses = Counter()
    annual = {}
    supporters_checked = 0
    articles_checked = 0
    for year in years:
        hierarchy = _read(root/f'outputs_selected/hierarchy_{year}.json')
        v2 = _read(root/f'research_outputs/label_v2/candidates_v2_{year}.json')
        v3 = _read(root/f'local_only/label_v3_dev/v3_dev_{year}.json')
        h = {(int(x['level']), str(x['id'])): x for x in hierarchy['supernodes']
             if int(x['level']) in (0, 1)}
        original = _bykey(v2)
        current = _bykey(v3)
        _require(len(h)==len(original)==len(current)==expected_per_year,
                 f'{year}: missing or duplicate labels')
        _require(set(h)==set(original)==set(current), f'{year}: hierarchy / label ID mismatch')
        annual_status = Counter()
        for key in sorted(h):
            prior, label, group = original[key], current[key], h[key]
            ids = [str(i) for i in group['member_ids']]
            _require(len(ids)==len(set(ids)), f'{year}/{key}: duplicate member IDs')
            _require(sorted(ids)==sorted(map(str,prior['member_ids'])),
                     f'{year}/{key}: V2 member set differs from frozen hierarchy')
            _require(len(ids)==int(prior['member_count'])==int(label['member_count']),
                     f'{year}/{key}: member-count mismatch')
            _require(all(i in nodes and int(nodes[i]['first_seen_year'])<=year for i in ids),
                     f'{year}/{key}: future or unknown member in frozen group')
            eligible = [i for i in ids if nodes[i]['type'] not in EXCLUDED_TYPES]
            _require(int(prior['eligible_member_count'])==len(eligible)==
                     int(label['eligible_member_count']),
                     f'{year}/{key}: nonmetadata denominator mismatch')
            _require(improve_case(prior)==label,
                     f'{year}/{key}: V3 output changed relative to deterministic rule')
            for phrase,ev in prior.get('phrase_evidence',{}).items():
                lexical = sorted(i for i in eligible
                                 if phrase in phrases(nodes[i]['surface_form']))
                claimed = sorted(map(str,ev['support_node_ids']))
                _require(claimed==lexical and int(ev['support_count'])==len(lexical),
                         f'{year}/{key}: unsupported/missing lexical phrase: {phrase}')
                source = sorted({aid for i in lexical
                                 for aid in _provenance_articles(nodes[i],byarticle,year)})
                _require(sorted(map(str, ev['provenance_article_ids']))==source,
                         f'{year}/{key}: missing/extra/undated publication provenance: {phrase}')
                supporters_checked += len(lexical)
                articles_checked += len(source)
            status = label['label_rule_status']
            _require(status in {'LEADING_NAME_PHRASE_MAJORITY',
                                'PARTIAL_NAME_PHRASE',
                                'ABSTAIN_INSUFFICIENT_DOMAIN_PHRASE'},
                     f'{year}/{key}: unknown label status')
            for text_field in ('v3_development_label','v3_development_gloss'):
                _require(bool(label.get(text_field)), f'{year}/{key}: empty {text_field}')
            annual_status[status]+=1
            statuses[status]+=1
            seen.add((year,key))
        annual[str(year)]={'checked_clusters':len(current),
                           'label_rule_statuses':dict(sorted(annual_status.items()))}
    total = len(seen)
    n_abstain = statuses['ABSTAIN_INSUFFICIENT_DOMAIN_PHRASE']
    result={
        'schema':'chronohyper_v3_full_provenance_audit_v1',
        'scope':'V3 developmental labels; frozen clusters and original source node names',
        'years':annual, 'n_labels_checked':total,
        'n_name_supported_leading_or_partial':total-n_abstain,
        'n_explicit_abstentions':n_abstain,
        'abstention_fraction':n_abstain/total if total else None,
        'by_status':dict(sorted(statuses.items())),
        'full_member_name_phrase_support_occurrences_checked':supporters_checked,
        'dated_article_provenance_references_checked':articles_checked,
        'structural_and_lexical_errors':0,
        'full_paper_semantic_entailment_evaluable_n':0,
        'independent_semantic_label_accuracy':None,
        'scientific_overclaim_rate':None,
        'locked_model_changed':False,
        'gold_answer_files_opened':False,
        'interpretation':(
            'All claimed source-name phrase occurrences and cutoff-eligible article IDs '
            'are audited against original records, across the full 180-case development '
            'set. This does NOT prove that a cluster is scientifically coherent, or that '
            'any linked article entails the label/gloss. The blind expert/AI review '
            'remains separate and incomplete.'
        )}
    destination = Path(out)
    if not destination.is_absolute(): destination=root/destination
    destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists():
        prior = _read(destination)
        # Deterministic repeated audits may be validated, but not overwritten without warning.
        _require(prior==result, 'Prior local V3 audit differs; keep both and investigate')
    else:
        destination.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',
                               encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--project',default='.')
    parser.add_argument('--out',default='local_only/label_v3_dev/provenance_audit.json')
    args=parser.parse_args()
    audit(args.project,args.out)

if __name__=='__main__':
    main()
