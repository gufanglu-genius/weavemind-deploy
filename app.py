"""
织觉引擎 WeaveMind — 统一部署入口
将5个独立Flask服务合并为单一应用，适配Render.com公网部署
"""
import os
from flask import Flask, send_from_directory, jsonify, Blueprint
from flask_cors import CORS

BASE = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app)

# API Key从环境变量读取
API_KEY = os.environ.get('DASHSCOPE_API_KEY', '')

# ============ 主站路由 ============

@app.route('/')
def index():
    return send_from_directory(BASE, 'index.html')

@app.route('/c2m.html')
def c2m():
    return send_from_directory(BASE, 'c2m.html')

@app.route('/assets/<path:fn>')
def main_assets(fn):
    return send_from_directory(os.path.join(BASE, 'generated-assets'), fn)

@app.route('/references/<path:fn>')
def main_references(fn):
    return send_from_directory(os.path.join(BASE, 'aesthetic-translator', 'references'), fn)

@app.route('/api/status')
def status():
    return jsonify({
        'name': '织觉引擎 WeaveMind',
        'version': '2.0',
        'engines': {
            'aesthetic_translator': {'path': '/translator', 'status': 'ready'},
            'spatial_engine': {'path': '/spatial', 'status': 'ready'},
            'trend_prophet': {'path': '/trend', 'status': 'ready'},
            'gene_editor': {'path': '/gene', 'status': 'ready'}
        }
    })


# ============ 审美翻译器 Blueprint ============

translator_bp = Blueprint('translator', __name__,
    url_prefix='/translator',
    static_folder=os.path.join(BASE, 'aesthetic-translator', 'frontend', 'static'),
    static_url_path='/translator/static')

TRANSLATOR_BASE = os.path.join(BASE, 'aesthetic-translator')
TRANSLATOR_FRONTEND = os.path.join(TRANSLATOR_BASE, 'frontend')
TRANSLATOR_GEN = os.path.join(TRANSLATOR_BASE, 'generated')
TRANSLATOR_META = os.path.join(TRANSLATOR_BASE, 'metadata')
TRANSLATOR_REF = os.path.join(TRANSLATOR_BASE, 'references', 'nantong-ich')

os.makedirs(TRANSLATOR_GEN, exist_ok=True)
os.makedirs(TRANSLATOR_META, exist_ok=True)

@translator_bp.route('/')
def translator_index():
    return send_from_directory(TRANSLATOR_FRONTEND, 'index.html')

@translator_bp.route('/assets/<path:fn>')
def translator_assets(fn):
    return send_from_directory(os.path.join(TRANSLATOR_FRONTEND, 'assets'), fn)

@translator_bp.route('/generated/<path:fn>')
def translator_generated(fn):
    return send_from_directory(TRANSLATOR_GEN, fn)

@translator_bp.route('/references/<path:fn>')
def translator_references(fn):
    return send_from_directory(os.path.join(TRANSLATOR_BASE, 'references'), fn)

