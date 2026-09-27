"""
织觉翻译器 v2
AestheticTranslator — 把世界万物翻译成家纺面料
深度融合南通非遗工艺基因
"""
import os, sys, json, time, base64
from datetime import datetime
import requests, numpy as np, cv2
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE = os.path.dirname(os.path.dirname(__file__))
FRONTEND = os.path.join(BASE, 'frontend')
REF_DIR = os.path.join(BASE, 'references', 'nantong-ich')
GEN_DIR = os.path.join(BASE, 'generated')
META_DIR = os.path.join(BASE, 'metadata')
CV_DIR = os.path.join(BASE, 'cv_modules')
os.makedirs(GEN_DIR, exist_ok=True)
os.makedirs(META_DIR, exist_ok=True)

sys.path.insert(0, CV_DIR)
from feature_extractor import extract_all, features_to_aesthetic_dna

API_KEY = "sk-ws-H.RPLXLRI.9MeJ.MEUCIQCufXQMexCjUnKnw9haLk8xnSgHuhZ7mXjTkKgNNd0mHAIgDfY-v5vB1-_MTHu1zq2eCfaGuXa2a3_yRKQQRoQVSlk"
TREND_API = "http://localhost:5002"
SPATIAL_API = "http://localhost:5001"


# ============ 南通非遗工艺基因库 ============
# 每种工艺有完整的DNA定义 + prompt模板 + 现代化融合方向

