import os
import json
import joblib
import numpy as np
from flask import Flask, request, jsonify

app = Flask(__name__)

# ================= 配置與模型載入 =================
MODEL_PATH = "models/pp_owa_svm.pkl"
SCALER_PATH = "models/scaler.pkl"

if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
    clf = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print("ML模型與縮放器載入成功")
else:
    clf, scaler = None, None
    print("找不到模型檔案，請先執行訓練腳本")

# ================= 混合特徵提取邏輯 =================

def extract_features(data):
    """
    特徵向量：[0:Key敏感詞數, 1:全文敏感詞數, 2:特殊符號比例, 3:最大嵌套深度]
    """
    features = [0, 0, 0, 0]
    sensitive_words = ['__proto__', 'constructor', 'prototype']
    
    raw_str = str(data).lower()
    
    # 特徵 1: 全文敏感詞出現次數 (捕捉藏在 Value 裡的攻擊)
    for word in sensitive_words:
        features[1] += raw_str.count(word)
    
    def recursive_scan(obj, depth):
        features[3] = max(features[3], depth)
        if isinstance(obj, dict):
            for k, v in obj.items():
                # 特徵 0: 專門檢查 Key (高風險特徵)
                for word in sensitive_words:
                    if word in str(k).lower():
                        features[0] += 1
                recursive_scan(v, depth + 1)
        elif isinstance(obj, list):
            for item in obj:
                recursive_scan(item, depth + 1)

    try:
        # 確保資料是 dict 格式進行結構掃描
        dict_data = data if isinstance(data, dict) else json.loads(data)
        recursive_scan(dict_data, 1)
    except:
        pass

    # 特徵 2: 符號比例
    if len(raw_str) > 0:
        special_chars = sum(1 for c in raw_str if c in '{}[].:,"\'\\')
        features[2] = special_chars / len(raw_str)

    return np.array(features).reshape(1, -1)

# ================= API 路由 =================

@app.route('/api/merge', methods=['POST'])
def ml_filter():
    if clf is None:
        return jsonify({"status": "error", "message": "Model not loaded"}), 500

    try:
        req_data = request.get_json()
        if not req_data:
            return jsonify({"status": "ignored"}), 200

        feat_vector = extract_features(req_data)
        scaled_feat = scaler.transform(feat_vector)
        prediction = clf.predict(scaled_feat)
        
        # Log 輸出便於除錯
        res_text = "正常" if prediction[0] == 1 else "異常 (攔截)"
        print(f"DEBUG - 特徵: {feat_vector.tolist()} | 預測: {res_text}")

        if prediction[0] == -1:
            return jsonify({"status": "blocked", "reason": "ML Anomaly Detected"}), 403

        return jsonify({"status": "success", "data": "OK"}), 200

    except Exception as e:
        print(f"處理錯誤: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)