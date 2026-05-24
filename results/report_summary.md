# 实验结果摘要（与 report.md 对应）

生成时间：2026-05-24 16:38:11

## 表 5-1 三种模型十折交叉验证结果对比

| 模型 | 平均 RMSLE | 标准差 | R² | 耗时(s) |
|------|-----------|--------|-----|---------|
| 决策树 | 0.2010 | 0.0262 | 0.7357 | 1.42 |
| 随机森林 | 0.1398 | 0.0234 | 0.8724 | 7.54 |
| LightGBM | 0.1243 | 0.0203 | 0.8993 | 13.52 |

## 表 5-2 LightGBM 十折交叉验证各折 RMSLE

| 折次 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|------|---|---|---|---|---|---|---|---|---|---|
| RMSLE | 0.1217 | 0.1454 | 0.1025 | 0.1205 | 0.1488 | 0.1391 | 0.1402 | 0.1114 | 0.1318 | 0.0811 |

## 5.4 特征重要性 Top 5

| 排名 | 特征 | 重要性 |
|------|------|--------|
| 1 | TotalSF | 461 |
| 2 | LotArea | 405 |
| 3 | OverallCond | 278 |
| 4 | GrLivArea | 272 |
| 5 | BsmtFinSF1 | 268 |

## 输出文件清单

- `experiment_summary.json`：完整 JSON 结果
- `submission_decisiontree.csv` / `submission_randomforest.csv` / `submission_lightgbm.csv`：Kaggle 提交文件
- `lgb_model.pkl`：LightGBM 最终模型
- `feature_importance_lgb.png`：特征重要性图
- `model_comparison.png`：模型对比图
- `prediction_scatter.png`：预测散点图
