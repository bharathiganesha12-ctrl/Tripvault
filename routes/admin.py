"""
TripVault – Admin blueprint
Routes: /admin  /admin/destinations  /admin/destinations/add  /admin/destinations/toggle
        /admin/destinations/delete  /admin/bookings  /admin/users
"""

from functools import wraps
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, abort)
from flask_login import login_required, current_user

from database.extensions import db
from database.models import Destination, Booking, User, Document
from database.forms import DestinationForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator: only allow is_admin users."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return login_required(decorated)


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@admin_bp.route('/')
@admin_required
def dashboard():
    total_users    = User.query.count()
    total_bookings = Booking.query.count()
    total_docs     = Document.query.count()
    total_revenue  = db.session.query(
        db.func.sum(Booking.total_price)
    ).scalar() or 0

    recent_bookings = (Booking.query
                       .order_by(Booking.created_at.desc())
                       .limit(10).all())
    top_destinations = (db.session
                        .query(Destination,
                               db.func.count(Booking.id).label('booking_count'))
                        .outerjoin(Booking)
                        .group_by(Destination.id)
                        .order_by(db.desc('booking_count'))
                        .limit(5).all())
    destinations = Destination.query.order_by(Destination.name).all()

    return render_template('admin_dashboard.html',
                           total_users=total_users,
                           total_bookings=total_bookings,
                           total_docs=total_docs,
                           total_revenue=total_revenue,
                           recent_bookings=recent_bookings,
                           top_destinations=top_destinations,
                           destinations=destinations)


# ---------------------------------------------------------------------------
# Destinations CRUD
# ---------------------------------------------------------------------------

@admin_bp.route('/destinations/add', methods=['GET', 'POST'])
@admin_required
def add_destination():
    form = DestinationForm()
    if form.validate_on_submit():
        dest = Destination(
            name        = form.name.data,
            country     = form.country.data,
            continent   = form.continent.data,
            category    = form.category.data,
            description = form.description.data,
            price       = form.price.data,
            duration    = form.duration.data,
            best_time   = form.best_time.data,
            rating      = form.rating.data or 4.5,
            image_url   = form.image_url.data,
            is_active   = form.is_active.data,
        )
        db.session.add(dest)
        db.session.commit()
        flash(f'Destination "{dest.name}" added successfully.', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin_dashboard.html', form=form)


@admin_bp.route('/destinations/toggle/<int:dest_id>', methods=['POST'])
@admin_required
def toggle_destination(dest_id):
    dest = Destination.query.get_or_404(dest_id)
    dest.is_active = not dest.is_active
    db.session.commit()
    state = 'activated' if dest.is_active else 'deactivated'
    flash(f'"{dest.name}" has been {state}.', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/destinations/delete/<int:dest_id>', methods=['POST'])
@admin_required
def delete_destination(dest_id):
    dest = Destination.query.get_or_404(dest_id)
    db.session.delete(dest)
    db.session.commit()
    flash(f'Destination "{dest.name}" deleted.', 'warning')
    return redirect(url_for('admin.dashboard'))


# ---------------------------------------------------------------------------
# Users list
# ---------------------------------------------------------------------------

@admin_bp.route('/users')
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_dashboard.html', all_users=all_users)