# 非遗工艺库
ICH_CRAFTS = {
    "blue_calico": {
        "id": "blue_calico", "name": "蓝印花布", "name_en": "Blue Calico",
        "origin": "南通", "level": "国家级非遗", "era": "明代至今",
        "desc": "以靛蓝为染料，豆粉石灰为防染浆，经刻版、刮浆、染色、刮灰等工序制成。蓝白相间，素雅清新。",
        "craft_traits": "防染印花、靛蓝染色、手工刻版",
        "dna": {"color_warmth":30,"saturation":35,"pattern_complex":70,"texture_feel":55,"style_modern":20,"material_weight":45,"luminosity":15,"organic_ratio":85},
        "prompt_core": "Chinese indigo blue calico, deep blue and white resist pattern, traditional folk art motifs, hand-block printed, artisan textile",
        "modern_fusion": "将蓝印花布的蓝白对比与现代几何结合，保留防染肌理感",
        "image": "/translator/references/nantong-ich/nantong_blue_calico.png"
    },
    "tie_dye": {
        "id": "tie_dye", "name": "扎染", "name_en": "Tie-Dye",
        "origin": "南通", "level": "省级非遗", "era": "唐代至今",
        "desc": "通过捆扎、缝绞、夹扎等手法防染，形成自然晕色和有机纹理。",
        "craft_traits": "手工捆扎、自然晕染、有机纹理",
        "dna": {"color_warmth":40,"saturation":50,"pattern_complex":45,"texture_feel":40,"style_modern":40,"material_weight":35,"luminosity":25,"organic_ratio":90},
        "prompt_core": "Chinese traditional tie-dye, indigo shibori, organic resist pattern, natural gradient, handcrafted unique texture",
        "modern_fusion": "扎染的随机性与数字渐变结合",
        "image": "/translator/references/nantong-ich/nantong_tie_dye.png"
    },
    "shen_embroidery": {
        "id": "shen_embroidery", "name": "沈绣", "name_en": "Shen Embroidery",
        "origin": "南通", "level": "国家级非遗", "era": "清末至今",
        "desc": "以沈寿为代表的仿真绣技法，融合西洋画理，针法细腻如照片般写实。",
        "craft_traits": "仿真绣法、丝线劈丝、光影渐变",
        "dna": {"color_warmth":55,"saturation":60,"pattern_complex":85,"texture_feel":30,"style_modern":35,"material_weight":25,"luminosity":55,"organic_ratio":70},
        "prompt_core": "fine silk embroidery, photorealistic needlework, delicate thread painting, Chinese Suzhou-style embroidery",
        "modern_fusion": "沈绣的写实技法与数码像素风格碰撞",
        "image": "/translator/references/nantong-ich/nantong_shen_embroidery.png"
    },
    "tubu_weaving": {
        "id": "tubu_weaving", "name": "土布纺织", "name_en": "Handwoven Cotton",
        "origin": "南通", "level": "省级非遗", "era": "千年传承",
        "desc": "手工纺纱、脚踏织机，经纬交错织出条格纹样。质朴厚实。",
        "craft_traits": "手工纺纱、脚踏织机、经纬交织",
        "dna": {"color_warmth":55,"saturation":20,"pattern_complex":25,"texture_feel":80,"style_modern":15,"material_weight":65,"luminosity":10,"organic_ratio":95},
        "prompt_core": "handwoven cotton cloth, rustic natural fiber, earth tone stripes and checks, raw cotton texture",
        "modern_fusion": "土布的粗粝质感与极简设计融合",
        "image": "/translator/references/nantong-ich/nantong_tubu_weaving.png"
    },
    "silk_weaving": {
        "id": "silk_weaving", "name": "丝绸织造", "name_en": "Silk Brocade",
        "origin": "南通", "level": "市级非遗", "era": "宋元至今",
        "desc": "南通丝绸以提花织造见长，云锦、宋锦等纹样在丝线上交织出华丽图案。",
        "craft_traits": "提花织造、金线交织、多层色彩",
        "dna": {"color_warmth":65,"saturation":70,"pattern_complex":80,"texture_feel":20,"style_modern":25,"material_weight":40,"luminosity":80,"organic_ratio":50},
        "prompt_core": "Chinese silk brocade, intricate jacquard weave, lustrous fabric, traditional cloud and crane pattern",
        "modern_fusion": "丝绸的华丽光泽与Art Deco几何结合",
        "image": "/translator/references/nantong-ich/nantong_silk_weaving.png"
    },
    "kite_pattern": {
        "id": "kite_pattern", "name": "板鹞风筝", "name_en": "Kite Art",
        "origin": "南通", "level": "国家级非遗", "era": "宋代至今",
        "desc": "南通板鹞风筝以哨口音乐和彩绘装饰闻名，几何骨架上绘满吉祥纹样。",
        "craft_traits": "几何骨架、彩绘装饰、哨口排列",
        "dna": {"color_warmth":60,"saturation":85,"pattern_complex":75,"texture_feel":30,"style_modern":40,"material_weight":20,"luminosity":60,"organic_ratio":45},
        "prompt_core": "Chinese ornamental kite pattern, bold geometric folk art, colorful decorative motifs",
        "modern_fusion": "板鹞风筝的浓烈色彩与孟菲斯设计风格碰撞",
        "image": "/translator/references/nantong-ich/nantong_kite_pattern.png"
    }
}

TRANSLATION_MODES = {
    "faithful": {"name": "忠实还原", "desc": "最大程度保留原图气质", "suffix": ""},
    "abstract": {"name": "抽象提炼", "desc": "提取核心视觉基因重构", "suffix": ", abstract artistic interpretation, simplified forms, textile design"},
    "pattern": {"name": "纹样生成", "desc": "转化为可重复的面料图案", "suffix": ", seamless repeating tile pattern, textile print, screen printable"},
    "fusion": {"name": "非遗融合", "desc": "与南通传统工艺深度结合", "suffix": ""}
}

def t2i_call_translator(prompt, size="1024*1024"):
    import requests as req
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "X-DashScope-Async": "enable"}
    body = {"model": "wanx2.1-t2i-turbo", "input": {"prompt": prompt}, "parameters": {"size": size, "n": 1}}
    r = req.post(url, headers=headers, json=body, timeout=30)
    r.raise_for_status()
    return r.json()["output"]["task_id"]

def poll_task_translator(task_id, timeout=120):
    import requests as req, time
    url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    start = time.time()
    while time.time() - start < timeout:
        r = req.get(url, headers=headers, timeout=15)
        data = r.json()
        status = data.get("output", {}).get("task_status", "")
        if status == "SUCCEEDED": return data["output"]["results"]
        elif status in ("FAILED", "UNKNOWN"): raise RuntimeError(f"Task {status}")
        time.sleep(2)
    raise TimeoutError("Timeout")

@translator_bp.route('/api/crafts', methods=['GET'])
def get_crafts():
    return jsonify({"crafts": list(ICH_CRAFTS.values())})

@translator_bp.route('/api/modes', methods=['GET'])
def get_modes():
    return jsonify({"modes": TRANSLATION_MODES})

