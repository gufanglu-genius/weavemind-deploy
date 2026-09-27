"""
织觉引擎 - 空间感知引擎 v3
核心策略：同源prompt生成，保持房间一致性
"""
import os, json, time, uuid, random
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOAD = os.path.join(BASE_DIR, 'uploads')
OUTPUT = os.path.join(BASE_DIR, 'outputs')
FRONTEND = os.path.join(BASE_DIR, 'frontend')
META_DIR = os.path.join(BASE_DIR, 'metadata')
HISTORY_FILE = os.path.join(BASE_DIR, 'history.json')

for d in [UPLOAD, OUTPUT, META_DIR]:
    os.makedirs(d, exist_ok=True)

API_KEY = "sk-ws-H.RPLXLRI.9MeJ.MEUCIQCufXQMexCjUnKnw9haLk8xnSgHuhZ7mXjTkKgNNd0mHAIgDfY-v5vB1-_MTHu1zq2eCfaGuXa2a3_yRKQQRoQVSlk"
T2I_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
TASK_URL = "https://dashscope.aliyuncs.com/api/v1/tasks"
DASHSCOPE_VL_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "X-DashScope-Async": "enable"}

# ============ 纺织品 ============
TEXTILES = {
    "chinese_ink": {
        "name": "水墨江南",
        "desc": "水墨花鸟窗帘 · 东方雅韵",
        "curtain_desc": "elegant Chinese ink wash style silk curtains with hand-painted bamboo and plum blossom patterns in soft ink-black on rice-paper white with subtle gold-thread embroidery along the hems, translucent fabric gently filtering light"
    },
    "nordic_minimal": {
        "name": "北欧极简",
        "desc": "几何纹理亚麻帘 · 北欧清新",
        "curtain_desc": "Scandinavian minimalist linen curtains with geometric diamond pattern in muted sage green and cream white, natural linen texture with visible weave, clean modern lines"
    },
    "japanese_wabi": {
        "name": "侘寂之美",
        "desc": "原色亚麻帘 · 侘寂禅意",
        "curtain_desc": "Japanese wabi-sabi style natural undyed linen curtains with irregular organic weave texture in warm earth tones, imperfect beauty aesthetic, gentle natural drape"
    },
    "french_roma": {
        "name": "法式浪漫",
        "desc": "法式田园印花帘 · 浪漫优雅",
        "curtain_desc": "French romantic toile curtains with pastoral floral scene pattern in dusty rose and ivory cream, silk-like subtle sheen, elegant swag draping with soft folds"
    },
    "modern_abstract": {
        "name": "现代艺术",
        "desc": "抽象艺术印花帘 · 现代摩登",
        "curtain_desc": "contemporary abstract art curtains with bold brushstroke pattern in navy blue, teal, and gold, modern gallery inspired design, premium silk blend with fluid drape"
    },
    "luxury_velvet": {
        "name": "奢华丝绒",
        "desc": "祖母绿丝绒帘 · 低调奢华",
        "curtain_desc": "luxurious deep emerald green velvet curtains with subtle embossed damask pattern, rich heavy draping with soft folds catching warm ambient light"
    }
}

ROOM_STYLES = {
    "modern": {
        "base": "A photorealistic modern bright living room interior with large floor-to-ceiling windows letting in abundant natural light, light oak hardwood floors, white walls, minimalist low-profile charcoal sofa, walnut coffee table, single potted fiddle-leaf fig",
        "mood": "clean, airy, contemporary"
    },
    "bedroom": {
        "base": "A photorealistic cozy modern bedroom interior with a large window with soft morning light, queen bed with white linen sheets, wooden nightstands with warm bedside lamps, plush area rug, soft warm ambient lighting",
        "mood": "warm, inviting, restful"
    },
    "chinese": {
        "base": "A photorealistic Chinese traditional style room interior with rosewood furniture, large window with garden view, warm amber lighting, elegant calligraphy scrolls on wall, ceramic vase with dried branches",
        "mood": "refined, cultural, warm"
    },
    "nordic": {
        "base": "A photorealistic Scandinavian style bright room interior with panoramic window, white walls, light birch wood furniture, green monstera plants, cozy wool throw blanket, soft diffused natural light",
        "mood": "minimal, natural, hygge"
    }
}


