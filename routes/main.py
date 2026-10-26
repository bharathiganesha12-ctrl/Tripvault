"""
TripVault – Main / public blueprint
Routes: /  /destinations  /trip/<id>  /dashboard  /booking  /my-bookings
"""

from datetime import date
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, abort)
from flask_login import login_required, current_user

from database.extensions import db
from database.models import Destination, Booking, BookingStatus
from database.forms import BookingForm
from services.booking_service import (create_booking, cancel_booking,
                                       get_user_bookings, get_upcoming_bookings)
from services.email_service import send_booking_confirmation, send_cancellation_email

main_bp = Blueprint('main', __name__)


# ---------------------------------------------------------------------------
# Landing
# ---------------------------------------------------------------------------

@main_bp.route('/')
def index():
    featured = Destination.query.filter_by(is_active=True).limit(6).all()
    return render_template('index.html', featured=featured)


# ---------------------------------------------------------------------------
# Destinations
# ---------------------------------------------------------------------------

@main_bp.route('/destinations')
def destinations():
    # Collect filter params
    search    = request.args.get('q', '').strip()
    continent = request.args.get('continent', '')
    category  = request.args.get('category', '')
    max_price = request.args.get('max_price', 5000, type=int)

    query = Destination.query.filter_by(is_active=True)

    if search:
        query = query.filter(Destination.name.ilike(f'%{search}%'))
    if continent:
        query = query.filter_by(continent=continent)
    if category:
        query = query.filter_by(category=category)
    if max_price:
        query = query.filter(Destination.price <= max_price)

    all_destinations = query.order_by(Destination.rating.desc()).all()
    return render_template('destinations.html',
                           destinations=all_destinations,
                           search=search, continent=continent,
                           category=category, max_price=max_price)


# ---------------------------------------------------------------------------
# Trip detail
# ---------------------------------------------------------------------------

@main_bp.route('/trip/<int:destination_id>')
def trip_details(destination_id):
    dest = Destination.query.get_or_404(destination_id)
    return render_template('trip_details.html', dest=dest)


# ---------------------------------------------------------------------------
# Booking
# ---------------------------------------------------------------------------

@main_bp.route('/booking/<int:destination_id>', methods=['GET', 'POST'])
@login_required
def booking(destination_id):
    dest = Destination.query.get_or_404(destination_id)
    form = BookingForm()
    form.destination_id.data = destination_id

    if form.validate_on_submit():
        booking_obj = create_booking(
            user_id   = current_user.id,
            form_data = {
                'destination_id':  destination_id,
                'travel_date':     form.travel_date.data,
                'return_date':     form.return_date.data,
                'num_adults':      form.num_adults.data,
                'num_children':    form.num_children.data,
                'lead_first_name': form.lead_first_name.data,
                'lead_last_name':  form.lead_last_name.data,
                'lead_email':      form.lead_email.data,
                'lead_phone':      form.lead_phone.data,
                'lead_passport':   form.lead_passport.data,
                'lead_nationality':form.lead_nationality.data,
                'lead_dob':        form.lead_dob.data,
                'dietary':         form.dietary.data,
                'notes':           form.notes.data,
            }
        )
        return redirect(url_for('main.booking_payment', booking_id=booking_obj.id))

    return render_template('booking.html', dest=dest, form=form)


@main_bp.route('/booking/pay/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def booking_payment(booking_id):
    """Review the booking and complete the local payment confirmation step."""
    booking_obj = Booking.query.filter_by(
        id=booking_id, user_id=current_user.id
    ).first_or_404()
    if booking_obj.status == BookingStatus.CONFIRMED:
        return redirect(url_for('main.booking_confirmation', booking_id=booking_obj.id))

    if request.method == 'POST':
        booking_obj.status = BookingStatus.CONFIRMED
        db.session.commit()
        flash(f'Payment confirmed! Booking reference: {booking_obj.booking_ref}.', 'success')
        send_booking_confirmation(booking_obj)
        return redirect(url_for('main.booking_confirmation', booking_id=booking_obj.id))

    return render_template('booking_payment.html', booking=booking_obj)


@main_bp.route('/booking/confirmation/<int:booking_id>')
@login_required
def booking_confirmation(booking_id):
    """Show the confirmation screen for a booking owned by the signed-in user."""
    booking_obj = Booking.query.filter_by(
        id=booking_id, user_id=current_user.id
    ).first_or_404()
    return render_template('booking_confirmation.html', booking=booking_obj)


# ---------------------------------------------------------------------------
# My bookings
# ---------------------------------------------------------------------------

@main_bp.route('/my-bookings')
@login_required
def my_bookings():
    all_bookings = get_user_bookings(current_user.id)
    upcoming     = [b for b in all_bookings
                    if b.travel_date >= date.today()
                    and b.status in (BookingStatus.PENDING, BookingStatus.CONFIRMED)]
    completed    = [b for b in all_bookings if b.status == BookingStatus.COMPLETED]
    cancelled    = [b for b in all_bookings if b.status == BookingStatus.CANCELLED]

    return render_template('my_bookings.html',
                           all_bookings=all_bookings,
                           upcoming=upcoming,
                           completed=completed,
                           cancelled=cancelled)


@main_bp.route('/booking/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking_route(booking_id):
    booking_obj = cancel_booking(booking_id, current_user.id)
    if booking_obj:
        send_cancellation_email(booking_obj)
    flash('Booking has been cancelled.', 'info')
    return redirect(url_for('main.my_bookings'))


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@main_bp.route('/dashboard')
@login_required
def dashboard():
    all_bookings = get_user_bookings(current_user.id)
    upcoming     = get_upcoming_bookings(current_user.id)
    completed    = [b for b in all_bookings if b.status == BookingStatus.COMPLETED]

    from services.document_service import get_user_documents
    docs = get_user_documents(current_user.id)

    return render_template('dashboard.html',
                           all_bookings=all_bookings,
                           upcoming=upcoming,
                           completed=completed,
                           docs=docs)
