from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_compress import Compress
from datetime import datetime

from config import Config
from models import db, User

# Initialize extensions
login_manager = LoginManager()
migrate = Migrate()
compress = Compress()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    compress.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Import and register blueprints
    from routes.auth import auth_bp
    from routes.contact import contact_bp
    from routes.orders import orders_bp
    from routes.payments import payments_bp
    from routes.addresses import addresses_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(payments_bp, url_prefix='/payments')
    app.register_blueprint(addresses_bp, url_prefix='/addresses')
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}, 200

    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