@translator_bp.route('/api/analyze', methods=['POST'])
def analyze():
    import time, json, base64, numpy as np, cv2
    from flask import request
    if 'image' not in request.files:
        return jsonify({"error": "请上传图片"}), 400
    f = request.files['image']
    fname = f"upload_{int(time.time())}.png"
    fpath = os.path.join(TRANSLATOR_GEN, fname)
    f.save(fpath)

    # CV特征提取
    try:
        sys_path_orig = os.sys.path.copy()
        os.sys.path.insert(0, os.path.join(TRANSLATOR_BASE, 'cv_modules'))
        from feature_extractor import extract_all, features_to_aesthetic_dna
        cv_features = extract_all(fpath)
        dna = features_to_aesthetic_dna(cv_features)
        os.sys.path = sys_path_orig
    except Exception:
        cv_features = {"color": {"warmth": 50, "saturation": 50, "dominant_colors": [{"hex": "#888"}]}, "texture": {"roughness": 50}, "composition": {"complexity": 50}}
        dna = {"color_warmth":50,"saturation":50,"pattern_complex":50,"texture_feel":50,"style_modern":50,"material_weight":50,"luminosity":50,"organic_ratio":50}

    # 非遗匹配
    craft_matches = []
    for cid, craft in ICH_CRAFTS.items():
        cdna = craft["dna"]
        dist = sum(abs(dna.get(k,50) - cdna.get(k,50)) for k in ["color_warmth","saturation","pattern_complex","texture_feel","style_modern","organic_ratio"])
        match_score = round(max(0, min(100, 70 - dist/3 + (100-dist/6)/5)))
        craft_matches.append({"craft_id": cid, "craft_name": craft["name"], "match_score": match_score, "reason": craft["modern_fusion"]})
    craft_matches.sort(key=lambda x: x["match_score"], reverse=True)

    return jsonify({"image_url": f"/translator/generated/{fname}", "cv_features": cv_features, "aesthetic_dna": dna, "craft_recommendations": craft_matches})

@translator_bp.route('/api/translate', methods=['POST'])
def translate():
    import time, json, requests as req
    from flask import request
    data = request.get_json()
    mode = data.get("mode", "faithful")
    base_prompt = data.get("base_prompt", "high quality textile curtain fabric design")
    dna = data.get("dna", {})
    craft_id = data.get("craft_id", "")
    mode_info = TRANSLATION_MODES.get(mode, TRANSLATION_MODES["faithful"])

    parts = [base_prompt]
    if mode_info.get("suffix"): parts.append(mode_info["suffix"])
    if dna.get("saturation",50) > 70: parts.append("vibrant saturated")
    elif dna.get("saturation",50) < 30: parts.append("muted neutral")
    if dna.get("color_warmth",50) > 65: parts.append("warm tones")
    elif dna.get("color_warmth",50) < 35: parts.append("cool tones")
    parts.append("professional textile photography, studio lighting, 8k")
    prompt = ", ".join(filter(None, parts))

    ts = int(time.time())
    try:
        task_id = t2i_call_translator(prompt)
        results = poll_task_translator(task_id)
        if results:
            img_url = results[0].get("url", "")
            fname = f"trans_{ts}.png"
            img_data = req.get(img_url, timeout=30).content
            with open(os.path.join(TRANSLATOR_GEN, fname), "wb") as fp: fp.write(img_data)
            return jsonify({"success": True, "image_url": f"/translator/generated/{fname}", "prompt": prompt})
    except Exception:
        pass

    ref_img = ICH_CRAFTS.get(craft_id, {}).get("image", "") if craft_id in ICH_CRAFTS else ""
    if ref_img:
        return jsonify({"success": True, "image_url": ref_img, "prompt": prompt, "note": "AI生图服务暂不可用，展示非遗参考作品"})
    return jsonify({"success": False, "error": "AI生图服务暂不可用"}), 503

@translator_bp.route('/api/history', methods=['GET'])
def translator_history():
    import json
    loaded = []
    if os.path.exists(TRANSLATOR_META):
        for fn in sorted(os.listdir(TRANSLATOR_META), reverse=True):
            if fn.startswith('trans_') and fn.endswith('.json'):
                try:
                    with open(os.path.join(TRANSLATOR_META, fn)) as f:
                        item = json.load(f)
                        if 'img_url' in item and item['img_url'] and not item['img_url'].startswith('/translator'):
                            item['img_url'] = '/translator' + item['img_url']
                        if 'image_url' in item and item['image_url'] and not item['image_url'].startswith('/translator'):
                            item['image_url'] = '/translator' + item['image_url']
                        loaded.append(item)
                except: pass
    return jsonify({"history": loaded[:30]})

@translator_bp.route('/api/trend_validate', methods=['POST'])
def trend_validate():
    # Simplified: return trend data from trend engine
    trends = sorted(TREND_DB.values(), key=lambda x: x['resonance_score'], reverse=True)
    matches = [{"trend_name": t["name"], "trend_score": t["score"], "resonance": t["resonance_score"], "confidence": min(95, t["resonance_score"] + 10)} for t in trends[:4]]
    return jsonify({"matches": matches})

app.register_blueprint(translator_bp)


# ============ 基因编辑器 Blueprint ============

gene_bp = Blueprint('gene', __name__,
    url_prefix='/gene',
    static_folder=os.path.join(BASE, 'textile-gene-editor', 'frontend', 'static'),
    static_url_path='/gene/static')

GENE_BASE = os.path.join(BASE, 'textile-gene-editor')
GENE_FRONTEND = os.path.join(GENE_BASE, 'frontend')
GENE_GEN = os.path.join(GENE_BASE, 'generated')
GENE_META = os.path.join(GENE_BASE, 'metadata')

