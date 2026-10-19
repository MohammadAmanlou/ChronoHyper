"""Read-only invariants for research-selected full multi-resolution exported data."""
import argparse,json
from collections import defaultdict
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',default='outputs_selected');a=p.parse_args()
 out=Path(a.out)
 man=json.loads((out/'selected_export_manifest.json').read_text(encoding='utf-8'))
 e=json.loads((out/'temporal_events.json').read_text(encoding='utf-8'))
 valid={'birth','growth','merge','split','death'}
 assert e['events'] and {x['event'] for x in e['events']}<=valid
 for year in sorted(map(int,man['snapshot_summaries'])):
  y=str(year)
  j=json.loads((out/f'hierarchy_{year}.json').read_text(encoding='utf-8'))
  cols=json.loads((out/f'collapsed_edges_{year}_level0.json').read_text(encoding='utf-8'))
  ev=json.loads((out/f'label_evidence_{year}.json').read_text(encoding='utf-8'))
  lv=defaultdict(list)
  for x in j['supernodes']:
   lv[x['level']].append(x)
   assert x['label'] and x['gloss'] and x['member_ids']
  assert len(lv)==4
  sizes=[len(lv[i]) for i in range(4)]
  assert sizes==man['snapshot_summaries'][y]['clusters_per_level']
  assert sizes[0]<=12 and sizes[1]<=48 and sizes[2]<=144
  assert all(len(a['member_ids'])==1 for a in lv[3])
  universe={a['member_ids'][0] for a in lv[3]}
  assert len(universe)==sizes[3]
  for level in range(4):
   members=[nid for group in lv[level] for nid in group['member_ids']]
   assert len(members)==len(universe) and set(members)==universe
   if level:
    parents={x['id']:set(x['member_ids']) for x in lv[level-1]}
    assert all((a['parent_id'] in parents and set(a['member_ids'])<=parents[a['parent_id']]) for a in lv[level])
  assert len(cols)==man['snapshot_summaries'][y]['train_edges']
  assert len(set(x['id'] for x in cols))==len(cols)
  for x in cols:
   assert sum(x['multiplicity'].values())==x['original_arity']
   assert set(map(int,x['multiplicity']))==set(x['coarse_members'])
  assert len(ev)==sizes[0]+sizes[1]
  assert man['snapshot_summaries'][y]['confirmed_assignment_identical']
  print('PASS',year,'nodes',len(universe),'levels',sizes,'events',len(cols))
 print('SELECTED-HIERARCHY CHECK PASSED (structural and evidence-presence invariants, NOT scientific correctness)')

if __name__=='__main__':main()
