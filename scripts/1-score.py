"""Gives every customer a churn score from four methods. Run from work/.
Models are scored with 5-fold cross validation: each customer's score comes from a model that never saw them.
Writes scores.csv and prints how well each method ranks leavers."""
import numpy as np, pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score

d = pd.read_csv("Telco-Customer-Churn.csv")
blank = d.TotalCharges.str.strip() == ""
print("blank total charges:", int(blank.sum()), "all with tenure", sorted(d.tenure[blank].unique()))
d["TotalCharges"] = pd.to_numeric(d.TotalCharges, errors="coerce").fillna(0.0)  # first-month customers, nothing billed yet
y = (d.Churn == "Yes").astype(int).values
num = ["tenure", "MonthlyCharges", "TotalCharges"]
cat = [c for c in d.columns if c not in num + ["customerID", "Churn", "SeniorCitizen"]] + ["SeniorCitizen"]
PERSONAL = ["gender", "SeniorCitizen", "Partner", "Dependents"]

def pipe(model, cols_num, cols_cat):
    pre = ColumnTransformer([("n", StandardScaler(), cols_num), ("c", OneHotEncoder(handle_unknown="ignore"), cols_cat)])
    return make_pipeline(pre, model)

def oof(make, cols_cat):
    s = np.zeros(len(d)); aucs = []
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=42).split(d, y):
        m = make(cols_cat).fit(d.iloc[tr], y[tr]); p = m.predict_proba(d.iloc[te])[:, 1]
        s[te] = p; aucs.append(roc_auc_score(y[te], p))
    return s, aucs

lr = lambda cc: pipe(LogisticRegression(max_iter=2000, C=1.0), num, cc)
gb = lambda cc: pipe(HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, max_leaf_nodes=15, random_state=0), num, cc)
out = pd.DataFrame({"id": d.customerID, "left": y, "monthly": d.MonthlyCharges, "tenure": d.tenure, "contract": d.Contract})

# Rule: a CRM filter anyone can build. Month-to-month contracts first, newest customers first within them.
out["rule"] = (d.Contract == "Month-to-month") * 1000 + (72 - d.tenure)
# Points checklist: one point per well-known risk flag. These flags are well known for this sample, so the checklist has some hindsight.
flags = {"Month-to-month contract": d.Contract == "Month-to-month", "Customer for 12 months or less": d.tenure <= 12,
         "Pays by electronic check": d.PaymentMethod == "Electronic check", "Fiber optic internet": d.InternetService == "Fiber optic",
         "No tech support": d.TechSupport == "No"}
out["points"] = sum(f.astype(int) for f in flags.values()) + d.tenure.rsub(72) / 1000  # ties broken by newest first
out["lr"], a_lr = oof(lr, cat)
out["gb"], a_gb = oof(gb, cat)
out["lr_np"], a_np = oof(lr, [c for c in cat if c not in PERSONAL])
for k, a in [("rule", None), ("points", None), ("lr", a_lr), ("gb", a_gb), ("lr_np", a_np)]:
    extra = f"  folds {min(a):.3f} to {max(a):.3f}" if a else ""
    print(f"{k:7} ranking score (AUC) {roc_auc_score(y, out[k]):.3f}{extra}")
print("points distribution:", out.points.astype(int).value_counts().sort_index().to_dict())
print("leave rate by points:", out.groupby(out.points.astype(int)).left.mean().round(3).to_dict())
out.to_csv("scores.csv", index=False)
