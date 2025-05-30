from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for all routes with more specific configuration
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })
    
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    jwt.init_app(app)
    
    # Register blueprints
    from app.routes.company_routes import company_bp
    from app.routes.employee_routes import employee_bp
    from app.routes.credit_routes import credit_bp
    from app.routes.investment_routes import investment_bp
    from app.routes.invitation_routes import invitation_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.users import users_bp
    from app.routes.manager_routes import manager_bp
    from app.routes.wallet_routes import wallet_bp
    
    app.register_blueprint(company_bp, url_prefix='/api/companies')
    app.register_blueprint(employee_bp, url_prefix='/api/employees')
    app.register_blueprint(credit_bp, url_prefix='/api/credits')
    app.register_blueprint(investment_bp, url_prefix='/api/investment')
    app.register_blueprint(invitation_bp, url_prefix='/api/invitations')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(manager_bp, url_prefix='/api/manager')
    app.register_blueprint(wallet_bp, url_prefix='/api')
    
    return app
