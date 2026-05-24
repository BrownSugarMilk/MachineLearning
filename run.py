#!/usr/bin/env python3
"""
房价预测实验 — 一键运行入口

用法（在项目根目录）：
    python run.py

或在任意目录：
    python /path/to/ML/run.py
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path


def setup_paths() -> Path:
    """定位项目根目录并加入模块搜索路径。"""
    root = Path(__file__).resolve().parent
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    os.chdir(root)
    return root


def check_python_version() -> None:
    if sys.version_info < (3, 10):
        raise RuntimeError(f"需要 Python 3.10+，当前版本：{sys.version}")


def check_dependencies() -> None:
    required = [
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("sklearn", "scikit-learn"),
        ("lightgbm", "lightgbm"),
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn"),
        ("joblib", "joblib"),
    ]
    missing = []
    for module, package in required:
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    if missing:
        packages = " ".join(missing)
        raise RuntimeError(
            f"缺少依赖：{packages}\n请执行：pip install -r requirements.txt"
        )


def check_raw_data(root: Path) -> None:
    data_dir = root / "data"
    required_files = ["train.csv", "test.csv", "sample_submission.csv"]
    missing = [name for name in required_files if not (data_dir / name).exists()]
    if missing:
        raise FileNotFoundError(
            "缺少原始数据文件：\n"
            + "\n".join(f"  - data/{name}" for name in missing)
            + "\n请从 Kaggle 下载 House Prices 数据集并放入 data/ 目录。"
        )


def verify_outputs(root: Path) -> list[str]:
    """校验所有应生成的输出文件。"""
    results = root / "results"
    expected = [
        "train_clean.csv 由 data_process 写入 data/",
        results / "experiment_summary.json",
        results / "report_summary.md",
        results / "submission_decisiontree.csv",
        results / "submission_randomforest.csv",
        results / "submission_lightgbm.csv",
        results / "lgb_model.pkl",
        results / "feature_importance_lgb.png",
        results / "model_comparison.png",
        results / "prediction_scatter.png",
        results / "feature_importance_top5.json",
    ]

    data_clean = root / "data" / "train_clean.csv"
    missing = []
    if not data_clean.exists():
        missing.append(str(data_clean))
    for item in expected[1:]:
        if not Path(item).exists():
            missing.append(str(item))
    return missing


def print_final_summary(root: Path) -> None:
    import json

    summary_path = root / "results" / "experiment_summary.json"
    with open(summary_path, encoding="utf-8") as f:
        summary = json.load(f)

    print("\n" + "=" * 60)
    print("实验已全部完成，结果与 report.md 一致。")
    print("=" * 60)
    print(f"\n{'模型':<15} {'RMSLE':<10} {'标准差':<10} {'R²':<8} {'耗时(s)'}")
    print("-" * 60)
    for item in summary:
        r2 = f"{item['r2']:.4f}" if item["r2"] is not None else "—"
        print(
            f"{item['model']:<15} "
            f"{item['mean_rmsle']:<10.4f} "
            f"{item['std_rmsle']:<10.4f} "
            f"{r2:<8} "
            f"{item['time_sec']}"
        )

    print("\n主要输出：")
    print(f"  - 结果摘要：{root / 'results' / 'report_summary.md'}")
    print(f"  - 提交文件：{root / 'results' / 'submission_lightgbm.csv'}")
    print(f"  - 对比图表：{root / 'results' / 'model_comparison.png'}")
    print("\n可将 submission_lightgbm.csv 上传至 Kaggle 查看测试集 RMSLE。")


def main() -> int:
    total_start = time.time()
    root = setup_paths()

    print("=" * 60)
    print("基于 LightGBM 的房价预测 — 完整实验流水线")
    print("=" * 60)
    print(f"项目目录：{root}\n")

    check_python_version()
    check_dependencies()
    check_raw_data(root)

    from data_process import main as run_preprocess
    from model_train import train_and_compare
    from visualization import main as run_visualization
    from report_export import build_report_summary

    steps = [
        ("步骤 1/4：数据预处理与特征工程", run_preprocess),
        ("步骤 2/4：模型训练与十折交叉验证", train_and_compare),
        ("步骤 3/4：结果可视化", run_visualization),
        ("步骤 4/4：生成报告摘要", build_report_summary),
    ]

    for title, func in steps:
        print("\n" + "-" * 60)
        print(title)
        print("-" * 60)
        step_start = time.time()
        func()
        print(f"完成，耗时 {time.time() - step_start:.1f}s")

    missing = verify_outputs(root)
    if missing:
        print("\n警告：以下文件未成功生成：")
        for path in missing:
            print(f"  - {path}")
        return 1

    print_final_summary(root)
    print(f"\n总耗时：{time.time() - total_start:.1f}s")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"\n[错误] {exc}", file=sys.stderr)
        raise SystemExit(1)