# ============ 工具 ============
def allowed_file(fn):
    return '.' in fn and fn.rsplit('.', 1)[1].lower() in {'png','jpg','jpeg','webp'}

def poll_task(tid, max_wait=90):
    start = time.time()
    while time.time() - start < max_wait:
        try:
            r = requests.get(f"{TASK_URL}/{tid}", headers={"Authorization": f"Bearer {API_KEY}"}, timeout=15)
            d = r.json()
            s = d.get('output',{}).get('task_status')
            if s == 'SUCCEEDED':
                res = d['output'].get('results',[])
                return {'success':True, 'url':res[0]['url'], 'prompt':res[0].get('actual_prompt','')}
            elif s == 'FAILED':
                return {'success':False, 'error':d['output'].get('message','任务失败')}
        except: pass
        time.sleep(3)
    return {'success':False, 'error':'任务超时'}

def t2i_call(prompt, retries=3):
    """文生图，带重试"""
    payload = {"model":"wanx2.1-t2i-turbo","input":{"prompt":prompt},"parameters":{"size":"1024*1024","n":1}}
    last_err = None
    for i in range(retries):
        try:
            r = requests.post(T2I_URL, headers=HEADERS, json=payload, timeout=30)
            d = r.json()
            tid = d.get('output',{}).get('task_id')
            if not tid:
                last_err = d.get('message','创建任务失败')
                time.sleep(2**i); continue
            result = poll_task(tid)
            if result['success']: return result
            last_err = result['error']
        except Exception as e:
            last_err = str(e)
        time.sleep(2**i)
    return {'success':False, 'error':f'生成失败: {last_err}'}

def save_img(url, prefix='img'):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        fn = f"{prefix}_{uuid.uuid4().hex[:12]}.png"
        with open(os.path.join(OUTPUT, fn), 'wb') as f: f.write(r.content)
        return {'success':True, 'filename':fn}
    except Exception as e:
        return {'success':False, 'error':str(e)}

