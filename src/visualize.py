"""Optional static visual evidence; never used to fit cluster assignments."""
from pathlib import Path
import json
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def generate(out='outputs'):
    out=Path(out)
    ranks=[]
    for yr in [2020,2022,2024]:
        obj=json.loads((out/f'hierarchy_{yr}.json').read_text(encoding='utf-8'))
        ranks.append((yr,obj['supernodes']))
    # Multi-year stable-identity trajectories show count for the six largest 2024 top-level groups
    top2024=[x for x in ranks[2][1] if x['level']==0]
    pick=sorted(top2024,key=lambda x:-len(x['member_ids']))[:6]
    fig,ax=plt.subplots(figsize=(10.7,5.3))
    for concept in pick:
        values=[]
        for yr,objs in ranks:
            match=next((x for x in objs if x['level']==0 and x['id']==concept['id']),None)
            values.append(len(match['member_ids']) if match else 0)
        ax.plot([2020,2022,2024],values,marker='o',label=concept['label'][:35])
    ax.set_xticks([2020,2022,2024]);ax.set_xlabel('Evidence cutoff');ax.set_ylabel('Number of member nodes');ax.set_title('Tracked macro-concept identity and growth (largest six at 2024)')
    ax.grid(alpha=.2);ax.legend(fontsize=8,frameon=False,bbox_to_anchor=(1.02,1),loc='upper left')
    fig.tight_layout();fig.savefig(out/'fig_stable_concept_trajectories.png',dpi=190,bbox_inches='tight');plt.close(fig)
    # Two-level excerpt of REAL nested hierarchy, not a schematic.
    root=max(top2024,key=lambda x:len(x['member_ids']))
    children=[x for x in ranks[2][1] if x['level']==1 and x['parent_id']==root['id']]
    grandchildren=[x for x in ranks[2][1] if x['level']==2 and x['parent_id'] in {c['id'] for c in children}]
    fig,ax=plt.subplots(figsize=(11.2,6.0));ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
    ax.text(.5,.93,f"2024 hierarchy excerpt: {root['label']} (n={len(root['member_ids'])})",ha='center',va='center',fontsize=14,fontweight='bold',bbox=dict(boxstyle='round',facecolor='#e5f0f6',edgecolor='#7395a5'))
    xco=np.linspace(.13,.87,len(children))
    for i,(child,x) in enumerate(zip(children,xco)):
        ax.plot([.5,x],[.89,.73],linewidth=1.3,color='#7a8793')
        ax.text(x,.67,child['label'][:29]+'\n'+str(len(child['member_ids']))+' nodes',ha='center',va='center',fontsize=8.5,bbox=dict(boxstyle='round',facecolor='#edf6ee',edgecolor='#78a58a'))
        sub=[g for g in grandchildren if g['parent_id']==child['id']]
        xx=np.linspace(x-.08,x+.08,len(sub)) if sub else []
        for leaf,dx in zip(sub,xx):
            ax.plot([x,dx],[.59,.41],linewidth=1,color='#9b9b9b')
            ax.text(dx,.32,leaf['label'][:18]+'\n'+str(len(leaf['member_ids'])),ha='center',va='center',fontsize=7.3,rotation=35,
                    bbox=dict(boxstyle='round',facecolor='#fcfaf1',edgecolor='#a99f86'))
    ax.text(.5,.07,'One observed parent and its actual children in the 2024 evidence slice; not an invented example.',ha='center',fontsize=9)
    fig.tight_layout();fig.savefig(out/'fig_real_nested_hierarchy.png',dpi=180,bbox_inches='tight');plt.close(fig)

if __name__=='__main__':import sys;generate(sys.argv[1] if len(sys.argv)>1 else 'outputs')
