import requests
import random
import time
import string

# ================= 配置區 =================
TARGET_URL = "http://localhost:5000/api/merge"
TOTAL_REQUESTS = 10000 
# =========================================

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def run_fuzzer():
    print(f"測試...")
    
    start_time = time.time()
    attack_count = 0
    attack_blocked = 0
    normal_count = 0
    false_positives = 0 # 誤判次數

    seeds = ["__proto__", "constructor", "prototype"]
    
    for i in range(TOTAL_REQUESTS):
        # 決定這筆是攻擊還是正常流量
        is_attack = random.random() > 0.5
        
        if is_attack:
            attack_count += 1
            key = random.choice(seeds)
            # 攻擊：將關鍵字放入敏感位置
            payload = { "user": { key: { "admin": True } }, "data": generate_random_string(20) }
        else:
            normal_count += 1
            # 正常流量：故意包含敏感字眼，但作為普通字串內容 (測試模型智慧度)
            fake_out = random.choice([
                f"I love this new prototype of my project",
                f"The constructor of this building is famous",
                f"Ordinary data with {generate_random_string(5)}",
                f"Long data: " + "A" * 500  # 測試長度特徵是否造成誤報
            ])
            payload = { "comment": fake_out, "status": "active" }

        try:
            response = requests.post(TARGET_URL, json=payload, timeout=2)
            
            if is_attack:
                if response.status_code == 403:
                    attack_blocked += 1
            else:
                if response.status_code == 403:
                    # 這裡是誤判！明明是正常流量卻被攔截
                    false_positives += 1
                    # print(f"⚠️ [誤判] 正常內容被攔截: {payload['comment'][:30]}...")

        except Exception as e:
            continue

        if (i + 1) % 500 == 0:
            print(f"已完成 {i + 1} 筆...")

    end_time = time.time()
    duration = end_time - start_time
    
    # --- 數據計算 ---
    recall = (attack_blocked / attack_count) * 100 if attack_count > 0 else 0
    fp_rate = (false_positives / normal_count) * 100 if normal_count > 0 else 0
    
    print("\n" + "="*40)
    print("測試報告 (Final Stress Test)")
    print(f"🔹 總請求數: {TOTAL_REQUESTS}")
    print(f"🔹 攻擊樣本數: {attack_count} | 攔截數: {attack_blocked}")
    print(f"🔹 正常樣本數: {normal_count} | 誤判數: {false_positives}")
    print("-" * 20)
    print(f"召回率 (Recall): {recall:.2f}%")
    print(f"誤判率 (False Positive Rate): {fp_rate:.2f}%")
    print(f"平均延遲: {(duration/TOTAL_REQUESTS)*1000:.2f} ms/req")
    print("="*40)

if __name__ == "__main__":
    run_fuzzer()