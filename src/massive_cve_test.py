import requests
import random
import string
import time

TARGET_URL = "http://localhost:5000/api/merge"

# === 輔助函數：產生隨機字串與雜訊 ===
def random_str(length=5):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_garbage_nesting(depth, core_payload):
    # 產生無意義的深層嵌套來隱藏 Payload
    result = core_payload
    for _ in range(depth):
        result = {random_str(8): result}
    return result

# === 核心產生器 ===
def generate_attack_variants(num_samples=5000):
    payloads = []
    for _ in range(num_samples):
        # 隨機選擇一種污染路徑 (原型或建構子)
        path = random.choice([
            "__proto__", 
            "constructor", 
            "prototype", 
            "\u005f\u005fproto\u005f\u005f", # Unicode
            "__pro" + "to__" # 模擬某些解析器的組合
        ])
        
        # 隨機選擇污染目標與惡意值
        malicious_key = random.choice(["admin", "role", "env", "NODE_OPTIONS", "execPath", "polluted"])
        malicious_val = random.choice([True, 1, "admin", "/bin/bash", "require('child_process').execSync('id')"])
        
        # 構造核心 Payload
        if path == "constructor" or path == "prototype":
            core = {"constructor": {"prototype": {malicious_key: malicious_val}}}
        else:
            core = {path: {malicious_key: malicious_val}}
            
        # 隨機加入 0 到 4 層的雜訊包裝 (模擬真實業務的深層 JSON)
        variant = generate_garbage_nesting(random.randint(0, 4), core)
        # 隨機混入一些正常的 Key-Value 掩人耳目
        variant[random_str(5)] = random_str(10)
        
        payloads.append(variant)
    return payloads

def generate_benign_variants(num_samples=5000):
    payloads = []
    for _ in range(num_samples):
        # 產生複雜但安全的 JSON
        safe_payload = generate_garbage_nesting(random.randint(1, 5), {random_str(5): random_str(10)})
        
        # 刻意混入敏感字眼，但「不作為 Key」或「不構成原型鏈路徑」(測試誤判率)
        if random.random() > 0.5:
            safe_payload["description"] = f"This is an article about __proto__ and constructor"
        if random.random() > 0.8:
            safe_payload[random_str(15)] = "prototype" # 長 key 測試
            
        payloads.append(safe_payload)
    return payloads

# === 執行主程式 ===
def run_massive_test():
    print("真實 CVE 變體壓力測試...")
    
    attacks = generate_attack_variants(5000)
    benigns = generate_benign_variants(5000)
    
    tp = 0 # True Positive (成功攔截攻擊)
    fn = 0 # False Negative (漏網之魚)
    fp = 0 # False Positive (誤殺正常流量)
    tn = 0 # True Negative (正確放行正常流量)
    
    start_time = time.time()
    
    print("\n[1/2] 正在測試 5000 筆攻擊變體...")
    for i, p in enumerate(attacks):
        try:
            res = requests.post(TARGET_URL, json=p, timeout=1)
            if res.status_code == 403: tp += 1
            else: fn += 1
        except: pass
        if (i+1) % 1000 == 0: print(f"  已處理 {i+1} 筆...")

    print("\n[2/2] 正在測試 5000 筆正常/干擾變體...")
    for i, p in enumerate(benigns):
        try:
            res = requests.post(TARGET_URL, json=p, timeout=1)
            if res.status_code == 403: fp += 1
            else: tn += 1
        except: pass
        if (i+1) % 1000 == 0: print(f"  已處理 {i+1} 筆...")

    duration = time.time() - start_time
    total = tp + fn + fp + tn
    
    recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0
    fp_rate = (fp / (fp + tn)) * 100 if (fp + tn) > 0 else 0
    
    print("\n" + "="*45)
    print("變體防禦報告")
    print(f"🔹 總測試樣本數: {total} 筆")
    print("-" * 45)
    print(f"成功防禦 (TP): {tp}")
    print(f"遺漏 (FN): {fn}")
    print(f"正常被誤殺 (FP): {fp}")
    print(f"正確放行 (TN): {tn}")
    print("-" * 45)
    print(f"最終召回率 (Recall):  {recall:.2f}%")
    print(f"最終誤判率 (FP Rate): {fp_rate:.2f}%")
    print(f"⚡ 平均延遲: {(duration/total)*1000:.2f} ms/req")
    print("="*45)

if __name__ == "__main__":
    run_massive_test()