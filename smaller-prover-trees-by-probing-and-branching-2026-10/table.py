import json, sys, os
S = os.path.join(os.environ.get('STUDY_DIR', os.path.dirname(os.path.abspath(__file__))), 'out')
labels = sys.argv[1].split(',')
games = [int(x) for x in sys.argv[2].split(',')]
def load(label, n):
    p = f'{S}/{label}-{n}.jsonl'
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        return None
    return json.loads(open(p).readline())
base = labels[0]
print('game ' + ' '.join(f'{l:>22}' for l in labels))
tot = {l: [0, 0.0] for l in labels}
for n in games:
    row = []
    b = load(base, n)
    for l in labels:
        r = load(l, n)
        if r is None:
            row.append(f'{"-":>22}')
            continue
        tot[l][0] += r['nodes']; tot[l][1] += r['secs']
        ratio = r['nodes'] / b['nodes'] if b else float('nan')
        row.append(f"{r['nodes']:>8} {r['secs']:>7.1f}s {ratio:>5.2f}")
    print(f'{n:>4} ' + ' '.join(row))
print('sum  ' + ' '.join(f'{tot[l][0]:>8} {tot[l][1]:>7.1f}s {tot[l][0]/max(tot[base][0],1):>5.2f}' for l in labels))
