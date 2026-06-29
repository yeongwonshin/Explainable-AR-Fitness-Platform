from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from app.pose.feature_extractor import extract_body_features, parse_views
from app.profiling.labeler import relabel_by_dominant_pattern


def main() -> None:
    parser = argparse.ArgumentParser(description="Kaggle/자체 keypoint JSONL을 F1~F5 CSV로 변환합니다.")
    parser.add_argument("--input-jsonl", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    args = parser.parse_args()

    rows = []
    with args.input_jsonl.open("r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            views = parse_views(item["views"])
            features, quality = extract_body_features(views)
            label = item.get("label") or relabel_by_dominant_pattern(features)
            rows.append({"sample_id": item.get("sample_id"), **features, "label": label, **quality})

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output_csv, index=False)
    print(f"saved: {args.output_csv}")


if __name__ == "__main__":
    main()
