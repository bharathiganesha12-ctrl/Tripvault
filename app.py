"""
TripVault – A Cloud-Based Travel Booking and Secure Document Management System
Application factory — Phase 3 (Email + Storage + Production config)
"""

import os
from flask import Flask, render_template
from dotenv import load_dotenv

load_dotenv()

from database.extensions import db, login_manager, bcrypt, csrf, mail


# ---------------------------------------------------------------------------
# Config classes
# ---------------------------------------------------------------------------

class Config:
    SECRET_KEY                    = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH            = 25 * 1024 * 1024   # 25 MB
    WTF_CSRF_TIME_LIMIT           = 3600

    # Mail defaults (overridden by subclass or env vars)
    MAIL_SERVER         = os.environ.get('MAIL_SERVER',  'smtp.gmail.com')
    MAIL_PORT           = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS        = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME       = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD       = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'TripVault <noreply@tripvault.dev>')
    MAIL_SUPPRESS_SEND  = False   # set True in tests


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.abspath('instance'), 'tripvault.db')
    )
    # Suppress real emails in dev if no mail creds configured
    MAIL_SUPPRESS_SEND = not bool(os.environ.get('MAIL_USERNAME'))


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://', 1
    )

    @classmethod
    def validate(cls):
        if not cls.SQLALCHEMY_DATABASE_URI:
            raise ValueError('DATABASE_URL must be set in production')


config_map = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app(config_name: str = None):
    app = Flask(__name__)

    cfg_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config_map.get(cfg_name, DevelopmentConfig))

    os.makedirs(app.instance_path, exist_ok=True)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    # User loader
    from database.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Blueprints
    from routes.auth      import auth_bp
    from routes.main      import main_bp
    from routes.documents import documents_bp
    from routes.admin     import admin_bp
    from routes.profile   import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(profile_bp)

    # Error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(413)
    def too_large(e):
        from flask import flash, redirect, url_for
        flash('File too large. Maximum upload size is 25 MB.', 'danger')
        return redirect(url_for('documents.documents'))

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    # CLI: flask seed
    @app.cli.command('seed')
    def seed_command():
        """Seed the database with sample destinations and demo accounts."""
        from database.seed import seed_db
        seed_db(app)

    # Auto-create tables + seed on first run
    with app.app_context():
        db.create_all()
        _auto_seed(app)

    @app.get('/healthz')
    def healthz():
        return {'status': 'ok'}, 200

    return app


def _auto_seed(app):
    # The seed routine is idempotent and adds new catalogue entries without
    # touching existing bookings, users, or destinations.
    from database.seed import seed_db
    seed_db(app)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.debug,
    )
