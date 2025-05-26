from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from config import config

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
jwt = JWTManager()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
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
    
    app.register_blueprint(company_bp, url_prefix='/companies')
    app.register_blueprint(employee_bp, url_prefix='/employees')
    app.register_blueprint(credit_bp, url_prefix='/credits')
    app.register_blueprint(investment_bp, url_prefix='/investments')
    app.register_blueprint(invitation_bp, url_prefix='/invitations')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    
    return app
