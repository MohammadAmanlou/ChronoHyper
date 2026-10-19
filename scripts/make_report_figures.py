"""Generate method tradeoff figure directly from the archived source-grouped development CSV."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/'research_outputs/final_matrix/method_summary.csv').open(encoding='utf-8-sig',newline='') as f:
 data=list(csv.DictReader(f))
keep=['semantic_kmeans','native_joint_70','incidence_svd','native_temporal_08','native_temporal_20','frozen_previous']
a={r['model']:r for r in data if r.get('year')=='2024' and r['model'] in keep}
fig,ax=plt.subplots(figsize=(6.2,3.4),dpi=180)
for m in keep:
 row=a[m]
 x=float(row['heldout_normalized_connectivity_lower_better_mean'])
 y=float(row['cross_year_shared_node_ari_mean'])
 ax.scatter([x],[y],s=38)
 ax.annotate(m.replace('native_','').replace('semantic_kmeans','semantic').replace('frozen_previous','frozen'),(x,y),xytext=(4,4),textcoords='offset points',fontsize=7)
ax.set(xlabel='Held-out normalized hyperedge cut (lower is better)',ylabel='Temporal ARI on shared nodes (higher is more stable)',title='2024: the cut-versus-stability tradeoff (5 seeds)')
ax.set_xlim(.52,.73);ax.set_ylim(0,1.06)
ax.grid(alpha=.25)
fig.tight_layout()
fig.savefig(ROOT/'figures/fig_selected_tradeoff.png',dpi=180)
plt.close(fig)
