const express = require('express');
const merge = require('lodash.merge');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json({limit: '10mb'}));

// PP漏洞API
app.post('/api/merge', (req, res) => {
  const defaults = {admin: false, info: {name: 'user'}};
  merge(defaults, req.body);  // 漏洞
  res.json({success: true, data: defaults});
});

app.get('/health', (req, res) => res.json({status: 'PP網站運行中'}));
app.listen(3000, () => console.log('PP網站: http://localhost:3000'));