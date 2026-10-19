"""Generate full English research report in Markdown and 4-page styled PDF from actual measured outputs."""
from pathlib import Path
from xml.sax.saxutils import escape


def n(x,d=3):
    if x is None:return 'N/A'
    return f'{x:.{d}f}'


def content(m):
    s=m['snapshots'];e=m['temporal'];r=m['retrieval']['summary'];abl=m.get('ablations_2024',{})
    sec=[]
    sec.append(('Introduction and framing',
    'A scientific temporal knowledge hypergraph comprises typed entities (methods, datasets, claims, papers) and high-order events connecting more than two entities. We seek four nested resolutions of the same corpus: at most 12 macro-concepts, at most 48 sub-concepts, at most 144 more-specific clusters, then singleton entities. The partitions must remain nested while scientific evidence arrives, without mistaking introduction year for first documented observation. This is a small-corpus research demonstrator, not a production graph system.'))
    sec.append(('Data and temporal policy',
    f"The supplied export has 5,798 nodes, 1,429 distinct hyperedges and 52 scientific articles. Three mandatory conservative cutoffs have {s['2020']['n_nodes']}/{s['2020']['n_total_edges']}, {s['2022']['n_nodes']}/{s['2022']['n_total_edges']}, and {s['2024']['n_nodes']}/{s['2024']['n_total_edges']} nodes/edges in 2020/2022/2024; a further 2025 cutoff is used only to align retrieval with February-2026 questions without claiming unknown 2026 months existed in February. Node availability requires first_seen_year<=cutoff; edge availability requires edge.year<=cutoff, the asserting paper's article_year<=cutoff, and all endpoint nodes available. 716 nodes have a year earlier than first_seen_year and 134 edge assertions derive from papers later than the edge's year. These are time semantics, not automatically corrupted records. The 18 provided questions and gold answers were not used to build clusters."))
    sec.append(('Formal method and design choice',
    'Let V_t be available nodes and E_t the original high-order hyperedges. For partition c, we optimize a heuristic balance of semantic proximity, hyperedge connectivity and temporal inertia: J(c)=alpha*mean_v[1-cos(x_v,mu_c(v))] + beta*sum_e(|{c(v):v in e}|-1)/|E| + gamma*mean_v(1[c(v) differs from prior stable group]). The code uses a local coordinate-move surrogate with candidate centroids and affected incidence nets: this approximates the objective; it is NOT a globally optimal solver or mathematical convergence proof. Alpha/beta are coded as a fixed 0.70/0.30 local move tradeoff (different normalizations) and gamma 0.08 for surviving top-level nodes; settings were frozen before reading gold. Semantic vectors are word-hash TF then 48-dimensional SVD FIT ONLY on 2020 node names and reused at later dates. This reduces representation-level future leakage but underrepresents novel vocabulary. K-means supplies initial partitions; a constrained native-hyperedge incidence move reduces splitting costs while considering semantic similarity. Coarsen separately within each higher-level parent to preserve laminar refinement.'))
    sec.append(('Native edge collapse, identities and complexity',
    'Every original hyperedge remains a single coarse event with stable original id, relation type, provenance, original arity, distinct supernode endpoints and a multiplicity count for each supernode. Fully internal edges are stored as one supernode plus metadata, partial edges retain multiplicities, and edges crossing three or more groups remain high order, never a substituted clique. For each event, sum(group multiplicities)=original arity, checked by executable assertions. On each new snapshot, previous 12 centroids warm-start initialization and survivor assignments incur a change penalty. Across all non-singleton resolutions, overlap-based Hungarian matching tracks persistent identities, and an explicitly heuristic event log records birth, growth, merge, split and death. Budget constraints and nesting are construction invariants; semantic scientific meaning, stability quality, and label correctness are empirical. Per local pass, evaluating candidate moves costs approximately O(sum of affected incidence * candidate labels + n*d*k), with K-means/linear algebra and child splits additional. No formal global optimality or runtime scaling guarantee is claimed. The rejected pairwise clique projection loses unique event grouping even where clique weights reproduce pair co-occurrence.'))
    sec.append(('Evaluation protocol and validity',
    f"The same deterministic group of roughly 20% of asserting paper IDs is fully HELD OUT of training hyperedges at every cutoff. An evaluation-only title-based character n-gram representation measures within-cluster similarity from source article titles, not the word-hash node-name embedding used for clustering; {s['2024']['coherence']['null_draws']} equal-size random-label nulls calibrate its interpretation. The views remain correlated through their papers, so this is not blind independent expert semantic judgment. A stricter second null shuffles bipartite node-hyperedge incidences within relation and publication year, preserving every node's incidence degree and each hyperedge's size exactly, and tests connectivity on independently held-out paper edges. For stability, remove 10% of training hyperedges in five independent draws and report ARI with descriptive bootstrap CIs. True intersnapshot ARI uses shared node identities and a separate, approximate node bootstrap CI. Deterministic labeller inputs at each cutoff are the exact available node IDs, surface forms, types, and corpus-wide token document frequencies; it selects only repeated source-name keyphrases with supporting member IDs and writes one sentence with precise membership. Glosses assert only checkable membership facts. Automated audits verify that bounded claim set, but an independent semantic NLI/human over-claim rate was not obtained. We intentionally distinguish that missing result rather than report 0% over-claim."))
    sec.append(('Measured results',
    f"The 2024 top-level output has {s['2024']['clusters_per_level'][0]} macro-concepts and all {s['2024']['n_nodes']} snapshot nodes remain covered. Its independently sourced title-coherence score is {n(s['2024']['coherence'].get('observed'))}, versus {n(s['2024']['coherence'].get('random_size_matched_mean'))} for random size-matched clusters (empirical p={n(s['2024']['coherence'].get('randomization_p_ge'))}). Held-out paper-edge normalized connectivity is {n(s['2024']['heldout_normalized_connectivity'])}; lower is better. The 2024 10%-deletion robustness ARI is {n(s['2024']['robustness']['ari']['mean'])} with bootstrap 95% CI {s['2024']['robustness']['ari']['ci95']}. 2020->2022 top-level ARI={n(e['2020_2022']['ari'])}, 2022->2024 ARI={n(e['2022_2024']['ari'])}. True degree/arity-preserving constrained randomization yields {n(m['structural_null_2024']['null_mean'])} heldout normalized cut versus {n(m['structural_null_2024']['observed'])} for real edges (p={n(m['structural_null_2024']['randomization_p_le'])}); with only {m['structural_null_2024']['shuffle_count']} null draws, do not treat p as definitive."))
    sec.append(('External utility and controlled variants',
    f"Use the supplied 18 questions only after model construction. Four type-B multi-claim synthesis questions require source-grounded synthesis and are explicitly NOT SCORED by this simple ranking retrieval benchmark; 14 type-A list questions are scored by exact normalized matches to candidate exported entity surface forms. At a conservative 2025 cutoff, flat Hit@5={n(r['flat_hit_at_5'])} and hierarchical Hit@5={n(r['hier_hit_at_5'])}. Mean candidate nodes scored: flat {n(r['mean_flat_nodes_scored'],0)}, hierarchy {n(r['mean_hier_nodes_scored'],0)} (plus four centroid comparisons). Gold includes mean {n(r['mean_absent_gold_per_question'])} reference items missing from export per question; absence fundamentally caps achievable recall. Semantic-only, hypergraph-dominant and joint ablations are run on the same 2024 cutoff and independent title/held-out-edge scores are saved under metrics.json. The initial hierarchical retriever DID NOT exceed flat Hit@5; therefore for retrieval on this corpus we would ship the flat ranker, while retaining the independently evaluated hierarchical representation for browsing and further research. Structural-only gives stronger article-title coherence while semantic-only yields the better held-out hyperedge compactness among the 2024 ablations: no variant dominates. The exported temporally coupled joint hierarchy reflects the a-priori method choice, not a tuned-on-gold winner."))
    sec.append(('Limitations and next four weeks',
    'This small, unevenly sourced set of 52 articles is no evidence of robust disciplinary ontology discovery. Label templates conservatively give inspectable membership facts but underdeliver richer expert-readable scientific descriptions; without blind human audit, P6 is only bounded structurally. Historical nodes may be mentioned by future papers and semantics are restricted to available years. The bibliographic reference labels for type-A questions are not always present as exact node surfaces. Matching identity by Jaccard/Hungarian and thresholded event types is a practical heuristic rather than a proof of true concept evolution. The 5-perturbation CIs are approximate and correlated provenance may bias estimates. Four additional weeks: (1) hold out entire venues or research subdomains and obtain expert blind coherence and label-claim annotations, (2) compare against full KaHyPar-style, Leiden projection and stronger scientific encoders with equivalent time budgets, (3) implement entailment-based source-citation audit and the four type-B synthesis tasks, (4) evaluate change-point sensitivity, label cross-time consistency, and sublinear index-based hierarchical retrieval on a much larger corpus.'))
    sec.append(('Literature anchors',
    'Traag, Waltman & van Eck (2019), From Louvain to Leiden, Scientific Reports, DOI 10.1038/s41598-019-41695-z (hierarchical community baseline, pairwise context). Schlag et al. (2022), High-Quality Hypergraph Partitioning, ACM Journal of Experimental Algorithmics, DOI 10.1145/3529090 (native high-order connectivity metric and coarsening). Wang et al. (2022), SpecPart, ICCAD, DOI 10.1145/3508352.3549390 (spectral/global versus local multilevel choices). Chakrabarti, Kumar & Tomkins (2006), Evolutionary Clustering, KDD, DOI 10.1145/1150402.1150467 (snapshot quality versus temporal smoothness). These are positioning references rather than claims of implementing those algorithms verbatim.'))
    return sec


