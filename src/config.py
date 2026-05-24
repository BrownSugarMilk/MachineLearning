"""项目路径与全局配置。"""
import os

# 以 src/ 为基准，定位项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")

RANDOM_STATE = 42
CV_FOLDS = 10
