"""
TripVault – SQLAlchemy Models
Tables: User, Destination, Booking, Document
"""

from datetime import datetime, timezone
from flask_login import UserMixin
from database.extensions import db


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    first_name    = db.Column(db.String(64),  nullable=False)
    last_name     = db.Column(db.String(64),  nullable=False)
    email         = db.Column(db.String(128), nullable=False, unique=True, index=True)
    phone         = db.Column(db.String(20),  nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin      = db.Column(db.Boolean, default=False, nullable=False)
    is_active     = db.Column(db.Boolean, default=True,  nullable=False)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    bookings  = db.relationship('Booking',  backref='user', lazy='dynamic',
                                cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='user', lazy='dynamic',
                                cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def initials(self):
        return f'{self.first_name[0]}{self.last_name[0]}'.upper()


# ---------------------------------------------------------------------------
# Destination
# ---------------------------------------------------------------------------

class Destination(db.Model):
    __tablename__ = 'destinations'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(128), nullable=False)
    country     = db.Column(db.String(64),  nullable=False)
    continent   = db.Column(db.String(32),  nullable=False)
    category    = db.Column(db.String(32),  nullable=False)   # adventure, cultural, etc.
    description = db.Column(db.Text,        nullable=True)
    price       = db.Column(db.Float,       nullable=False)   # per person USD
    duration    = db.Column(db.Integer,     nullable=False)   # days
    best_time   = db.Column(db.String(64),  nullable=True)
    rating      = db.Column(db.Float,  default=4.5)
    review_count= db.Column(db.Integer, default=0)
    image_url   = db.Column(db.String(512), nullable=True)
    is_active   = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    bookings = db.relationship('Booking', backref='destination', lazy='dynamic')

    def __repr__(self):
        return f'<Destination {self.name}>'

    @property
    def tag(self):
        """Display tag derived from category."""
        return self.category.replace('_', ' ').title()


# ---------------------------------------------------------------------------
# Booking
# ---------------------------------------------------------------------------

class BookingStatus:
    PENDING   = 'pending'
    CONFIRMED = 'confirmed'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

    ALL = [PENDING, CONFIRMED, COMPLETED, CANCELLED]


class Booking(db.Model):
    __tablename__ = 'bookings'

    id              = db.Column(db.Integer, primary_key=True)
    booking_ref     = db.Column(db.String(16), nullable=False, unique=True, index=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    destination_id  = db.Column(db.Integer, db.ForeignKey('destinations.id'), nullable=False)

    # Trip details
    travel_date     = db.Column(db.Date,    nullable=False)
    return_date     = db.Column(db.Date,    nullable=True)
    num_adults      = db.Column(db.Integer, nullable=False, default=1)
    num_children    = db.Column(db.Integer, nullable=False, default=0)

    # Lead traveller
    lead_first_name = db.Column(db.String(64),  nullable=False)
    lead_last_name  = db.Column(db.String(64),  nullable=False)
    lead_email      = db.Column(db.String(128), nullable=False)
    lead_phone      = db.Column(db.String(20),  nullable=True)
    lead_passport   = db.Column(db.String(32),  nullable=True)
    lead_nationality= db.Column(db.String(64),  nullable=True)
    lead_dob        = db.Column(db.Date,         nullable=True)

    # Extras
    dietary         = db.Column(db.String(32),  default='None')
    notes           = db.Column(db.Text,         nullable=True)

    # Pricing snapshot
    price_per_person= db.Column(db.Float, nullable=False)
    total_price     = db.Column(db.Float, nullable=False)
    taxes           = db.Column(db.Float, default=180.0)

    # Status
    status          = db.Column(db.String(16), default=BookingStatus.PENDING, nullable=False)
    created_at      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                                onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Booking {self.booking_ref}>'

    @property
    def traveller_count(self):
        return self.num_adults + self.num_children

    @property
    def status_badge_class(self):
        mapping = {
            'pending':   'warning',
            'confirmed': 'success',
            'completed': 'info',
            'cancelled': 'danger',
        }
        return mapping.get(self.status, 'secondary')


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------

class DocumentType:
    PASSPORT   = 'passport'
    VISA       = 'visa'
    INSURANCE  = 'insurance'
    TICKET     = 'ticket'
    HOTEL      = 'hotel'
    VACCINE    = 'vaccine'
    OTHER      = 'other'

    ALL = [PASSPORT, VISA, INSURANCE, TICKET, HOTEL, VACCINE, OTHER]
    LABELS = {
        PASSPORT:  'Passport',
        VISA:      'Visa',
        INSURANCE: 'Insurance',
        TICKET:    'Flight Ticket',
        HOTEL:     'Hotel Confirmation',
        VACCINE:   'Vaccination Certificate',
        OTHER:     'Other',
    }


class Document(db.Model):
    __tablename__ = 'documents'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doc_type      = db.Column(db.String(32),  nullable=False)
    display_name  = db.Column(db.String(128), nullable=False)
    original_name = db.Column(db.String(256), nullable=False)
    file_size     = db.Column(db.Integer,     nullable=False)   # bytes
    mime_type     = db.Column(db.String(64),  nullable=True)

    # Storage
    storage_key   = db.Column(db.String(512), nullable=True)    # S3 key (Phase 3)
    local_path    = db.Column(db.String(512), nullable=True)    # local encrypted path

    is_encrypted  = db.Column(db.Boolean, default=False)
    uploaded_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Document {self.display_name}>'

    @property
    def size_display(self):
        kb = self.file_size / 1024
        if kb >= 1024:
            return f'{kb/1024:.1f} MB'
        return f'{kb:.0f} KB'

    @property
    def type_label(self):
        return DocumentType.LABELS.get(self.doc_type, 'Other')

    @property
    def type_icon(self):
        icons = {
            'passport':  'bi-person-vcard-fill',
            'visa':      'bi-file-earmark-text-fill',
            'insurance': 'bi-shield-fill-check',
            'ticket':    'bi-airplane-fill',
            'hotel':     'bi-building',
            'vaccine':   'bi-heart-pulse-fill',
            'other':     'bi-file-earmark-fill',
        }
        return icons.get(self.doc_type, 'bi-file-earmark-fill')

    @property
    def type_color(self):
        colors = {
            'passport':  'primary',
            'visa':      'success',
            'insurance': 'info',
            'ticket':    'warning',
            'hotel':     'orange',
            'vaccine':   'teal',
            'other':     'secondary',
        }
        return colors.get(self.doc_type, 'secondary')
