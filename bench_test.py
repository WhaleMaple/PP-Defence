import requests

TARGET_URL = "http://localhost:5000/api/merge"

def run_real_json_bench():
    print("開始真實 Server-Side JSON 基準測試...")

    # 這些才是真正針對 Express + lodash.merge 的 JSON 攻擊載荷
    real_pocs = [
        # 基本款原型污染
        {"__proto__": {"admin": True}},
        {"constructor": {"prototype": {"polluted": "yes"}}},
        
        # 隱蔽與變體款 (測試模型的泛化能力)
        {"user": "test", "data": {"__proto__": {"role": "admin"}}},
        {"\u005f\u005fproto\u005f\u005f": {"bypass": 1}},
        
        # 深層嵌套污染
        {"a": {"b": {"c": {"__proto__": {"deep_pollute": True}}}}},
        
        # 針對 Node.js 內部環境的進階污染嘗試
        {"__proto__": {"env": "NODE_OPTIONS='--require malicious.js'"}},
        {"constructor": {"prototype": {"outputFunctionName": "a; return global.process.mainModule.constructor._load('child_process').execSync('whoami'); //"}}}
    ]

    success_count = 0
    total_count = len(real_pocs)

    for i, payload in enumerate(real_pocs):
        try:
            response = requests.post(TARGET_URL, json=payload, timeout=2)
            # 如果 Proxy 成功抓到並回傳 403
            if response.status_code == 403:
                success_count += 1
            else:
                print(f"[漏失] Payload {i+1}: {payload}")
        except Exception as e:
            print(f"請求失敗: {e}")

    recall = (success_count / total_count) * 100 if total_count > 0 else 0

    print("\n" + "="*40)
    print("實驗數據總結 (Server-Side JSON Benchmark)")
    print(f"🔹 總測試樣本數: {total_count}")
    print(f"🔹 成功攔截數量: {success_count}")
    print(f"🔹 ML 召回率 (Recall): {recall:.2f}%")
    print("="*40)

if __name__ == "__main__":
    run_real_json_bench()