"""
TripVault – Booking helpers
"""

import random
import string
from datetime import date

from database.extensions import db
from database.models import Booking, BookingStatus, Destination


def generate_booking_ref() -> str:
    """Generate a unique booking reference like TV-A3X9K2."""
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choices(chars, k=6))
    return f'TV-{suffix}'


def create_booking(user_id: int, form_data: dict) -> Booking:
    """
    Create and persist a Booking from validated form data dict.
    form_data keys mirror BookingForm fields.
    """
    dest = Destination.query.get_or_404(form_data['destination_id'])

    child_price   = round(dest.price * 0.7, 2)
    adult_total   = dest.price * form_data['num_adults']
    children_total= child_price * form_data['num_children']
    taxes         = 180.0
    total         = adult_total + children_total + taxes

    # Ensure unique ref
    while True:
        ref = generate_booking_ref()
        if not Booking.query.filter_by(booking_ref=ref).first():
            break

    booking = Booking(
        booking_ref      = ref,
        user_id          = user_id,
        destination_id   = dest.id,
        travel_date      = form_data['travel_date'],
        return_date      = form_data.get('return_date'),
        num_adults       = form_data['num_adults'],
        num_children     = form_data['num_children'],
        lead_first_name  = form_data['lead_first_name'],
        lead_last_name   = form_data['lead_last_name'],
        lead_email       = form_data['lead_email'],
        lead_phone       = form_data.get('lead_phone'),
        lead_passport    = form_data.get('lead_passport'),
        lead_nationality = form_data.get('lead_nationality'),
        lead_dob         = form_data.get('lead_dob'),
        dietary          = form_data.get('dietary', 'None'),
        notes            = form_data.get('notes'),
        price_per_person = dest.price,
        total_price      = total,
        taxes            = taxes,
        # Payment is completed on the separate review/pay screen.
        status           = BookingStatus.PENDING,
    )
    db.session.add(booking)
    db.session.commit()
    return booking


def cancel_booking(booking_id: int, user_id: int) -> Booking | None:
    """Cancel a booking if it belongs to the user and is not already completed."""
    booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first()
    if booking and booking.status not in (BookingStatus.COMPLETED, BookingStatus.CANCELLED):
        booking.status = BookingStatus.CANCELLED
        db.session.commit()
    return booking


def get_user_bookings(user_id: int):
    return (Booking.query
            .filter_by(user_id=user_id)
            .order_by(Booking.created_at.desc())
            .all())


def get_upcoming_bookings(user_id: int):
    today = date.today()
    return (Booking.query
            .filter(Booking.user_id == user_id,
                    Booking.travel_date >= today,
                    Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]))
            .order_by(Booking.travel_date)
            .all())