os.makedirs(GENE_GEN, exist_ok=True)
os.makedirs(GENE_META, exist_ok=True)

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
    "wabi_sabi_gene": {"name": "侘寂基因", "desc": "自然朴素、手工质感、大地色调", "dna": {"color_warmth":70,"saturation":20,"pattern_complex":15,"texture_feel":75,"style_modern":30,"material_weight":55,"luminosity":15,"organic_ratio":90}, "prompt_hint": "wabi-sabi linen curtain, natural undyed texture, earth tones, handwoven, imperfect beauty, minimalist", "color": "#8b7d6b"},
    "dopamine_gene": {"name": "多巴胺基因", "desc": "高饱和、明亮撞色、快乐活力", "dna": {"color_warmth":65,"saturation":95,"pattern_complex":60,"texture_feel":25,"style_modern":85,"material_weight":30,"luminosity":70,"organic_ratio":15}, "prompt_hint": "dopamine decor curtain, vibrant rainbow colors, gradient, high saturation, joyful, modern textile", "color": "#ff6b6b"},
    "quiet_lux_gene": {"name": "静奢基因", "desc": "低调奢华、高支纯色、触感高级", "dna": {"color_warmth":40,"saturation":10,"pattern_complex":5,"texture_feel":30,"style_modern":55,"material_weight":45,"luminosity":60,"organic_ratio":65}, "prompt_hint": "quiet luxury curtain, pure cashmere texture, ivory and taupe, no pattern, ultra refined, subtle sheen", "color": "#d4c9b8"},
    "cyber_chinese_gene": {"name": "赛博中式基因", "desc": "传统纹样+未来科技、霓虹水墨", "dna": {"color_warmth":50,"saturation":80,"pattern_complex":75,"texture_feel":35,"style_modern":80,"material_weight":40,"luminosity":85,"organic_ratio":40}, "prompt_hint": "neo-chinese curtain, traditional cloud pattern with neon glow, cyber ink wash, metallic thread, futuristic oriental", "color": "#ff0040"},
    "digital_garden_gene": {"name": "数字花园基因", "desc": "AI生成花卉、超现实植物纹样", "dna": {"color_warmth":55,"saturation":75,"pattern_complex":85,"texture_feel":20,"style_modern":95,"material_weight":25,"luminosity":65,"organic_ratio":50}, "prompt_hint": "digital garden curtain, AI-generated surreal floral pattern, dreamlike botany, vibrant fantasy flowers", "color": "#7b68ee"},
    "eco_gene": {"name": "可持续基因", "desc": "再生纤维、有机棉、绿色制造", "dna": {"color_warmth":50,"saturation":30,"pattern_complex":25,"texture_feel":60,"style_modern":50,"material_weight":50,"luminosity":20,"organic_ratio":95}, "prompt_hint": "sustainable eco curtain, organic cotton, bamboo fiber texture, natural green earth tones", "color": "#228b22"},
    "soft_minimal_gene": {"name": "温柔极简基因", "desc": "奶油色、燕麦色、柔软触感", "dna": {"color_warmth":60,"saturation":15,"pattern_complex":5,"texture_feel":40,"style_modern":45,"material_weight":35,"luminosity":40,"organic_ratio":60}, "prompt_hint": "soft minimalist curtain, cream and oatmeal colors, gentle texture, warm white, hygge style", "color": "#e8ddd0"},
    "maximalist_gene": {"name": "极繁主义基因", "desc": "大胆几何、佩斯利、大马士革纹", "dna": {"color_warmth":45,"saturation":70,"pattern_complex":95,"texture_feel":50,"style_modern":35,"material_weight":65,"luminosity":55,"organic_ratio":30}, "prompt_hint": "maximalist curtain, bold damascus pattern, paisley, rich jewel tones, ornate, luxurious jacquard weave", "color": "#8b0000"}
}

@gene_bp.route('/')
def gene_index():
    return send_from_directory(GENE_FRONTEND, 'index.html')

@gene_bp.route('/assets/<path:fn>')
def gene_assets(fn):
    return send_from_directory(os.path.join(GENE_FRONTEND, 'assets'), fn)

@gene_bp.route('/generated/<path:fn>')
def gene_generated(fn):
    return send_from_directory(GENE_GEN, fn)

def dna_to_prompt(dna, preset_hint=""):
    parts = ["high quality textile curtain fabric design, close-up detail shot"]
    if dna.get("color_warmth",50) > 65: parts.append("warm color palette, golden amber tones")
    elif dna.get("color_warmth",50) < 35: parts.append("cool color palette, blue grey tones")
    sat = dna.get("saturation",50)
    if sat > 75: parts.append("vibrant high saturation colors")
    elif sat < 25: parts.append("muted desaturated neutral tones")
    pc = dna.get("pattern_complex",50)
    if pc > 75: parts.append("intricate complex pattern, ornate detailed design")
    elif pc < 25: parts.append("solid color, minimal pattern, plain weave")
    tx = dna.get("texture_feel",50)
    if tx > 70: parts.append("rough handwoven texture, visible weave structure")
    elif tx < 30: parts.append("smooth silk-like surface, refined finish")
    if dna.get("style_modern",50) > 70: parts.append("contemporary modern design")
    elif dna.get("style_modern",50) < 30: parts.append("traditional classic design")
    mw = dna.get("material_weight",50)
    if mw > 70: parts.append("heavy thick fabric, velvet or tapestry")
    elif mw < 30: parts.append("sheer lightweight fabric, translucent voile")
    lum = dna.get("luminosity",50)
    if lum > 70: parts.append("glossy satin finish, light catching surface")
    elif lum < 30: parts.append("matte finish, no shine")
    org = dna.get("organic_ratio",50)
    if org > 70: parts.append("natural organic fibers, raw material feel")
    elif org < 30: parts.append("synthetic modern material, engineered textile")
    if preset_hint: parts.append(preset_hint)
    parts.append("professional product photography, studio lighting, 8k resolution")
    return ", ".join(parts)

