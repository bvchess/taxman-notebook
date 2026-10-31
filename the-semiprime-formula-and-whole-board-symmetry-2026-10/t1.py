import time, sys
from tx import *
known = [0, 0, 2, 3, 7, 9, 15, 17, 21, 30, 40, 44, 50, 52, 66, 81, 89, 93, 111, 113, 124, 144, 166, 170, 182, 198, 224, 251, 279, 285, 301, 303, 319, 352, 386, 418, 442, 448, 486, 503, 525]
for n in range(2, 41):
    t = time.time()
    o, sets = brute_opt(n)
    print(n, o, len(sets), round(time.time() - t, 2), 'OK' if n >= len(known) or known[n] == o else 'MISMATCH', flush=True)
