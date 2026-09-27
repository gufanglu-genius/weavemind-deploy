"""生成南通非遗参考素材"""
import requests, time, os, sys

API_KEY = "sk-ws-H.RPLXLRI.9MeJ.MEUCIQCufXQMexCjUnKnw9haLk8xnSgHuhZ7mXjTkKgNNd0mHAIgDfY-v5vB1-_MTHu1zq2eCfaGuXa2a3_yRKQQRoQVSlk"
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "references", "nantong-ich")
os.makedirs(OUT, exist_ok=True)

PROMPTS = [
    {
        "name": "nantong_blue_calico",
        "prompt": "Nantong blue calico fabric, traditional Chinese indigo blue印花布, white patterns on deep blue background, floral and bird motifs, folk art textile, close-up detail, studio lighting, 8k",
        "desc": "南通蓝印花布"
    },
    {
        "name": "nantong_tubu_weaving",
        "prompt": "traditional Chinese handwoven cotton cloth, Nantong土布, earth tone stripes, natural cotton texture, rustic weave pattern, artisan textile, close-up, 8k",
        "desc": "南通土布纺织"
    },
    {
        "name": "nantong_shen_embroidery",
        "prompt": "Chinese Suzhou-style embroidery art, fine silk thread embroidery, delicate flower and bird pattern, Nantong沈绣, realistic needlework, close-up texture, 8k",
        "desc": "南通沈绣"
    },
    {
        "name": "nantong_kite_pattern",
        "prompt": "Nantong板鹞风筝 ornamental pattern, colorful geometric folk art, whistles and decorative motifs, traditional Chinese kite design, flat textile pattern, 8k",
        "desc": "南通板鹞风筝纹样"
    },
    {
        "name": "nantong_tie_dye",
        "prompt": "Chinese traditional tie-dye textile, indigo blue and white, circular mandala pattern, Nantong扎染, organic resist dye, fabric texture, close-up, 8k",
        "desc": "南通扎染"
    },
    {
        "name": "nantong_silk_weaving",
        "prompt": "traditional Chinese silk brocade, intricate cloud and crane pattern, gold thread on red background, Nantong丝绸织造, luxury textile, 8k",
        "desc": "南通丝绸织造"
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
    print(f"  Task created: {task_id}")

    # Poll
    poll_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
    poll_headers = {"Authorization": f"Bearer {API_KEY}"}
    for _ in range(60):
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
            print(f"  Saved: {out_path} ({len(img_data)} bytes)")
            return out_path
        elif status in ("FAILED", "UNKNOWN"):
            print(f"  FAILED: {status}")
            return None
    return None

if __name__ == "__main__":
    print("生成南通非遗参考素材...")
    for p in PROMPTS:
        print(f"\n[{p['desc']}]")
        generate(p["prompt"], p["name"])
    print("\n全部完成！")