def t2i_call_gene(prompt, size="1024*1024"):
    import requests as req
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "X-DashScope-Async": "enable"}
    body = {"model": "wanx2.1-t2i-turbo", "input": {"prompt": prompt}, "parameters": {"size": size, "n": 1}}
    r = req.post(url, headers=headers, json=body, timeout=30)
    r.raise_for_status()
    return r.json()["output"]["task_id"]

def poll_task_gene(task_id, timeout=120):
    import requests as req, time
    url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    start = time.time()
    while time.time() - start < timeout:
        r = req.get(url, headers=headers, timeout=15)
        data = r.json()
        status = data.get("output", {}).get("task_status", "")
        if status == "SUCCEEDED": return data["output"]["results"]
        elif status in ("FAILED", "UNKNOWN"): raise RuntimeError(f"Task {status}")
        time.sleep(2)
    raise TimeoutError("Timeout")

@gene_bp.route('/api/genome', methods=['GET'])
def get_genome():
    return jsonify({'dimensions': GENOME_DIMENSIONS})

@gene_bp.route('/api/presets', methods=['GET'])
def get_presets():
    return jsonify({'presets': DNA_PRESETS})

@gene_bp.route('/api/generate', methods=['POST'])
def gene_generate():
    import time, json, requests as req
    from flask import request
    data = request.get_json()
    dna = data.get('dna', {})
    preset_id = data.get('preset_id', '')
    custom_desc = data.get('custom_desc', '')
    hint = DNA_PRESETS.get(preset_id, {}).get("prompt_hint", "") if preset_id in DNA_PRESETS else ""
    if custom_desc: hint = custom_desc + ", " + hint if hint else custom_desc
    prompt = dna_to_prompt(dna, hint)
    ts = int(time.time())
    try:
        task_id = t2i_call_gene(prompt)
        results = poll_task_gene(task_id)
        if results:
            img_url = results[0].get("url", "")
            fname = f"gene_{ts}.png"
            r = req.get(img_url, timeout=30)
            with open(os.path.join(GENE_GEN, fname), "wb") as f: f.write(r.content)
            return jsonify({'success': True, 'image_url': f"/gene/generated/{fname}", 'prompt': prompt})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    return jsonify({'success': False, 'error': '生成失败'}), 500

@gene_bp.route('/api/mutate', methods=['POST'])
def mutate():
    import random
    from flask import request
    data = request.get_json()
    dna = data.get('dna', {})
    intensity = data.get('intensity', 20)
    mutated = {}
    for key, val in dna.items():
        mutated[key] = max(0, min(100, val + random.randint(-intensity, intensity)))
    return jsonify({'dna': mutated})

@gene_bp.route('/api/breed', methods=['POST'])
def breed():
    import random
    from flask import request
    data = request.get_json()
    parent_a = data.get('parent_a', {})
    parent_b = data.get('parent_b', {})
    ratio = data.get('ratio', 0.5)
    child = {}
    for key in GENOME_DIMENSIONS:
        va = parent_a.get(key, 50)
        vb = parent_b.get(key, 50)
        child[key] = max(0, min(100, int(va * ratio + vb * (1 - ratio)) + random.randint(-5, 5)))
    return jsonify({'dna': child})

@gene_bp.route('/api/trend_seeds', methods=['GET'])
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

@gene_bp.route('/api/history', methods=['GET'])
def gene_history():
    import json
    loaded = []
    if os.path.exists(GENE_META):
        for fn in sorted(os.listdir(GENE_META), reverse=True):
            if fn.endswith('.json'):
                try:
                    with open(os.path.join(GENE_META, fn)) as f:
                        item = json.load(f)
                        # Fix image paths for Blueprint routing
                        if 'img_url' in item and item['img_url'] and not item['img_url'].startswith('/gene'):
                            item['img_url'] = '/gene' + item['img_url']
                        if 'image_url' in item and item['image_url'] and not item['image_url'].startswith('/gene'):
                            item['image_url'] = '/gene' + item['image_url']
                        loaded.append(item)
                except: pass
    return jsonify({'history': loaded[:30]})

app.register_blueprint(gene_bp)


# ============ 空间感知引擎 Blueprint ============

spatial_bp = Blueprint('spatial', __name__,
    url_prefix='/spatial',
    static_folder=os.path.join(BASE, 'spatial-engine', 'frontend', 'static'),
    static_url_path='/spatial/static')

SPATIAL_BASE = os.path.join(BASE, 'spatial-engine')
SPATIAL_FRONTEND = os.path.join(SPATIAL_BASE, 'frontend')
SPATIAL_UPLOAD = os.path.join(SPATIAL_BASE, 'uploads')
SPATIAL_OUTPUT = os.path.join(SPATIAL_BASE, 'outputs')
SPATIAL_META = os.path.join(SPATIAL_BASE, 'metadata')

for d in [SPATIAL_UPLOAD, SPATIAL_OUTPUT, SPATIAL_META]:
    os.makedirs(d, exist_ok=True)

