"""
TripVault – Authentication helpers
"""

from database.extensions import db, bcrypt
from database.models import User


def create_user(first_name: str, last_name: str, email: str,
                password: str, phone: str = None) -> User:
    """Hash password and persist a new User row."""
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(
        first_name    = first_name.strip(),
        last_name     = last_name.strip(),
        email         = email.strip().lower(),
        phone         = phone,
        password_hash = hashed,
    )
    db.session.add(user)
    db.session.commit()
    return user


def verify_password(user: User, password: str) -> bool:
    return bcrypt.check_password_hash(user.password_hash, password)


def get_user_by_email(email: str) -> User | None:
    return User.query.filter_by(email=email.strip().lower()).first()
