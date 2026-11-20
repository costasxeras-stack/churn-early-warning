"""Turns the scores into contact lists and prints every number the page and docs use. Run from work/ after 1-score.py.
Writes ../data/results.json."""
import json
import numpy as np, pandas as pd

s = pd.read_csv("scores.csv"); n = len(s); L = s.left.sum()
rev_all = (s.monthly * s.left).sum()
NAMES = {"rule": "Rule: month-to-month, newest first", "points": "Points checklist (5 risk flags)",
         "lr": "Model (logistic regression)", "gb": "Model (gradient boosting)", "lr_np": "Model without gender, senior or family fields"}
CAP = [0.05, 0.10, 0.20, 0.30]

def take(order, k):
    return s.loc[order[:k]]

lists = {}
for m in NAMES:
    order = s[m].sort_values(ascending=False, kind="mergesort").index
    rows = []
    for c in CAP:
        t = take(order, int(round(n * c)))
        rows.append(dict(cap=c, contacted=len(t), leavers=int(t.left.sum()), right=float(t.left.mean()), caught=float(t.left.sum() / L),
                         revenue=float((t.monthly * t.left).sum() / rev_all)))
    lists[m] = rows
    print(f"{NAMES[m]:44}", "  ".join(f"{r['cap']:.0%}: right {r['right']:.0%} caught {r['caught']:.0%} rev {r['revenue']:.0%}" for r in rows))

# Ranking by revenue at risk: chance of leaving times monthly charges (model scores are probabilities).
s["value"] = s.lr * s.monthly
vo = s.value.sort_values(ascending=False, kind="mergesort").index
ro = s.lr.sort_values(ascending=False, kind="mergesort").index
value = []
for c in CAP:
    k = int(round(n * c)); a, b = take(ro, k), take(vo, k)
    value.append(dict(cap=c, risk_caught=float(a.left.sum() / L), risk_rev=float((a.monthly * a.left).sum() / rev_all),
                      value_caught=float(b.left.sum() / L), value_rev=float((b.monthly * b.left).sum() / rev_all),
                      overlap=float(len(set(a.id) & set(b.id)) / k), risk_monthly=float(a.monthly.mean()), value_monthly=float(b.monthly.mean())))
    print(f"value list {c:.0%}: leavers caught risk {value[-1]['risk_caught']:.0%} vs value {value[-1]['value_caught']:.0%}, revenue {value[-1]['risk_rev']:.0%} vs {value[-1]['value_rev']:.0%}, same people {value[-1]['overlap']:.0%}, avg monthly {value[-1]['risk_monthly']:.0f} vs {value[-1]['value_monthly']:.0f}")

# Calibration: does the model's expected number of leavers match what happened?
s["bin"] = pd.qcut(s.lr, 10, labels=False)
cal = [dict(pred=float(g.lr.mean()), actual=float(g.left.mean()), n=len(g)) for _, g in s.groupby("bin")]
print("expected leavers", round(s.lr.sum()), "actual", L)
for c in cal: print(f"  predicted {c['pred']:.0%} actual {c['actual']:.0%}")

# Who the 20% list misses (model).
k = int(round(n * 0.2)); top = set(take(ro, k).id); miss = s[(s.left == 1) & ~s.id.isin(top)]; hit = s[(s.left == 1) & s.id.isin(top)]
def prof(g):
    return dict(n=len(g), tenure=float(g.tenure.median()), monthly=float(g.monthly.median()), m2m=float((g.contract == "Month-to-month").mean()))
missed = dict(caught=prof(hit), missed=prof(miss))
print("leavers on the 20% list", missed["caught"], "\nleavers missed", missed["missed"])

# Overlap between the points checklist and the model at 20%.
po = s.points.sort_values(ascending=False, kind="mergesort").index
ov = len(set(take(po, k).id) & top) / k
print(f"points and model 20% lists share {ov:.0%} of customers")

# Curves for the slider: every list size from 1% to 50% of customers.
curves = {}
for m in NAMES:
    order = s[m].sort_values(ascending=False, kind="mergesort").index
    lv = s.left.values[order]; mv = (s.monthly * s.left).values[order]
    cl, cr = np.cumsum(lv), np.cumsum(mv)
    curves[m] = [[round(float(cl[int(round(n * c / 100)) - 1] / L), 4), round(float(cl[int(round(n * c / 100)) - 1] / int(round(n * c / 100))), 4),
                  round(float(cr[int(round(n * c / 100)) - 1] / rev_all), 4)] for c in range(1, 51)]

res = dict(curves=curves, customers=n, leavers=int(L), leaveRate=float(L / n), blankTotal=11, names=NAMES, lists=lists, value=value, calibration=cal,
           expected=float(s.lr.sum()), missed=missed, pointsModelOverlap=float(ov))
json.dump(res, open("../data/results.json", "w"), indent=1)
print("wrote data/results.json")
