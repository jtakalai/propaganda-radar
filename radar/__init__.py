"""Propaganda Radar - flagging Serbian headlines against CRTA's manipulation criteria.

Subpackages follow the six data-lifecycle stages the course grades
(docs/data-lifecycle.md):

    collect/   stage 2 - RSS, sitemap archive, CRTA's published reports
    prepare/   stage 3 - script normalisation, outlet canonicalisation
    label/     stage 3 - human CLI and LLM-assisted labelling
    model/     stage 5 - the rungs of the model ladder
    evaluate/  stage 5 - precision/recall, the metrics that survive a 2% base rate

Stage 4 (explore) is analysis/eda.py; stage 6 (communicate) is app/dashboard.py.
"""
