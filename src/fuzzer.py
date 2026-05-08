import requests
import random
import time

def mutate_payload(payload_type):
    # 模擬變體攻擊
    pp_payloads = [
        {"__proto__": {"vulnerable": "true"}},
        {"__pRoTo__": {"case_bypass": "true"}},
        {"constructor": {"prototype": {"bypass": "1"}}},
        {"\u005f\u005fproto\u005f\u005f": {"unicode_bypass": "true"}}
    ]
    
    benign_payloads = [
        {"text": "Hello world"},
        {"tags": ["__proto__", "constructor"]}, # 容易導致誤判的正常流量
        {"content": {"depth1": {"depth2": {"depth3": "deep"}}}},
        {"user_id": random.randint(1, 10000)}
    ]

    if payload_type == "attack":
        return random.choice(pp_payloads)
    else:
        return random.choice(benign_payloads)

def run_fuzzer(total_reqs=10000):
    print("啟動強化版通用防禦能力測試 (含變體繞過)...")
    
    results = {"total": 0, "tp": 0, "fp": 0, "tn": 0, "fn": 0}
    start_time = time.time()

    for i in range(total_reqs):
        is_attack = random.choice([True, False])
        payload = mutate_payload("attack" if is_attack else "benign")
        
        try:
            # 透過 Proxy 傳送
            response = requests.post("http://localhost:5000/api/merge", json=payload, timeout=2)
            
            if is_attack:
                if response.status_code == 403: # 被攔截
                    results["tp"] += 1
                else: # 遺漏
                    results["fn"] += 1
            else:
                if response.status_code == 403: # 正常流量被誤殺
                    results["fp"] += 1
                else:
                    results["tn"] += 1
            
            results["total"] += 1
        except Exception as e:
            continue

        if (i + 1) % 1000 == 0:
            print(f"已完成 {i+1} 筆測試...")

    duration = time.time() - start_time
    
    print("\n" + "="*40)
    print("實驗結果：測試報告")
    print(f"🔹 總請求數: {results['total']}")
    print(f"🔹 成功攔截 (TP): {results['tp']}")
    print(f"🔹 遺漏 (FN): {results['fn']}")
    print(f"🔹 正常流量誤判 (FP): {results['fp']}")
    print("-" * 20)
    
    recall = (results["tp"] / (results["tp"] + results["fn"])) * 100 if (results["tp"] + results["fn"]) > 0 else 0
    fp_rate = (results["fp"] / (results["fp"] + results["tn"])) * 100 if (results["fp"] + results["tn"]) > 0 else 0
    
    print(f"召回率 (Recall): {recall:.2f}%")
    print(f"誤判率 (FP Rate): {fp_rate:.2f}%")
    print(f"平均延遲: {(duration/results['total'])*1000:.2f} ms/req")
    print("="*40)

if __name__ == "__main__":
    run_fuzzer()