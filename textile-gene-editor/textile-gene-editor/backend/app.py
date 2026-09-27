"""
织物基因编辑器 v2 — 上海大赛版
趋势驱动的AI花型生成引擎
"""
import os, json, time, base64, random
from datetime import datetime
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE = os.path.dirname(os.path.dirname(__file__))
FRONTEND = os.path.join(BASE, 'frontend')
GEN_DIR = os.path.join(BASE, 'generated')
META_DIR = os.path.join(BASE, 'metadata')
os.makedirs(GEN_DIR, exist_ok=True)
os.makedirs(META_DIR, exist_ok=True)

API_KEY = os.environ.get('DASHSCOPE_API_KEY', '')

# ============ DashScope API ============

def t2i_call(prompt, size="1024*1024", n=1):
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "X-DashScope-Async": "enable"}
    body = {"model": "wanx2.1-t2i-turbo", "input": {"prompt": prompt}, "parameters": {"size": size, "n": n}}
    r = requests.post(url, headers=headers, json=body, timeout=30)
    r.raise_for_status()
    return r.json()["output"]["task_id"]

def poll_task(task_id, timeout=120):
    url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    start = time.time()
    while time.time() - start < timeout:
        r = requests.get(url, headers=headers, timeout=15)
        data = r.json()
        status = data.get("output", {}).get("task_status", "")
        if status == "SUCCEEDED":
            return data["output"]["results"]
        elif status in ("FAILED", "UNKNOWN"):
            raise RuntimeError(f"Task {status}: {json.dumps(data, ensure_ascii=False)}")
        time.sleep(2)
    raise TimeoutError("Task timeout")

def save_img(url, name):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    path = os.path.join(GEN_DIR, name)
    with open(path, "wb") as f:
        f.write(r.content)
    return path

# ============ 纺织品基因库 ============

GENOME_DIMENSIONS = {
    "color_warmth":    {"name": "色彩温度",   "min": 0, "max": 100, "labels": ["冷调", "暖调"],     "icon": "🌡"},
    "saturation":      {"name": "饱和度",     "min": 0, "max": 100, "labels": ["素雅", "艳丽"],     "icon": "🎨"},
    "pattern_complex": {"name": "图案复杂度", "min": 0, "max": 100, "labels": ["极简", "繁复"],     "icon": "✦"},
    "texture_feel":    {"name": "织物肌理",   "min": 0, "max": 100, "labels": ["光滑", "粗糙"],     "icon": "🧶"},
    "style_modern":    {"name": "风格倾向",   "min": 0, "max": 100, "labels": ["传统", "现代"],     "icon": "⚡"},
    "material_weight": {"name": "材质厚薄",   "min": 0, "max": 100, "labels": ["轻薄", "厚重"],     "icon": "🪶"},
    "luminosity":      {"name": "光泽度",     "min": 0, "max": 100, "labels": ["哑光", "高光"],     "icon": "✨"},
    "organic_ratio":   {"name": "自然感",     "min": 0, "max": 100, "labels": ["人工", "天然"],     "icon": "🌿"}
}

