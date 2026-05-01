import requests
import random
import time
import string
import json

# ================= 配置區 =================
TARGET_URL = "http://localhost:5000/api/merge"
TOTAL_REQUESTS = 10000
# =========================================

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_advanced_attack():
    """產生包含編碼與深度嵌套的變體攻擊"""
    seeds = ["__proto__", "constructor", "prototype"]
    # 混淆技巧：1.原樣 2.URL編碼 3.Unicode轉義
    obfuscations = [
        lambda x: x,
        lambda x: x.replace("_", "%5f"), 
        lambda x: "".join([f"\\u{ord(c):04x}" for c in x])
    ]
    
    target_key = random.choice(obfuscations)(random.choice(seeds))
    
    # 隨機產生 1-4 層的嵌套結構，增加掃描難度
    payload = {"timestamp": time.time(), "trace_id": generate_random_string(8)}
    curr = payload
    for _ in range(random.randint(1, 3)):
        new_key = generate_random_string(5)
        curr[new_key] = {}
        curr = curr[new_key]
    
    # 將攻擊載荷注入最深層
    curr[target_key] = {"polluted": "true", "role": "admin"}
    return payload

def run_fuzzer():
    print(f"啟動測試...")
    
    start_time = time.time()
    attack_count = 0
    attack_blocked = 0
    normal_count = 0
    false_positives = 0 

    for i in range(TOTAL_REQUESTS):
        is_attack = random.random() > 0.5
        
        if is_attack:
            attack_count += 1
            payload = generate_advanced_attack()
        else:
            normal_count += 1
            # 正常流量：故意包含敏感字眼但作為 Value (測試語義區分能力)
            fake_out = random.choice([
                f"Project status: active prototype phase",
                f"User requested a new constructor function",
                f"Regular data logging {generate_random_string(10)}",
                "A" * 300 # 長字串壓力
            ])
            payload = {"comment": fake_out, "metadata": {"tags": ["dev", "test"]}}

        try:
            # 傳送 JSON 請求
            response = requests.post(TARGET_URL, json=payload, timeout=2)
            
            if is_attack:
                if response.status_code == 403:
                    attack_blocked += 1
            else:
                if response.status_code == 403:
                    false_positives += 1

        except Exception:
            continue

        if (i + 1) % 1000 == 0:
            print(f"已完成 {i + 1} 筆 ")

    end_time = time.time()
    duration = end_time - start_time
    
    # --- 指標計算 ---
    recall = (attack_blocked / attack_count) * 100 if attack_count > 0 else 0
    fp_rate = (false_positives / normal_count) * 100 if normal_count > 0 else 0
    
    print("\n" + "="*40)
    print("測試報告")
    print(f"🔹 總請求數: {TOTAL_REQUESTS}")
    print(f"🔹 攻擊樣本 (含變體): {attack_count} | 攔截數: {attack_blocked}")
    print(f"🔹 正常樣本 (含混淆): {normal_count} | 誤判數: {false_positives}")
    print("-" * 20)
    print(f"召回率 (Recall): {recall:.2f}%")
    print(f"誤判率 (FP Rate): {fp_rate:.2f}%")
    print(f"平均延遲: {(duration/TOTAL_REQUESTS)*1000:.2f} ms/req")
    print("="*40)

if __name__ == "__main__":
    run_fuzzer()