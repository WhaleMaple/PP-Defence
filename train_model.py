import os
import joblib
import random
import numpy as np
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler

MODEL_DIR = "models"
if not os.path.exists(MODEL_DIR): os.makedirs(MODEL_DIR)

def train():
    print("提高包容度")
    X_train = []

    # 模擬 2000 筆更具多樣性的正常流量
    for _ in range(2000):
        # [Key敏感詞數, 全文敏感詞數, 符號比例, 嵌套深度]
        X_train.append([
            0,                             # Key 絕對不能有攻擊詞
            random.randint(0, 1),          # 允許全文偶爾出現 1 個關鍵字
            random.uniform(0.05, 0.45),    # 符號比提高到 0.45
            random.randint(1, 6)           # 嵌套深度提高到 6 層
        ])
    
    # 手動加入一些「極端複雜但正常」的邊界樣本
    X_train.append([0, 2, 0.5, 8]) 

    X_train = np.array(X_train)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    
    # 調整 OneClassSVM 參數：
    # nu 稍微增加到 0.02，這會讓邊界稍微「軟」化一點，減少誤判
    clf = OneClassSVM(kernel='rbf', gamma='scale', nu=0.02)
    clf.fit(X_scaled)
    
    joblib.dump(clf, os.path.join(MODEL_DIR, "pp_owa_svm.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))
    print(f"模型邊界擴張完成！樣本數: {len(X_train)}")

if __name__ == "__main__":
    train()