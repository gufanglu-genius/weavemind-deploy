"""
织觉引擎 — AI视觉素材生成
用千问API生成高质量装饰素材，提升产品视觉效果
"""
import requests, time, os, json

API_KEY = "sk-ws-H.RPLXLRI.9MeJ.MEUCIQCufXQMexCjUnKnw9haLk8xnSgHuhZ7mXjTkKgNNd0mHAIgDfY-v5vB1-_MTHu1zq2eCfaGuXa2a3_yRKQQRoQVSlk"
OUT = os.path.join(os.path.dirname(__file__), "generated-assets")
os.makedirs(OUT, exist_ok=True)

ASSETS = [
    {
        "name": "hero-textile",
        "prompt": "abstract textile art, flowing silk fabric waves, warm golden and indigo blue gradient, soft studio lighting, luxury home textile aesthetic, minimalist composition, 8k ultra detailed",
        "desc": "Hero区背景 — 丝绸波浪抽象画"
    },
    {
        "name": "pattern-blue-calcio",
        "prompt": "seamless tileable pattern, Chinese indigo blue calico, white floral and bird motifs on deep blue background, traditional folk art, clean vector style, textile print design, 8k",
        "desc": "蓝印花布纹样 — 装饰图案"
    },
    {
        "name": "pattern-tie-dye",
        "prompt": "abstract tie-dye textile pattern, indigo blue and white circular mandala, organic shibori resist dye, handcrafted texture, warm earth tones, seamless design, 8k",
        "desc": "扎染纹样 — 装饰图案"
    },
    {
        "name": "workspace-preview",
        "prompt": "luxury living room interior with beautiful linen curtains, warm natural light, modern minimalist furniture, soft earth tone palette, professional interior photography, 8k",
        "desc": "空间预览示例 — 客厅场景"
    },
    {
        "name": "trend-abstract",
        "prompt": "abstract data visualization art, flowing lines and dots connected, warm gold and cool blue gradient, dark background, futuristic textile trend visualization, minimal, 8k",
        "desc": "趋势可视化 — 抽象数据艺术"
    },
    {
        "name": "dna-helix",
        "prompt": "abstract DNA double helix made of colorful silk threads, warm golden light, textile fiber aesthetic, 8 color dimensions represented as flowing threads, dark elegant background, 8k",
        "desc": "审美DNA — 丝线双螺旋"
    }
]

def generate(prompt, name):
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }
    body = {
        "model": "wanx2.1-t2i-turbo",
        "input": {"prompt": prompt},
        "parameters": {"size": "1024*1024", "n": 1}
    }
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
    print("  ⏰ Timeout")
    return None

if __name__ == "__main__":
    print("🎨 织觉引擎 — AI视觉素材生成")
    print(f"输出目录: {OUT}\n")
    results = []
    for a in ASSETS:
        print(f"[{a['desc']}]")
        path = generate(a["prompt"], a["name"])
        results.append({"name": a["name"], "desc": a["desc"], "path": path})
        print()

    print("═" * 40)
    ok = sum(1 for r in results if r["path"])
    print(f"完成: {ok}/{len(results)} 张素材生成成功")
