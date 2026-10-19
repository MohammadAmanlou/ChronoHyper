"""Source-grounded HUMAN audit worklist and scorer. Does NOT make up ratings.
Generate: python upgrade_scripts/label_audit.py make --project .
Score filled-in CSV: python upgrade_scripts/label_audit.py score --file ...
Annotator must be independent of model building to justify 'blind'; otherwise disclose nonblind.
"""
from pathlib import Path
from collections import defaultdict
import argparse,csv,json,math,random,sys
sys.path.insert(0, str(Path.cwd().resolve()))

OUT='outputs/label_review_sheet.csv'
FIELDS=['snapshot','level','stable_id','label','gloss','cluster_member_count','evidence_node_ids','evidence_node_texts',
        'random_member_node_ids','random_member_texts','source_article_titles','label_rating_accurate_vague_wrong',
        'gloss_overclaim_yes_no_unclear','adequate_evidence_yes_no','reviewer_id','review_notes']

def make(project,out,seed=807):
    from src.t1_audit import parse_archive
    root=Path(project)
    graph,articles,_,_=parse_archive(str(root/'inputs/data.zip'))
    lookup={n['id']:n for n in graph['nodes']};article_lookup={str(a['id']):a for a in articles}
    selected=[]
    rng=random.Random(seed)
    for year in [2022,2024]:
        hierarchy=json.loads((root/f'outputs/hierarchy_{year}.json').read_text(encoding='utf-8'))
        level0=[s for s in hierarchy['supernodes'] if s['level']==0]
        level1=[s for s in hierarchy['supernodes'] if s['level']==1]
        assert len(level0)==12
        selected.extend([(year,s) for s in level0])
        if year==2024:selected.extend([(year,s) for s in rng.sample(sorted(level1,key=lambda x:x['id']),min(24,len(level1)))])
    rows=[]
    for year,s in selected:
        ids=s['member_ids']
        raw_sources=json.loads((root/f'outputs/label_evidence_{year}.json').read_text(encoding='utf-8'))
        ev=raw_sources.get(s['id'],{})
        evidence_ids=ev.get('evidence',{}).get('source_node_ids',[])[:8]
        rest=[x for x in ids if x not in evidence_ids]
        sample=rng.sample(rest,min(12,len(rest)))
        citing=set()
        for nid in evidence_ids+sample:
            citing.update(str(a) for a in lookup[nid].get('provenance',{}).get('articles',[]))
        citations=[article_lookup[a]['title'] for a in sorted(citing) if a in article_lookup and int(article_lookup[a]['year'])<=year]
        rows.append(dict(snapshot=year,level=s['level'],stable_id=s['id'],label=s['label'],gloss=s['gloss'],
            cluster_member_count=len(ids),evidence_node_ids=' | '.join(evidence_ids),
            evidence_node_texts=' | '.join(lookup[nid]['surface_form'] for nid in evidence_ids),
            random_member_node_ids=' | '.join(sample),
            random_member_texts=' | '.join(lookup[nid]['surface_form'] for nid in sample),
            source_article_titles=' | '.join(citations[:8]),
            label_rating_accurate_vague_wrong='',gloss_overclaim_yes_no_unclear='',
            adequate_evidence_yes_no='',reviewer_id='',review_notes=''))
    target=root/out;target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('w',newline='',encoding='utf-8-sig') as fp:
        w=csv.DictWriter(fp,FIELDS);w.writeheader();w.writerows(rows)
    print('CREATED',target,'rows',len(rows),'0 human labels completed')
    return rows

def score(file):
    path=Path(file)
    with path.open(newline='',encoding='utf-8-sig') as fp: rows=list(csv.DictReader(fp))
    evaluated=[r for r in rows if r['gloss_overclaim_yes_no_unclear'].strip().lower() in ('yes','no')]
    unsupported=[r for r in evaluated if r['gloss_overclaim_yes_no_unclear'].strip().lower()=='yes']
    n=len(evaluated);k=len(unsupported)
    p=k/n if n else None
    if n:
        z=1.96; den=1+z*z/n;center=(p+z*z/(2*n))/den
        span=z*math.sqrt((p*(1-p)+z*z/(4*n))/n)/den
        ci=[max(0.,center-span),min(1.,center+span)]
    else:ci=[None,None]
    statuses={cat:sum(r['label_rating_accurate_vague_wrong'].strip().lower()==cat for r in rows) for cat in ['accurate','vague','wrong']}
    result={'n_requested':len(rows),'n_evaluable':n,'n_overclaim':k,'overclaim_rate':p,'wilson_95_ci':ci,
            'n_unclear':sum(r['gloss_overclaim_yes_no_unclear'].strip().lower()=='unclear' for r in rows),
            'n_missing':len(rows)-n-sum(r['gloss_overclaim_yes_no_unclear'].strip().lower()=='unclear' for r in rows),
            'label_ratings':statuses,'status':'HUMAN_ANNOTATED' if n==len(rows) else 'PARTIAL_HUMAN_ANNOTATION',
            'note':'Reviewer identity, independence and visibility to algorithm must be reported truthfully; Wilson CI measures annotation sample only, not paper-level uncertainty.'}
    outfile=path.with_name('label_review_results.json')
    outfile.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2));print('RESULTS',outfile)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['make','score']);ap.add_argument('--project',default='.');ap.add_argument('--out',default=OUT);ap.add_argument('--file',default=OUT);a=ap.parse_args()
    if a.mode=='make':make(a.project,a.out)
    else:score(a.file)
