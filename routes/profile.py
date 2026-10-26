"""
TripVault – Profile blueprint
Routes: /profile  (GET view, POST update)
        /profile/change-password
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TelField, PasswordField
from wtforms.validators import DataRequired, Length, Optional, EqualTo, ValidationError

from database.extensions import db, bcrypt
from services.auth_service import verify_password

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


# ---------------------------------------------------------------------------
# Forms (defined here to keep profile self-contained)
# ---------------------------------------------------------------------------

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name  = StringField('Last Name',  validators=[DataRequired(), Length(max=64)])
    phone      = TelField('Phone Number',  validators=[Optional(), Length(max=20)])


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password     = PasswordField('New Password',
                                     validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password',
                                     validators=[DataRequired(),
                                                 EqualTo('new_password', 'Passwords must match')])

    def validate_current_password(self, field):
        if not verify_password(current_user, field.data):
            raise ValidationError('Current password is incorrect.')


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@profile_bp.route('/', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def profile():
    pform = ProfileForm(obj=current_user)
    cform = ChangePasswordForm()

    if 'save_profile' in request.form and pform.validate_on_submit():
        current_user.first_name = pform.first_name.data.strip()
        current_user.last_name  = pform.last_name.data.strip()
        current_user.phone      = pform.phone.data or None
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile.profile'))

    if 'change_password' in request.form and cform.validate_on_submit():
        current_user.password_hash = bcrypt.generate_password_hash(
            cform.new_password.data).decode('utf-8')
        db.session.commit()
        flash('Password changed successfully.', 'success')
        return redirect(url_for('profile.profile'))

    return render_template('profile.html', pform=pform, cform=cform)
