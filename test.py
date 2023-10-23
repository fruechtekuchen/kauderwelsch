import re
import time
import random

PATTERN = r"hallo|welt|ich|heiße|nein|ja|kek"
WORDS = ["hallo", "welt", "ich", "heiße", "nein", "ja", "kek"]

t1 = 0
t2 = 0

for i in range(10000):
    word = random.choice(WORDS)
    t = time.perf_counter_ns()
    re.match(PATTERN, word)
    t1 += time.perf_counter_ns() - t
    t = time.perf_counter_ns()
    for w in WORDS:
        if re.match(w, word):
            break
    t2 += time.perf_counter_ns() - t

print(f"{t1=}; {t2=}; winner: {'t1' if t1 < t2 else 't2'}; diff: {abs(t2-t1)}")
