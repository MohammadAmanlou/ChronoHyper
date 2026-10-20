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


def recover_frozen_blind_key(project='.', destination=None):
    """Recover A/B mapping solely from frozen candidate labels and glosses.

    This operation DOES NOT rewrite the original blind worksheet, rerun label
    generation, or score any ratings. The recovered key is machine-local and
    must never be sent to a reviewer or pushed to GitHub.
    """
    root=Path(project)
    base=root/'research_outputs/label_v2'
    with (base/'BLIND_LABEL_COMPARISON_TO_FILL.csv').open(
            encoding='utf-8-sig', newline='') as fp:
        blind=list(csv.DictReader(fp))
    records=[]
    for year in (2022,2024):
        records+=json.loads((base/f'candidates_v2_{year}.json').read_text(encoding='utf-8'))
    candidates={f'{x["year"]}:{x["stable_id"]}':x for x in records}
    keys={}
    for row in blind:
        ident=f'{row["year"]}:{row["stable_id"]}'
        if ident in keys or ident not in candidates:
            raise ValueError('Duplicate or unmatched blind record: '+ident)
        c=candidates[ident]
        a=(row['label_A']==c['v2_label'] and row['gloss_A']==c['v2_gloss']
           and row['label_B']==c['v1_label'] and row['gloss_B']==c['v1_gloss'])
        b=(row['label_B']==c['v2_label'] and row['gloss_B']==c['v2_gloss']
           and row['label_A']==c['v1_label'] and row['gloss_A']==c['v1_gloss'])
        if a == b:
            raise ValueError('Ambiguous or changed frozen A/B content: '+ident)
        keys[ident]='A' if a else 'B'
    if len(keys)!=24:
        raise ValueError('Expected 24 uniquely matched frozen label cases')
    destination=Path(destination) if destination else base/'BLIND_KEY_KEEP_SEPARATE.json'
    destination.parent.mkdir(parents=True,exist_ok=True)
    # Never accidentally overwrite a previous secret key.
    if destination.exists():
        saved=json.loads(destination.read_text(encoding='utf-8'))
        if saved!=keys:
            raise ValueError('Existing private key differs: investigate before scoring')
    else:
        destination.write_text(json.dumps(keys,indent=2)+'\n',encoding='utf-8')
    print('RECOVERED 24/24 A/B keys from frozen texts; PRIVATE key location:',destination)
    return keys


def score_blind(sheet, key_file, out):
    """Paired scoring, preserving unrated/uncertain pairs instead of imputing them."""
    with Path(sheet).open(encoding='utf-8-sig', newline='') as fp:
        rows=list(csv.DictReader(fp))
    # A reviewer is allowed to change ratings and notes, never frozen evidence or A/B texts.
    # Check against the canonical 24-case sheet when running inside this repo.
    canonical=Path(__file__).resolve().parents[1]/'research_outputs/label_v2/BLIND_LABEL_COMPARISON_TO_FILL.csv'
    if len(rows)==24 and canonical.exists():
        with canonical.open(encoding='utf-8-sig',newline='') as f:
            baseline=list(csv.DictReader(f))
        def identity(row):return (row['year'],row['stable_id'])
        fixed=['year','level','stable_id','cluster_member_count',
           'random_member_ids','random_member_names','linked_source_article_titles',
           'label_A','gloss_A','label_B','gloss_B']
        origin={identity(x):x for x in baseline}
        if len(origin)!=24 or len(baseline)!=24 or {identity(x) for x in rows}!=set(origin):
            raise ValueError('Rated sheet IDs differ from the 24 frozen reference cases')
        for row in rows:
            if any(row.get(field)!=origin[identity(row)].get(field) for field in fixed):
                raise ValueError('Reviewer copy changed original evidence or A/B texts: '+str(identity(row)))
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
    # Reviewer IDs can self-identify as AI; this is a diagnostic, not human evidence.
    # Identity is a metadata claim, never proof that an external reviewer is independent.
    reviewer_ids={x['reviewer_id'] for x in pairs}
    def explicitly_ai(name):
        lowered=name.casefold()
        return lowered.startswith('ai_') or 'gpt-' in lowered or 'chatgpt' in lowered or 'non-human' in lowered
    ai_count=sum(explicitly_ai(x) for x in reviewer_ids)
    if len(pairs)!=len(rows):
        review_status='PARTIAL_REVIEW'
    elif ai_count==len(reviewer_ids) and reviewer_ids:
        review_status='COMPLETE_AI_ONLY_DIAGNOSTIC'
    elif ai_count:
        review_status='MIXED_AI_AND_OTHER_REVIEWS'
    else:
        review_status='COMPLETE_REVIEWER_REPORTED'
    result={'status':review_status,
           'requested_cases':len(rows),'paired_cases_with_both_ratings_and_reviewer_id':len(pairs),
           'v2_wins':wins,'v2_losses':losses,'ties':ties,
           'mean_rating_delta_v2_minus_v1':sum(x['difference_v2_minus_v1'] for x in pairs)/len(pairs) if pairs else None,
           'two_sided_exact_paired_sign_test_p':pval,
           'v1_gloss':gloss_rate('v1_overclaim'),'v2_gloss':gloss_rate('v2_overclaim'),
           'reviewer_ids_observed':sorted(set(x['reviewer_id'] for x in pairs)),
           'human_independence_verified':False,
           'all_reported_reviewers_explicitly_ai':bool(reviewer_ids) and ai_count==len(reviewer_ids),
           'reviewer_origin_is_self_reported':True,
           'note':'A/B method order was hidden in the worksheet but reviewer independence is self-reported, not automatically validated. Ratings are based on sampled names/titles, not exhaustive full-text entailment; small-N p-values do not establish scientific truth.'}
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/'v2_paired_blind_scores.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    print('V2 PAIRED ASSESSMENT',json.dumps(result,indent=2))
    return result