TEXTILES = {
    "chinese_ink": {"name": "水墨江南", "desc": "水墨花鸟窗帘 · 东方雅韵", "curtain_desc": "elegant Chinese ink wash style silk curtains with hand-painted bamboo and plum blossom patterns in soft ink-black on rice-paper white with subtle gold-thread embroidery along the hems, translucent fabric gently filtering light"},
    "nordic_minimal": {"name": "北欧极简", "desc": "几何纹理亚麻帘 · 北欧清新", "curtain_desc": "Scandinavian minimalist linen curtains with geometric diamond pattern in muted sage green and cream white, natural linen texture with visible weave, clean modern lines"},
    "japanese_wabi": {"name": "侘寂之美", "desc": "原色亚麻帘 · 侘寂禅意", "curtain_desc": "Japanese wabi-sabi style natural undyed linen curtains with irregular organic weave texture in warm earth tones, imperfect beauty aesthetic, gentle natural drape"},
    "french_roma": {"name": "法式浪漫", "desc": "法式田园印花帘 · 浪漫优雅", "curtain_desc": "French romantic toile curtains with pastoral floral scene pattern in dusty rose and ivory cream, silk-like subtle sheen, elegant swag draping with soft folds"},
    "modern_abstract": {"name": "现代艺术", "desc": "抽象艺术印花帘 · 现代摩登", "curtain_desc": "contemporary abstract art curtains with bold brushstroke pattern in navy blue, teal, and gold, modern gallery inspired design, premium silk blend with fluid drape"},
    "luxury_velvet": {"name": "奢华丝绒", "desc": "祖母绿丝绒帘 · 低调奢华", "curtain_desc": "luxurious deep emerald green velvet curtains with subtle embossed damask pattern, rich heavy draping with soft folds catching warm ambient light"}
}

ROOM_STYLES = {
    "modern": {"base": "A photorealistic modern bright living room interior with large floor-to-ceiling windows letting in abundant natural light, light oak hardwood floors, white walls, minimalist low-profile charcoal sofa, walnut coffee table, single potted fiddle-leaf fig", "mood": "clean, airy, contemporary"},
    "bedroom": {"base": "A photorealistic cozy modern bedroom interior with a large window with soft morning light, queen bed with white linen sheets, wooden nightstands with warm bedside lamps, plush area rug, soft warm ambient lighting", "mood": "warm, inviting, restful"},
    "chinese": {"base": "A photorealistic Chinese traditional style room interior with rosewood furniture, large window with garden view, warm amber lighting, elegant calligraphy scrolls on wall, ceramic vase with dried branches", "mood": "refined, cultural, warm"},
    "nordic": {"base": "A photorealistic Scandinavian style bright room interior with panoramic window, white walls, light birch wood furniture, green monstera plants, cozy wool throw blanket, soft diffused natural light", "mood": "minimal, natural, hygge"}
}

@spatial_bp.route('/')
def spatial_index():
    return send_from_directory(SPATIAL_FRONTEND, 'index.html')

@spatial_bp.route('/assets/<path:fn>')
def spatial_assets(fn):
    return send_from_directory(os.path.join(SPATIAL_FRONTEND, 'assets'), fn)

@spatial_bp.route('/outputs/<path:fn>')
def spatial_outputs(fn):
    return send_from_directory(SPATIAL_OUTPUT, fn)

@spatial_bp.route('/uploads/<path:fn>')
def spatial_uploads(fn):
    return send_from_directory(SPATIAL_UPLOAD, fn)

def t2i_call_spatial(prompt, retries=3):
    import requests as req, time
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "X-DashScope-Async": "enable"}
    body = {"model": "wanx2.1-t2i-turbo", "input": {"prompt": prompt}, "parameters": {"size": "1024*1024", "n": 1}}
    for i in range(retries):
        try:
            r = req.post(url, headers=headers, json=body, timeout=30)
            tid = r.json().get('output', {}).get('task_id')
            if not tid: time.sleep(2**i); continue
            start = time.time()
            while time.time() - start < 90:
                r = req.get(f"https://dashscope.aliyuncs.com/api/v1/tasks/{tid}", headers={"Authorization": f"Bearer {API_KEY}"}, timeout=15)
                d = r.json()
                s = d.get('output', {}).get('task_status')
                if s == 'SUCCEEDED': return {'success': True, 'url': d['output']['results'][0]['url']}
                elif s == 'FAILED': break
                time.sleep(3)
        except Exception: pass
        time.sleep(2**i)
    return {'success': False, 'error': '生成失败'}

@spatial_bp.route('/api/textiles', methods=['GET'])
def get_textiles():
    return jsonify({'textiles': [{'id': k, 'name': v['name'], 'description': v['desc']} for k, v in TEXTILES.items()]})

@spatial_bp.route('/api/upload-room', methods=['POST'])
def upload_room():
    import uuid
    from flask import request
    from werkzeug.utils import secure_filename
    if 'file' not in request.files: return jsonify({'error': '未选择文件'}), 400
    f = request.files['file']
    fn = f"room_{uuid.uuid4().hex[:12]}_{secure_filename(f.filename)}"
    f.save(os.path.join(SPATIAL_UPLOAD, fn))
    return jsonify({'success': True, 'filename': fn})

@spatial_bp.route('/api/generate-room', methods=['POST'])
def generate_room():
    import requests as req, uuid
    from flask import request
    data = request.json
    style = data.get('style', 'modern')
    desc = data.get('description', '')
    style_info = ROOM_STYLES.get(style, ROOM_STYLES['modern'])
    full_prompt = f"{style_info['base']}. {desc}. Interior photography, 35mm lens, natural lighting, 8k detail, no curtains visible, empty window with bright daylight coming through."
    result = t2i_call_spatial(full_prompt)
    if not result['success']: return jsonify({'error': result['error']}), 500
    r = req.get(result['url'], timeout=30)
    fn = f"room_{uuid.uuid4().hex[:12]}.png"
    with open(os.path.join(SPATIAL_OUTPUT, fn), 'wb') as f: f.write(r.content)
    return jsonify({'success': True, 'filename': fn})

