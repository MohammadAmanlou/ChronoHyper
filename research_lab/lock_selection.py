#!/usr/bin/env python3
"""Freeze ONE development-selected method before a confirmatory evaluation.
Makes no scientific claim and never reads reference answers.
"""
import argparse,json,hashlib
from pathlib import Path
from research_lab.experiment_suite import IDS,hash_file

def main():
 p=argparse.ArgumentParser();p.add_argument('--development',default='research_outputs/development')
 p.add_argument('--method',required=True,choices=list(IDS));p.add_argument('--out',default='research_outputs/model_lock.json')
 args=p.parse_args();base=Path(args.development);prot=json.loads((base/'protocol.json').read_text(encoding='utf-8'))
 if prot.get('evaluation_stage')!='development':p.error('Input must be DEVELOPMENT experiment outputs')
 if args.method not in prot['method_ids']:p.error('Method not found in predeclared development protocol')
 for seed in prot['seeds']:
  sp=base/'runs'/f'{args.method}__seed{seed}'/'status.json'
  if not sp.exists() or json.loads(sp.read_text(encoding='utf-8')).get('status')!='complete':
   p.error('Candidate method incomplete for seed '+str(seed))
 lock={'method':args.method,'years':prot['years'],'seeds':prot['seeds'],
       'data_sha256':prot['data_sha256'],'development_protocol_sha256':hash_file(base/'protocol.json'),
       'method_description':IDS[args.method].explanation,
       'frozen_by':'Applicant chooses ONE method using dev evidence, no use of reference gold; author must explain decision.',
       'confirmation_caveat':'Transductive source node text exists and 52 articles overall; report as restricted source-grouped confirmation, not unseen corpus generalization.'}
 out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
 if out.exists():p.error('Lock already exists; preserve original selection and do not silently overwrite')
 out.write_text(json.dumps(lock,indent=2,ensure_ascii=False),encoding='utf-8');print('LOCKED',args.method,out)
if __name__=='__main__':main()
