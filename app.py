from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import json
import okey_ai
import os

app = Flask(__name__)
CORS(app)

# Global AI instance
ai_engine = okey_ai.OkeyAI()

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        tiles = data.get('tiles', [])
        indicator = data.get('indicator', {})
        discarded_tiles = data.get('discarded_tiles', [])
        
        # AI analizi
        result = ai_engine.analyze_hand(tiles, discarded_tiles, indicator)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/suggest_tile', methods=['POST'])
def suggest_tile():
    try:
        data = request.get_json()
        tiles = data.get('tiles', [])
        indicator = data.get('indicator', {})
        discarded_tiles = data.get('discarded_tiles', [])
        
        # Taş önerisi
        result = ai_engine.suggest_best_tile(tiles, discarded_tiles, indicator)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulate', methods=['POST'])
def simulate():
    try:
        data = request.get_json()
        tiles = data.get('tiles', [])
        indicator = data.get('indicator', {})
        discarded_tiles = data.get('discarded_tiles', [])
        
        # Monte Carlo simülasyonu
        result = ai_engine.monte_carlo_simulation(tiles, discarded_tiles, indicator)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 