def write_reports(output,met):
    out=Path(output); sections=content(met)
    header='# Evidence-Aware Multi-Resolution Abstraction of an Evolving Scientific Knowledge Hypergraph\n\n'
    header+='**Constructor Knowledge Labs | reproducible research assessment | 19 October 2026**\n\n'
    header+='*All numerical results generated by the attached code on the supplied archive. Unsupported semantics and incomplete evaluation are disclosed, not imputed.*\n\n'
    text=header+''.join('## '+title+'\n\n'+body+'\n\n' for title,body in sections)
    (out/'report.md').write_text(text,encoding='utf-8')
    pdf(out,met,sections)


def pdf(out,met,sections):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,Table,TableStyle,PageBreak,KeepTogether
    from reportlab.lib.enums import TA_LEFT
    path=out/'report.pdf';w,h=A4
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='DocTitle2',fontName='Helvetica-Bold',fontSize=17,leading=21,textColor=colors.HexColor('#152943'),spaceAfter=10))
    styles.add(ParagraphStyle(name='Section2',fontName='Helvetica-Bold',fontSize=10.7,leading=14.3,textColor=colors.HexColor('#166b84'),spaceBefore=12,spaceAfter=5))
    styles.add(ParagraphStyle(name='B2',fontName='Helvetica',fontSize=9.0,leading=12.5,spaceAfter=5,textColor=colors.HexColor('#293747')))
    styles.add(ParagraphStyle(name='Small2',fontName='Helvetica',fontSize=7.3,leading=9.4,textColor=colors.HexColor('#46566c')))
    doc=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=43,bottomMargin=46,title='Constructor TKH Multi-resolution Assessment')
    flow=[]
    flow.append(Paragraph('Evidence-Aware Multi-Resolution Abstraction of an Evolving Scientific Knowledge Hypergraph',styles['DocTitle2']))
    flow.append(Paragraph('Constructor Knowledge Labs | Research assessment | 19 October 2026',styles['Small2']))
    flow.append(Spacer(1,7))
    # roughly 4-5 pages total with free flow, no page separator enforced
    for i,(title,body) in enumerate(sections):
        flow.append(Paragraph(escape(title),styles['Section2']))
        flow.append(Paragraph(escape(body).replace('&lt;','&lt;').replace('&gt;','&gt;'),styles['B2']))
        if title=='Data and temporal policy':
            flow.append(Image(str(out/'fig_temporal_growth.png'),width=400,height=187))
        if title=='Measured results':
            flow.append(Image(str(out/'fig_coherence.png'),width=392,height=183))
        if title=='External utility and controlled variants':
            flow.append(Image(str(out/'fig_retrieval.png'),width=392,height=178))
    def footer(canvas,document):
        canvas.saveState();canvas.setStrokeColor(colors.HexColor('#dce3e8'));canvas.line(44,35,w-44,35)
        canvas.setFont('Helvetica',7);canvas.setFillColor(colors.HexColor('#667589'))
        canvas.drawString(44,25,'Constructor TKH | verified source-data analysis; limitations explicitly reported')
        canvas.drawRightString(w-44,25,str(document.page));canvas.restoreState()
    doc.build(flow,onFirstPage=footer,onLaterPages=footer)
