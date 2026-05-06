const express = require('express');
const merge = require('lodash.merge');
const cors = require('cors');
const app = express();

// 啟用 CORS 以允許跨來源請求
app.use(cors());

// 設定 JSON 解析限制，確保能接收較大的 Payload
app.use(express.json({limit: '10mb'}));

/**
 * 漏洞 API：/api/merge
 * 此處使用了具有原型污染（Prototype Pollution）漏洞的 lodash.merge
 * 攻擊者可以透過傳送特定的 JSON 來修改 Object.prototype
 */
app.post('/api/merge', (req, res) => {
  // 預設物件結構
  const defaults = {
    admin: false, 
    info: { name: 'user' }
  };

  try {
    // 執行合併操作，此處為漏洞發生點[cite: 1]
    merge(defaults, req.body); 
    
    // 回傳合併後的結果以供驗證[cite: 1]
    res.json({
      success: true, 
      data: defaults,
      // 增加一個檢查點，確認是否被污染
      isPolluted: ({}).polluted || "false" 
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 健康檢查接口[cite: 1]
app.get('/health', (req, res) => res.json({ status: 'PP網站運行中', timestamp: new Date() }));

// 伺服器啟動於 3000 埠[cite: 1]
// 注意：ml_proxy_2.py 會監聽 5000 埠並轉發至此處（或直接攔截）
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`[Target] PP標靶網站已啟動: http://localhost:${PORT}`);
});