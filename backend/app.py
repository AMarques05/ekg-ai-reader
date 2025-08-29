from flask import Flask
from flask_cors import CORS
from routes.ekg_routes import bp as ekg_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(ekg_bp, url_prefix="/ekg")

if __name__ == "__main__":
    app.run(debug=True)
