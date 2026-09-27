"""织觉引擎统一入口服务 port 5000"""
import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE = os.path.dirname(__file__)

@app.route('/')
def index():
    return send_from_directory(BASE, 'index.html')

@app.route('/c2m.html')
def c2m():
    return send_from_directory(BASE, 'c2m.html')

@app.route('/references/<path:fn>')
def references(fn):
    ref_dir = os.path.join(BASE, 'aesthetic-translator', 'references')
    return send_from_directory(ref_dir, fn)

@app.route('/assets/<path:fn>')
def assets(fn):
    return send_from_directory(os.path.join(BASE, 'generated-assets'), fn)

@app.route('/api/status')
def status():
    return jsonify({
        'name': '织觉引擎 WeaveMind',
        'version': '2.0',
        'engines': {
            'aesthetic_translator': {'port': 5004, 'status': 'ready'},
            'spatial_engine': {'port': 5001, 'status': 'ready'},
            'trend_prophet': {'port': 5002, 'status': 'ready'},
            'gene_editor': {'port': 5003, 'status': 'ready'}
        }
    })

if __name__ == '__main__':
    print("织觉引擎入口启动: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