ICH_CRAFTS = {
    "blue_calico": {
        "id": "blue_calico",
        "name": "蓝印花布",
        "name_en": "Blue Calico",
        "origin": "南通",
        "level": "国家级非遗",
        "era": "明代至今",
        "desc": "以靛蓝为染料，豆粉石灰为防染浆，经刻版、刮浆、染色、刮灰等工序制成。蓝白相间，素雅清新。",
        "craft_traits": "防染印花、靛蓝染色、手工刻版",
        "dna": {
            "color_warmth": 30, "saturation": 35, "pattern_complex": 70,
            "texture_feel": 55, "style_modern": 20, "material_weight": 45,
            "luminosity": 15, "organic_ratio": 85
        },
        "prompt_core": "Chinese indigo blue calico, deep blue and white resist pattern, traditional folk art motifs, hand-block printed, artisan textile",
        "modern_fusion": "将蓝印花布的蓝白对比与现代几何结合，保留防染肌理感，图案从传统花鸟演变为抽象线条",
        "image": "/references/nantong-ich/nantong_blue_calico.png"
    },
    "tie_dye": {
        "id": "tie_dye",
        "name": "扎染",
        "name_en": "Tie-Dye",
        "origin": "南通",
        "level": "省级非遗",
        "era": "唐代至今",
        "desc": "通过捆扎、缝绞、夹扎等手法防染，形成自然晕色和有机纹理，每件作品独一无二。",
        "craft_traits": "手工捆扎、自然晕染、有机纹理",
        "dna": {
            "color_warmth": 40, "saturation": 50, "pattern_complex": 45,
            "texture_feel": 40, "style_modern": 40, "material_weight": 35,
            "luminosity": 25, "organic_ratio": 90
        },
        "prompt_core": "Chinese traditional tie-dye, indigo shibori, organic resist pattern, natural gradient, handcrafted unique texture",
        "modern_fusion": "扎染的随机性与数字渐变结合，靛蓝扩展为多色系，保留手工痕迹的同时加入几何扎法",
        "image": "/references/nantong-ich/nantong_tie_dye.png"
    },
    "shen_embroidery": {
        "id": "shen_embroidery",
        "name": "沈绣",
        "name_en": "Shen Embroidery",
        "origin": "南通",
        "level": "国家级非遗",
        "era": "清末至今",
        "desc": "以沈寿为代表的仿真绣技法，融合西洋画理，针法细腻如照片般写实，被誉为中国刺绣的巅峰。",
        "craft_traits": "仿真绣法、丝线劈丝、光影渐变",
        "dna": {
            "color_warmth": 55, "saturation": 60, "pattern_complex": 85,
            "texture_feel": 30, "style_modern": 35, "material_weight": 25,
            "luminosity": 55, "organic_ratio": 70
        },
        "prompt_core": "fine silk embroidery, photorealistic needlework, delicate thread painting, Chinese Suzhou-style embroidery, raised texture detail",
        "modern_fusion": "沈绣的写实技法与数码像素风格碰撞，用渐变丝线表现现代图案，保留浮雕般的立体触感",
        "image": "/references/nantong-ich/nantong_shen_embroidery.png"
    },
    "tubu_weaving": {
        "id": "tubu_weaving",
        "name": "土布纺织",
        "name_en": "Handwoven Cotton",
        "origin": "南通",
        "level": "省级非遗",
        "era": "千年传承",
        "desc": "手工纺纱、脚踏织机，经纬交错织出条格纹样。质朴厚实，是最原始的家纺面料形态。",
        "craft_traits": "手工纺纱、脚踏织机、经纬交织",
        "dna": {
            "color_warmth": 55, "saturation": 20, "pattern_complex": 25,
            "texture_feel": 80, "style_modern": 15, "material_weight": 65,
            "luminosity": 10, "organic_ratio": 95
        },
        "prompt_core": "handwoven cotton cloth, rustic natural fiber, earth tone stripes and checks, raw cotton texture, artisan loom woven",
        "modern_fusion": "土布的粗粝质感与极简设计融合，条格纹用现代色彩重新诠释，保留手工织造的不规则肌理",
        "image": "/references/nantong-ich/nantong_tubu_weaving.png"
    },
    "silk_weaving": {
        "id": "silk_weaving",
        "name": "丝绸织造",
        "name_en": "Silk Brocade",
        "origin": "南通",
        "level": "市级非遗",
        "era": "宋元至今",
        "desc": "南通丝绸以提花织造见长，云锦、宋锦等纹样在丝线上交织出华丽图案，光泽流转。",
        "craft_traits": "提花织造、金线交织、多层色彩",
        "dna": {
            "color_warmth": 65, "saturation": 70, "pattern_complex": 80,
            "texture_feel": 20, "style_modern": 25, "material_weight": 40,
            "luminosity": 80, "organic_ratio": 50
        },
        "prompt_core": "Chinese silk brocade, intricate jacquard weave, lustrous fabric, traditional cloud and crane pattern, gold thread accent",
        "modern_fusion": "丝绸的华丽光泽与Art Deco几何结合，传统云纹抽象化为现代装饰图案，保留丝线的高级光泽",
        "image": "/references/nantong-ich/nantong_silk_weaving.png"
    },
    "kite_pattern": {
        "id": "kite_pattern",
        "name": "板鹞风筝",
        "name_en": "Kite Art",
        "origin": "南通",
        "level": "国家级非遗",
        "era": "宋代至今",
        "desc": "南通板鹞风筝以哨口音乐和彩绘装饰闻名，几何骨架上绘满吉祥纹样，色彩浓烈大胆。",
        "craft_traits": "几何骨架、彩绘装饰、哨口排列",
        "dna": {
            "color_warmth": 60, "saturation": 85, "pattern_complex": 75,
            "texture_feel": 30, "style_modern": 40, "material_weight": 20,
            "luminosity": 60, "organic_ratio": 45
        },
        "prompt_core": "Chinese ornamental kite pattern, bold geometric folk art, colorful decorative motifs, traditional auspicious symbols",
        "modern_fusion": "板鹞风筝的浓烈色彩与孟菲斯设计风格碰撞，几何骨架变体为现代图案结构",
        "image": "/references/nantong-ich/nantong_kite_pattern.png"
    }
}

# 翻译模式
TRANSLATION_MODES = {
    "faithful":   {"name": "忠实还原", "desc": "最大程度保留原图气质", "suffix": ""},
    "abstract":   {"name": "抽象提炼", "desc": "提取核心视觉基因重构", "suffix": ", abstract artistic interpretation, simplified forms, textile design"},
    "pattern":    {"name": "纹样生成", "desc": "转化为可重复的面料图案", "suffix": ", seamless repeating tile pattern, textile print, screen printable"},
    "fusion":     {"name": "非遗融合", "desc": "与南通传统工艺深度结合", "suffix": ""}  # 融合模式prompt在translate中动态生成
}


# ============ DashScope API ============

