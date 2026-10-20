"""Experimental conservative labeler V3 over frozen V2 evidence.

Purpose: demonstrate a GENERAL deterministic rule, NOT post-hoc edits to 24 names.
No cluster refitting, no gold answers, no automatic replacement of V1/V2 labels.
Thresholds are DEVELOPMENT-ONLY and need independent held-out semantic judging.
Gloss checks factual occurrence counts and cutoff year, not scientific entailment.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

YEARS=(2020,2022,2024)
GENERIC=frozenset('accurate accuracy prediction predictions set sets automatic automatically calculation calculations properties property result results approach approaches method methods model models different efficient novel system systems data dataset datasets materials material structure structures analysis analyses study studies paper papers general work task tasks technique techniques application applications energy highly high low'.split())
MIN_MAJOR=0.60
MIN_PARTIAL=0.30
MIN_ARTICLES=2

def _domain_phrase(phrase):
    tokens=phrase.lower().split()
    return bool(tokens) and not all(token in GENERIC for token in tokens)

def improve_case(row):
    """Never use former human/AI judgment columns or original 24 repair proposals."""
    y=int(row['year'])
    n=int(row['eligible_member_count'])
    evidence=row.get('phrase_evidence',{})
    cand=[]
    for phr,ev in evidence.items():
        inside=int(ev['support_count'])
        support_ids=ev['support_node_ids']
        article_ids=ev['provenance_article_ids']
        if inside!=len(support_ids) or inside>n or inside<0:
            raise ValueError('Corrupt provenance support for '+str(row['stable_id']))
        coverage=(inside/n) if n else 0
        if _domain_phrase(phr) and inside>=3 and len(set(article_ids))>=MIN_ARTICLES:
            cand.append((coverage,inside,len(set(article_ids)),phr,ev))
    cand.sort(key=lambda x:(-x[0],-x[1],-x[2],x[3]))
    if not cand or cand[0][0]<MIN_PARTIAL:
        title='Unresolved heterogeneous cluster'
        gloss=(f'At the {y} cutoff, none of the archived V2 candidate phrases meets the '
               'specificity, two-paper provenance and 30% name-coverage rules; '
               'a unified scientific theme is not asserted.')
        status='ABSTAIN_INSUFFICIENT_DOMAIN_PHRASE'
        used=None
    else:
        coverage,inside,n_sources,phrase,ev=cand[0]
        if coverage>=MIN_MAJOR:
            title=phrase.title()
            status='LEADING_NAME_PHRASE_MAJORITY'
        else:
            title='Partial theme: '+phrase.title()
            status='PARTIAL_NAME_PHRASE'
        gloss=(f'At the {y} cutoff, {inside} of {n} non-metadata members explicitly '
               f'mention "{phrase}" in their names; this is lexical provenance '
               'rather than an independently verified scientific description.')
        used={'phrase':phrase,'support_count':inside,'eligible_count':n,
              'coverage':round(coverage,6),'source_article_count':n_sources,
              'support_node_ids':sorted(ev['support_node_ids']),
              'source_article_ids':sorted(set(ev['provenance_article_ids']))}
    return {'year':y,'level':int(row['level']),'stable_id':row['stable_id'],
            'member_count':int(row['member_count']),'eligible_member_count':n,
            'v2_original_label':row['v2_label'],'v3_development_label':title,
            'v3_development_gloss':gloss,'label_rule_status':status,
            'source_phrase_evidence':used,
            'scientific_full_text_entailment':'NOT_CHECKED',
            'independent_label_quality':'NOT_EVALUATED',
            'new_model_weights_trained':False,
            'replaces_frozen_ensemble':False}

def run(project='.',out='local_only/label_v3_dev'):
    root=Path(project)
    target=Path(out)
    if not target.is_absolute(): target=root/target
    target.mkdir(parents=True,exist_ok=True)
    summary={'schema':'chronohyper_v3_general_conservative_development_v1',
             'years':{},'rule':{'majority_min':MIN_MAJOR,'partial_min':MIN_PARTIAL,
                                'independent_article_min':MIN_ARTICLES,
                                'generic_token_filter':sorted(GENERIC)},
             'source':'original frozen V2 phrase evidence for all level 0/1 clusters',
             'gold_answers_accessed':False,'locked_clusters_modified':False,
             'heldout_semantic_accuracy_measured':False,
             'claim':'Development-only rule; no V3 quality gain asserted'}
    for year in YEARS:
        source=root/f'research_outputs/label_v2/candidates_v2_{year}.json'
        data=json.loads(source.read_text(encoding='utf-8-sig'))
        got=[improve_case(r) for r in data if int(r['level']) in (0,1)]
        if len(got)!=60 or len({(r['level'],r['stable_id']) for r in got})!=60:
            raise ValueError('Expected 12+48 frozen hierarchy nodes in '+str(year))
        (target/f'v3_dev_{year}.json').write_text(
            json.dumps(got,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        status={k:sum(r['label_rule_status']==k for r in got) for k in
                ('LEADING_NAME_PHRASE_MAJORITY','PARTIAL_NAME_PHRASE',
                 'ABSTAIN_INSUFFICIENT_DOMAIN_PHRASE')}
        if sum(status.values())!=60:raise AssertionError('Incomplete status categorization')
        summary['years'][str(year)]={'clusters':len(got),'by_status':status,
                                     'unchanged_titles_vs_v2':sum(
                                         r['v2_original_label']==r['v3_development_label'] for r in got)}
    (target/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',
                                       encoding='utf-8')
    print(json.dumps(summary,indent=2))
    return summary

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--project',default='.')
    ap.add_argument('--out',default='local_only/label_v3_dev')
    a=ap.parse_args()
    run(a.project,a.out)

if __name__=='__main__':main()
