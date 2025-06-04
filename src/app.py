import os
import logging
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///neuropulse.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
}

# Initialize database
db = SQLAlchemy(app, model_class=Base)

# Initialize database with error handling
with app.app_context():
    try:
        # Use existing models from models.py with proper table extension
        import models
        db.create_all()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")
        # Continue without database if needed
        pass

# Initialize core application first
app.config['ADVANCED_FEATURES_ENABLED'] = True

# Import routes with graceful fallback
def import_routes():
    try:
        # Import working core routes first
        import core_routes
        logger.info("Core routes imported successfully")
        
        # Try to import additional features
        try:
            import advanced_routes
            logger.info("Advanced feature routes imported")
        except Exception as e:
            logger.warning(f"Advanced routes not available: {e}")
            app.config['ADVANCED_FEATURES_ENABLED'] = False
            
    except Exception as e:
        logger.error(f"Route import error: {e}")
        app.config['ADVANCED_FEATURES_ENABLED'] = False

# Execute route imports
import_routes()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