def cv_fallback_analysis(cv_features):
    """当VL API不可用时，从CV特征推导出分析结果"""
    if not cv_features:
        return {"subject": "图片", "mood": "现代", "style": "通用", "color_desc": "自然配色",
                "texture_hint": "织物", "pattern_type": "混合", "ich_suggestion": "",
                "textile_prompt": "high quality textile curtain fabric design"}

    c = cv_features.get("color", {})
    t = cv_features.get("texture", {})
    p = cv_features.get("composition", {})
    warmth = c.get("warmth", 50)
    sat = c.get("saturation", 50)
    rough = t.get("roughness", 50)
    dom = c.get("dominant_colors", [])

    # 情绪
    if warmth > 60 and sat > 60: mood = "热烈"
    elif warmth > 60 and sat < 40: mood = "温馨"
    elif warmth < 40 and sat < 40: mood = "宁静"
    elif warmth < 40: mood = "冷峻"
    else: mood = "现代"

    # 风格
    if rough > 60: style = "民族"
    elif rough < 30: style = "极简"
    else: style = "现代"

    # 配色描述
    hex0 = dom[0]["hex"] if dom else "#888"
    color_desc = f"主色{hex0}"
    if len(dom) > 1: color_desc += f"，辅色{dom[1]['hex']}"

    # 图案类型
    complexity = p.get("complexity", 50)
    if complexity > 70: pattern = "复杂纹样"
    elif complexity < 30: pattern = "纯色"
    else: pattern = "几何图案"

    # 材质
    if rough > 70: texture = "粗糙"
    elif rough < 30: texture = "丝滑"
    else: texture = "织物"

    # 非遗推荐
    ich = ""
    if warmth < 40 and sat < 50: ich = "蓝印花布"
    elif rough > 60: ich = "土布纺织"
    elif sat > 70: ich = "板鹞风筝"
    elif warmth > 60 and rough < 30: ich = "丝绸织造"
    else: ich = "扎染"

    # 生成prompt
    parts = ["high quality textile curtain fabric design"]
    if warmth > 60: parts.append("warm color palette")
    elif warmth < 40: parts.append("cool color palette")
    if sat > 60: parts.append("vivid saturated colors")
    elif sat < 40: parts.append("muted neutral tones")
    if rough > 60: parts.append("rough handwoven texture")
    elif rough < 30: parts.append("smooth silk surface")
    parts.append("studio lighting, 8k detail")

    return {
        "subject": f"{style}风格织物",
        "mood": mood, "style": style,
        "color_desc": color_desc,
        "texture_hint": texture,
        "pattern_type": pattern,
        "ich_suggestion": ich,
        "textile_prompt": ", ".join(parts)
    }


def qwen_vl_analyze(image_path):
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    ext = os.path.splitext(image_path)[1].lower()
    mime = {".jpg":"image/jpeg",".jpeg":"image/jpeg",".png":"image/png",".webp":"image/webp"}.get(ext, "image/jpeg")

    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    body = {
        "model": "qwen-vl-max",
        "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64}"}},
            {"type": "text", "text": """从家纺设计视角分析此图，输出JSON：
{
  "subject": "主体描述(20字内)",
  "mood": "情绪(宁静/热烈/复古/现代/浪漫/自然/庄重/活泼)",
  "style": "风格(东方/西方/民族/极简/田园/赛博/古典/前卫)",
  "color_desc": "主色调和配色特点(30字内)",
  "texture_hint": "材质暗示(丝滑/粗糙/木质/金属/植物/矿物)",
  "pattern_type": "图案类型(几何/花卉/抽象/写实/条纹/纯色/波点/云纹)",
  "textile_prompt": "50词英文prompt用于AI生成家纺面料",
  "ich_suggestion": "最适合融合的南通非遗工艺(蓝印花布/扎染/沈绣/土布纺织/丝绸织造/板鹞风筝)，给出理由"
}
只输出JSON。"""}
        ]}]
    }
    r = requests.post(url, headers=headers, json=body, timeout=60)
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    try:
        start = content.index('{')
        end = content.rindex('}') + 1
        return json.loads(content[start:end])
    except:
        return None


def t2i_call(prompt, size="1024*1024"):
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "X-DashScope-Async": "enable"}
    body = {"model": "wanx2.1-t2i-turbo", "input": {"prompt": prompt}, "parameters": {"size": size, "n": 1}}
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
        if status == "SUCCEEDED": return data["output"]["results"]
        elif status in ("FAILED", "UNKNOWN"): raise RuntimeError(f"Task {status}")
        time.sleep(2)
    raise TimeoutError("Timeout")


