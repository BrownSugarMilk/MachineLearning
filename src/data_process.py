"""数据加载、特征工程与持久化。"""
import os

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer

from config import DATA_DIR

TRAIN_FILE = "train.csv"
TEST_FILE = "test.csv"

# 缺失值在业务上表示“无该项设施”
NONE_COLS = [
    "Alley", "PoolQC", "MiscFeature", "Fence", "FireplaceQu",
    "GarageType", "GarageFinish", "GarageQual", "GarageCond",
    "BsmtQual", "BsmtCond", "BsmtExposure", "BsmtFinType1", "BsmtFinType2",
    "MasVnrType", "MSSubClass",
]

# 缺失值在业务上表示“面积为 0 / 数量为 0”
ZERO_COLS = [
    "MasVnrArea", "BsmtFinSF1", "BsmtFinSF2", "BsmtUnfSF",
    "TotalBsmtSF", "BsmtFullBath", "BsmtHalfBath", "GarageYrBlt",
    "GarageArea", "GarageCars",
]

# 右偏数值特征，做对数变换以缓解长尾分布
SKEW_COLS = [
    "LotFrontage", "LotArea", "MasVnrArea", "BsmtFinSF1", "BsmtFinSF2",
    "BsmtUnfSF", "TotalBsmtSF", "1stFlrSF", "2ndFlrSF", "GrLivArea",
    "GarageArea", "WoodDeckSF", "OpenPorchSF", "EnclosedPorch",
    "3SsnPorch", "ScreenPorch", "PoolArea", "MiscVal",
]


def load_data():
    """加载原始 Kaggle 数据集。"""
    train = pd.read_csv(os.path.join(DATA_DIR, TRAIN_FILE))
    test = pd.read_csv(os.path.join(DATA_DIR, TEST_FILE))
    print(f"原始训练集形状: {train.shape}")
    print(f"原始测试集形状: {test.shape}")
    return train, test


def add_domain_features(df):
    """构造与房价强相关的组合特征。"""
    df = df.copy()
    df["TotalSF"] = (
        df["TotalBsmtSF"].fillna(0)
        + df["1stFlrSF"].fillna(0)
        + df["2ndFlrSF"].fillna(0)
    )
    df["TotalBath"] = (
        df["FullBath"].fillna(0)
        + 0.5 * df["HalfBath"].fillna(0)
        + df["BsmtFullBath"].fillna(0)
        + 0.5 * df["BsmtHalfBath"].fillna(0)
    )
    df["HouseAge"] = df["YrSold"] - df["YearBuilt"]
    df["RemodAge"] = df["YrSold"] - df["YearRemodAdd"]
    df["GarageAge"] = df["YrSold"] - df["GarageYrBlt"]
    df["GarageAge"] = df["GarageAge"].fillna(0)
    df["IsNewHouse"] = (df["YearBuilt"] == df["YrSold"]).astype(int)
    df["HasPool"] = (df["PoolArea"].fillna(0) > 0).astype(int)
    df["Has2ndFloor"] = (df["2ndFlrSF"].fillna(0) > 0).astype(int)
    return df


def fix_skewed_features(df):
    """对右偏特征做 log1p 变换。"""
    df = df.copy()
    for col in SKEW_COLS:
        if col in df.columns:
            df[col] = np.log1p(df[col].clip(lower=0))
    return df


def preprocess_data(train, test):
    """完整预处理流程：缺失值处理、特征工程、编码。"""
    y_train = np.log1p(train["SalePrice"])
    train = train.drop(["Id", "SalePrice"], axis=1)
    test = test.drop(["Id"], axis=1)

    ntrain = train.shape[0]
    all_data = pd.concat((train, test), axis=0).reset_index(drop=True)

    for col in NONE_COLS:
        if col in all_data.columns:
            all_data[col] = all_data[col].fillna("None")

    for col in ZERO_COLS:
        if col in all_data.columns:
            all_data[col] = all_data[col].fillna(0)

    numeric_cols = all_data.select_dtypes(include=[np.number]).columns
    imputer = SimpleImputer(strategy="median")
    all_data[numeric_cols] = imputer.fit_transform(all_data[numeric_cols])

    cat_cols = all_data.select_dtypes(include=["object"]).columns
    for col in cat_cols:
        all_data[col] = all_data[col].fillna(all_data[col].mode()[0])

    all_data = add_domain_features(all_data)
    all_data = fix_skewed_features(all_data)
    all_data = pd.get_dummies(all_data)

    train_processed = all_data.iloc[:ntrain].copy()
    test_processed = all_data.iloc[ntrain:].copy()

    print(f"处理后训练集形状: {train_processed.shape}")
    print(f"处理后测试集形状: {test_processed.shape}")
    return train_processed, test_processed, y_train


def save_processed_data(train_processed, test_processed, y_train):
    """保存清洗后的特征与标签。"""
    train_processed.to_csv(os.path.join(DATA_DIR, "train_clean.csv"), index=False)
    test_processed.to_csv(os.path.join(DATA_DIR, "test_clean.csv"), index=False)
    y_train.to_csv(os.path.join(DATA_DIR, "y_train_clean.csv"), index=False)


def main():
    print("正在加载数据...")
    train_raw, test_raw = load_data()

    print("正在进行数据清洗和特征工程...")
    train_final, test_final, y_final = preprocess_data(train_raw, test_raw)
    save_processed_data(train_final, test_final, y_final)

    print("数据预处理完成，文件已保存至 data/ 目录。")


if __name__ == "__main__":
    main()
