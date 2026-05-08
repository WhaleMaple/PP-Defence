import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import os

os.makedirs("models", exist_ok=True)

def generate_multiclass_data():
    print("正在生成【7 維度進階版】訓練數據 (包含關聯距離特徵)...")
    # 特徵維度: [PP關鍵字, SQLi關鍵字, XSS關鍵字, LFI關鍵字, 符號密度, JSON深度, 關聯距離]
    # 關聯距離 (dist): 越小代表越危險 (關鍵字緊貼著特殊符號)，999 代表安全 (找不到配對)
    
    # 0: 正常流量 (特徵乾淨，距離極遠 999)
    benign = np.random.normal(loc=[0, 0, 0, 0, 0.05, 1.0, 999.0], scale=[0.1, 0.1, 0.1, 0.1, 0.02, 0.5, 0.0], size=(6000, 7))
    
    # 1: PP (高 PP關鍵字, 高 深度, 距離 999)
    pp = np.random.normal(loc=[2.0, 0, 0, 0, 0.1, 4.0, 999.0], scale=[0.5, 0.1, 0.1, 0.1, 0.05, 1.0, 0.0], size=(2000, 7))
    
    # 2: SQLi (高 SQLi關鍵字, 高 符號密度, 淺 深度, 距離極短 < 10)
    sqli = np.random.normal(loc=[0, 2.0, 0, 0, 0.3, 1.0, 5.0], scale=[0.1, 0.5, 0.1, 0.1, 0.1, 0.2, 3.0], size=(2000, 7))
    
    # 3: XSS (高 XSS關鍵字, 高 符號密度, 淺 深度, 距離極短 < 5)
    xss = np.random.normal(loc=[0, 0, 2.0, 0, 0.25, 1.0, 3.0], scale=[0.1, 0.1, 0.5, 0.1, 0.1, 0.2, 2.0], size=(2000, 7))
    
    # 4: LFI (高 LFI關鍵字, 中 符號密度, 淺 深度, 距離 999)
    lfi = np.random.normal(loc=[0, 0, 0, 2.0, 0.15, 1.0, 999.0], scale=[0.1, 0.1, 0.1, 0.5, 0.05, 0.2, 0.0], size=(2000, 7))
    
    # 合併數據並確保特徵值不為負數
    all_data = np.vstack([benign, pp, sqli, xss, lfi])
    all_data = np.clip(all_data, 0, None) 
    
    labels = np.concatenate([
        np.zeros(6000), # 0 (增加正常流量的樣本數，強化防誤判能力)
        np.ones(2000),  # 1
        np.full(2000, 2), # 2
        np.full(2000, 3), # 3
        np.full(2000, 4)  # 4
    ])
    
    df = pd.DataFrame(all_data, columns=['pp_kw', 'sqli_kw', 'xss_kw', 'lfi_kw', 'syntax', 'depth', 'dist'])
    df['label'] = labels
    return df.sample(frac=1).reset_index(drop=True)

df = generate_multiclass_data()
X = df.drop('label', axis=1)
y = df['label']

# 訓練 Random Forest
model = RandomForestClassifier(
    n_estimators=100,
    class_weight={0: 5.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0}, # 加重正常流量的權重
    max_depth=8, # 稍微加深樹的深度以學習更複雜的 7 維特徵
    random_state=42
)

model.fit(X.values, y)

print("\n模型訓練完成！訓練集分類報告：")
print(classification_report(y, model.predict(X.values), target_names=['Benign', 'PP', 'SQLi', 'XSS', 'LFI']))

MODEL_PATH = "models/rf_multiclass_model.pkl"
joblib.dump(model, MODEL_PATH)
print(f"7 維度多類別模型已成功儲存至 {MODEL_PATH}")