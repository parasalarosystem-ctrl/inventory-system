from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, limiter, socketio
from flask_migrate import Migrate
from app.models import User

migrate = Migrate()  # Initialize Flask-Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ---------------------
    # Initialize extensions
    # ---------------------
    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    limiter.init_app(app)
    socketio.init_app(app, cors_allowed_origins='*', async_mode='eventlet')

    login_manager.login_view = 'main.login'

    # ---------------------
    # Initialize Google OAuth
    # ---------------------


    # ---------------------
    # Register blueprints
    # ---------------------
    from app.main.routes import main
    app.register_blueprint(main)


    # Inventory blueprint
    from app.inventory.routes import inventory_bp
    app.register_blueprint(inventory_bp)  # URL prefix handled in blueprint

    # ---------------------
    # User loader
    # ---------------------
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

 # ---------------------
    # Database setup
    # ---------------------
    with app.app_context():
        from app.models import User
        db.create_all()

        # Check if admin exists by USERNAME (since that is what caused the error)
        if not User.query.filter_by(username='admin').first(): 
            admin_user = User(
                username='admin', 
                email='krich7901@gmail.com', 
                oauth_provider='local'
            )
            admin_user.set_password('adminpassword')
            db.session.add(admin_user)
            db.session.commit()
            print("[OK] Default admin created")
        else:
            print("[INFO] Admin already exists, skipping creation.")
   
    return app
