import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

# 建立 models 資料夾
os.makedirs("models", exist_ok=True)

def generate_data():
    print("正在生成訓練數據...")
    # 攻擊樣本 (特徵明顯)
    malicious = np.random.normal(loc=[1.0, 0.15, 2.0, 3.0], scale=0.05, size=(5000, 4))
    # 正常樣本 (特徵乾淨)
    normal = np.random.normal(loc=[0.0, 0.05, 0.0, 1.0], scale=0.02, size=(5000, 4))
    
    df_m = pd.DataFrame(malicious, columns=['v1', 'v2', 'v3', 'v4'])
    df_m['label'] = 1 # 1為攻擊
    
    df_n = pd.DataFrame(normal, columns=['v1', 'v2', 'v3', 'v4'])
    df_n['label'] = 0 # 0為正常
    
    return pd.concat([df_m, df_n]).sample(frac=1).reset_index(drop=True)

df = generate_data()
X = df.drop('label', axis=1)
y = df['label']

# 訓練 Random Forest (給正常樣本 10倍 權重，強迫降低誤判)
model = RandomForestClassifier(
    n_estimators=100,
    class_weight={0: 10.0, 1: 1.0},
    max_depth=5,
    random_state=42
)
model.fit(X.values, y)

# 儲存新模型
MODEL_PATH = "models/rf_model.pkl"
joblib.dump(model, MODEL_PATH)
print(f"✅ 模型已成功儲存至 {MODEL_PATH} (不需要 Scaler)")