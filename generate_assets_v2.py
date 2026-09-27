"""
织觉引擎 — AI视觉素材第二轮（优化版）
根据千问VL分析反馈优化prompt
"""
import requests, time, os

API_KEY = "sk-ws-H.RPLXLRI.9MeJ.MEUCIQCufXQMexCjUnKnw9haLk8xnSgHuhZ7mXjTkKgNNd0mHAIgDfY-v5vB1-_MTHu1zq2eCfaGuXa2a3_yRKQQRoQVSlk"
OUT = os.path.join(os.path.dirname(__file__), "generated-assets")

ASSETS = [
    {
        "name": "hero-textile-v2",
        "prompt": "flowing silk fabric waves, strong contrast between deep indigo blue and warm golden orange, soft luminous highlights on fabric texture, clean minimalist composition with generous negative space, luxury home textile brand aesthetic, subtle elegant folds, professional studio lighting, 8k ultra detailed, cinematic mood",
        "desc": "Hero背景v2 — 高对比丝绸"
    },
    {
        "name": "ich-fusion-preview",
        "prompt": "modern luxury living room interior, floor-to-ceiling windows with beautiful blue calico inspired curtains, traditional Chinese indigo blue and white pattern on modern curtain design, warm afternoon light, minimalist furniture, professional interior photography, 8k",
        "desc": "非遗融合预览 — 蓝印花布窗帘"
    },
    {
        "name": "aesthetic-dna-viz",
        "prompt": "abstract visualization of 8-dimensional aesthetic DNA, eight flowing colorful silk threads converging into a central point, each thread a different color representing warmth, saturation, pattern, texture, modernity, weight, luminosity, organic, dark elegant background, data art, 8k",
        "desc": "8维DNA可视化"
    },
    {
        "name": "nantong-heritage",
        "prompt": "aerial view of Nantong textile factory district, traditional Chinese architecture mixed with modern buildings, river flowing through, soft golden hour light, cinematic wide shot, warm color palette, 8k photography",
        "desc": "南通家纺产业带"
    }
]

def generate(prompt, name):
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "X-DashScope-Async": "enable"}
    body = {"model": "wanx2.1-t2i-turbo", "input": {"prompt": prompt}, "parameters": {"size": "1024*1024", "n": 1}}
    r = requests.post(url, headers=headers, json=body, timeout=30)
    r.raise_for_status()
    task_id = r.json()["output"]["task_id"]
    print(f"  Task: {task_id}")

    poll_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
    poll_headers = {"Authorization": f"Bearer {API_KEY}"}
    for _ in range(90):
        time.sleep(3)
        r = requests.get(poll_url, headers=poll_headers, timeout=15)
        data = r.json()
        status = data.get("output", {}).get("task_status", "")
        if status == "SUCCEEDED":
            img_url = data["output"]["results"][0]["url"]
            img_data = requests.get(img_url, timeout=30).content
            out_path = os.path.join(OUT, f"{name}.png")
            with open(out_path, "wb") as f:
                f.write(img_data)
            print(f"  ✅ {out_path} ({len(img_data)//1024}KB)")
            return out_path
        elif status in ("FAILED", "UNKNOWN"):
            print(f"  ❌ {status}")
            return None
    return None

if __name__ == "__main__":
    print("🎨 织觉引擎 — AI素材第二轮（VL优化版）\n")
    for a in ASSETS:
        print(f"[{a['desc']}]")
        generate(a["prompt"], a["name"])
        print()
    print("完成！")