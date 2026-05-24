"""实验结果可视化：特征重要性与预测分析图。"""
import os

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from config import DATA_DIR, RESULTS_DIR

sns.set_style("whitegrid")
plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def plot_feature_importance(model, feature_names, title, save_path, top_k=20):
    """绘制 Top-K 特征重要性条形图。"""
    importance = pd.Series(model.feature_importances_, index=feature_names)
    top_features = importance.sort_values(ascending=False).head(top_k)

    plt.figure(figsize=(10, 8))
    sns.barplot(x=top_features.values, y=top_features.index, hue=top_features.index, legend=False, palette="viridis")
    plt.title(title, fontsize=14)
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_model_comparison():
    """绘制三种模型的交叉验证 RMSLE 对比图。"""
    summary_path = os.path.join(RESULTS_DIR, "experiment_summary.json")
    if not os.path.exists(summary_path):
        print("未找到 experiment_summary.json，请先运行 model_train.py")
        return

    import json

    with open(summary_path, encoding="utf-8") as f:
        summary = json.load(f)

    names = [item["model"] for item in summary]
    means = [item["mean_rmsle"] for item in summary]
    stds = [item["std_rmsle"] for item in summary]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(names, means, yerr=stds, capsize=6, color=["#4C72B0", "#55A868", "#C44E52"])
    plt.ylabel("RMSLE (10-Fold CV)")
    plt.title("Model Comparison on House Price Prediction")
    for bar, mean in zip(bars, means):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{mean:.4f}", ha="center", va="bottom")
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "model_comparison.png"), dpi=300)
    plt.close()
    print("模型对比图已保存。")


def plot_prediction_analysis():
    """绘制 LightGBM 在训练集上的真实值-预测值散点图。"""
    model_path = os.path.join(RESULTS_DIR, "lgb_model.pkl")
    if not os.path.exists(model_path):
        print("未找到 lgb_model.pkl，请先运行 model_train.py")
        return

    X_train = pd.read_csv(os.path.join(DATA_DIR, "train_clean.csv"))
    y_train = pd.read_csv(os.path.join(DATA_DIR, "y_train_clean.csv")).squeeze()
    model = joblib.load(model_path)
    y_pred = model.predict(X_train)

    plt.figure(figsize=(8, 6))
    plt.scatter(y_train, y_pred, alpha=0.5, edgecolors="k", s=20)
    low, high = min(y_train.min(), y_pred.min()), max(y_train.max(), y_pred.max())
    plt.plot([low, high], [low, high], "r--", lw=2, label="Ideal Prediction")
    plt.xlabel("True Values (log scale)")
    plt.ylabel("Predictions (log scale)")
    plt.title("LightGBM: True vs Predicted House Prices")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "prediction_scatter.png"), dpi=300)
    plt.close()
    print("预测散点图已保存。")


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    feature_names = pd.read_csv(os.path.join(DATA_DIR, "train_clean.csv")).columns

    model_path = os.path.join(RESULTS_DIR, "lgb_model.pkl")
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        plot_feature_importance(
            model,
            feature_names,
            "LightGBM Feature Importance (Top 20)",
            os.path.join(RESULTS_DIR, "feature_importance_lgb.png"),
        )
        print("LightGBM 特征重要性图已保存。")

    plot_model_comparison()
    plot_prediction_analysis()
    print("\n可视化任务完成。")


if __name__ == "__main__":
    main()
