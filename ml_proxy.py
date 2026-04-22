from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
import joblib
import os

app = Flask(__name__)

class PPDetector:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.load_model()
    
    def load_model(self):
        if os.path.exists('data/ocsvm_model.pkl'):
            self.model = joblib.load('data/ocsvm_model.pkl')
            self.scaler = joblib.load('data/scaler.pkl')
            print("✅ ML模型載入")
        else:
            print("⚠️ 訓練模型: python train_model.py")
    
    def extract_features(self, data):
        return np.array([[
            len(data),  # 請求大小
            self.max_nest_depth(data),  # 巢狀深度
            data.count('__proto__') + data.count('constructor')  # PP特徵
        ]])
    
    def max_nest_depth(self, obj):
        if isinstance(obj, dict):
            return 1 + max((self.max_nest_depth(v) for v in obj.values()), default=0)
        return 0

detector = PPDetector()

@app.before_request
def detect_pp():
    if request.path == '/api/merge' and request.is_json:
        features = detector.extract_features(str(request.json))
        if detector.model is not None:
            pred = detector.model.predict(detector.scaler.transform(features))
            if pred[0] == -1:
                return jsonify({'error': 'PP攻擊阻擋!'}), 403
        print(f"特徵: {features.flatten()}")

@app.route('/api/merge', methods=['POST'])
def proxy_merge():
    return app.response_class('Proxy到Node.js', status=200)

if __name__ == '__main__':
    app.run(port=5000, debug=True)