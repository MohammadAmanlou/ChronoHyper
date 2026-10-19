"""Generate source-backed selected-model metric registry. No speculative values.
Run from repository root: python scripts/generate_selected_metrics.py
"""
from __future__ import annotations
import csv, json, statistics, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def rows(p):
 with (ROOT/p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def fp(v):
 try:return float(v) if v not in ('',None) else None
 except (ValueError,TypeError):return None
def summarize(p):
 output={}
 for r in rows(p):
  year=str(r['year']);mid=r['model']
  output.setdefault(mid,{})[year]={
    'seed_count':int(r['n_seeds']),
    'heldout_hyperedge_cut_lower_better':fp(r['heldout_normalized_connectivity_lower_better_mean']),
    'heldout_hyperedge_cut_sd_across_seeds':fp(r['heldout_normalized_connectivity_lower_better_sd_over_seeds']),
    'article_title_coherence_proxy_higher_better':fp(r['independent_article_title_view_coherence_higher_better_mean']),
    'temporal_ari_shared_nodes':fp(r['cross_year_shared_node_ari_mean']),
    'runtime_seconds_per_snapshot_mean':fp(r['elapsed_seconds_mean']),
    'n_heldout_source_papers':fp(r['n_heldout_papers_mean']),
  }
 return output
lock=load('research_outputs/model_lock.json')
manifest=load('outputs_selected/selected_export_manifest.json')
assert lock['method']==manifest['locked_method']
assert lock['data_sha256']==manifest['dataset_sha256']
actual=hashlib.sha256((ROOT/'inputs/data.zip').read_bytes()).hexdigest()
assert actual==lock['data_sha256']
dev=summarize('research_outputs/final_matrix/method_summary.csv')
conf=summarize('research_outputs/confirmation/method_summary.csv')
clique=summarize('research_outputs/projection_5seed/method_summary.csv')
assert all(str(y) in conf[lock['method']] for y in lock['years'])
selected=lock['method']
x=dev[selected]['2024']['heldout_hyperedge_cut_lower_better']
y=conf[selected]['2024']['heldout_hyperedge_cut_lower_better']
stress=load('research_outputs/stress_temporal20_extended/result.json')
label=load('outputs_selected/label_review_results.json')
retr=load('outputs_selected/selected_retrieval_EXPLORATORY_2025.json')
randomization_p=stress.get('randomization_p_lower_better')
pert=stress['perturbation_10pct_ARI']
result={
 'schema':'constructor-ckl-selected-v1',
 'status':'SOURCE_BACKED_WORKING_RESULTS_NOT_YET_SCIENTIFICALLY_COMPLETE',
 'original_source_data_sha256':actual,
 'locked_method':selected,
 'frozen_seeds':lock['seeds'],
 'frozen_development_protocol_sha256':lock['development_protocol_sha256'],
 'confirmation_protocol_sha256':manifest['confirmation_protocol_sha256'],
 'snapshot_output_summaries':manifest['snapshot_summaries'],
 'source_grouped_development':dev,
 'source_grouped_confirmation_selected_only':conf,
 'pairwise_projection_development':clique,
 'heldout_cut_2024_selected_dev_vs_confirmation':{
  'development':x,'confirmation':y,'absolute_higher_is_worse':y-x,
  'relative_higher_is_worse':(y-x)/x,
  'important':'Only heldout-cut eval paper set changes; fixed learned assignments yield identical title coherence and temporal ARI. Do not count those as new independent confirmation signals.',
 },
 'stress_selected_2024_seed17':{
  'n_edge_deletion_trials':len(pert),
  'deletion_ari_mean':statistics.mean(pert),
  'deletion_ari_values':pert,
  'null_count':stress['null_count'],
  'randomization_p_lower_better':randomization_p,
  'null_hypothesis_note':'99 degree-and-arity preserving shuffles; no significant superiority at alpha=.05 (observed p>=.05).',
  'source':'research_outputs/stress_temporal20_extended/result.json',
 },
 'label_audit':{
  'n_requested':label['n_requested'],'title_ratings':label['label_ratings'],
  'n_overclaim_determinately_evaluable':label['n_evaluable'],
  'n_overclaim':label['n_overclaim'],
  'n_overclaim_unclear':label['n_unclear'],
  'conditional_overclaim_rate_evaluable_only':label['overclaim_rate'],
  'wilson95_evaluable_only':label['wilson_95_ci'],
  'independent_blind_overclaim_rate':None,
  'honesty':'40/48 gloss judgments unclear; 8 not overclaims among only 8 resolvable, not 0/48 and not independent blind review; 12/48 wrong topic titles and 28/48 vague.',
  'source':'outputs_selected/label_review_results.json',
 },
 'retrieval_exploratory_2025':retr['summary'],
 'source_map':{
  'experiment_registry':'research_outputs/final_matrix/experiment_registry.csv',
  'development_per_method':'research_outputs/final_matrix/method_summary.csv',
  'confirmation_per_seed':'research_outputs/confirmation/all_runs.csv',
  'confirmation_protocol':'research_outputs/confirmation/protocol.json',
  'source_group_split':'research_outputs/confirmation/paper_split.json',
  'pairwise_comparison':'research_outputs/projection_5seed/method_summary.csv',
  'selected_export':'outputs_selected/selected_export_manifest.json',
  'label_worksheet':'outputs_selected/label_review_sheet.csv',
  'label_result':'outputs_selected/label_review_results.json',
 },
 'critical_notes':[
  'Title-source coherence is a related second view; it is NOT a blind external semantic judgement.',
  'The number of papers is small; bootstrap intervals and 5 random seeds do not prove across-corpus generalization.',
  'The training objective is a bounded local heuristic surrogate, not a proven globally optimized objective.',
  'Selected 2025 question evaluation uses already-inspected questions: exploratory only; 4 multi-claim Type B questions unscored.',
  'The displayed score count excludes centroid computations and is NOT a verified latency speedup.',
  'Some source audit and gloss semantic validity remain unresolved; see current report and LABEL_AUDIT_STATUS.md.',
 ],
}
(ROOT/'outputs_selected/metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(ROOT/'metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('SELECTED METRICS GENERATED',selected,'cut dev',x,'conf',y,'p',randomization_p,'label definite',label['n_evaluable'])