def save_meta(filename, data):
    """保存图片元数据（prompt等）"""
    meta_file = os.path.join(META_DIR, filename.replace('.png','.json'))
    with open(meta_file, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_meta(filename):
    """加载图片元数据"""
    meta_file = os.path.join(META_DIR, filename.replace('.png','.json'))
    if os.path.exists(meta_file):
        with open(meta_file, 'r') as f: return json.load(f)
    return None

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f: return json.load(f)
        except: pass
    return []

def save_history(entry):
    h = load_history()
    h.insert(0, entry)
    h = h[:50]
    with open(HISTORY_FILE, 'w') as f: json.dump(h, f, ensure_ascii=False)

def evaluate_fit(room_style, textile_id, custom):
    base = 75
    match = {
        'modern':   {'modern_abstract':8,'nordic_minimal':6,'luxury_velvet':5,'french_roma':3,'chinese_ink':2,'japanese_wabi':4},
        'bedroom':  {'luxury_velvet':8,'french_roma':7,'japanese_wabi':6,'chinese_ink':4,'nordic_minimal':5,'modern_abstract':3},
        'chinese':  {'chinese_ink':9,'japanese_wabi':5,'luxury_velvet':6,'french_roma':2,'nordic_minimal':2,'modern_abstract':3},
        'nordic':   {'nordic_minimal':9,'japanese_wabi':7,'modern_abstract':5,'chinese_ink':2,'french_roma':3,'luxury_velvet':3}
    }
    if room_style and textile_id:
        base += match.get(room_style,{}).get(textile_id, 0)
    elif custom:
        base += random.randint(3,7)
    score = min(98, base + random.randint(-3,5))
    pools = {
        'high': ['该纺织品与房间整体风格高度协调','色彩搭配自然和谐，视觉效果出众','材质质感与空间氛围形成完美呼应','建议搭配同色系靠枕进一步提升整体感'],
        'mid':  ['纺织品与空间整体协调度良好','建议搭配相近色系的地毯增强统一感','自然光下的呈现效果值得期待','可考虑增加装饰元素呼应窗帘色调'],
        'low':  ['建议选择更贴近房间主色调的纺织品','可尝试降低花型复杂度以匹配空间风格','推荐先确定房间主色调再选择窗帘','考虑使用纯色或简约纹理窗帘']
    }
    pool = pools['high'] if score>=85 else pools['mid'] if score>=70 else pools['low']
    return {'score':score, 'suggestions':random.sample(pool, min(3,len(pool))), 'level':'excellent' if score>=85 else 'good' if score>=70 else 'fair'}


# ============ 路由 ============
@app.route('/')
def index(): return send_from_directory(FRONTEND, 'index.html')

@app.route('/assets/<path:fn>')
def assets(fn): return send_from_directory(os.path.join(FRONTEND,'assets'), fn)

@app.route('/outputs/<path:fn>')
def outputs(fn): return send_from_directory(OUTPUT, fn)

@app.route('/uploads/<path:fn>')
def uploads(fn): return send_from_directory(UPLOAD, fn)


@app.route('/api/textiles', methods=['GET'])
def get_textiles():
    return jsonify({'textiles':[{'id':k,'name':v['name'],'description':v['desc']} for k,v in TEXTILES.items()]})


@app.route('/api/upload-room', methods=['POST'])
def upload_room():
    if 'file' not in request.files: return jsonify({'error':'未选择文件'}),400
    f = request.files['file']
    if f.filename=='': return jsonify({'error':'文件为空'}),400
    if not allowed_file(f.filename): return jsonify({'error':'不支持的格式'}),400
    fn = f"room_{uuid.uuid4().hex[:12]}_{secure_filename(f.filename)}"
    f.save(os.path.join(UPLOAD, fn))
    return jsonify({'success':True, 'filename':fn, 'size':os.path.getsize(os.path.join(UPLOAD,fn))})


@app.route('/api/generate-room', methods=['POST'])
def generate_room():
    """生成房间，同时保存prompt元数据用于后续预览一致性"""
    data = request.json
    style = data.get('style','modern')
    desc = data.get('description','')

    style_info = ROOM_STYLES.get(style, ROOM_STYLES['modern'])
    base_prompt = style_info['base']

    # 用户补充描述
    if desc:
        base_prompt += f", {desc}"

    # 添加摄影参数
    full_prompt = f"{base_prompt}. Interior photography, 35mm lens, natural lighting, 8k detail, no curtains visible, empty window with bright daylight coming through."

    result = t2i_call(full_prompt)
    if not result['success']:
        return jsonify({'error':result['error']}),500

    dl = save_img(result['url'], 'room')
    if not dl['success']:
        return jsonify({'error':dl['error']}),500

    # 保存元数据：基础prompt（不含窗帘，用于后续拼接）
    actual_prompt = result.get('prompt', full_prompt)
    meta = {
        'style': style,
        'user_desc': desc,
        'base_prompt': actual_prompt,  # 实际被模型增强后的prompt
        'room_base': style_info['base'],
        'mood': style_info['mood']
    }
    save_meta(dl['filename'], meta)

    save_history({
        'type':'room_generate', 'style':style, 'description':desc,
        'filename':dl['filename'], 'timestamp':time.strftime('%Y-%m-%d %H:%M:%S')
    })

    return jsonify({'success':True, 'filename':dl['filename'], 'prompt':actual_prompt})


@app.route('/api/preview-textile', methods=['POST'])
def preview_textile():
    """
    核心：同源prompt生成预览
    策略：
    1. AI生成的房间 → 读取保存的base_prompt，拼接纺织品描述
    2. 上传的房间 → 用Qwen-VL分析图片生成描述，拼接纺织品描述
    """
    data = request.json
    room_fn = data.get('room_image')
    textile_id = data.get('textile_id')
    custom = data.get('custom_prompt','')

    if not room_fn: return jsonify({'error':'缺少房间图片'}),400

    # 获取纺织品描述
    if textile_id and textile_id in TEXTILES:
        curtain_desc = TEXTILES[textile_id]['curtain_desc']
        textile_name = TEXTILES[textile_id]['name']
    elif custom:
        curtain_desc = custom
        textile_name = '自定义'
    else:
        return jsonify({'error':'请选择纺织品'}),400

    # 尝试加载房间元数据
    meta = load_meta(room_fn)

    if meta and meta.get('base_prompt'):
        # 有元数据 → 同源prompt生成，房间一致性最好
        base = meta['base_prompt']
        # 拼接：去掉原来"no curtains"的部分，加上窗帘描述
        preview_prompt = (
            f"{base}. "
            f"The large window now has beautiful {curtain_desc}. "
            f"The curtains drape naturally with realistic folds and light filtering through the fabric. "
            f"Interior photography, 35mm lens, natural lighting, 8k detail."
        )
    else:
        # 没有元数据（上传的图片）→ 用通用描述 + 纺织品
        # 判断是否在uploads目录
        is_uploaded = os.path.exists(os.path.join(UPLOAD, room_fn))
        if is_uploaded:
            # 上传的图片：尝试用Qwen-VL分析
            room_desc = analyze_room_image(os.path.join(UPLOAD, room_fn))
            if room_desc:
                preview_prompt = (
                    f"{room_desc}. "
                    f"The window has {curtain_desc}. "
                    f"Interior photography, 35mm lens, natural lighting, 8k detail."
                )
            else:
                preview_prompt = (
                    f"A bright modern room with large window. "
                    f"The window has {curtain_desc}. "
                    f"Interior photography, 35mm lens, natural lighting, 8k detail."
                )
        else:
            # 其他情况
            preview_prompt = (
                f"A bright modern room with large window, natural light, hardwood floor. "
                f"The window has {curtain_desc}. "
                f"Interior photography, 35mm lens, natural lighting, 8k detail."
            )

    result = t2i_call(preview_prompt)
    if not result['success']:
        return jsonify({'error':result['error']}),500

    dl = save_img(result['url'], 'preview')
    if not dl['success']:
        return jsonify({'error':dl['error']}),500

    # 保存预览的元数据（继承房间的）
    if meta:
        save_meta(dl['filename'], {**meta, 'textile':textile_id, 'curtain_desc':curtain_desc})

    save_history({
        'type':'textile_preview', 'room':room_fn, 'textile':textile_id or 'custom',
        'filename':dl['filename'], 'timestamp':time.strftime('%Y-%m-%d %H:%M:%S')
    })

    return jsonify({
        'success':True, 'filename':dl['filename'],
        'textile_name':textile_name, 'prompt':preview_prompt
    })


def analyze_room_image(image_path):
    """用Qwen-VL分析房间图片，生成描述"""
    try:
        import base64
        with open(image_path, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode()

        ext = image_path.rsplit('.',1)[-1].lower()
        mime = {'jpg':'jpeg','jpeg':'jpeg','png':'png','webp':'webp'}.get(ext,'jpeg')

        r = requests.post(DASHSCOPE_VL_URL, headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }, json={
            "model": "qwen-vl-max",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/{mime};base64,{b64}"}},
                    {"type": "text", "text": "Describe this room in English in one detailed paragraph for image generation. Include: room type, furniture, colors, lighting, flooring, walls, style. Be specific about the window. Do NOT describe any curtains or window treatments - the window should be described as bare/empty with light coming through. Output only the description, no preamble."}
                ]
            }],
            "max_tokens": 500
        })
        d = r.json()
        desc = d.get('choices',[{}])[0].get('message',{}).get('content','')
        return desc.strip() if desc else None
    except Exception as e:
        print(f"VL analysis error: {e}")
        return None


@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    d = request.json
    return jsonify(evaluate_fit(d.get('room_style','modern'), d.get('textile_id'), d.get('custom_prompt','')))


@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify({'history':load_history()[:request.args.get('limit',20,type=int)]})

@app.route('/api/history', methods=['DELETE'])
def clear_history():
    if os.path.exists(HISTORY_FILE): os.remove(HISTORY_FILE)
    return jsonify({'success':True})


if __name__ == '__main__':
    print("织觉引擎 v3 启动: http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)