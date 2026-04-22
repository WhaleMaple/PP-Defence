import os
import requests

# ================= 配置區 =================
TARGET_URL = "http://localhost:5000/api/merge"
BASE_DIR = "client-side-prototype-pollution"
# =========================================

def run_bench():
    success_count = 0
    total_count = 0
    
    if not os.path.exists(BASE_DIR):
        print(f"找不到目錄: {BASE_DIR}")
        return

    print(f"開始全量基準測試 (Real Web Test)...")
    
    # 使用 os.walk 進行遞迴搜尋
    for root, dirs, files in os.walk(BASE_DIR):
        # 排除 git 相關目錄
        if '.git' in root:
            continue
            
        for filename in files:
            # 抓取所有資料夾下的 .md 攻擊樣本
            if filename.endswith(".md"):
                file_path = os.path.join(root, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().strip()
                        if not content or len(content) < 10:
                            continue
                        
                        total_count += 1
                        payload = {
                            "source_file": file_path,
                            "content": content
                        }
                        
                        response = requests.post(TARGET_URL, json=payload, timeout=2)
                        
                        if response.status_code == 403:
                            success_count += 1
                        else:
                            print(f"[漏失] {file_path}")
                            
                except Exception as e:
                    continue

    recall = (success_count / total_count) * 100 if total_count > 0 else 0
    
    print("\n" + "="*40)
    print("實驗數據總結 (RealWebTest - Full Scan)")
    print(f"🔹 總測試樣本數: {total_count}")
    print(f"🔹 成功攔截數量: {success_count}")
    print(f"🔹 ML 召回率 (Recall): {recall:.2f}%")
    print("="*40)

if __name__ == "__main__":
    run_bench()