DNA_PRESETS = {
    "wabi_sabi_gene": {
        "name": "侘寂基因", "desc": "自然朴素、手工质感、大地色调",
        "dna": {"color_warmth":70, "saturation":20, "pattern_complex":15, "texture_feel":75, "style_modern":30, "material_weight":55, "luminosity":15, "organic_ratio":90},
        "prompt_hint": "wabi-sabi linen curtain, natural undyed texture, earth tones, handwoven, imperfect beauty, minimalist",
        "related_trend": "wabi_sabi", "color": "#8b7d6b"
    },
    "dopamine_gene": {
        "name": "多巴胺基因", "desc": "高饱和、明亮撞色、快乐活力",
        "dna": {"color_warmth":65, "saturation":95, "pattern_complex":60, "texture_feel":25, "style_modern":85, "material_weight":30, "luminosity":70, "organic_ratio":15},
        "prompt_hint": "dopamine decor curtain, vibrant rainbow colors, gradient, high saturation, joyful, modern textile",
        "related_trend": "dopamine_home", "color": "#ff6b6b"
    },
    "quiet_lux_gene": {
        "name": "静奢基因", "desc": "低调奢华、高支纯色、触感高级",
        "dna": {"color_warmth":40, "saturation":10, "pattern_complex":5, "texture_feel":30, "style_modern":55, "material_weight":45, "luminosity":60, "organic_ratio":65},
        "prompt_hint": "quiet luxury curtain, pure cashmere texture, ivory and taupe, no pattern, ultra refined, subtle sheen",
        "related_trend": "quiet_luxury", "color": "#d4c9b8"
    },
    "cyber_chinese_gene": {
        "name": "赛博中式基因", "desc": "传统纹样+未来科技、霓虹水墨",
        "dna": {"color_warmth":50, "saturation":80, "pattern_complex":75, "texture_feel":35, "style_modern":80, "material_weight":40, "luminosity":85, "organic_ratio":40},
        "prompt_hint": "neo-chinese curtain, traditional cloud pattern with neon glow, cyber ink wash, metallic thread, futuristic oriental",
        "related_trend": "neon_chinese", "color": "#ff0040"
    },
    "digital_garden_gene": {
        "name": "数字花园基因", "desc": "AI生成花卉、超现实植物纹样",
        "dna": {"color_warmth":55, "saturation":75, "pattern_complex":85, "texture_feel":20, "style_modern":95, "material_weight":25, "luminosity":65, "organic_ratio":50},
        "prompt_hint": "digital garden curtain, AI-generated surreal floral pattern, dreamlike botany, vibrant fantasy flowers",
        "related_trend": "digital_garden", "color": "#7b68ee"
    },
    "eco_gene": {
        "name": "可持续基因", "desc": "再生纤维、有机棉、绿色制造",
        "dna": {"color_warmth":50, "saturation":30, "pattern_complex":25, "texture_feel":60, "style_modern":50, "material_weight":50, "luminosity":20, "organic_ratio":95},
        "prompt_hint": "sustainable eco curtain, organic cotton, bamboo fiber texture, natural green earth tones",
        "related_trend": "eco_revolution", "color": "#228b22"
    },
    "soft_minimal_gene": {
        "name": "温柔极简基因", "desc": "奶油色、燕麦色、柔软触感",
        "dna": {"color_warmth":60, "saturation":15, "pattern_complex":5, "texture_feel":40, "style_modern":45, "material_weight":35, "luminosity":40, "organic_ratio":60},
        "prompt_hint": "soft minimalist curtain, cream and oatmeal colors, gentle texture, warm white, hygge style",
        "related_trend": "soft_minimalism", "color": "#e8ddd0"
    },
    "maximalist_gene": {
        "name": "极繁主义基因", "desc": "大胆几何、佩斯利、大马士革纹",
        "dna": {"color_warmth":45, "saturation":70, "pattern_complex":95, "texture_feel":50, "style_modern":35, "material_weight":65, "luminosity":55, "organic_ratio":30},
        "prompt_hint": "maximalist curtain, bold damascus pattern, paisley, rich jewel tones, ornate, luxurious jacquard weave",
        "related_trend": "maximalist_pattern", "color": "#8b0000"
    }
}

history = []

def dna_to_prompt(dna, preset_hint=""):
    parts = ["high quality textile curtain fabric design, close-up detail shot"]
    if dna.get("color_warmth", 50) > 65: parts.append("warm color palette, golden amber tones")
    elif dna.get("color_warmth", 50) < 35: parts.append("cool color palette, blue grey tones")
    sat = dna.get("saturation", 50)
    if sat > 75: parts.append("vibrant high saturation colors")
    elif sat < 25: parts.append("muted desaturated neutral tones")
    pc = dna.get("pattern_complex", 50)
    if pc > 75: parts.append("intricate complex pattern, ornate detailed design")
    elif pc < 25: parts.append("solid color, minimal pattern, plain weave")
    tx = dna.get("texture_feel", 50)
    if tx > 70: parts.append("rough handwoven texture, visible weave structure")
    elif tx < 30: parts.append("smooth silk-like surface, refined finish")
    if dna.get("style_modern", 50) > 70: parts.append("contemporary modern design")
    elif dna.get("style_modern", 50) < 30: parts.append("traditional classic design")
    mw = dna.get("material_weight", 50)
    if mw > 70: parts.append("heavy thick fabric, velvet or tapestry")
    elif mw < 30: parts.append("sheer lightweight fabric, translucent voile")
    lum = dna.get("luminosity", 50)
    if lum > 70: parts.append("glossy satin finish, light catching surface")
    elif lum < 30: parts.append("matte finish, no shine")
    org = dna.get("organic_ratio", 50)
    if org > 70: parts.append("natural organic fibers, raw material feel")
    elif org < 30: parts.append("synthetic modern material, engineered textile")
    if preset_hint: parts.append(preset_hint)
    parts.append("professional product photography, studio lighting, 8k resolution")
    return ", ".join(parts)

