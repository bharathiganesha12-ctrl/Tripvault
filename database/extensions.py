"""
Shared Flask extension instances.
Import from here everywhere to avoid circular imports.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail

db           = SQLAlchemy()
login_manager = LoginManager()
bcrypt       = Bcrypt()
csrf         = CSRFProtect()
mail         = Mail()

# Redirect to login page when @login_required fails
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'