def summarize_ai_review(project='.', output=None):
    """Reconcile prior AI-only A/B judgments with frozen V1/V2 candidates.

    No unblinding key is read, no worksheet is modified and no human review is
    inferred. Only aggregate counts are written: never publish per-case mapping.
    """
    root=Path(project)
    base=root/'research_outputs/label_v2'
    def load(path):
        with path.open(encoding='utf-8-sig', newline='') as stream:
            return list(csv.DictReader(stream))
    sheet=load(base/'BLIND_LABEL_COMPARISON_TO_FILL.csv')
    ai=load(base/'ai_label_review.csv')
    candidates=[]
    for year in (2022,2024):
        candidates += json.loads((base/f'candidates_v2_{year}.json').read_text(encoding='utf-8'))
    def ident(row):
        return f'{row["year"]}:{row["stable_id"]}'
    original={ident(row):row for row in sheet}
    judgments={ident(row):row for row in ai}
    source={ident(row):row for row in candidates}
    if len(sheet)!=24 or len(ai)!=24 or len(original)!=24 or len(judgments)!=24:
        raise ValueError('Expected 24 unique blinded cases and 24 AI judgments')
    if set(original)!=set(judgments) or not set(original).issubset(source):
        raise ValueError('Reviewed IDs do not match the frozen candidate records')
    grades={'accurate':2,'vague':1,'wrong':0}
    wins=losses=ties=pref_v2=pref_v1=pref_tie=0
    arm_v2={'A':0,'B':0}
    changes=[]
    for key in sorted(original):
        blind=original[key]
        r=judgments[key]
        c=source[key]
        if r.get('not_independent_human')!='TRUE':
            raise ValueError('AI review must explicitly disclose non-human origin')
        validA=(blind['label_A']==c['v2_label'] and blind['gloss_A']==c['v2_gloss']
                and blind['label_B']==c['v1_label'] and blind['gloss_B']==c['v1_gloss'])
        validB=(blind['label_B']==c['v2_label'] and blind['gloss_B']==c['v2_gloss']
                and blind['label_A']==c['v1_label'] and blind['gloss_A']==c['v1_gloss'])
        if validA == validB:
            raise ValueError('Blinded records mismatch or ambiguous: '+key)
        arm='A' if validA else 'B'
        arm_v2[arm]+=1
        other='B' if validA else 'A'
        va=r.get(arm+'_label_rating_AI','').strip().lower()
        vb=r.get(other+'_label_rating_AI','').strip().lower()
        if va not in grades or vb not in grades:
            raise ValueError('Incomplete or invalid AI rating: '+key)
        delta=grades[va]-grades[vb]
        changes.append(delta)
        if delta>0:wins+=1
        elif delta<0:losses+=1
        else:ties+=1
        preference=r.get('provisional_A_B_preference_AI','')
        if preference=='tie':pref_tie+=1
        elif preference==arm:pref_v2+=1
        elif preference==other:pref_v1+=1
        else:raise ValueError('Invalid AI preference: '+key)
    n=wins+losses
    sign_p=(min(1.,2*sum(math.comb(n,k) for k in range(min(wins,losses)+1))/2**n)
            if n else None)
    result={
        'schema':'ckl_v1_v2_ai_diagnostic_summary_v1',
        'sample_n':len(changes),
        'derived_v2_matching':'exact candidate label+gloss vs frozen A/B pairs (24 unambiguous matches); original local A/B key NOT read',
        'v2_arm_counts':arm_v2,
        'rating_scale':grades,
        'v2_rating_wins':wins,
        'v1_rating_wins':losses,
        'rating_ties':ties,
        'mean_delta_v2_minus_v1':sum(changes)/len(changes),
        'exact_sign_test_p_descriptive_only':sign_p,
        'general_preference_v2':pref_v2,
        'general_preference_v1':pref_v1,
        'general_preference_ties':pref_tie,
        'gloss_overclaim_rate':None,
        'human_review':False,
        'independent_evidence_validation':False,
        'inference_validity':'EXPLORATORY AI self-evaluation on previously inspected sampled nodes and article titles, NOT independent blind expert ground truth; p-value only describes an arithmetic pairing, no confirmatory significance inference',
        'scientific_conclusion':'V2 scientific accuracy advantage NOT established; refrain from reporting source-rubric coverage or lexical checks as entailment'
    }
    target=Path(output) if output else base/'ai_paired_summary.json'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    print('AI-ONLY DIAGNOSTIC: V2',wins,'V1',losses,'ties',ties,'sign p (descriptive only)',sign_p)
    return result


