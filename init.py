from flask import Flask
from flask_cors import CORS

# Create Flask app instance
app = Flask(__name__)

# Configure CORS
CORS(app, 
     resources={r"/api/*": {
         "origins": ["http://localhost:3000", "https://exper-frontend-production.up.railway.app", "https://expergle.com"], 
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization", "Accept"],
         "expose_headers": ["Content-Type", "Authorization"],
         "supports_credentials": True,
         "allow_credentials": True,
         "max_age": 120
     }},
     supports_credentials=True)