@spatial_bp.route('/api/preview-textile', methods=['POST'])
def preview_textile():
    import requests as req, uuid
    from flask import request
    data = request.json
    room_fn = data.get('room_image')
    textile_id = data.get('textile_id')
    if not room_fn: return jsonify({'error': '缺少房间图片'}), 400
    curtain_desc = TEXTILES.get(textile_id, {}).get('curtain_desc', data.get('custom_prompt', ''))
    textile_name = TEXTILES.get(textile_id, {}).get('name', '自定义')
    preview_prompt = f"A bright modern room with large window, natural light, hardwood floor. The window has {curtain_desc}. The curtains drape naturally with realistic folds and light filtering through the fabric. Interior photography, 35mm lens, natural lighting, 8k detail."
    result = t2i_call_spatial(preview_prompt)
    if not result['success']: return jsonify({'error': result['error']}), 500
    r = req.get(result['url'], timeout=30)
    fn = f"preview_{uuid.uuid4().hex[:12]}.png"
    with open(os.path.join(SPATIAL_OUTPUT, fn), 'wb') as f: f.write(r.content)
    return jsonify({'success': True, 'filename': fn, 'textile_name': textile_name})

@spatial_bp.route('/api/evaluate', methods=['POST'])
def evaluate():
    import random
    from flask import request
    d = request.json
    room_style = d.get('room_style', 'modern')
    textile_id = d.get('textile_id', '')
    match = {'modern': {'modern_abstract':8,'nordic_minimal':6,'luxury_velvet':5}, 'chinese': {'chinese_ink':9,'japanese_wabi':5}, 'nordic': {'nordic_minimal':9,'japanese_wabi':7}}
    score = min(98, 75 + match.get(room_style, {}).get(textile_id, 0) + random.randint(-3, 5))
    level = 'excellent' if score >= 85 else 'good' if score >= 70 else 'fair'
    return jsonify({'score': score, 'level': level})

app.register_blueprint(spatial_bp)


# ============ 趋势先知 Blueprint ============

trend_bp = Blueprint('trend', __name__,
    url_prefix='/trend',
    static_folder=os.path.join(BASE, 'trend-prophet', 'frontend', 'static'),
    static_url_path='/trend/static')

TREND_BASE = os.path.join(BASE, 'trend-prophet')
TREND_FRONTEND = os.path.join(TREND_BASE, 'frontend')

TREND_DB = {
    "wabi_sabi": {"id":"wabi_sabi","name":"侘寂美学","name_en":"Wabi-Sabi Textiles","category":"风格趋势","score":87,"velocity":2.3,"lifecycle":"growth","peak_month":"2027-03","signals":{"social":92,"fashion":85,"culture":78,"economic":70,"search":88,"design":90},"resonance_score":84,"trend_data":[45,48,52,55,58,62,65,68,72,76,80,84,87,90,92,94],"recommendation":"推荐开发原色亚麻窗帘系列"},
    "dopamine_home": {"id":"dopamine_home","name":"多巴胺家居","name_en":"Dopamine Decor","category":"色彩趋势","score":79,"velocity":3.1,"lifecycle":"growth","peak_month":"2027-01","signals":{"social":85,"fashion":90,"culture":72,"economic":65,"search":78,"design":75},"resonance_score":78,"trend_data":[30,35,40,48,55,60,65,68,72,75,78,80,82,83,84,85],"recommendation":"开发彩色拼接窗帘和渐变色床品系列"},
    "quiet_luxury": {"id":"quiet_luxury","name":"静奢风","name_en":"Quiet Luxury","category":"品质趋势","score":82,"velocity":1.8,"lifecycle":"growth","peak_month":"2027-06","signals":{"social":75,"fashion":92,"culture":68,"economic":85,"search":72,"design":80},"resonance_score":79,"trend_data":[50,52,55,57,60,63,65,68,70,73,75,77,79,81,83,85],"recommendation":"开发高支数纯色棉麻系列"},
    "digital_garden": {"id":"digital_garden","name":"数字花园","name_en":"Digital Garden","category":"图案趋势","score":74,"velocity":4.2,"lifecycle":"emerging","peak_month":"2027-09","signals":{"social":68,"fashion":65,"culture":82,"economic":55,"search":60,"design":95},"resonance_score":71,"trend_data":[15,18,22,28,35,40,45,50,55,58,62,65,68,71,73,75],"recommendation":"结合AI花型生成能力开发限量版数字艺术窗帘"},
    "eco_revolution": {"id":"eco_revolution","name":"可持续革新","name_en":"Eco-Revolution","category":"材料趋势","score":80,"velocity":2.0,"lifecycle":"growth","peak_month":"2027-12","signals":{"social":72,"fashion":78,"culture":85,"economic":60,"search":75,"design":82},"resonance_score":75,"trend_data":[40,42,45,48,52,55,58,62,65,68,72,75,78,80,82,84],"recommendation":"开发竹纤维窗帘和有机棉床品线"},
    "neon_chinese": {"id":"neon_chinese","name":"新赛博中式","name_en":"Neo-Cyber Chinese","category":"风格趋势","score":71,"velocity":3.8,"lifecycle":"emerging","peak_month":"2027-06","signals":{"social":78,"fashion":62,"culture":88,"economic":55,"search":65,"design":72},"resonance_score":70,"trend_data":[20,25,30,35,42,48,52,56,60,63,66,68,70,72,73,74],"recommendation":"开发金属光泽提花窗帘"},
    "soft_minimalism": {"id":"soft_minimalism","name":"温柔极简","name_en":"Soft Minimalism","category":"风格趋势","score":85,"velocity":1.5,"lifecycle":"mature","peak_month":"2026-12","signals":{"social":88,"fashion":72,"culture":65,"economic":75,"search":90,"design":70},"resonance_score":77,"trend_data":[60,62,65,68,70,72,75,78,80,82,83,84,85,85,86,86],"recommendation":"开发奶油色纯色棉麻系列"},
    "maximalist_pattern": {"id":"maximalist_pattern","name":"极繁主义复兴","name_en":"Maximalist Revival","category":"图案趋势","score":65,"velocity":2.5,"lifecycle":"emerging","peak_month":"2027-09","signals":{"social":55,"fashion":75,"culture":70,"economic":50,"search":52,"design":78},"resonance_score":63,"trend_data":[30,32,35,38,40,43,46,48,52,55,58,60,62,63,64,65],"recommendation":"开发大马士革纹提花窗帘"}
}

