import json
import os

def generate_dataset():
    # 1. 正常樣本 (增加混淆項與複雜結構)
    benign_samples = [
        {"user": "alice", "age": 25},
        {"settings": {"theme": "dark", "language": "en"}},
        {"items": [1, 2, 3], "status": "ok"},
        # 混淆項：包含敏感字眼但結構安全的正常流量
        {"comment": "How to use __proto__ in JS safely?"},
        {"path": "configs/system.constructor.json"},
        {"search": "constructor property tutorial"},
        {"id": "user_123", "meta": {"tags": ["admin", "root"]}},
        {"note": "The prototype of this object is null"},
        {"email": "proto_user@example.com"}
    ] * 250  # 擴展樣本數

    # 2. 攻擊樣本 (混合 PP, XSS, RCE)
    attack_samples = [
        # 原型污染 (PP)
        {"__proto__": {"admin": True}},
        {"constructor": {"prototype": {"polluted": "yes"}}},
        # XSS
        {"name": "<script>alert(1)</script>"},
        {"img": "<img src=x onerror=alert(1)>"},
        # RCE / Injection
        {"cmd": "require('child_process').exec('ls')"},
        {"sql": "SELECT * FROM users WHERE id = '1' OR '1'='1'"}
    ] * 250

    dataset = []
    for s in benign_samples:
        dataset.append({"data": s, "label": 0})
    for s in attack_samples:
        dataset.append({"data": s, "label": 1})

    os.makedirs("data", exist_ok=True)
    with open("data/dataset.json", "w") as f:
        json.dump(dataset, f)
    print(f"成功生成數據集：共 {len(dataset)} 筆樣本")

if __name__ == "__main__":
    generate_dataset()