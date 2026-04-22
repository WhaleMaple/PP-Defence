import pandas as pd
import numpy as np
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
import joblib
import os

# 1. 建立存放模型的資料夾
os.makedirs('data', exist_ok=True)

# 2. 模擬正常流量數據 (作為訓練基準)
# size: 請求大小, depth: JSON深度, proto_count: 關鍵字出現次數
np.random.seed(42)
normal_data = pd.DataFrame({
    'size': np.random.normal(500, 100, 1000),
    'depth': np.random.poisson(2, 1000),
    'proto_count': np.random.poisson(0, 1000)
})

# 3. 特徵標準化 (Standardization)
# 建立 Scaler 並「訓練 (fit)」它學習正常數據的分布
scaler = StandardScaler()
scaler.fit(normal_data) 

# 將數據轉換為模型可理解的格式
X_scaled = scaler.transform(normal_data)

# 4. 訓練 OneClassSVM 模型
# nu=0.1 代表預期有 10% 的數據可能是異常值
model = OneClassSVM(kernel='rbf', nu=0.1, gamma='auto')
model.fit(X_scaled)

# 5. 儲存模型與 Scaler (這步最重要，代理伺服器會讀取這兩個檔案)
joblib.dump(model, 'data/ocsvm_model.pkl')
joblib.dump(scaler, 'data/scaler.pkl')

print("模型訓練完成！")
print("已產生檔案：data/ocsvm_model.pkl, data/scaler.pkl")
print("訓練數據範例：")
print(normal_data.head())