SIGNAL_DIMENSIONS = {
    "social": {"name": "社交热度", "weight": 0.20},
    "fashion": {"name": "时尚上游", "weight": 0.18},
    "culture": {"name": "文化事件", "weight": 0.15},
    "economic": {"name": "经济情绪", "weight": 0.12},
    "search": {"name": "搜索趋势", "weight": 0.20},
    "design": {"name": "设计社区", "weight": 0.15}
}

@trend_bp.route('/')
def trend_index():
    return send_from_directory(TREND_FRONTEND, 'index.html')

@trend_bp.route('/assets/<path:fn>')
def trend_assets(fn):
    return send_from_directory(os.path.join(TREND_FRONTEND, 'assets'), fn)

@trend_bp.route('/api/dimensions', methods=['GET'])
def get_dimensions():
    return jsonify({'dimensions': SIGNAL_DIMENSIONS})

@trend_bp.route('/api/trends', methods=['GET'])
def get_trends():
    trends = sorted(TREND_DB.values(), key=lambda x: x['resonance_score'], reverse=True)
    return jsonify({'trends': trends})

@trend_bp.route('/api/trends/<tid>', methods=['GET'])
def get_trend(tid):
    t = TREND_DB.get(tid)
    if not t: return jsonify({'error': '不存在'}), 404
    return jsonify(t)

@trend_bp.route('/api/radar', methods=['GET'])
def radar():
    dims = {}
    for dim_key, dim_info in SIGNAL_DIMENSIONS.items():
        scores = [t['signals'][dim_key] for t in TREND_DB.values()]
        dims[dim_key] = {'name': dim_info['name'], 'avg_score': round(sum(scores)/len(scores), 1), 'max_score': max(scores)}
    return jsonify({'radar': dims})

@trend_bp.route('/api/predictions', methods=['GET'])
def predictions():
    import random
    preds = []
    for tid, t in TREND_DB.items():
        headroom = (100 - t['score']) / 100
        mult = 2.0 if t['lifecycle']=='emerging' else 1.2 if t['lifecycle']=='growth' else 0.4
        predicted = min(96, t['score'] + t['velocity'] * 6 * mult * headroom)
        preds.append({'id': t['id'], 'name': t['name'], 'current_score': t['score'], 'predicted_score': round(predicted), 'velocity': t['velocity'], 'lifecycle': t['lifecycle'], 'confidence': min(95, t['resonance_score'] + random.randint(-5, 10)), 'recommendation': t['recommendation']})
    preds.sort(key=lambda x: x['predicted_score'], reverse=True)
    return jsonify({'predictions': preds})

@trend_bp.route('/api/resonance', methods=['GET'])
def resonance():
    matrix = []
    trends = list(TREND_DB.values())
    for i, t1 in enumerate(trends):
        for j, t2 in enumerate(trends):
            if i >= j: continue
            total_sim = sum(max(0, 1 - abs(t1['signals'][d] - t2['signals'][d])/100) for d in SIGNAL_DIMENSIONS)
            resonance_val = total_sim / len(SIGNAL_DIMENSIONS)
            if resonance_val > 0.5:
                matrix.append({'trend_a': t1['name'], 'trend_b': t2['name'], 'resonance': round(resonance_val, 2)})
    matrix.sort(key=lambda x: x['resonance'], reverse=True)
    return jsonify({'matrix': matrix})

@trend_bp.route('/api/timeline/<tid>', methods=['GET'])
def timeline(tid):
    t = TREND_DB.get(tid)
    if not t: return jsonify({'error': '不存在'}), 404
    return jsonify({'months': [f"2025-{str(m).zfill(2)}" for m in range(6,13)] + [f"2026-{str(m).zfill(2)}" for m in range(1,10)], 'data': t['trend_data'], 'name': t['name']})

app.register_blueprint(trend_bp)


# ============ 启动 ============

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    print(f"织觉引擎 WeaveMind 统一服务启动: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)