def build_fusion_prompt(base_prompt, craft, dna):
    """非遗融合模式：智能混合原图prompt与工艺基因"""
    craft_prompt = craft["prompt_core"]
    parts = []

    # 核心：工艺基底
    parts.append(craft_prompt)

    # 从原图提取的元素
    if base_prompt:
        parts.append(f"inspired by {base_prompt}")

    # DNA驱动的风格调节
    if dna.get("saturation", 50) > 65:
        parts.append("rich vivid colors")
    elif dna.get("saturation", 50) < 35:
        parts.append("muted subdued palette")
    if dna.get("pattern_complex", 50) > 70:
        parts.append("intricate detailed ornamentation")
    elif dna.get("pattern_complex", 50) < 30:
        parts.append("clean minimal elements")
    if dna.get("style_modern", 50) > 60:
        parts.append("contemporary modern interpretation")
    if dna.get("organic_ratio", 50) > 70:
        parts.append("natural handmade feel")

    parts.append("high quality textile product photography, studio lighting, 8k")
    return ", ".join(parts)


# ============ 路由 ============

@app.route('/')
def index():
    return send_from_directory(FRONTEND, 'index.html')

@app.route('/assets/<path:fn>')
def assets(fn):
    return send_from_directory(os.path.join(FRONTEND, 'assets'), fn)

@app.route('/generated/<path:fn>')
def generated(fn):
    return send_from_directory(GEN_DIR, fn)

@app.route('/references/<path:fn>')
def references(fn):
    return send_from_directory(os.path.join(BASE, 'references'), fn)


@app.route('/api/crafts', methods=['GET'])
def get_crafts():
    """获取非遗工艺库"""
    items = []
    for cid, c in ICH_CRAFTS.items():
        items.append({
            "id": c["id"], "name": c["name"], "name_en": c["name_en"],
            "origin": c["origin"], "level": c["level"], "era": c["era"],
            "desc": c["desc"], "craft_traits": c["craft_traits"],
            "modern_fusion": c["modern_fusion"],
            "dna": c["dna"], "image": c["image"], "prompt_core": c["prompt_core"]
        })
    return jsonify({"crafts": items})

@app.route('/api/modes', methods=['GET'])
def get_modes():
    return jsonify({"modes": TRANSLATION_MODES})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """分析图片：CV特征 + AI理解 + 非遗推荐"""
    if 'image' not in request.files:
        return jsonify({"error": "请上传图片"}), 400

    f = request.files['image']
    fname = f"upload_{int(time.time())}.png"
    fpath = os.path.join(GEN_DIR, fname)
    f.save(fpath)

    # CV特征
    cv_features = extract_all(fpath)
    dna = features_to_aesthetic_dna(cv_features)

    # AI理解 — 优先VL，失败时用CV兜底
    try:
        ai = qwen_vl_analyze(fpath)
        if ai is None:
            raise RuntimeError("VL返回空")
        ai["source"] = "vl"
    except Exception as e:
        ai = cv_fallback_analysis(cv_features)
        ai["source"] = "cv"
        ai["note"] = "AI视觉模型暂不可用，基于CV特征生成"

    # 智能推荐非遗工艺：基于CV特征匹配
    craft_matches = []
    for cid, craft in ICH_CRAFTS.items():
        cdna = craft["dna"]
        # 计算DNA距离（越小越匹配）
        dist = 0
        for k in ["color_warmth","saturation","pattern_complex","texture_feel","style_modern","organic_ratio"]:
            dist += abs(dna.get(k, 50) - cdna.get(k, 50))
        # 但也计算互补性（差异大 = 融合更有张力）
        tension = 100 - dist / 6
        match_score = round(max(0, min(100, 70 - dist/3 + tension/5)))
        craft_matches.append({
            "craft_id": cid,
            "craft_name": craft["name"],
            "match_score": match_score,
            "reason": craft["modern_fusion"]
        })
    craft_matches.sort(key=lambda x: x["match_score"], reverse=True)

    result = {
        "image_url": f"/generated/{fname}",
        "cv_features": cv_features,
        "aesthetic_dna": dna,
        "ai_analysis": ai,
        "craft_recommendations": craft_matches
    }

    meta_path = os.path.join(META_DIR, f"analysis_{int(time.time())}.json")
    with open(meta_path, "w") as fp:
        json.dump(result, fp, ensure_ascii=False, indent=2, default=str)

    return jsonify(result)