def audit_v2_24_literal_source_claims(project='.', out='research_outputs/label_v2'):
    """Check 24 V2 glosses against FULL original node records, not sampled names.

    This performs factual/count/provenance verification; it does not perform a
    blinded independent assessment of scientific meaning or full-paper entailment.
    No source model, original frozen result, A/B key or human worksheet is changed.
    """
    root=Path(project);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    base=root/'research_outputs/label_v2'
    with (base/'BLIND_LABEL_COMPARISON_TO_FILL.csv').open(encoding='utf-8-sig',newline='') as f:
        case_rows=list(csv.DictReader(f))
    if len(case_rows)!=24 or len({(x['year'],x['stable_id']) for x in case_rows})!=24:
        raise ValueError('Expected 24 unique frozen A/B cases')
    all_candidates=[]
    for year in (2022,2024):
        all_candidates+=json.loads((base/f'candidates_v2_{year}.json').read_text(encoding='utf-8'))
    c_by_id={(str(c['year']),c['stable_id']):c for c in all_candidates}
    graph,articles,_,_=parse_archive(root/'inputs/data.zip')
    nodes={n['id']:n for n in graph['nodes']}
    hierarchy={}
    for year in (2022,2024):
        h=json.loads((root/f'outputs_selected/hierarchy_{year}.json').read_text(encoding='utf-8'))
        hierarchy[year]={x['id']:x for x in h['supernodes'] if x['level']==1}
    fields=['year','stable_id','level','title','gloss','member_count','eligible_member_count',
        'claimed_year','primary_phrase','gloss_numerical_support_count',
        'generator_supporter_count','source_support_node_ids',
        'machine_lexical_claim_status','lexical_overclaim_status',
        'independent_scientific_overclaim_status','label_semantic_status','audit_scope']
    rows=[];n_literal=0;n_qualitative=0
    rx=re.compile(r'At the ([0-9]+) cutoff, ([0-9]+) of ([0-9]+) non-metadata members explicitly mention "([^"]+)" in their exported names; this does not imply that every cluster member shares the topic[.]')
    for case in case_rows:
        key=(case['year'],case['stable_id'])
        if key not in c_by_id:raise ValueError('Missing V2 candidate: '+str(key))
        c=c_by_id[key];year=int(case['year'])
        same_a=(case['label_A']==c['v2_label'] and case['gloss_A']==c['v2_gloss'])
        same_b=(case['label_B']==c['v2_label'] and case['gloss_B']==c['v2_gloss'])
        if same_a==same_b:raise ValueError('Frozen A/B text mismatch: '+str(key))
        if c['level']!=int(case['level']) or c['member_count']!=int(case['cluster_member_count']):
            raise ValueError('Frozen cluster metadata mismatch: '+str(key))
        sn=hierarchy[year].get(c['stable_id'])
        if sn is None or sorted(sn['member_ids'])!=sorted(c['member_ids']):
            raise ValueError('Frozen hierarchy membership differs from candidate: '+str(key))
        members=[]
        for ident in c['member_ids']:
            n=nodes[ident]
            if int(n['first_seen_year'])>year:raise ValueError('Future node in cluster: '+ident)
            members.append(n)
        eligible=[n for n in members if n['type'] not in EXCLUDED_TYPES]
        if len(eligible)!=c['eligible_member_count']:raise ValueError('Nonmetadata denominator mismatch: '+str(key))
        found=rx.fullmatch(c['v2_gloss'])
        if found:
            claimed_year,claimed_num,claimed_den,phrase=found.groups()
            supporters=sorted(n['id'] for n in eligible if phrase in phrases(n['surface_form']))
            evidence=c['phrase_evidence'].get(phrase)
            if (int(claimed_year)!=year or int(claimed_num)!=len(supporters)
                or int(claimed_den)!=len(eligible) or not evidence
                or evidence['support_count']!=len(supporters)
                or sorted(evidence['support_node_ids'])!=supporters):
                raise ValueError('Unsupported V2 literal count or phrase evidence: '+str(key))
            n_literal+=1
            claim='PASS_FULL_MEMBER_RECOUNT';overclaim='no'
            source_ids='|'.join(supporters)
            claimed_num=int(claimed_num)
            claimed_year=int(claimed_year)
        else:
            if not (c['v2_label']=='Unresolved heterogeneous cluster'
                    and c['v2_gloss']==f'This snapshot contains {len(members)} exported entities, with insufficient contrastive lexical evidence to name a unified scientific topic.'
                    and c['confidence']=='abstain'):
                raise ValueError('Unsupported/unknown qualitative gloss: '+str(key))
            claim='QUALITATIVE_ABSTENTION_NOT_ENTAILMENT_VERIFIED';overclaim='unclear'
            claimed_num='';claimed_year='';phrase='';source_ids=''
            n_qualitative+=1
        rows.append({'year':year,'stable_id':c['stable_id'],'level':c['level'],
            'title':c['v2_label'],'gloss':c['v2_gloss'],
            'member_count':len(members),'eligible_member_count':len(eligible),
            'claimed_year':claimed_year,'primary_phrase':phrase,
            'gloss_numerical_support_count':claimed_num,
            'generator_supporter_count':len(source_ids.split('|')) if source_ids else '',
            'source_support_node_ids':source_ids,'machine_lexical_claim_status':claim,
            'lexical_overclaim_status':overclaim,
            'independent_scientific_overclaim_status':'unclear',
            'label_semantic_status':'AI_DIAGNOSTIC_NOT_INDEPENDENT',
            'audit_scope':'Complete original source-node membership, year and literal phrase count only; NOT full-paper semantic entailment'})
    if (n_literal,n_qualitative)!=(23,1):raise ValueError('Expected 23 literal glosses and one epistemic abstention')
    with (out/'v2_gloss_source_audit_24.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    from math import sqrt
    z=1.959963984540054
    upper=z*z/(n_literal+z*z)
    summary={
        'schema':'ckl_v2_24_claim_scoped_audit_v1','n_selected_v2_glosses':len(rows),
        'n_literal_count_claims':n_literal,'n_qualitative_abstentions':n_qualitative,
        'source_scope_full_member_recounts_verified':n_literal,
        'source_scope_false_literal_claims_found':0,
        'source_scope_limited_overclaim_evaluable_n':n_literal,
        'source_scope_limited_overclaim_rate':0.0,
        'source_scope_limited_overclaim_wilson95_upper':upper,
        'source_scope_limited_overclaim_unclear_n':n_qualitative,
        'full_text_scientific_overclaim_evaluable_n':0,
        'full_text_scientific_overclaim_unclear_n':len(rows),
        'full_text_scientific_overclaim_rate':None,
        'independent_semantic_title_accuracy':None,
        'independent_expert_review':False,
        'audit_caveat':'Literal occurrence counts verified on all frozen member node names and year cutoffs, not just samples. This is NOT independent scientific title/gloss entailment. All 24 full-text semantic overclaim statuses remain UNCLEAR. No human annotation is claimed.'
    }
    (out/'v2_gloss_source_summary_24.json').write_text(
        json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    print('V2 source-literal audit',n_literal,'verified count glosses;',n_qualitative,
          'qualitative unclear; scientific-entailment unclear',len(rows))
    return summary

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--project',default='.')
    ap.add_argument('--out',default='research_outputs/label_v2')
    ap.add_argument('--years',default='2020,2022,2024')
    ap.add_argument('--score-blind',default=None,help='CSV with human A/B judgments; do not set this until actually completed')
    ap.add_argument('--key',default=None,help='Local A/B key kept away from the reviewer')
    ap.add_argument('--summarize-ai',action='store_true',help='Score existing AI-only diagnostic review separately, NOT human ratings')
    ap.add_argument('--recover-key',action='store_true',help='Safely recover frozen A/B mapping into ignored local secret; do not share')
    a=ap.parse_args()
    if a.recover_key:
        recover_frozen_blind_key(a.project, a.key)
        return
    if a.summarize_ai:
        summarize_ai_review(a.project, Path(a.out)/'ai_paired_summary.json')
        return
    if a.score_blind:
        if not a.key:ap.error('--score-blind requires --key')
        score_blind(a.score_blind,a.key,a.out)
        return
    m=write_outputs(a.project,a.out,[int(y) for y in a.years.split(',')])
    for y,row in m['years'].items():print(f'V2 {y}: {row["labels"]} labels; {row["with_abstention"]} abstentions; {row["lexical_source_assertions_checked"]} cited node-name occurrences source-verified')
    print('NO LABEL ADVANTAGE CLAIMED until external blinded evaluation is completed.')

if __name__=='__main__':main()
