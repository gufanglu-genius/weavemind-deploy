# 织觉引擎 WeaveMind

AI驱动的家纺审美计算与空间预览平台。

## 四大引擎

- **审美翻译器** `/translator` — 上传图片，解码8维审美DNA
- **基因编辑器** `/gene` — 拖拽滑块，秒级生成花型
- **空间感知引擎** `/spatial` — 上传房间照片，预览真实搭配效果
- **趋势先知** `/trend` — 6维信号融合，预测未来6个月趋势

## 本地运行

```bash
pip install -r requirements.txt
python app.py
```

访问 http://localhost:10000

## 环境变量

- `DASHSCOPE_API_KEY` — 阿里云DashScope API密钥（千问VL + 万相文生图）