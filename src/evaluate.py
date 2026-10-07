"""
Bonus 3: bao cao precision / recall chi tiet sau moi lan huan luyen.

Doc models/model.joblib va tap holdout, in confusion matrix dang van ban
va ghi precision / recall cua tung lop ra outputs/detail.txt.
"""
import os
import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

LABEL_NAMES = ["thu_nhap_thap (<=50K)", "thu_nhap_cao (>50K)"]


def evaluate(
    model_path: str = "models/model.joblib",
    eval_path: str = "data/holdout.csv",
    out_path: str = "outputs/detail.txt",
) -> str:
    model = joblib.load(model_path)
    df_eval = pd.read_csv(eval_path)
    X_eval = df_eval.drop(columns=["target"])
    y_eval = df_eval["target"]
    preds = model.predict(X_eval)

    tn, fp, fn, tp = confusion_matrix(y_eval, preds, labels=[0, 1]).ravel()
    lines = [
        "CONFUSION MATRIX (hang = thuc te, cot = du doan)",
        f"{'':>14}{'pred=0':>10}{'pred=1':>10}",
        f"{'actual=0':>14}{tn:>10}{fp:>10}",
        f"{'actual=1':>14}{fn:>10}{tp:>10}",
        "",
        f"TN={tn}  FP={fp} (gan nham thu nhap thap thanh cao)",
        f"FN={fn}  TP={tp} (FN = bo sot nguoi thu nhap cao)",
        "",
        "PRECISION / RECALL THEO TUNG LOP",
        classification_report(
            y_eval, preds, labels=[0, 1], target_names=LABEL_NAMES, digits=4, zero_division=0
        ),
    ]
    text = "\n".join(lines)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    return text


if __name__ == "__main__":
    evaluate()
