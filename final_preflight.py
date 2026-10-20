#!/usr/bin/env python3
"""Read-only pre-submission audit for Constructor CKL selected research outputs.

Run in applicant's project root:
 python final_preflight.py --project . --write research_outputs/final_preflight.json

Uses only Python standard library. Never modifies research runs, reports, or labels.
"""
import argparse, json, csv, hashlib, statistics
from pathlib import Path

def read(p):
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding='utf-8-sig'))
    except (ValueError, UnicodeError) as e:
        return {'_read_error': str(e)}

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for buf in iter(lambda: stream.read(1<<20),b''):
            h.update(buf)
    return h.hexdigest()

def mean(x):
    return statistics.mean(x) if x else None

def audit(root):
    errors=[];warnings=[];passed=[];details={}
    lock_path=root/'research_outputs/model_lock.json'
    lock=read(lock_path)
    confirm=root/'research_outputs/confirmation'; protocol=read(confirm/'protocol.json')
    man=read(root/'outputs_selected/selected_export_manifest.json')
    if lock is None:errors.append('Model lock missing')
    elif '_read_error' in lock:errors.append('Model lock JSON unreadable: '+lock['_read_error'])
    else:
        details['locked_method']=lock.get('method')
        if lock.get('method')!='native_temporal_20':warnings.append('Selected method not native_temporal_20; verify intentionally')
    if protocol is None:errors.append('Confirmation protocol missing')
    elif '_read_error' in protocol:errors.append('Confirmation protocol unreadable')
    if isinstance(lock,dict) and isinstance(protocol,dict) and '_read_error' not in protocol:
        if protocol.get('method_ids')!=[lock.get('method')]:errors.append('Confirmation model differs from frozen selection')
        if protocol.get('seeds')!=lock.get('seeds') or protocol.get('years')!=lock.get('years'):errors.append('Confirmation seed/year protocol differs from lock')
        if protocol.get('selection_lock')!=digest(lock_path):errors.append('Confirmation uses different selection lock content')
        input_path=root/'inputs/data.zip'
        if not input_path.is_file():errors.append('Original data.zip missing')
        elif digest(input_path)!=lock.get('data_sha256'):errors.append('Original data fingerprint does not match lock')
        else:passed.append('Original data hash equals frozen lock')
    elif not (root/'inputs/data.zip').exists():errors.append('Original dataset missing')
    if not isinstance(man,dict) or '_read_error' in man:
        errors.append('Selected export manifest missing or unreadable')
    else:
        if isinstance(lock,dict) and man.get('locked_method')!=lock.get('method'):errors.append('Selected hierarchy model differs from lock')
        if (root/'inputs/data.zip').is_file() and man.get('dataset_sha256')!=digest(root/'inputs/data.zip'):errors.append('Selected output built from different dataset')
        if (root/'research_outputs/model_lock.json').is_file() and man.get('lock_sha256')!=digest(lock_path):errors.append('Selected output built using another lock')
        missing=[]
        for year in ['2020','2022','2024']:
            for f in [f'hierarchy_{year}.json',f'collapsed_edges_{year}_level0.json',f'label_evidence_{year}.json']:
                if not (root/'outputs_selected'/f).is_file():missing.append(f)
        if missing:errors.append('Missing selected outputs: '+', '.join(missing))
        elif (root/'outputs_selected/temporal_events.json').is_file():passed.append('Selected 3-year hierarchies, collapsed edges, labels, temporal events present')
        else:errors.append('Temporal events missing')
        details['selected_snapshots']=man.get('snapshot_summaries')
        if not (root/'outputs_selected/hierarchy_2025.json').exists():warnings.append('Optional exploratory 2025 snapshot absent')
    if not (root/'research_outputs/final_matrix/experiment_registry.csv').exists():warnings.append('Development experiment registry absent')
    if not (root/'research_outputs/projection_5seed/experiment_registry.csv').exists():warnings.append('Five-seed pairwise experiment registry absent')
    if not (root/'research_outputs/final_matrix/paired_paper_bootstrap.csv').exists():warnings.append('Paired paper bootstrap comparison absent')
    method=lock.get('method') if isinstance(lock,dict) else 'native_temporal_20'
    seeds=lock.get('seeds',[]) if isinstance(lock,dict) else [11,17,29,41,53]
    details['per_seed_comparison_2024']=[]
    dev_vals=[];conf_vals=[]
    for seed in seeds:
        rid=f'{method}__seed{seed}'
        dt=read(root/'research_outputs/final_matrix/runs'/rid/'metrics_2024.json')
        ct=read(confirm/'runs'/rid/'metrics_2024.json')
        status=read(confirm/'runs'/rid/'status.json')
        if dt is None or ct is None:errors.append(f'Missing development or confirmation metrics for {rid}') ;continue
        if status is None or status.get('status')!='complete':errors.append(f'Confirmation {rid} is not complete');continue
        if '_read_error' in dt or '_read_error' in ct:errors.append(f'Malformed numerical output for {rid}');continue
        dv=dt.get('heldout_normalized_connectivity_lower_better');cv=ct.get('heldout_normalized_connectivity_lower_better')
        if dv is not None and cv is not None:dev_vals.append(float(dv));conf_vals.append(float(cv))
        details['per_seed_comparison_2024'].append({'seed':seed,'development_cut':dv,'confirmation_cut':cv,'confirmation_minus_development':cv-dv if dv is not None and cv is not None else None,'development_n_heldout_papers':dt.get('n_heldout_papers'),'confirmation_n_heldout_papers':ct.get('n_heldout_papers'),'title_view_identical':dt.get('independent_article_title_view_coherence_higher_better')==ct.get('independent_article_title_view_coherence_higher_better'),'temporal_ari_identical':dt.get('cross_year_shared_node_ari')==ct.get('cross_year_shared_node_ari')})
    if len(details['per_seed_comparison_2024'])==len(seeds):passed.append('All five development-vs-confirmation pair records available')
    details['development_2024_mean_cut']=mean(dev_vals)
    details['confirmation_2024_mean_cut']=mean(conf_vals)
    details['confirmation_minus_development_2024_mean_cut']=(mean(conf_vals)-mean(dev_vals)) if dev_vals and conf_vals else None
    if details['confirmation_minus_development_2024_mean_cut'] is not None and details['confirmation_minus_development_2024_mean_cut']>0:
        warnings.append('Heldout cut worsens from development to confirmation; report gap (DO NOT call independent gain)')
    details['label_audit']=read(root/'outputs_selected/label_review_results.json')
    la=details['label_audit']
    if not isinstance(la,dict) or '_read_error' in la:errors.append('Human label faithfulness audit results missing')
    elif la.get('n_evaluable',0)==0:errors.append('Zero independently evaluated label glosses: overclaim rate UNMEASURED (0 / 48 is NOT 0%)')
    elif la.get('n_evaluable',0)<la.get('n_requested',48):warnings.append(f'Only {la["n_evaluable"]}/{la.get("n_requested",48)} label glosses evaluated; report partial annotation')
    else:passed.append('All 48 label audit overclaim judgments present (verify ratings and reviewer independence manually)')
    if isinstance(la,dict) and la.get('status')=='PARTIAL_AI_ASSISTED_DIAGNOSTIC':
        warnings.append('48-case label audit is ChatGPT AI-assisted and non-blind, NOT independent human label validation; 40 of 48 gloss overclaims remain unclear')
        details['independent_label_review_verified']=False
    if isinstance(la,dict) and la.get('status')=='HUMAN_ANNOTATED':
        sheet=root/'outputs_selected/label_review_sheet.csv'
        try:
            rows=list(csv.DictReader(sheet.open(encoding='utf-8-sig',newline='')))
            missing_rating=[i+2 for i,r in enumerate(rows) if r.get('label_rating_accurate_vague_wrong') not in ('accurate','vague','wrong') or r.get('adequate_evidence_yes_no') not in ('yes','no') or not r.get('reviewer_id','').strip()]
            if missing_rating:errors.append(f'Label audit may claim HUMAN_ANNOTATED while {len(missing_rating)} rating/evidence/reviewer rows incomplete')
            else:passed.append('All annotation columns and reviewer IDs present')
        except Exception as e:errors.append('Cannot recheck human audit CSV: '+str(e))
    retrieval=read(root/'outputs_selected/selected_retrieval_EXPLORATORY_2025.json')
    if isinstance(retrieval,dict) and 'summary' in retrieval:
        details['retrieval_2025_exploratory']=retrieval['summary']
        if retrieval['summary'].get('type_B_not_scored',0)>0:
            type_b=read(root/'research_outputs/type_b_audit/type_b_source_scores.json')
            if isinstance(type_b,dict) and type_b.get('n_type_b')==4 and type_b.get('claim_answer_accuracy_measured') is False:
                details['type_b_source_retrieval_exploratory']=type_b.get('summary')
                passed.append('Type-B paper-source retrieval scored for four questions (answer accuracy NOT evaluated)')
                warnings.append('Type-B claim-answer correctness and full-text entailment are UNMEASURED; do not confuse source retrieval with answer accuracy')
            else:
                warnings.append('Type-B question source and answer evaluations have not been completed')
        warnings.append('Original benchmark questions previously inspected: 2025 retrieval is EXPLORATORY, not an unseen test')
    else:warnings.append('No optional 2025 retrieval result; still need an extrinsic-task score')
    # Modern independently scoped evidence is recorded SEPARATELY from older AI-only audits.
    # Its presence does not turn subjective assessments into scientific full-text validation.
    projection=read(root/'research_outputs/projection_loss/projection_loss.json')
    if isinstance(projection,dict) and '_read_error' not in projection:
        pg=projection.get('global',{})
        if (pg.get('native_events')!=1429 or pg.get('higher_order_events_arity_at_least_3')!=1150
                or pg.get('clique_pair_occurrences')!=72701 or pg.get('simple_unique_pairs')!=70022):
            errors.append('Pairwise projection audit counts differ from frozen original corpus')
        elif isinstance(lock,dict) and projection.get('dataset_sha256')!=lock.get('data_sha256'):
            errors.append('Pairwise projection audit dataset fingerprint differs from lock')
        else:
            passed.append('Original 1429 hyperedges and 72701 clique-pair occurrences are source-audited')
            details['projection_counts']=pg
    else:
        warnings.append('New original-data pairwise representation audit missing or unreadable')
    v2_scoped=read(root/'research_outputs/label_v2/v2_gloss_source_summary_24.json')
    if isinstance(v2_scoped,dict) and v2_scoped.get('n_literal_count_claims')==23:
        details['v2_scoped_claim_audit']={k:v2_scoped.get(k) for k in (
            'n_literal_count_claims','n_qualitative_abstentions',
            'source_scope_false_literal_claims_found',
            'full_text_scientific_overclaim_evaluable_n',
            'full_text_scientific_overclaim_unclear_n')}
        passed.append('23/23 frozen V2 literal source-name counts verified; 1 abstention')
        warnings.append('This literal count audit is NOT independent scientific full-paper gloss entailment')
    else: warnings.append('Scoped 24-case V2 source-count audit missing')
    ai=read(root/'research_outputs/fresh_semantic/summary_AI_only.json')
    if isinstance(ai,dict) and isinstance(ai.get('summary'),dict):
        s=ai['summary']
        if (s.get('n_matched_pairs')!=24 or s.get('evaluable_pairs')!=24
                or s.get('real_higher_pairs',0)+s.get('control_higher_pairs',0)+s.get('ties',0)!=24):
            errors.append('Fresh AI coherence aggregate has inconsistent paired sample counts')
        else:
            passed.append('Fresh 24-pair AI-only coherence aggregate internally consistent')
            details['fresh_ai_coherence_scoped']={
                'model_ids':ai.get('reviewer_model_identifiers_as_supplied'),
                'mean_paired_delta':s.get('mean_paired_delta'),
                'exact_unadjusted_p_descriptive':s.get('exact_sign_p_descriptive_only'),
                'strict_independence_verified_by_software':ai.get('strict_independence_verified_by_software'),
                'independent_full_paper_entailment_verified':ai.get('paper_full_text_verified')}
            if ai.get('strict_independence_verified_by_software') is not False or ai.get('paper_full_text_verified') is not False:
                errors.append('AI study must not be promoted as independently verified full-paper entailment')
            else:
                warnings.append('Fresh AI-only name/paper-title coherence (unadjusted p=0.049) is NOT full-paper independent verification')
    else:warnings.append('Fresh 24-pair AI-only coherence aggregate absent')
    if (root/'research_lab/label_v3.py').exists():
        passed.append('General experimental V3 labeller implementation present (180 development cases)')
        warnings.append('V3 semantic-title accuracy unmeasured on genuinely new independently checked cases')
    local_v3=read(root/'local_only/label_v3_dev/provenance_audit.json')
    if isinstance(local_v3,dict):
        full_counts=local_v3.get('by_status',{})
        valid_v3=(local_v3.get('schema')=='chronohyper_v3_full_provenance_audit_v1'
                  and local_v3.get('n_labels_checked')==180
                  and sum(full_counts.values())==180
                  and local_v3.get('structural_and_lexical_errors')==0
                  and local_v3.get('gold_answer_files_opened') is False
                  and local_v3.get('independent_semantic_label_accuracy') is None
                  and local_v3.get('scientific_overclaim_rate') is None)
        if valid_v3:
            passed.append('Applicant local audit reports all 180 V3 source-name/provenance cases checked; scientific entailment remains unmeasured')
            details['v3_full_member_lexical_audit']={k:local_v3.get(k) for k in
                ('n_labels_checked','n_explicit_abstentions',
                 'full_member_name_phrase_support_occurrences_checked',
                 'dated_article_provenance_references_checked',
                 'independent_semantic_label_accuracy')}
        else:
            errors.append('Local V3 audit has inconsistent status/evidence counts; rerun or investigate')
    else:
        warnings.append('Full 180-case V3 lexical/provenance audit not yet generated locally')
    retr_new=read(root/'research_outputs/retrieval_v2/dev_diagnostic_2025.json')
    if isinstance(retr_new,dict):
        if retr_new.get('n_queries')!=14:
            errors.append('Development retrieval diagnostic query count unexpectedly changed')
        else:
            details['new_retrieval_development_only']={k:retr_new.get(k) for k in
                ('flat_hit_at_5','hier_hit_at_5','mean_flat_candidate_dots',
                 'mean_hier_candidate_dots','mean_flat_score_ms',
                 'mean_hier_score_ms_including_routing')}
            passed.append('Gold-separated shared-scoring retrieval development diagnostic present')
            warnings.append('New routed retrieval has no confirmed fresh-query Hit@5 advantage (2/14 each on reused questions)')
    else:warnings.append('New fair retrieval development diagnostic missing')
    postlock_ai=read(root/'local_only/review_status/summary.json')
    if isinstance(postlock_ai,dict):
        p=postlock_ai.get('v2_v3',{})
        c=postlock_ai.get('coherence_matched',{})
        if (postlock_ai.get('schema')!='chronohyper_postlock_ai_review_status_v1' or
                postlock_ai.get('independent_full_paper_entailment_verified') is not False or
                postlock_ai.get('independent_human_expert_review_verified') is not False or
                p.get('total_pairs')!=24 or not isinstance(p.get('evaluable_pairs'),int) or
                not 0 <= p.get('evaluable_pairs') <= 24 or
                c.get('total_pairs')!=24 or not isinstance(c.get('evaluable_pairs'),int) or
                not 0 <= c.get('evaluable_pairs') <= 24):
            errors.append('Local post-lock AI review status invalid; check source JSON and rating-sheet hashes')
        else:
            passed.append('Post-lock 24-pair label and 24-pair AI-only coherence summaries are arithmetically audited')
            details['postlock_ai_review_scoped']={
                'label_v3_wins':p.get('v3_wins'),
                'label_v3_losses':p.get('v3_losses'),
                'label_ties':p.get('ties'),
                'label_sign_p_unadjusted':p.get('descriptive_unadjusted_sign_p'),
                'coherence_delta':c.get('mean_paired_delta'),
                'coherence_sign_p_unadjusted':c.get('descriptive_unadjusted_sign_p'),
                'human_expert_verified':False,
                'fullpaper_entailment_verified':False,
            }
            warnings.append('Post-lock key-separated AI review is SAME-CORPUS, name/title-only; scientific overclaim and full-paper entailment are not independently verified')
    else:
        warnings.append('No local post-lock AI-only score audit; not a canonical deliverable')
    stress=read(root/'research_outputs/stress_temporal20_extended/result.json')
    if stress is None:
        # documented prior path
        stress=read(root/f'research_outputs/final_matrix/stress/{method}__seed17__2024/result.json')
    if isinstance(stress,dict) and '_read_error' not in stress:details['stress_result_raw']=stress
    else:warnings.append('Selected method stress result not found; include stress directory in hand-in')
    for path in ['report.pdf','report.md','README.md','AI_USAGE.md','requirements.txt']:
        if not (root/path).exists():errors.append('Missing required deliverable: '+path)
    if (root/'report.pdf').exists() and (root/'outputs_selected/selected_export_manifest.json').exists():
        manuscript=(root/'report.md').read_text(encoding='utf-8', errors='replace') if (root/'report.md').exists() else ''
        if method in manuscript and 'confirmation' in manuscript.lower():
            passed.append('Working report.md refers to selected locked method and source-grouped confirmation')
            warnings.append('Manually verify that report.pdf renders the current report.md; this preflight does not parse PDFs')
        else:
            warnings.append('report.md may be STALE: missing locked method or confirmation discussion; regenerate before employer delivery')
    details['read_only']=True
    details['scientific_boundary']='Read-only structural/evidence audit. Does not check scientific novelty, accuracy of reviewer judgments, code correctness, confidence interval construction, PDF page count, or truthful literature reading.'
    return {'ready_for_submission_without_caveat':len(errors)==0 and len(warnings)==0,'blocking_items':errors,'qualifications':warnings,'checks_passed':passed,'details':details}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--project',default='.')
    ap.add_argument('--write',default='research_outputs/final_preflight.json')
    args=ap.parse_args()
    root=Path(args.project).resolve()
    result=audit(root)
    for name,tag in [('checks_passed','PASS'),('blocking_items','BLOCK'),('qualifications','WARN')]:
        for msg in result[name]:print(tag,msg)
    dst=root/args.write
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(result,indent=2,ensure_ascii=False,default=str),encoding='utf-8')
    print('PREFLIGHT:', 'PASS' if result['ready_for_submission_without_caveat'] else 'ACTION REQUIRED', 'saved',dst)
    # Exit 0 to allow user to inspect even when scientific work is incomplete.
if __name__=='__main__':main()
