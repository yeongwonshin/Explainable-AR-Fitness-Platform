from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

from app.profiling.labeler import relabel_by_dominant_pattern
from app.profiling.model_service import FEATURE_ORDER


def generate_synthetic_dataset(n: int = 300, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n):
        base = rng.normal(0.15, 0.06, size=5).clip(0, 0.45)
        dominant = rng.integers(0, 4)
        if dominant == 0:  # A
            base[1] += rng.uniform(0.18, 0.40)
        elif dominant == 1:  # B
            base[0] += rng.uniform(0.18, 0.40)
        elif dominant == 2:  # C
            base[2] += rng.uniform(0.14, 0.30)
            base[3] += rng.uniform(0.08, 0.24)
        else:  # D
            base[4] += rng.uniform(0.18, 0.40)
        features = {name: round(float(value), 6) for name, value in zip(FEATURE_ORDER, base.clip(0, 1))}
        label = relabel_by_dominant_pattern(features)
        rows.append({**features, "label": label})
    return pd.DataFrame(rows)


def load_dataset(path: Path | None, synthetic: bool) -> pd.DataFrame:
    if synthetic:
        return generate_synthetic_dataset()
    if path is None:
        raise SystemExit("--input 또는 --synthetic 중 하나가 필요합니다.")
    df = pd.read_csv(path)
    missing = set(FEATURE_ORDER + ["label"]) - set(df.columns)
    if missing:
        raise SystemExit(f"Missing columns: {sorted(missing)}")
    return df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=None, help="F1~F5와 label 컬럼을 포함한 CSV")
    parser.add_argument("--synthetic", action="store_true", help="샘플 실행용 synthetic 데이터 생성")
    parser.add_argument("--output-dir", type=Path, default=Path("models"))
    args = parser.parse_args()

    df = load_dataset(args.input, args.synthetic)
    le = LabelEncoder()
    y = le.fit_transform(df["label"].astype(str))
    x = df[FEATURE_ORDER].astype(float)

    stratify = y if len(set(y)) > 1 else None
    x_train, x_valid, y_train, y_valid = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=stratify
    )

    model = XGBClassifier(
        n_estimators=120,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="multi:softprob",
        eval_metric="mlogloss",
        random_state=42,
    )
    model.fit(x_train, y_train)
    pred = model.predict(x_valid)

    report = classification_report(y_valid, pred, target_names=le.classes_, output_dict=True, zero_division=0)
    print(classification_report(y_valid, pred, target_names=le.classes_, zero_division=0))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    model.save_model(str(args.output_dir / "body_profile_xgb.json"))
    (args.output_dir / "label_encoder.json").write_text(
        json.dumps({str(i): label for i, label in enumerate(le.classes_)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (args.output_dir / "feature_summary.json").write_text(
        json.dumps(
            {
                "feature_order": FEATURE_ORDER,
                "classification_report": report,
                "train_size": int(len(x_train)),
                "valid_size": int(len(x_valid)),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
