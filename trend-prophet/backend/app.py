"""
趋势先知引擎 v1
跨6个信号维度检测趋势共振，预测家纺行业未来6个月走向
"""
import os, json, time, math, random
from datetime import datetime, timedelta
from collections import defaultdict
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE = os.path.dirname(os.path.dirname(__file__))
FRONTEND = os.path.join(BASE, 'frontend')
DATA_DIR = os.path.join(BASE, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

API_KEY = "sk-ws-H.RPLXLRI.9MeJ.MEUCIQCufXQMexCjUnKnw9haLk8xnSgHuhZ7mXjTkKgNNd0mHAIgDfY-v5vB1-_MTHu1zq2eCfaGuXa2a3_yRKQQRoQVSlk"

# ============ 趋势数据库 ============
# 真实场景下从API/爬虫获取，这里基于行业研究构建模拟数据

TREND_DB = {
    "wabi_sabi": {
        "id": "wabi_sabi",
        "name": "侘寂美学",
        "name_en": "Wabi-Sabi Textiles",
        "category": "风格趋势",
        "description": "源自日本的不完美之美，强调自然材质、手工质感、素雅色调。在家纺领域表现为未漂染的原色亚麻、不规则织纹、大地色系。",
        "keywords": ["侘寂", "wabi-sabi", "原色亚麻", "手工感", "大地色", "不完美", "自然材质", "留白"],
        "color_palette": ["#d4c5a9", "#8b7d6b", "#a0926e", "#c8bfa0", "#6b5b4a"],
        "score": 87,
        "velocity": 2.3,  # 增速（每月%）
        "lifecycle": "growth",  # 萌芽/爆发/成熟/衰退
        "peak_month": "2027-03",
        "signals": {
            "social": 92,     # 社交热度
            "fashion": 85,    # 时尚上游
            "culture": 78,    # 文化事件
            "economic": 70,   # 经济情绪
            "search": 88,     # 搜索趋势
            "design": 90      # 设计社区
        },
        "resonance_score": 84,  # 共振得分
        "trend_data": [45, 48, 52, 55, 58, 62, 65, 68, 72, 76, 80, 84, 87, 90, 92, 94],
        "months": ["2025-06","2025-07","2025-08","2025-09","2025-10","2025-11","2025-12","2026-01","2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09"],
        "recommendation": "推荐开发原色亚麻窗帘系列，搭配手工编织纹理，定价中高端。目标客群：25-40岁追求生活品质的都市人群。"
    },
    "dopamine_home": {
        "id": "dopamine_home",
        "name": "多巴胺家居",
        "name_en": "Dopamine Decor",
        "category": "色彩趋势",
        "description": "高饱和度色彩在家纺中的大胆应用，通过明亮的色彩刺激愉悦感。从时装界的多巴胺穿搭延伸到家居领域。",
        "keywords": ["多巴胺", "高饱和", "明亮色彩", "撞色", "快乐", "活力", "彩虹", "糖果色"],
        "color_palette": ["#ff6b6b", "#ffd93d", "#6bcb77", "#4d96ff", "#ff6bd6"],
        "score": 79,
        "velocity": 3.1,
        "lifecycle": "growth",
        "peak_month": "2027-01",
        "signals": {
            "social": 85,
            "fashion": 90,
            "culture": 72,
            "economic": 65,
            "search": 78,
            "design": 75
        },
        "resonance_score": 78,
        "trend_data": [30, 35, 40, 48, 55, 60, 65, 68, 72, 75, 78, 80, 82, 83, 84, 85],
        "months": ["2025-06","2025-07","2025-08","2025-09","2025-10","2025-11","2025-12","2026-01","2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09"],
        "recommendation": "开发彩色拼接窗帘和渐变色床品系列，主打年轻市场。建议先在小红书/抖音做内容种草测试市场反应。"
    },
    "quiet_luxury": {
        "id": "quiet_luxury",
        "name": "静奢风",
        "name_en": "Quiet Luxury",
        "category": "品质趋势",
        "description": "低调奢华的极简主义，强调材质本身的高级感而非logo。在家纺领域表现为高支棉、真丝、羊绒等天然材质的纯色设计。",
        "keywords": ["静奢", "quiet luxury", "低调奢华", "高支棉", "真丝", "纯色", "质感", "无logo"],
        "color_palette": ["#f5f0e8", "#d4c9b8", "#8a7f72", "#2c2825", "#c5b9a8"],
        "score": 82,
        "velocity": 1.8,
        "lifecycle": "growth",
        "peak_month": "2027-06",
        "signals": {
            "social": 75,
            "fashion": 92,
            "culture": 68,
            "economic": 85,
            "search": 72,
            "design": 80
        },
        "resonance_score": 79,
        "trend_data": [50, 52, 55, 57, 60, 63, 65, 68, 70, 73, 75, 77, 79, 81, 83, 85],
        "months": ["2025-06","2025-07","2025-08","2025-09","2025-10","2025-11","2025-12","2026-01","2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09"],
        "recommendation": "开发高支数纯色棉麻系列，强调面料触感和工艺细节。适合高端酒店和精品住宅市场。"
    },
    "digital_garden": {
        "id": "digital_garden",
        "name": "数字花园",
        "name_en": "Digital Garden",
        "category": "图案趋势",
        "description": "将数字艺术的超现实花卉图案应用到纺织品上，结合AI生成的梦幻植物纹样，打破传统花型的写实边界。",
        "keywords": ["数字花园", "AI花型", "超现实", "梦幻花卉", "赛博植物", "生成艺术", "数码印花"],
        "color_palette": ["#7b68ee", "#00ced1", "#ff69b4", "#98fb98", "#dda0dd"],
        "score": 74,
        "velocity": 4.2,
        "lifecycle": "emerging",
        "peak_month": "2027-09",
        "signals": {
            "social": 68,
            "fashion": 65,
            "culture": 82,
            "economic": 55,
            "search": 60,
            "design": 95
        },
        "resonance_score": 71,
        "trend_data": [15, 18, 22, 28, 35, 40, 45, 50, 55, 58, 62, 65, 68, 71, 73, 75],
        "months": ["2025-06","2025-07","2025-08","2025-09","2025-10","2025-11","2025-12","2026-01","2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09"],
        "recommendation": "结合织觉引擎的AI花型生成能力，开发限量版数字艺术窗帘。适合与设计师联名，打造话题性产品。"
    },
    "eco_revolution": {
        "id": "eco_revolution",
        "name": "可持续革新",
        "name_en": "Eco-Revolution",
        "category": "材料趋势",
        "description": "环保不再只是营销口号，而是从纤维到成品的全链路革新。再生涤纶、有机棉、竹纤维等可持续材料成为主流选择。",
        "keywords": ["可持续", "环保", "再生纤维", "有机棉", "竹纤维", "碳中和", "绿色制造", "可降解"],
        "color_palette": ["#228b22", "#8fbc8f", "#f0e68c", "#deb887", "#556b2f"],
        "score": 80,
        "velocity": 2.0,
        "lifecycle": "growth",
        "peak_month": "2027-12",
        "signals": {
            "social": 72,
            "fashion": 78,
            "culture": 85,
            "economic": 60,
            "search": 75,
            "design": 82
        },
        "resonance_score": 75,
        "trend_data": [40, 42, 45, 48, 52, 55, 58, 62, 65, 68, 72, 75, 78, 80, 82, 84],
        "months": ["2025-06","2025-07","2025-08","2025-09","2025-10","2025-11","2025-12","2026-01","2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09"],
        "recommendation": "开发竹纤维窗帘和有机棉床品线，主打环保故事。建议申请绿色认证，作为品牌差异化卖点。"
    },
    "neon_chinese": {
        "id": "neon_chinese",
        "name": "新赛博中式",
        "name_en": "Neo-Cyber Chinese",
        "category": "风格趋势",
        "description": "传统中式元素与未来科技感的碰撞，将水墨、云纹、龙凤等传统图案用霓虹色和金属质感重新演绎。",
        "keywords": ["赛博中式", "新中式", "霓虹", "金属质感", "未来国风", "数字东方", "科技水墨"],
        "color_palette": ["#ff0040", "#00ff88", "#ffd700", "#1a1a2e", "#c0c0c0"],
        "score": 71,
        "velocity": 3.8,
        "lifecycle": "emerging",
        "peak_month": "2027-06",
        "signals": {
            "social": 78,
            "fashion": 62,
            "culture": 88,
            "economic": 55,
            "search": 65,
            "design": 72
        },
        "resonance_score": 70,
        "trend_data": [20, 25, 30, 35, 42, 48, 52, 56, 60, 63, 66, 68, 70, 72, 73, 74],
        "months": ["2025-06","2025-07","2025-08","2025-09","2025-10","2025-11","2025-12","2026-01","2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09"],
        "recommendation": "开发金属光泽提花窗帘，融合传统云纹/水波纹图案。目标Z世代国潮爱好者，可与国潮IP联名。"
    },
    "soft_minimalism": {
        "id": "soft_minimalism",
        "name": "温柔极简",
        "name_en": "Soft Minimalism",
        "category": "风格趋势",
        "description": "极简主义的柔和进化，不再是冰冷的黑白灰，而是加入奶油色、燕麦色等温暖色调的极简风格。",
        "keywords": ["温柔极简", "奶油风", "燕麦色", "暖白", "柔和", "舒适极简", "hygge"],
        "color_palette": ["#f5f0e8", "#e8ddd0", "#d4c9b8", "#c5b9a8", "#b8a99a"],
        "score": 85,
        "velocity": 1.5,
        "lifecycle": "mature",
        "peak_month": "2026-12",
        "signals": {
            "social": 88,
            "fashion": 72,
            "culture": 65,
            "economic": 75,
            "search": 90,
            "design": 70
        },
        "resonance_score": 77,
        "trend_data": [60, 62, 65, 68, 70, 72, 75, 78, 80, 82, 83, 84, 85, 85, 86, 86],
        "months": ["2025-06","2025-07","2025-08","2025-09","2025-10","2025-11","2025-12","2026-01","2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09"],
        "recommendation": "开发奶油色/燕麦色纯色棉麻系列，强调柔软触感。适合大众市场，可作为基础款长期供应。"
    },
    "maximalist_pattern": {
        "id": "maximalist_pattern",
        "name": "极繁主义复兴",
        "name_en": "Maximalist Revival",
        "category": "图案趋势",
        "description": "与极简主义的对撞，大胆的几何、佩斯利、大马士革等复杂图案重新回归，强调'更多即是更多'。",
        "keywords": ["极繁主义", "maximalist", "佩斯利", "大马士革", "几何", "混搭", "繁复", "华丽"],
        "color_palette": ["#8b0000", "#006400", "#191970", "#daa520", "#800080"],
        "score": 65,
        "velocity": 2.5,
        "lifecycle": "emerging",
        "peak_month": "2027-09",
        "signals": {
            "social": 55,
            "fashion": 75,
            "culture": 70,
            "economic": 50,
            "search": 52,
            "design": 78
        },
        "resonance_score": 63,
        "trend_data": [30, 32, 35, 38, 40, 43, 46, 48, 52, 55, 58, 60, 62, 63, 64, 65],
        "months": ["2025-06","2025-07","2025-08","2025-09","2025-10","2025-11","2025-12","2026-01","2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09"],
        "recommendation": "开发大马士革纹提花窗帘和佩斯利印花床品，主打酒店和高端住宅市场。需要精准的色彩搭配避免视觉疲劳。"
    }
}

# 信号维度定义
SIGNAL_DIMENSIONS = {
    "social":  {"name": "社交热度", "icon": "S", "desc": "小红书/抖音/微博 家纺相关内容热度", "weight": 0.20},
    "fashion": {"name": "时尚上游", "icon": "F", "desc": "巴黎/米兰/纽约时装周色彩与面料趋势", "weight": 0.18},
    "culture": {"name": "文化事件", "icon": "C", "desc": "电影/综艺/展览/艺术潮流对家纺的影响", "weight": 0.15},
    "economic":{"name": "经济情绪", "icon": "E", "desc": "消费信心/房价/就业数据对家居消费的影响", "weight": 0.12},
    "search":  {"name": "搜索趋势", "icon": "Q", "desc": "电商平台家纺品类搜索词热度变化", "weight": 0.20},
    "design":  {"name": "设计社区", "icon": "D", "desc": "Behance/Dribbble/Pinterest 家纺设计趋势", "weight": 0.15}
}

# 行业新闻（模拟）
INDUSTRY_NEWS = [
    {"title": "米兰设计周：自然材质成最大赢家", "source": "设计在线", "date": "2026-09-15", "trend": "wabi_sabi", "impact": "high"},
    {"title": "小红书'奶油风'搜索量月增35%", "source": "电商报", "date": "2026-09-12", "trend": "soft_minimalism", "impact": "high"},
    {"title": "可持续纺织品市场规模突破500亿", "source": "产业经济", "date": "2026-09-10", "trend": "eco_revolution", "impact": "medium"},
    {"title": "AI生成花型在家纺领域应用激增", "source": "科技日报", "date": "2026-09-08", "trend": "digital_garden", "impact": "high"},
    {"title": "Z世代国潮消费同比增长42%", "source": "消费报告", "date": "2026-09-05", "trend": "neon_chinese", "impact": "medium"},
    {"title": "巴黎时装周：极繁主义强势回归", "source": "Vogue", "date": "2026-09-02", "trend": "maximalist_pattern", "impact": "high"},
    {"title": "高端酒店家纺采购偏好转向静奢风", "source": "酒店业", "date": "2026-08-28", "trend": "quiet_luxury", "impact": "medium"},
    {"title": "多巴胺色彩在家居领域搜索量翻倍", "source": "Pinterest", "date": "2026-08-25", "trend": "dopamine_home", "impact": "high"},
    {"title": "南通家纺产业带出口订单回暖12%", "source": "南通日报", "date": "2026-08-20", "trend": "eco_revolution", "impact": "low"},
    {"title": "侘寂风窗帘在小红书种草笔记超10万篇", "source": "社交数据", "date": "2026-08-18", "trend": "wabi_sabi", "impact": "high"},
]


# ============ 分析引擎 ============

def get_current_month():
    return datetime.now().strftime("%Y-%m")

def get_trend_summary():
    """获取所有趋势概览"""
    trends = []
    for tid, t in TREND_DB.items():
        trends.append({
            'id': t['id'],
            'name': t['name'],
            'name_en': t['name_en'],
            'category': t['category'],
            'score': t['score'],
            'velocity': t['velocity'],
            'lifecycle': t['lifecycle'],
            'peak_month': t['peak_month'],
            'resonance_score': t['resonance_score'],
            'color_palette': t['color_palette'],
            'signals': t['signals']
        })
    # 按共振得分排序
    trends.sort(key=lambda x: x['resonance_score'], reverse=True)
    return trends

def get_trend_detail(trend_id):
    """获取单个趋势详情"""
    t = TREND_DB.get(trend_id)
    if not t: return None
    return {
        **t,
        'signal_dimensions': SIGNAL_DIMENSIONS,
        'news': [n for n in INDUSTRY_NEWS if n['trend'] == trend_id]
    }

def get_radar_data():
    """获取雷达图数据 - 各维度平均分"""
    dims = {}
    for dim_key, dim_info in SIGNAL_DIMENSIONS.items():
        scores = [t['signals'][dim_key] for t in TREND_DB.values()]
        dims[dim_key] = {
            'name': dim_info['name'],
            'avg_score': round(sum(scores)/len(scores), 1),
            'max_score': max(scores),
            'max_trend': max(TREND_DB.values(), key=lambda t: t['signals'][dim_key])['name']
        }
    return dims

def get_resonance_matrix():
    """计算趋势间的共振矩阵"""
    matrix = []
    trends = list(TREND_DB.values())
    for i, t1 in enumerate(trends):
        for j, t2 in enumerate(trends):
            if i >= j: continue
            # 基于信号维度相似度计算共振（加权平均差值）
            total_sim = 0
            shared = []
            for dim in SIGNAL_DIMENSIONS:
                diff = abs(t1['signals'][dim] - t2['signals'][dim])
                sim = max(0, 1 - diff/100)
                total_sim += sim
                if sim > 0.7:
                    shared.append(SIGNAL_DIMENSIONS[dim]['name'] if isinstance(SIGNAL_DIMENSIONS[dim], dict) else dim)
            resonance = total_sim / len(SIGNAL_DIMENSIONS)
            if resonance > 0.5:
                matrix.append({
                    'trend_a': t1['name'],
                    'trend_b': t2['name'],
                    'resonance': round(resonance, 2),
                    'shared_dims': shared
                })
    matrix.sort(key=lambda x: x['resonance'], reverse=True)
    return matrix

def get_predictions():
    """趋势预测 - 未来6个月"""
    predictions = []
    now = datetime.now()
    for tid, t in TREND_DB.items():
        # 基于当前得分和速度预测未来（S曲线衰减）
        months_ahead = 6
        # 已经很高的趋势增长空间小，低分趋势有更多上升空间
        headroom = (100 - t['score']) / 100
        mult = 2.0 if t['lifecycle']=='emerging' else 1.2 if t['lifecycle']=='growth' else 0.4
        predicted_score = min(96, t['score'] + t['velocity'] * months_ahead * mult * headroom)

        # 计算置信度
        resonance = t['resonance_score']
        confidence = min(95, resonance + random.randint(-5, 10))

        predictions.append({
            'id': t['id'],
            'name': t['name'],
            'current_score': t['score'],
            'predicted_score': round(predicted_score),
            'velocity': t['velocity'],
            'lifecycle': t['lifecycle'],
            'confidence': confidence,
            'recommendation': t['recommendation'],
            'peak_month': t['peak_month']
        })

    predictions.sort(key=lambda x: x['predicted_score'], reverse=True)
    return predictions


# ============ 路由 ============

@app.route('/')
def index():
    return send_from_directory(FRONTEND, 'index.html')

@app.route('/assets/<path:fn>')
def assets(fn):
    return send_from_directory(os.path.join(FRONTEND, 'assets'), fn)

@app.route('/api/dimensions', methods=['GET'])
def get_dimensions():
    """获取信号维度定义"""
    return jsonify({'dimensions': SIGNAL_DIMENSIONS})

@app.route('/api/trends', methods=['GET'])
def get_trends():
    """获取所有趋势概览"""
    return jsonify({'trends': get_trend_summary()})

@app.route('/api/trends/<tid>', methods=['GET'])
def get_trend(tid):
    """获取单个趋势详情"""
    detail = get_trend_detail(tid)
    if not detail: return jsonify({'error':'趋势不存在'}),404
    return jsonify(detail)

@app.route('/api/radar', methods=['GET'])
def radar():
    """获取雷达图数据"""
    return jsonify({'radar': get_radar_data()})

@app.route('/api/resonance', methods=['GET'])
def resonance():
    """获取共振矩阵"""
    return jsonify({'matrix': get_resonance_matrix()})

@app.route('/api/predictions', methods=['GET'])
def predictions():
    """获取趋势预测"""
    return jsonify({'predictions': get_predictions()})

@app.route('/api/news', methods=['GET'])
def news():
    """获取行业新闻"""
    limit = request.args.get('limit', 10, type=int)
    return jsonify({'news': INDUSTRY_NEWS[:limit]})

@app.route('/api/timeline/<tid>', methods=['GET'])
def timeline(tid):
    """获取趋势时间线数据"""
    t = TREND_DB.get(tid)
    if not t: return jsonify({'error':'不存在'}),404
    return jsonify({
        'months': t['months'],
        'data': t['trend_data'],
        'name': t['name'],
        'lifecycle': t['lifecycle']
    })


if __name__ == '__main__':
    print("趋势先知引擎启动: http://localhost:5002")
    app.run(host='0.0.0.0', port=5002, debug=False)