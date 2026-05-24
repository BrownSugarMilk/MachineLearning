# 基于 LightGBM 的房价预测

华中科技大学研究生《高级机器学习理论》课程项目，使用 Kaggle [House Prices](https://www.kaggle.com/c/house-prices-advanced-regression-techniques) 竞赛数据集，对比决策树、随机森林与 LightGBM 三种模型的预测效果。

## 环境配置

- Python 3.10+
- 依赖见 `requirements.txt`

```bash
python -m venv my_venv
source my_venv/bin/activate   # Windows: my_venv\Scripts\activate
pip install -r requirements.txt
```

## 数据说明

原始数据位于 `data/` 目录：

| 文件 | 说明 |
|------|------|
| `train.csv` | 训练集（1460 条） |
| `test.csv` | 测试集（1459 条） |
| `sample_submission.csv` | 提交格式样例 |

数据来源：[Kaggle House Prices 竞赛](https://www.kaggle.com/c/house-prices-advanced-regression-techniques/data)

项目地址：https://github.com/BrownSugarMilk/MachineLearning

## 运行流程

**推荐：一键运行（自动完成预处理、训练、可视化与结果摘要生成）**

```bash
# Linux / macOS
python run.py
# 或
bash run.sh

# Windows
python run.py
# 或双击 run.bat
```

也可分步执行：

```bash
python src/data_process.py
python src/model_train.py
python src/visualization.py
python src/fill_report_docx.py   # 将 report.md 内容填入 Word 模板，生成 report.docx
```

## 目录结构

```
ML/
├── data/                  # 原始与清洗后的数据
├── results/               # 模型、提交文件、实验结果与图表
├── src/
│   ├── config.py          # 路径与全局配置
│   ├── data_process.py    # 数据预处理
│   ├── model_train.py     # 模型训练与评估
│   ├── visualization.py   # 结果可视化
│   └── report_export.py   # 报告结果摘要导出
├── run.py                 # 一键运行入口（推荐）
├── run.sh / run.bat       # 脚本入口（Linux/macOS / Windows）
├── requirements.txt
├── report.md              # 课程报告
└── README.md
```

## 输出文件

- `results/report_summary.md`：与 report.md 对应的实验结果摘要
- `results/feature_importance_top5.json`：Top 5 特征重要性
- `results/submission_*.csv`：各模型 Kaggle 提交文件
- `results/feature_importance_lgb.png`：LightGBM 特征重要性
- `results/model_comparison.png`：模型性能对比图
- `results/prediction_scatter.png`：预测值-真实值散点图

## 评价指标

- 交叉验证：RMSLE（对数变换后标签的 RMSE）
- Kaggle 官方：RMSLE（Root Mean Squared Logarithmic Error）
