#!/usr/bin/env python3
"""NON-INVASIVE export of the *locked, confirmed* top-level method to complete P1/P2/P4/T3/T5 hierarchy.

Input MUST be a real applicant-produced confirmation run; this does not rerun or change
model selection, does not consult benchmark questions/gold and does not create a final
report. Output is a separate folder and is never advertised as independently validated
scientific claim. Run from project root:
 python export_locked_full_hierarchy.py --lock research_outputs/model_lock.json --confirmation research_outputs/confirmation --seed 17 --out outputs_selected
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from src.run import snapshot_raw,semantic_embeddings,group_id_map,hierarchy_records,write_json
from src.core import fit_hierarchy,check_laminar,collapse_all
from src.labeling import generate_levels,support_audit
from research_lab.experiment_suite import IDS,_fit,hash_file,parse_science_only_zip


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--lock',default='research_outputs/model_lock.json')
    p.add_argument('--confirmation',default='research_outputs/confirmation')
    p.add_argument('--data',default='inputs/data.zip')
    p.add_argument('--seed',type=int,default=17)
    p.add_argument('--out',default='outputs_selected')
    p.add_argument('--with-2025',action='store_true',help='Optional exploratory 2025 hierarchical retrieval on previously inspected gold questions')
    a=p.parse_args()
    lock=json.loads(Path(a.lock).read_text(encoding='utf-8'))
    conf=Path(a.confirmation)
    protocol=json.loads((conf/'protocol.json').read_text(encoding='utf-8'))
    split=json.loads((conf/'paper_split.json').read_text(encoding='utf-8'))
    model=lock['method']
    if model not in IDS or model!=protocol['method_ids'][0] or protocol['evaluation_stage']!='confirmation':
        raise ValueError('Not a locked single-model confirmatory protocol')
    if protocol['years']!=lock['years'] or protocol['seeds']!=lock['seeds']:
        raise ValueError('Confirmation snapshots/seeds disagree with original lock')
    if a.seed not in lock['seeds']:
        raise ValueError('Seed was not in frozen protocol; cannot cherry-pick unrecorded seed')
    if hash_file(a.data)!=lock['data_sha256'] or protocol['data_sha256']!=lock['data_sha256']:
        raise ValueError('Original input checksum is inconsistent')
    if protocol['selection_lock']!=hash_file(a.lock):
        raise ValueError('Confirmation protocol does not match frozen lock file')
    rid=f'{model}__seed{a.seed}'
    source=conf/'runs'/rid
    status=json.loads((source/'status.json').read_text(encoding='utf-8'))
    if status.get('status')!='complete':
        raise ValueError('Selected confirmatory seed does not have a COMPLETE fit')
    learned=json.loads((source/'assignments.json').read_text(encoding='utf-8'))
    years=list(protocol['years'])
    graph,articles=parse_science_only_zip(a.data)  # This module does not access benchmark gold for fitting
    export_years=years+([2025] if a.with_2025 else [])
    snaps={str(y):snapshot_raw(graph,y) for y in export_years}
    embeddings,_=semantic_embeddings(snaps,seed=protocol['embedding_seed'])
    excluded=set(split['paper_ids_heldout_of_all_model_fitting'])
    out=Path(a.out)
    if out.exists() and list(out.iterdir()):
        raise ValueError('Output is nonempty: use a NEW output directory; do not overwrite earlier experiment results')
    out.mkdir(parents=True,exist_ok=True)
    prev_levels=prev_ids=None
    serial=0
    event_log=[]
    summaries={}
    for y in export_years:
        snap=snaps[str(y)]
        nodes=snap['nodes'];node_ids=[n['id'] for n in nodes]
        X=embeddings[str(y)]
        train=[e for e in snap['hyperedges'] if str(e.get('provenance',{}).get('article_id','unknown')) not in excluded]
        if y in years:
            top=learned[str(y)]
        else:
            # Optional extra snapshot; model ID and fitting protocol are locked, but this
            # prediction is NOT part of the confirmation claim.
            previous_assignment=learned[str(years[-1])]
            fitted,_=_fit(node_ids,X,train,IDS[model],a.seed,previous_assignment)
            top=dict(zip(node_ids,map(int,fitted)))
        if set(top)!=set(node_ids):
            raise AssertionError('Confirmed top-level assignment does not cover exactly snapshot nodes')
        # The exact assignments from the locked confirmation run are re-used, NOT re-fitted.
        top_array=np.asarray([int(top[x]) for x in node_ids],dtype=int)
        levels=fit_hierarchy(nodes,train,X,top_array,seed=a.seed)
        check_laminar(levels,node_ids)
        pids,events,matches,serial=group_id_map(levels,prev_levels,prev_ids,serial,y)
        event_log.extend([{'snapshot':y,**ev} for ev in events])
        prefixed=[{g:'L'+str(l)+'_'+s for g,s in imap.items()} for l,imap in enumerate(pids[:3])]
        labels,evidence=generate_levels(nodes,levels,y,prefixed)
        audited=support_audit(evidence,nodes,levels,prefixed)
        records=hierarchy_records(nodes,levels,pids,labels,y)
        collapse=collapse_all(train,levels[0])
        assert len(collapse)==len(train)
        assert all(sum(v['multiplicity'].values())==v['original_arity'] for v in collapse)
        write_json(out/f'hierarchy_{y}.json',{'cutoff':y,'levels':[{'level':l,'n_clusters':len(set(part.values()))} for l,part in enumerate(levels)],'supernodes':records})
        write_json(out/f'collapsed_edges_{y}_level0.json',collapse)
        write_json(out/f'label_evidence_{y}.json',evidence)
        summaries[str(y)]={'nodes':len(node_ids),'train_edges':len(train),'top_clusters':len(set(top_array.tolist())),
                            'clusters_per_level':[len(set(part.values())) for part in levels],
                            'automatic_label_audit':audited,'confirmed_assignment_identical':True}
        print('SELECTED HIERARCHY',y,'nodes',len(node_ids),'cluster sizes',summaries[str(y)]['clusters_per_level'],flush=True)
        prev_levels=levels;prev_ids=pids
        if y==2025:
            from src.t1_audit import parse_archive
            from src.retrieval import evaluate_retrieval
            _,_,questions,gold=parse_archive(a.data)
            ret=evaluate_retrieval(nodes,train,articles,questions,gold,levels[0])
            write_json(out/'selected_retrieval_EXPLORATORY_2025.json',ret)
            print('EXPLORATORY known-question retrieval',ret['summary'],flush=True)
    write_json(out/'temporal_events.json',{'events':event_log,'attribution':'overlap-based heuristic, not independently verified scientific events'})
    write_json(out/'selected_export_manifest.json',{'locked_method':model,'confirmation_run_id':rid,
          'confirmation_protocol_sha256':hash_file(conf/'protocol.json'),
          'lock_sha256':hash_file(a.lock),'dataset_sha256':hash_file(a.data),
          'paper_ids_excluded_from_training':sorted(excluded),
          'splits':{'development':split['paper_ids_for_development'], 'confirmation':split['paper_ids_reserved_for_confirmation']},
          'snapshot_summaries':summaries,
          'extra_2025_status':'exploratory model prediction and known-question evaluation, NOT confirmation' if a.with_2025 else 'not requested',
          'honesty':'Reuses CONFIRMATION top-level assignments but fine-grained hierarchies/labels are generated afterward. This output is NOT independently expert-annotated, has NO retriever result or fully final 3-5pp report; report only verified claims. Original author semantic overclaim is NOT_EVALUATED.'})
    print('EXPORT COMPLETE',out,'method',model,'seed',a.seed,flush=True)

if __name__=='__main__':main()
