import requests
import json
import time

TARGET_URL = "http://localhost:5000/api/merge"

def run_github_cve_test():
    print("啟動真實世界 CVE 漏洞與 GitHub Payload 挑戰測試...\n")

    # 這些是真實世界中被用來打穿 Node.js 與 lodash 的經典 Payload
    real_world_payloads = [
        # 1. 經典 Lodash CVE-2018-16487 變體 (PayloadsAllTheThings)
        {
            "name": "CVE-2018-16487 (Basic)",
            "payload": {"__proto__": {"oops": "It works !"}}
        },
        # 2. 繞過簡單關鍵字檢查的構造 (常見於 GitHub 上的 CTF 腳本)
        {
            "name": "Constructor Prototype Bypass",
            "payload": {"constructor": {"prototype": {"isAdmin": True}}}
        },
        # 3. Lodash CVE-2019-10744 變體 (深層陣列污染)
        {
            "name": "CVE-2019-10744 (Array Path)",
            "payload": {"constructor": {"prototype": {"execPath": "/bin/bash"}}}
        },
        # 4. 針對 Express.js 結合 JSON 解析的污染
        {
            "name": "Express.js Parameter Pollution",
            "payload": {"__proto__": {"parameterLimit": 1}}
        },
        # 5. 結合 RCE (遠端代碼執行) 意圖的進階污染
        {
            "name": "RCE via Prototype Pollution",
            "payload": {"__proto__": {"env": "NODE_OPTIONS='--require child_process'"}}
        },
        # 6. Unicode 混淆繞過 (測試模型的抗干擾能力)
        {
            "name": "Unicode Obfuscation",
            "payload": {"\u005f\u005fproto\u005f\u005f": {"polluted": "yes"}}
        },
        # 7. 真實世界中常見的長 JSON 結構 (隱藏惡意屬性)
        {
            "name": "Deep Nested Payload",
            "payload": {
                "user": {"id": 12345, "preferences": {"theme": "dark", "notifications": True}},
                "metadata": {"version": "1.0", "source": "web"},
                "__proto__": {"admin": True} 
            }
        }
    ]

    # 模擬真實的正常流量 (長結構、包含敏感字眼但安全的請求)
    real_world_benign = [
        {
            "name": "Normal Deep JSON",
            "payload": {"app": {"config": {"features": {"beta_ui": True, "new_login": False}}}}
        },
        {
            "name": "Normal JSON with Sensitive Words (False Positive Test)",
            "payload": {"discussion": {"topic": "How to prevent __proto__ pollution", "author": "admin"}}
        }
    ]

    print("--- 攻擊樣本測試 (預期結果：Blocked) ---")
    tp = 0
    for item in real_world_payloads:
        try:
            res = requests.post(TARGET_URL, json=item["payload"], timeout=2)
            if res.status_code == 403:
                print(f"✅ 成功攔截: {item['name']}")
                tp += 1
            else:
                print(f"❌ 漏網之魚 (FN): {item['name']}")
        except Exception as e:
            print(f"連線失敗: {e}")
            
    print("\n--- 正常樣本測試 (預期結果：Success) ---")
    fp = 0
    for item in real_world_benign:
        try:
            res = requests.post(TARGET_URL, json=item["payload"], timeout=2)
            if res.status_code == 403:
                print(f"⚠️ 誤判攔截 (FP): {item['name']}")
                fp += 1
            else:
                print(f"✅ 正確放行: {item['name']}")
        except Exception as e:
            print(f"連線失敗: {e}")

    # 計算結果
    total_attacks = len(real_world_payloads)
    total_benign = len(real_world_benign)
    recall = (tp / total_attacks) * 100 if total_attacks > 0 else 0
    fp_rate = (fp / total_benign) * 100 if total_benign > 0 else 0

    print("\n" + "="*40)
    print("真實世界 GitHub 數據測試報告")
    print(f"🔹 測試 CVE/Payload 數量: {total_attacks}")
    print(f"🔹 成功防禦數量: {tp}")
    print(f"🔹 召回率 (Recall): {recall:.2f}%")
    print(f"🔹 誤判率 (FP Rate): {fp_rate:.2f}%")
    print("="*40)

if __name__ == "__main__":
    run_github_cve_test()