"""The committed chain and the prover's files, read from a checkout of the main repository at commit 2896cdd.

The checkout is the folder named by the environment variable TAXMAN_REPO, or the current folder.
"""
import gzip, json, os
W = os.environ.get('TAXMAN_REPO', '.')

def results():
    res = {}
    with gzip.open(W + '/results/optimal.jsonl.gz', 'rt') as f:
        for l in f:
            d = json.loads(l)
            res[d['n']] = d
    return res

def moves(d):
    m = d['moves']
    return json.loads(m) if isinstance(m, str) else m

def prover_lines():
    prov = {}
    for fn in ['exact_parity_2_1300.jsonl', 'exact_parity_1301_2175.jsonl']:
        with open(W + '/solver/noframe/data/' + fn) as f:
            for l in f:
                d = json.loads(l)
                prov[d['n']] = d
    return prov

def optsets(res):
    out = {}
    with open(W + '/solver/noframe/data/optsets_2_989.jsonl') as f:
        for l in f:
            d = json.loads(l)
            n = d['n']
            if d['ended'] != 'complete':
                continue
            canon = set(d['canonical']) if not d['recorded_is_canonical'] else set(moves(res[n]))
            sets = [canon] + [(canon - set(o['out'])) | set(o['in']) for o in d['others']]
            if d['sets'] != len(sets):
                continue
            out[n] = sets
    return out
