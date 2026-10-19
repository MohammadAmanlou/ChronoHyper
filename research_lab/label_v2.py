"""Temporal, contrastive, source-auditable label candidates for *frozen* CKL hierarchies.

A research candidate and NOT a replacement for external scientific verification.
This module never refits/moves members, reads Q/A gold, or changes the confirmed model.

Design: evidence-visible, contrastive keyphrase extraction over dated source node names;
lexical support and source-article diversity control what the one-sentence gloss
can assert. Explicitly abstain from claims of a coherent topic at low coverage.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import random
import re
import unicodedata

from src.t1_audit import parse_archive

EXCLUDED_TYPES = {'article', 'author', 'claim', 'cited_work'}
# Retain domain nouns (e.g. graph, neural, material, potential) but reject general filler.
STOP = frozenset('a an and are as at be by can for from has in into is its of on or the their this to using use used via was were with within approach approaches method methods model models new novel high low based study studies paper papers result results analysis analyses framework frameworks system systems technique techniques dataset datasets data work works proposed efficient different comparison comparisons'.split())


def tokenize(s):
    s = unicodedata.normalize('NFKC', str(s)).lower()
    return re.findall(r'[a-z]+(?:[+\-][a-z0-9]+)*|[a-z]+\d+', s)


def phrases(name):
    """Exact contiguous non-stopword n-grams: no artificial cross-stopword phrase."""
    toks = tokenize(name)
    found = set()
    for i in range(len(toks)):
        for n in (1, 2, 3):
            seq = toks[i:i+n]
            if len(seq) < n or any(len(t)<3 or t in STOP for t in seq):
                continue
            ph = ' '.join(seq)
            if len(ph) <= 48:
                found.add(ph)
    return found


def _provenance_articles(node, by_article, year):
    result=set()
    for key in node.get('provenance',{}).get('articles',[]):
        a=by_article.get(str(key))
        if a is None: continue
        try: article_year=int(a['year'])
        except (KeyError, ValueError, TypeError): continue
        if article_year <= year:
            result.add(str(key))
    return result


def label_partition(nodes, supernodes, articles, year, levels=(0,1)):
    """Return (records, audit) with a per-phrase complete source-node membership check.

    This only extracts descriptions of explicit phrase occurrences in exported names,
    not inferred semantics of all members. Source article IDs are provenance links,
    never claims that the full article entails the generated phrase.
    """
    byid={n['id']:n for n in nodes if int(n['first_seen_year']) <= year}
    by_article={str(a['id']):a for a in articles}
    eligible={i:n for i,n in byid.items() if n['type'] not in EXCLUDED_TYPES}
    term_map={i:phrases(n['surface_form']) for i,n in eligible.items()}
    all_df=Counter(p for phs in term_map.values() for p in phs)
    nall=len(eligible)
    records=[]
    for sn in sorted(supernodes,key=lambda x:(int(x['level']),str(x['id']))):
        if sn['level'] not in levels:continue
        ids=sorted(sn['member_ids'])
        if any(v not in byid for v in ids):
            raise ValueError(f'{sn["id"]}: node not available by year {year}')
        avail=[v for v in ids if v in eligible]
        ctr=Counter(p for v in avail for p in term_map[v])
        pair_counts={}
        for p,inside in ctr.items():
            if inside<2:continue
            outside=all_df[p]-inside
            # Contrastively specific to *this cluster*, with size/frequency guards.
            # Sentence-level names only; no embedding trained on gold labels.
            odds=math.log((inside+0.5)/(max(1,len(avail))-inside+0.5)) - math.log((outside+0.5)/(max(1,nall-len(avail))-outside+0.5))
            article_ids=set()
            supporters=[v for v in avail if p in term_map[v]]
            for v in supporters:article_ids.update(_provenance_articles(byid[v],by_article,year))
            diversification=1+0.08*min(5, len(article_ids))
            size_term=(1+.09*(len(p.split())-1))
            score=math.log1p(inside)*odds*diversification*size_term
            pair_counts[p]={'score':score,'inside':inside,'outside':outside,'article_ids':sorted(article_ids), 'support_node_ids':supporters}
        ordered=sorted(pair_counts, key=lambda p:(-pair_counts[p]['score'],-pair_counts[p]['inside'],p))
        selected=[]
        for p in ordered:
            if pair_counts[p]['score'] <= 0:break
            if any(set(p.split()) & set(q.split()) for q in selected):continue
            selected.append(p)
            if len(selected)==2:break
        if not selected:
            # Genuine abstention is better than inventing a scientific consensus.
            title='Unresolved heterogeneous cluster'
            gloss=f'This snapshot contains {len(ids)} exported entities, with insufficient contrastive lexical evidence to name a unified scientific topic.'
            confidence='abstain'
        else:
            primary=selected[0]
            ph=pair_counts[primary]
            fraction=ph['inside']/max(1,len(avail))
            strong=(fraction>=.15 and ph['inside']>=3 and len(ph['article_ids'])>=2)
            confidence='source_supported_partial' if strong else 'low_support_partial'
            name=' / '.join(p.title() for p in selected)
            title=name if strong else 'Mixed topics: '+name
            gloss=(f'At the {year} cutoff, {ph["inside"]} of {len(avail)} non-metadata members explicitly mention '
                   f'"{primary}" in their exported names; this does not imply that every cluster member shares the topic.')
        item={'stable_id':sn['id'],'year':year,'level':int(sn['level']),
              'member_count':len(ids),'member_ids':ids,'eligible_member_count':len(avail),
              'v1_label':sn['label'],'v1_gloss':sn['gloss'],
              'v2_label':title,'v2_gloss':gloss,'confidence':confidence,
              'selected_phrases':selected,'phrase_evidence':{p:{'phrase':p,'support_node_ids':pair_counts[p]['support_node_ids'],
                'support_count':pair_counts[p]['inside'],'contrast_score':round(pair_counts[p]['score'],6),
                'provenance_article_ids':pair_counts[p]['article_ids']}
                for p in selected},
              'temporal_policy':'Only nodes with first_seen_year <= cutoff; provenance article IDs counted only when article year <= cutoff.',
              'epistemic_scope':'Exact phrase occurrence in exported node names; NOT a validated scientific summary of all cluster members.'}
        # Structural self-audit of ALL cited supporters, not a truncated top-N sample.
        for p,ev in item['phrase_evidence'].items():
            support=set(ev['support_node_ids'])
            if support-{*ids} or any(p not in term_map[v] or int(byid[v]['first_seen_year'])>year for v in support):
                raise AssertionError(f'Unfaithful phrase evidence for {sn["id"]}: {p}')
            assert ev['support_count']==len(support)
            for article_id in ev['provenance_article_ids']:
                if any(article_id in _provenance_articles(byid[v],by_article,year) for v in support): continue
                raise AssertionError('Unsupported article-provenance link')
        records.append(item)
    audit={'year':year,'labels':len(records),'with_abstention':sum(x['confidence']=='abstain' for x in records),
           'with_low_support':sum(x['confidence']=='low_support_partial' for x in records),
           'with_partial_source_support':sum(x['confidence']=='source_supported_partial' for x in records),
           'lexical_source_assertions_checked':sum(len(v['support_node_ids']) for x in records for v in x['phrase_evidence'].values()),
           'lexical_source_assertions_unsupported':0,
           'human_semantic_label_accuracy':'NOT_MEASURED_FOR_V2',
           'independent_gloss_overclaim_rate':None,
           'caveat':'Source IDs/phrases verified, but label correctness and scientific coherence cannot be certified from the same node-name source.'}
    return records,audit


def make_blind_sheet(records, v1_previous_rows, nodes, articles, seed=451, limit=24):
    """Paired V1/V2 review on previously-unrated source cases.

    The node sample is RANDOM, independent of V1/V2 source phrase supporters,
    preventing an accidental biased prompt that privileges the new method.
    The key is kept separate from the blinded sheet.
    """
    old={(str(r['snapshot']),str(r['stable_id'])) for r in v1_previous_rows}
    byid={n['id']:n for n in nodes}
    byarticle={str(a['id']):a for a in articles}
    r=random.Random(seed)
    candidates=[x for x in records if (str(x['year']),str(x['stable_id'])) not in old and x['year'] in (2022,2024)]
    chosen=r.sample(sorted(candidates,key=lambda x:(x['year'],x['stable_id'])), min(limit,len(candidates)))
    sheet=[];secret={}
    for x in chosen:
        flip=bool(r.randint(0,1))
        A=(x['v2_label'],x['v2_gloss']) if flip else (x['v1_label'],x['v1_gloss'])
        B=(x['v1_label'],x['v1_gloss']) if flip else (x['v2_label'],x['v2_gloss'])
        full=list(x['member_ids'])
        # Fixed random evidence, with no candidate-dependent sampling.
        sample=r.sample(full,min(14,len(full)))
        paper_ids=set()
        for nid in sample:
            node=byid[nid]
            for art in node.get('provenance',{}).get('articles',[]):
                rec=byarticle.get(str(art))
                if rec is not None and int(rec['year'])<=x['year']:
                    paper_ids.add(str(art))
        paper_names=[byarticle[i].get('title','(unknown article title)') for i in sorted(paper_ids)][:5]
        sheet.append({'year':x['year'],'level':x['level'],'stable_id':x['stable_id'],
                 'cluster_member_count':x['member_count'],
                 'random_member_ids':' | '.join(sample),
                 'random_member_names':' | '.join(byid[nid]['surface_form'] for nid in sample),
                 'linked_source_article_titles':' | '.join(paper_names),
                 'label_A':A[0], 'gloss_A':A[1], 'label_B':B[0], 'gloss_B':B[1],
                 'A_accuracy_accurate_vague_wrong':'','B_accuracy_accurate_vague_wrong':'',
                 'A_gloss_overclaim_yes_no_unclear':'','B_gloss_overclaim_yes_no_unclear':'',
                 'reviewer_id':'','review_notes':''})
        secret[f'{x["year"]}:{x["stable_id"]}']='A' if flip else 'B'
    return sheet,secret


def write_outputs(project, out, years=(2020,2022,2024), blind_seed=451):
    root=Path(project);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    graph,articles,_,_=parse_archive(root/'inputs/data.zip')
    all_nodes=graph['nodes']
    old_path=root/'outputs_selected/label_review_sheet.csv'
    with old_path.open(encoding='utf-8-sig',newline='') as f: reviewed=list(csv.DictReader(f))
    metrics={'schema':'ckl-label-v2-research','status':'AUTO_SOURCE_AUDITED_BUT_NOT_EXPERT_VALIDATED',
             'frozen_cluster_assignments':'UNCHANGED','old_review_ratings':dict(Counter(r.get('label_rating_accurate_vague_wrong','').strip() for r in reviewed)),
             'old_reviewer_identifiers':sorted(set(r.get('reviewer_id','').strip() for r in reviewed)),
             'years':{},'data_sha256':hashlib.sha256((root/'inputs/data.zip').read_bytes()).hexdigest()}
    all_items=[]
    for year in years:
        h=json.loads((root/f'outputs_selected/hierarchy_{year}.json').read_text(encoding='utf-8'))
        available=[n for n in all_nodes if int(n['first_seen_year'])<=year]
        records,audit=label_partition(available,h['supernodes'],articles,year)
        (out/f'candidates_v2_{year}.json').write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding='utf-8')
        metrics['years'][str(year)]=audit
        all_items+=records
    blind,secret=make_blind_sheet(all_items,reviewed,all_nodes,articles,blind_seed)
    # Key kept separate and MUST NOT be shared with a blinded reviewer.
    if not blind:raise ValueError('No unseen label cases for blind comparison')
    with (out/'BLIND_LABEL_COMPARISON_TO_FILL.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(blind[0]));writer.writeheader();writer.writerows(blind)
    (out/'BLIND_KEY_KEEP_SEPARATE.json').write_text(json.dumps(secret,indent=2),encoding='utf-8')
    metrics['blind_review_cases_unseen_in_prior_sheet']=len(blind)
    metrics['blind_review_status']='UNRATED'
    (out/'v2_source_audit.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    lines=['# CKL V2 contrastive labeller — real-data experimental result','','This is an **exploratory** implementation on the fixed, locked `native_temporal_20` hierarchy.',
           'It does not reassign nodes or improve T2/T3 results, and no reviewer has rated V2 yet.','','## Output audit',
           '| Year | Labels | Source-supported partial | Low-support partial | Abstain | Verified lexical supporters |','|---|---:|---:|---:|---:|---:|']
    for year,a in metrics['years'].items():
        lines.append(f'| {year} | {a["labels"]} | {a["with_partial_source_support"]} | {a["with_low_support"]} | {a["with_abstention"]} | {a["lexical_source_assertions_checked"]} |')
    lines+=['','**What was established:** all cited phrase occurrences and year-eligible article IDs checked against real input node records (lexical/provenance validity only).',
            '**What was NOT established:** a domain expert finding these clusters scientifically coherent, label improvement over V1, independent NLI/overclaim rate.',
            f'**Untouched review cases available:** {len(blind)}. Provide `BLIND_LABEL_COMPARISON_TO_FILL.csv` to an independent reviewer; DO NOT give them `BLIND_KEY_KEEP_SEPARATE.json`.',
            f'**Prior review identifiers:** {metrics["old_reviewer_identifiers"]}. These must not be described as blinded independent human review without direct evidence.',
            '', '## Reproduction', '```bash','python -m research_lab.label_v2 --project . --out research_outputs/label_v2','```',
            'The method contrasts candidate phrases against other members of the same year/level vocabulary. Generic statements are calibrated to *explicit token occurrence* and explicitly refuse to generalize from keyword mentions to all members.',
            'It uses article IDs as provenance only and does not imply an entire article scientifically entails its keyword mention.',
            'The old V1 review is a development diagnostic, not a held-out V2 result.', '']
    (out/'V2_FINDINGS.md').write_text('\n'.join(lines),encoding='utf-8')
    return metrics


def score_blind(sheet, key_file, out):
    """Paired scoring, preserving unrated/uncertain pairs instead of imputing them."""
    with Path(sheet).open(encoding='utf-8-sig', newline='') as fp:
        rows=list(csv.DictReader(fp))
    key=json.loads(Path(key_file).read_text(encoding='utf-8'))
    scale={'accurate':2,'vague':1,'wrong':0}
    pairs=[];all_ids=set()
    for r in rows:
        ident=f'{r["year"]}:{r["stable_id"]}'
        if ident in all_ids:raise ValueError(f'Duplicate blinded case {ident}')
        all_ids.add(ident)
        if ident not in key:raise ValueError(f'Missing blinded mapping for {ident}')
        ra=r['A_accuracy_accurate_vague_wrong'].strip().lower()
        rb=r['B_accuracy_accurate_vague_wrong'].strip().lower()
        rev=r['reviewer_id'].strip()
        if ra not in scale or rb not in scale or not rev:
            continue
        v2_is_A=(key[ident]=='A')
        a,b=scale[ra],scale[rb]
        v2,v1=(a,b) if v2_is_A else (b,a)
        pairs.append({'id':ident,'v1':v1,'v2':v2,'difference_v2_minus_v1':v2-v1,'reviewer_id':rev,
                      'v1_overclaim':r['B_gloss_overclaim_yes_no_unclear'].strip().lower() if v2_is_A else r['A_gloss_overclaim_yes_no_unclear'].strip().lower(),
                      'v2_overclaim':r['A_gloss_overclaim_yes_no_unclear'].strip().lower() if v2_is_A else r['B_gloss_overclaim_yes_no_unclear'].strip().lower()})
    wins=sum(x['difference_v2_minus_v1']>0 for x in pairs)
    losses=sum(x['difference_v2_minus_v1']<0 for x in pairs)
    ties=len(pairs)-wins-losses
    n=wins+losses
    pval=min(1.,2*sum(math.comb(n,k) for k in range(min(wins,losses)+1)) / (2**n)) if n else None
    def gloss_rate(field):
        yes=sum(x[field]=='yes' for x in pairs)
        eligible=sum(x[field] in ('yes','no') for x in pairs)
        return {'overclaim_yes':yes,'evaluable':eligible,'rate':yes/eligible if eligible else None}
    result={'status':'COMPLETE_AUTHOR_REVIEW' if len(pairs)==len(rows) else 'PARTIAL_REVIEW',
           'requested_cases':len(rows),'paired_cases_with_both_ratings_and_reviewer_id':len(pairs),
           'v2_wins':wins,'v2_losses':losses,'ties':ties,
           'mean_rating_delta_v2_minus_v1':sum(x['difference_v2_minus_v1'] for x in pairs)/len(pairs) if pairs else None,
           'two_sided_exact_paired_sign_test_p':pval,
           'v1_gloss':gloss_rate('v1_overclaim'),'v2_gloss':gloss_rate('v2_overclaim'),
           'reviewer_ids_observed':sorted(set(x['reviewer_id'] for x in pairs)),
           'human_independence_verified':False,
           'note':'A/B method order was hidden in the worksheet but reviewer independence is self-reported, not automatically validated. Ratings are based on sampled names/titles, not exhaustive full-text entailment; small-N p-values do not establish scientific truth.'}
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/'v2_paired_blind_scores.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    print('V2 PAIRED ASSESSMENT',json.dumps(result,indent=2))
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--project',default='.')
    ap.add_argument('--out',default='research_outputs/label_v2')
    ap.add_argument('--years',default='2020,2022,2024')
    ap.add_argument('--score-blind',default=None,help='CSV with human A/B judgments; do not set this until actually completed')
    ap.add_argument('--key',default=None,help='Local A/B key kept away from the reviewer')
    a=ap.parse_args()
    if a.score_blind:
        if not a.key:ap.error('--score-blind requires --key')
        score_blind(a.score_blind,a.key,a.out)
        return
    m=write_outputs(a.project,a.out,[int(y) for y in a.years.split(',')])
    for y,row in m['years'].items():print(f'V2 {y}: {row["labels"]} labels; {row["with_abstention"]} abstentions; {row["lexical_source_assertions_checked"]} cited node-name occurrences source-verified')
    print('NO LABEL ADVANTAGE CLAIMED until external blinded evaluation is completed.')

if __name__=='__main__':main()
