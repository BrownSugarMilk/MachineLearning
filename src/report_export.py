"""生成与课程报告格式一致的结果摘要。"""
import json
import os
from datetime import datetime

import joblib
import pandas as pd

from config import DATA_DIR, RESULTS_DIR


def _round4(value):
    return f"{float(value):.4f}"


def export_feature_importance(model_path, output_path, top_k=5):
    """导出 LightGBM Top-K 特征重要性。"""
    if not os.path.exists(model_path):
        return []

    model = joblib.load(model_path)
    features = pd.read_csv(os.path.join(DATA_DIR, "train_clean.csv")).columns
    importance = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
    top = [{"rank": i + 1, "feature": name, "importance": int(score)} for i, (name, score) in enumerate(importance.head(top_k).items())]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(top, f, ensure_ascii=False, indent=2)
    return top


def build_report_summary(summary_path=None, output_path=None):
    """根据 experiment_summary.json 生成 report_summary.md。"""
    summary_path = summary_path or os.path.join(RESULTS_DIR, "experiment_summary.json")
    output_path = output_path or os.path.join(RESULTS_DIR, "report_summary.md")

    with open(summary_path, encoding="utf-8") as f:
        summary = json.load(f)

    lines = [
        "# 实验结果摘要（与 report.md 对应）",
        "",
        f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 表 5-1 三种模型十折交叉验证结果对比",
        "",
        "| 模型 | 平均 RMSLE | 标准差 | R² | 耗时(s) |",
        "|------|-----------|--------|-----|---------|",
    ]

    name_map = {
        "DecisionTree": "决策树",
        "RandomForest": "随机森林",
        "LightGBM": "LightGBM",
    }

    lgb_folds = []
    for item in summary:
        r2_text = f"{item['r2']:.4f}" if item["r2"] is not None else "—"
        lines.append(
            f"| {name_map.get(item['model'], item['model'])} "
            f"| {_round4(item['mean_rmsle'])} "
            f"| {_round4(item['std_rmsle'])} "
            f"| {r2_text} "
            f"| {item['time_sec']} |"
        )
        if item["model"] == "LightGBM":
            lgb_folds = item["fold_scores"]

    lines.extend([
        "",
        "## 表 5-2 LightGBM 十折交叉验证各折 RMSLE",
        "",
        "| 折次 | " + " | ".join(str(i) for i in range(1, 11)) + " |",
        "|------|" + "|".join(["---"] * 10) + "|",
        "| RMSLE | " + " | ".join(f"{x:.4f}" for x in lgb_folds) + " |",
        "",
    ])

    top_features = export_feature_importance(
        os.path.join(RESULTS_DIR, "lgb_model.pkl"),
        os.path.join(RESULTS_DIR, "feature_importance_top5.json"),
    )
    if top_features:
        lines.extend([
            "## 5.4 特征重要性 Top 5",
            "",
            "| 排名 | 特征 | 重要性 |",
            "|------|------|--------|",
        ])
        for row in top_features:
            lines.append(f"| {row['rank']} | {row['feature']} | {row['importance']} |")
        lines.append("")

    lines.extend([
        "## 输出文件清单",
        "",
        "- `experiment_summary.json`：完整 JSON 结果",
        "- `submission_decisiontree.csv` / `submission_randomforest.csv` / `submission_lightgbm.csv`：Kaggle 提交文件",
        "- `lgb_model.pkl`：LightGBM 最终模型",
        "- `feature_importance_lgb.png`：特征重要性图",
        "- `model_comparison.png`：模型对比图",
        "- `prediction_scatter.png`：预测散点图",
        "",
    ])

    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    return output_path
