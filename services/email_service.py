"""
TripVault – Email service (Flask-Mail / SMTP)
Replaces AWS SES with free Gmail or Mailtrap SMTP.

Configure via .env:
  MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS,
  MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER

If MAIL_USERNAME is not set, emails are suppressed in development
(MAIL_SUPPRESS_SEND = True) so the app still works with no email config.
"""

from flask import current_app, render_template_string
import os
from flask_mail import Message
from database.extensions import mail


# ---------------------------------------------------------------------------
# Email templates (inline — move to files/Jinja templates in Phase 4)
# ---------------------------------------------------------------------------

_BOOKING_CONFIRM_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <style>
    body  {{ font-family: Inter, Arial, sans-serif; background:#f1f5f9; margin:0; padding:20px; }}
    .card {{ background:#fff; border-radius:12px; max-width:580px; margin:0 auto; overflow:hidden; }}
    .header {{ background:linear-gradient(135deg,#1a6bcc,#0d9488); padding:32px 32px 24px; text-align:center; }}
    .header h1 {{ color:#fff; font-size:1.6rem; margin:8px 0 0; }}
    .header p  {{ color:rgba(255,255,255,.8); margin:4px 0 0; font-size:.9rem; }}
    .body  {{ padding:28px 32px; }}
    .row   {{ display:flex; justify-content:space-between; padding:8px 0;
              border-bottom:1px solid #e2e8f0; font-size:.875rem; }}
    .row:last-child {{ border-bottom:none; }}
    .label {{ color:#64748b; }}
    .value {{ font-weight:600; color:#0f172a; }}
    .total {{ font-size:1.1rem; color:#1a6bcc; }}
    .btn   {{ display:inline-block; background:#1a6bcc; color:#fff; padding:12px 28px;
              border-radius:8px; text-decoration:none; font-weight:700; margin-top:20px; }}
    .footer{{ background:#f8fafc; padding:16px 32px; text-align:center;
              font-size:.75rem; color:#94a3b8; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div style="font-size:2.5rem;">✈️</div>
      <h1>Booking Confirmed!</h1>
      <p>Reference: <strong>{ref}</strong></p>
    </div>
    <div class="body">
      <p>Hi <strong>{name}</strong>,</p>
      <p>Your trip to <strong>{destination}</strong> is confirmed. Here's a summary:</p>

      <div class="row"><span class="label">Booking Ref</span><span class="value">{ref}</span></div>
      <div class="row"><span class="label">Destination</span><span class="value">{destination}</span></div>
      <div class="row"><span class="label">Travel Date</span><span class="value">{travel_date}</span></div>
      <div class="row"><span class="label">Return Date</span><span class="value">{return_date}</span></div>
      <div class="row"><span class="label">Travellers</span><span class="value">{travellers}</span></div>
      <div class="row"><span class="label">Total Paid</span><span class="value total">{total}</span></div>

      <p style="margin-top:20px; color:#64748b; font-size:.875rem;">
        Free cancellation is available within 48 hours of booking.
        To manage your booking, log in to your TripVault account.
      </p>
      <a href="http://127.0.0.1:5000/my-bookings" class="btn">View My Bookings</a>
    </div>
    <div class="footer">
      &copy; 2026 TripVault &bull; MCA Cloud Computing Project<br/>
      You received this because you booked a trip on TripVault.
    </div>
  </div>
</body>
</html>
"""

_WELCOME_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <style>
    body  {{ font-family: Inter, Arial, sans-serif; background:#f1f5f9; margin:0; padding:20px; }}
    .card {{ background:#fff; border-radius:12px; max-width:540px; margin:0 auto; overflow:hidden; }}
    .header {{ background:linear-gradient(135deg,#1a6bcc,#0d9488); padding:32px; text-align:center; }}
    .header h1 {{ color:#fff; font-size:1.5rem; margin:8px 0 0; }}
    .body  {{ padding:28px 32px; color:#334155; line-height:1.65; }}
    .feature {{ display:flex; align-items:flex-start; gap:12px; margin-bottom:14px; }}
    .icon  {{ font-size:1.4rem; flex-shrink:0; }}
    .btn   {{ display:inline-block; background:#1a6bcc; color:#fff; padding:12px 28px;
              border-radius:8px; text-decoration:none; font-weight:700; margin-top:16px; }}
    .footer{{ background:#f8fafc; padding:16px 32px; text-align:center;
              font-size:.75rem; color:#94a3b8; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div style="font-size:2.5rem;">🌍</div>
      <h1>Welcome to TripVault, {name}!</h1>
    </div>
    <div class="body">
      <p>Your account has been created. Here's what you can do:</p>
      <div class="feature"><span class="icon">🔍</span><div><strong>Explore Destinations</strong><br/>Browse 150+ hand-picked trips.</div></div>
      <div class="feature"><span class="icon">📋</span><div><strong>Book Trips</strong><br/>Secure booking with instant confirmation.</div></div>
      <div class="feature"><span class="icon">🔒</span><div><strong>Document Vault</strong><br/>Upload passports and visas — encrypted with AES-256.</div></div>
      <a href="http://127.0.0.1:5000/destinations" class="btn">Explore Destinations</a>
    </div>
    <div class="footer">
      &copy; 2026 TripVault &bull; MCA Cloud Computing Project
    </div>
  </div>
</body>
</html>
"""

_CANCEL_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <style>
    body  {{ font-family: Inter, Arial, sans-serif; background:#f1f5f9; margin:0; padding:20px; }}
    .card {{ background:#fff; border-radius:12px; max-width:540px; margin:0 auto; overflow:hidden; }}
    .header {{ background:#dc2626; padding:24px 32px; text-align:center; }}
    .header h1 {{ color:#fff; font-size:1.3rem; margin:8px 0 0; }}
    .body  {{ padding:28px 32px; color:#334155; }}
    .row   {{ display:flex; justify-content:space-between; padding:8px 0;
              border-bottom:1px solid #e2e8f0; font-size:.875rem; }}
    .label {{ color:#64748b; }}
    .value {{ font-weight:600; }}
    .btn   {{ display:inline-block; background:#1a6bcc; color:#fff; padding:12px 28px;
              border-radius:8px; text-decoration:none; font-weight:700; margin-top:20px; }}
    .footer{{ background:#f8fafc; padding:16px; text-align:center;
              font-size:.75rem; color:#94a3b8; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div style="font-size:2rem;">❌</div>
      <h1>Booking Cancelled</h1>
    </div>
    <div class="body">
      <p>Hi <strong>{name}</strong>, your booking has been cancelled.</p>
      <div class="row"><span class="label">Reference</span><span class="value">{ref}</span></div>
      <div class="row"><span class="label">Destination</span><span class="value">{destination}</span></div>
      <div class="row"><span class="label">Travel Date</span><span class="value">{travel_date}</span></div>
      <p style="margin-top:16px; color:#64748b; font-size:.875rem;">
        If you cancelled by mistake, you can rebook any time from the destinations page.
      </p>
      <a href="http://127.0.0.1:5000/destinations" class="btn">Browse Destinations</a>
    </div>
    <div class="footer">&copy; 2026 TripVault</div>
  </div>
</body>
</html>
"""


def _app_url(path: str) -> str:
    """Build links that work locally and on Render."""
    base_url = os.environ.get('PUBLIC_BASE_URL', 'http://127.0.0.1:5000').rstrip('/')
    return f'{base_url}{path}'


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _send(to: str, subject: str, html: str) -> bool:
    """
    Send an email. Returns True on success, False if suppressed or failed.
    Errors are logged but never crash the request.
    """
    try:
        if current_app.config.get('MAIL_SUPPRESS_SEND'):
            current_app.logger.info(f'[Mail suppressed] To: {to} | Subject: {subject}')
            return False
        msg = Message(subject=subject, recipients=[to], html=html)
        mail.send(msg)
        current_app.logger.info(f'[Mail sent] To: {to} | Subject: {subject}')
        return True
    except Exception as exc:
        current_app.logger.warning(f'[Mail failed] {exc}')
        return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def send_welcome_email(user) -> bool:
    html = _WELCOME_HTML.format(name=user.first_name).replace(
        'http://127.0.0.1:5000/destinations', _app_url('/destinations')
    )
    return _send(user.email, 'Welcome to TripVault! 🌍', html)


def send_booking_confirmation(booking) -> bool:
    return_date = booking.return_date.strftime('%d %b %Y') if booking.return_date else 'Open return'
    html = _BOOKING_CONFIRM_HTML.format(
        name        = booking.lead_first_name,
        ref         = booking.booking_ref,
        destination = booking.destination.name,
        travel_date = booking.travel_date.strftime('%d %b %Y'),
        return_date = return_date,
        travellers  = f'{booking.num_adults} adult(s)'
                      + (f', {booking.num_children} child(ren)' if booking.num_children else ''),
        total       = f'${booking.total_price:,.0f}',
    ).replace('http://127.0.0.1:5000/my-bookings', _app_url('/my-bookings'))
    return _send(booking.lead_email,
                 f'Booking Confirmed – {booking.booking_ref} ✈️', html)


def send_cancellation_email(booking) -> bool:
    html = _CANCEL_HTML.format(
        name        = booking.lead_first_name,
        ref         = booking.booking_ref,
        destination = booking.destination.name,
        travel_date = booking.travel_date.strftime('%d %b %Y'),
    ).replace('http://127.0.0.1:5000/destinations', _app_url('/destinations'))
    return _send(booking.lead_email,
                 f'Booking Cancelled – {booking.booking_ref}', html)