# ============ 路由 ============

@app.route('/')
def index(): return send_from_directory(FRONTEND, 'index.html')

@app.route('/generated/<path:fn>')
def generated(fn): return send_from_directory(GEN_DIR, fn)

@app.route('/api/genome', methods=['GET'])
def get_genome(): return jsonify({'dimensions': GENOME_DIMENSIONS})

@app.route('/api/presets', methods=['GET'])
def get_presets(): return jsonify({'presets': DNA_PRESETS})

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.get_json()
    dna = data.get('dna', {})
    preset_id = data.get('preset_id', '')
    custom_desc = data.get('custom_desc', '')
    hint = DNA_PRESETS[preset_id].get("prompt_hint", "") if preset_id and preset_id in DNA_PRESETS else ""
    if custom_desc: hint = custom_desc + ", " + hint if hint else custom_desc
    prompt = dna_to_prompt(dna, hint)
    try:
        task_id = t2i_call(prompt)
        results = poll_task(task_id)
        if results:
            img_url = results[0].get("url", "")
            timestamp = int(time.time())
            fname = f"gene_{timestamp}.png"
            save_img(img_url, fname)
            meta = {"id": f"gene_{timestamp}", "prompt": prompt, "dna": dna, "preset_id": preset_id, "image": fname, "created_at": datetime.now().isoformat(), "img_url": f"/generated/{fname}"}
            with open(os.path.join(META_DIR, f"gene_{timestamp}.json"), "w") as f: json.dump(meta, f, ensure_ascii=False, indent=2)
            history.insert(0, meta)
            return jsonify({'success': True, 'image_url': f"/generated/{fname}", 'prompt': prompt, 'meta': meta})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    return jsonify({'success': False, 'error': '生成失败'}), 500

@app.route('/api/mutate', methods=['POST'])
def mutate():
    data = request.get_json()
    dna = data.get('dna', {})
    intensity = data.get('intensity', 20)
    mutated = {k: max(0, min(100, v + random.randint(-intensity, intensity))) for k, v in dna.items()}
    return jsonify({'dna': mutated})

@app.route('/api/breed', methods=['POST'])
def breed():
    data = request.get_json()
    parent_a, parent_b, ratio = data.get('parent_a', {}), data.get('parent_b', {}), data.get('ratio', 0.5)
    child = {k: max(0, min(100, int(parent_a.get(k, 50) * ratio + parent_b.get(k, 50) * (1 - ratio)) + random.randint(-5, 5))) for k in GENOME_DIMENSIONS}
    return jsonify({'dna': child})

@app.route('/api/trend_seeds', methods=['GET'])
def trend_seeds():
    seeds = [
        {"id": "wabi_sabi", "name": "侘寂美学", "momentum": 87, "gene": "wabi_sabi_gene"},
        {"id": "dopamine_home", "name": "多巴胺家居", "momentum": 79, "gene": "dopamine_gene"},
        {"id": "quiet_luxury", "name": "静奢风", "momentum": 82, "gene": "quiet_lux_gene"},
        {"id": "neon_chinese", "name": "新赛博中式", "momentum": 71, "gene": "cyber_chinese_gene"},
        {"id": "digital_garden", "name": "数字花园", "momentum": 74, "gene": "digital_garden_gene"},
        {"id": "eco_revolution", "name": "可持续革新", "momentum": 80, "gene": "eco_gene"},
        {"id": "soft_minimalism", "name": "温柔极简", "momentum": 85, "gene": "soft_minimal_gene"},
        {"id": "maximalist_pattern", "name": "极繁主义复兴", "momentum": 65, "gene": "maximalist_gene"}
    ]
    return jsonify({'seeds': seeds})

@app.route('/api/history', methods=['GET'])
def get_history():
    loaded = []
    if os.path.exists(META_DIR):
        for fn in sorted(os.listdir(META_DIR), reverse=True):
            if fn.endswith('.json'):
                try:
                    with open(os.path.join(META_DIR, fn)) as f: loaded.append(json.load(f))
                except: pass
    return jsonify({'history': loaded[:30]})

if __name__ == '__main__':
    print("织物基因编辑器启动: http://localhost:5003")
    app.run(host='0.0.0.0', port=5003, debug=False)