from flask import Flask, request, jsonify
from flask_cors import CORS
from g4f.client import Client
import g4f.Provider
import os

app = Flask(__name__)
CORS(app)

# Inicializar cliente
client = Client(provider=g4f.Provider.Video)

@app.route('/')
def home():
    return jsonify({
        "message": "Video Generation API",
        "status": "running",
        "endpoints": {
            "/models": "GET - Get available models",
            "/generate": "POST - Generate video"
        }
    })

@app.route('/models', methods=['GET'])
def get_models():
    """Obtener modelos disponibles"""
    try:
        video_models = client.models.get_video()
        return jsonify({
            "success": True,
            "models": video_models
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/generate', methods=['POST'])
def generate_video():
    """Generar video a partir de un prompt"""
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                "success": False,
                "error": "Prompt is required"
            }), 400
        
        prompt = data['prompt']
        model = data.get('model', 'search')
        
        if not prompt.strip():
            return jsonify({
                "success": False,
                "error": "Prompt cannot be empty"
            }), 400
        
        # Generar video (g4f maneja internamente lo asíncrono)
        result = client.media.generate(
            model=model,
            prompt=prompt,
            response_format="url"
        )
        
        if result and hasattr(result, 'data') and len(result.data) > 0:
            return jsonify({
                "success": True,
                "video_url": result.data[0].url,
                "model_used": model,
                "prompt": prompt
            })
        else:
            return jsonify({
                "success": False,
                "error": "No video generated"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
