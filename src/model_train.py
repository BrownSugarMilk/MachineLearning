"""模型训练、交叉验证评估与 Kaggle 提交文件生成。"""
import json
import os
import time

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import make_scorer, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.tree import DecisionTreeRegressor

from config import CV_FOLDS, DATA_DIR, RANDOM_STATE, RESULTS_DIR


def load_processed_data():
    """加载预处理后的训练/测试数据。"""
    X_train = pd.read_csv(os.path.join(DATA_DIR, "train_clean.csv"))
    X_test = pd.read_csv(os.path.join(DATA_DIR, "test_clean.csv"))
    y_train = pd.read_csv(os.path.join(DATA_DIR, "y_train_clean.csv")).squeeze()
    print(f"加载数据成功，训练集特征维度: {X_train.shape}")
    return X_train, X_test, y_train


def rmse_score(y_true, y_pred):
    """计算 RMSE；在对数标签上即为 RMSLE。"""
    return np.sqrt(mean_squared_error(y_true, y_pred))


def evaluate_model(model, X, y, cv=CV_FOLDS):
    """十折交叉验证，返回每折 RMSE、均值、标准差与 R²。"""
    kfold = KFold(n_splits=cv, shuffle=True, random_state=RANDOM_STATE)
    rmse_scorer = make_scorer(rmse_score)
    r2_scorer = make_scorer(r2_score)

    fold_scores = cross_val_score(model, X, y, scoring=rmse_scorer, cv=kfold, n_jobs=-1)
    r2_mean = cross_val_score(model, X, y, scoring=r2_scorer, cv=kfold, n_jobs=-1).mean()
    return fold_scores, fold_scores.mean(), fold_scores.std(), r2_mean


def evaluate_lgb_with_early_stopping(X, y, params, cv=CV_FOLDS):
    """LightGBM 专用交叉验证，每折使用早停防止过拟合。"""
    kfold = KFold(n_splits=cv, shuffle=True, random_state=RANDOM_STATE)
    fold_scores = []
    fold_r2 = []

    for train_idx, valid_idx in kfold.split(X):
        model = lgb.LGBMRegressor(**params, random_state=RANDOM_STATE, n_jobs=-1, verbosity=-1)
        model.fit(
            X.iloc[train_idx],
            y.iloc[train_idx],
            eval_set=[(X.iloc[valid_idx], y.iloc[valid_idx])],
            callbacks=[lgb.early_stopping(50, verbose=False)],
        )
        pred = model.predict(X.iloc[valid_idx])
        y_valid = y.iloc[valid_idx]
        fold_scores.append(rmse_score(y_valid, pred))
        fold_r2.append(r2_score(y_valid, pred))

    fold_scores = np.array(fold_scores)
    return fold_scores, fold_scores.mean(), fold_scores.std(), float(np.mean(fold_r2))


def get_models():
    """定义基线模型与扩展模型。"""
    return {
        "DecisionTree": DecisionTreeRegressor(random_state=RANDOM_STATE, max_depth=10),
        "RandomForest": RandomForestRegressor(
            n_estimators=200,
            max_depth=12,
            min_samples_leaf=3,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "LightGBM": {
            "n_estimators": 5000,
            "learning_rate": 0.03,
            "num_leaves": 31,
            "max_depth": 6,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
            "min_child_samples": 20,
        },
    }


def save_submission(model, X_test, filename):
    """生成 Kaggle 提交文件。"""
    test_id = pd.read_csv(os.path.join(DATA_DIR, "test.csv"))["Id"]
    pred = np.expm1(model.predict(X_test))
    submission = pd.DataFrame({"Id": test_id, "SalePrice": pred})
    submission.to_csv(os.path.join(RESULTS_DIR, filename), index=False)


def train_and_compare():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    X_train, X_test, y_train = load_processed_data()
    models = get_models()
    summary = []

    print("\n====== 十折交叉验证实验 ======\n")
    for name, spec in models.items():
        print(f"正在评估 {name}...")
        start = time.time()

        if name == "LightGBM":
            folds, mean_rmse, std_rmse, r2_mean = evaluate_lgb_with_early_stopping(X_train, y_train, spec)

            # 使用 10% 验证集做早停，再在全量训练集上复训
            X_tr, X_val, y_tr, y_val = train_test_split(
                X_train, y_train, test_size=0.1, random_state=RANDOM_STATE
            )
            model = lgb.LGBMRegressor(**spec, random_state=RANDOM_STATE, n_jobs=-1, verbosity=-1)
            model.fit(
                X_tr,
                y_tr,
                eval_set=[(X_val, y_val)],
                callbacks=[lgb.early_stopping(50, verbose=False)],
            )
            best_iter = model.best_iteration_ or spec["n_estimators"]
            final_model = lgb.LGBMRegressor(
                **{**spec, "n_estimators": best_iter},
                random_state=RANDOM_STATE,
                n_jobs=-1,
                verbosity=-1,
            )
            final_model.fit(X_train, y_train)
            joblib.dump(final_model, os.path.join(RESULTS_DIR, "lgb_model.pkl"))
            save_submission(final_model, X_test, "submission_lightgbm.csv")
        else:
            folds, mean_rmse, std_rmse, r2_mean = evaluate_model(spec, X_train, y_train)
            spec.fit(X_train, y_train)
            save_submission(spec, X_test, f"submission_{name.lower()}.csv")

        elapsed = time.time() - start
        result = {
            "model": name,
            "mean_rmsle": float(mean_rmse),
            "std_rmsle": float(std_rmse),
            "r2": None if r2_mean is None else float(r2_mean),
            "time_sec": round(elapsed, 2),
            "fold_scores": [round(float(x), 5) for x in folds],
        }
        summary.append(result)

        r2_text = f", R² = {r2_mean:.4f}" if r2_mean is not None else ""
        print(f"  RMSLE = {mean_rmse:.5f} (+/- {std_rmse:.5f}){r2_text}, 耗时 {elapsed:.1f}s")
        print(f"  各折结果: {result['fold_scores']}\n")

    print("====== 实验结果汇总 ======")
    print(f"{'模型':<15} | {'RMSLE':<12} | {'R²':<8} | {'耗时(s)':<8}")
    print("-" * 55)
    for item in summary:
        r2_text = f"{item['r2']:.4f}" if item["r2"] is not None else "N/A"
        print(f"{item['model']:<15} | {item['mean_rmsle']:<12.5f} | {r2_text:<8} | {item['time_sec']:<8}")

    with open(os.path.join(RESULTS_DIR, "experiment_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("\n实验完成。结果已保存至 results/ 目录。")


if __name__ == "__main__":
    train_and_compare()
