"""
TripVault – WTForms form definitions
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (
    StringField, PasswordField, BooleanField, SelectField,
    RadioField,
    IntegerField, TextAreaField, DateField, HiddenField,
    TelField, EmailField, FloatField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, Optional,
    NumberRange, ValidationError
)
from database.models import User


# ---------------------------------------------------------------------------
# Auth forms
# ---------------------------------------------------------------------------

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name',
        validators=[DataRequired(), Length(min=2, max=64)])
    last_name  = StringField('Last Name',
        validators=[DataRequired(), Length(min=2, max=64)])
    email      = EmailField('Email Address',
        validators=[DataRequired(), Email()])
    phone      = TelField('Phone Number',
        validators=[Optional(), Length(max=20)])
    password   = PasswordField('Password',
        validators=[DataRequired(), Length(min=8, max=128)])
    confirm    = PasswordField('Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    terms      = BooleanField('I agree to the Terms of Service',
        validators=[DataRequired(message='You must accept the terms')])

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('An account with this email already exists.')


class LoginForm(FlaskForm):
    email    = EmailField('Email Address',
        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
        validators=[DataRequired()])
    remember = BooleanField('Remember me')


# ---------------------------------------------------------------------------
# Booking form
# ---------------------------------------------------------------------------

class BookingForm(FlaskForm):
    destination_id   = HiddenField()
    travel_date      = DateField('Travel Date',    validators=[DataRequired()])
    return_date      = DateField('Return Date',    validators=[Optional()])
    num_adults       = SelectField('Adults',
        choices=[(i, f'{i} Adult{"s" if i > 1 else ""}') for i in range(1, 9)],
        coerce=int, default=2)
    num_children     = SelectField('Children',
        choices=[(i, f'{i} Child{"ren" if i > 1 else ""}' if i > 0 else '0 Children') for i in range(0, 6)],
        coerce=int, default=0)

    # Lead traveller
    title            = SelectField('Title', choices=['Mr', 'Ms', 'Mrs', 'Dr'])
    lead_first_name  = StringField('First Name',
        validators=[DataRequired(), Length(max=64)])
    lead_last_name   = StringField('Last Name',
        validators=[DataRequired(), Length(max=64)])
    lead_email       = EmailField('Email',
        validators=[DataRequired(), Email()])
    lead_phone       = TelField('Phone',
        validators=[Optional(), Length(max=20)])
    lead_dob         = DateField('Date of Birth', validators=[Optional()])
    lead_nationality = StringField('Nationality', validators=[Optional(), Length(max=64)])
    lead_passport    = StringField('Passport Number', validators=[Optional(), Length(max=32)])

    dietary          = RadioField('Dietary Requirements',
        choices=['None', 'Vegetarian', 'Vegan', 'Halal', 'Kosher', 'Gluten-free'])
    notes            = TextAreaField('Additional Notes', validators=[Optional(), Length(max=500)])


# ---------------------------------------------------------------------------
# Document upload form
# ---------------------------------------------------------------------------

ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png', 'docx']

class DocumentUploadForm(FlaskForm):
    doc_type     = SelectField('Document Type',
        choices=[
            ('passport',  'Passport'),
            ('visa',      'Visa'),
            ('insurance', 'Travel Insurance'),
            ('ticket',    'Flight Ticket'),
            ('hotel',     'Hotel Confirmation'),
            ('vaccine',   'Vaccination Certificate'),
            ('other',     'Other'),
        ],
        validators=[DataRequired()])
    display_name = StringField('Document Name',
        validators=[DataRequired(), Length(max=128)])
    file         = FileField('File',
        validators=[
            FileRequired(),
            FileAllowed(ALLOWED_EXTENSIONS, 'Only PDF, JPG, PNG, and DOCX files allowed.'),
        ])


# ---------------------------------------------------------------------------
# Admin – destination management
# ---------------------------------------------------------------------------

class DestinationForm(FlaskForm):
    name        = StringField('Destination Name',
        validators=[DataRequired(), Length(max=128)])
    country     = StringField('Country',
        validators=[DataRequired(), Length(max=64)])
    continent   = SelectField('Continent',
        choices=['Europe', 'Asia', 'Americas', 'Africa', 'Oceania'])
    category    = SelectField('Category',
        choices=['adventure', 'cultural', 'romantic', 'luxury', 'beach', 'wildlife'])
    description = TextAreaField('Description', validators=[Optional()])
    price       = FloatField('Price (USD per person)',
        validators=[DataRequired(), NumberRange(min=0)])
    duration    = IntegerField('Duration (days)',
        validators=[DataRequired(), NumberRange(min=1)])
    best_time   = StringField('Best Travel Time', validators=[Optional(), Length(max=64)])
    rating      = FloatField('Rating', validators=[Optional(), NumberRange(min=0, max=5)],
                             default=4.5)
    image_url   = StringField('Cover Image URL', validators=[Optional(), Length(max=512)])
    is_active   = BooleanField('Publish immediately', default=True)