@app.route('/api/translate', methods=['POST'])
def translate():
    """翻译生成花型"""
    data = request.get_json()
    mode = data.get("mode", "faithful")
    base_prompt = data.get("base_prompt", "high quality textile curtain fabric design")
    dna = data.get("dna", {})
    craft_id = data.get("craft_id", "")

    mode_info = TRANSLATION_MODES.get(mode, TRANSLATION_MODES["faithful"])

    if mode == "fusion" and craft_id and craft_id in ICH_CRAFTS:
        # 非遗融合模式：深度结合
        craft = ICH_CRAFTS[craft_id]
        prompt = build_fusion_prompt(base_prompt, craft, dna)
    else:
        # 其他模式
        parts = [base_prompt]
        if mode_info.get("suffix"):
            parts.append(mode_info["suffix"])
        # DNA微调
        if dna.get("saturation", 50) > 70: parts.append("vibrant saturated")
        elif dna.get("saturation", 50) < 30: parts.append("muted neutral")
        if dna.get("color_warmth", 50) > 65: parts.append("warm tones")
        elif dna.get("color_warmth", 50) < 35: parts.append("cool tones")
        if dna.get("organic_ratio", 50) > 70: parts.append("natural organic")
        parts.append("professional textile photography, studio lighting, 8k")
        prompt = ", ".join(filter(None, parts))

    ts = int(time.time())

    try:
        task_id = t2i_call(prompt)
        results = poll_task(task_id)
        if results:
            img_url = results[0].get("url", "")
            fname = f"trans_{ts}.png"
            img_data = requests.get(img_url, timeout=30).content
            with open(os.path.join(GEN_DIR, fname), "wb") as fp:
                fp.write(img_data)

            meta = {
                "id": f"trans_{ts}", "prompt": prompt, "mode": mode,
                "dna": dna, "craft_id": craft_id,
                "craft_name": ICH_CRAFTS[craft_id]["name"] if craft_id in ICH_CRAFTS else "",
                "image": fname, "created_at": datetime.now().isoformat(),
                "img_url": f"/generated/{fname}"
            }
            with open(os.path.join(META_DIR, f"trans_{ts}.json"), "w") as fp:
                json.dump(meta, fp, ensure_ascii=False, indent=2)

            return jsonify({"success": True, "image_url": f"/generated/{fname}", "prompt": prompt, "meta": meta})
    except Exception:
        pass  # 降级到参考图

    # AI生图不可用时，使用非遗参考图
    ref_img = None
    ref_name = ""
    if craft_id and craft_id in ICH_CRAFTS:
        ref_img = ICH_CRAFTS[craft_id].get("image", "")
        ref_name = ICH_CRAFTS[craft_id]["name"]
    if not ref_img:
        # 选一个最匹配的参考图
        for cid, c in ICH_CRAFTS.items():
            if c.get("image"):
                ref_img = c["image"]
                ref_name = c["name"]
                break

    if ref_img:
        meta = {
            "id": f"trans_{ts}", "prompt": prompt, "mode": mode,
            "dna": dna, "craft_id": craft_id,
            "craft_name": ref_name,
            "image": os.path.basename(ref_img), "created_at": datetime.now().isoformat(),
            "img_url": ref_img, "is_reference": True
        }
        return jsonify({
            "success": True,
            "image_url": ref_img,
            "prompt": prompt,
            "meta": meta,
            "note": f"AI生图服务暂不可用，展示{ref_name}非遗参考作品"
        })

    return jsonify({"success": False, "error": "AI生图服务暂不可用，请充值DashScope账户后重试"}), 503


@app.route('/api/trend_validate', methods=['POST'])
def trend_validate():
    """趋势校验"""
    data = request.get_json()
    try:
        r = requests.get(f"{TREND_API}/api/trends", timeout=5)
        trends = r.json().get("trends", [])
        matches = []
        for t in trends:
            matches.append({
                "trend_name": t["name"], "trend_score": t["score"],
                "resonance": t["resonance_score"], "lifecycle": t["lifecycle"],
                "confidence": min(95, t["resonance_score"] + 10)
            })
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        return jsonify({"matches": matches[:4]})
    except:
        return jsonify({"matches": [], "note": "趋势引擎未启动"})


@app.route('/api/history', methods=['GET'])
def history():
    items = []
    if os.path.exists(META_DIR):
        for fn in sorted(os.listdir(META_DIR), reverse=True):
            if fn.startswith('trans_') and fn.endswith('.json'):
                try:
                    with open(os.path.join(META_DIR, fn)) as f:
                        items.append(json.load(f))
                except: pass
    return jsonify({"history": items[:30]})


if __name__ == '__main__':
    print("织觉翻译器 v2 启动: http://localhost:5004")
    app.run(host='0.0.0.0', port=5004, debug=False)