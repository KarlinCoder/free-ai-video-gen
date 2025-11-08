from flask import Flask, request, jsonify
from flask_cors import CORS
from g4f.client import Client
import g4f.Provider
import asyncio
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class VideoGenerator:
    def __init__(self):
        self.client = Client(provider=g4f.Provider.Video)
        self.video_models = None
    
    async def get_models(self):
        """Obtener modelos de video disponibles"""
        if self.video_models is None:
            self.video_models = self.client.models.get_video()
        return self.video_models
    
    async def generate_video(self, prompt, model_index=0):
        """Generar video basado en el prompt"""
        try:
            models = await self.get_models()
            
            if not models:
                return {"error": "No video models available"}
            
            if model_index >= len(models):
                model_index = 0
            
            logger.info(f"Generating video with model: {models[model_index]}, prompt: {prompt}")
            
            result = await self.client.media.generate(
                model=models[model_index],
                prompt=prompt,
                response_format="url"
            )
            
            if result and hasattr(result, 'data') and len(result.data) > 0:
                return {
                    "success": True,
                    "video_url": result.data[0].url,
                    "model_used": models[model_index]
                }
            else:
                return {"error": "No video generated"}
                
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}")
            return {"error": str(e)}

# Instancia global del generador
video_generator = VideoGenerator()

@app.route('/')
def home():
    return jsonify({
        "message": "Video Generation API",
        "endpoints": {
            "/models": "GET - List available models",
            "/generate": "POST - Generate video"
        }
    })

@app.route('/models', methods=['GET'])
async def get_models():
    """Endpoint para obtener modelos disponibles"""
    try:
        models = await video_generator.get_models()
        return jsonify({
            "success": True,
            "models": models
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/generate', methods=['POST'])
async def generate_video():
    """Endpoint para generar video"""
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                "success": False,
                "error": "Prompt is required"
            }), 400
        
        prompt = data['prompt']
        model_index = data.get('model_index', 0)
        
        if not prompt.strip():
            return jsonify({
                "success": False,
                "error": "Prompt cannot be empty"
            }), 400
        
        result = await video_generator.generate_video(prompt, model_index)
        
        if "error" in result:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 500
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in generate endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

# Handler para funciones asíncronas en Flask
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "video-generation-api"})

if __name__ == '__main__':
    port = 5000
    app.run(host='0.0.0.0', port=port, debug=False)