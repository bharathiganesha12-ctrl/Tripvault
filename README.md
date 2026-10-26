# TripVault
### A Cloud-Based Travel Booking and Secure Document Management System

> **MCA Cloud Computing Project** — Built with Flask, Bootstrap 5, and AWS (Phase 2+)

---

## Project Overview

TripVault is a full-stack web application that allows users to:

- **Explore and book** travel destinations from a curated catalogue.
- **Manage bookings** — view status, traveller details, and history.
- **Store travel documents** securely using AES-256 encryption on AWS S3.
- **Admin panel** — manage destinations, monitor bookings, and view system analytics.

---

## Tech Stack

| Layer        | Technology                                |
|------------- |-------------------------------------------|
| Backend      | Python 3.11, Flask 3.0                    |
| Frontend     | HTML5, Bootstrap 5.3, Vanilla JS          |
| Database     | SQLite (dev) → PostgreSQL / AWS RDS (prod)|
| Auth         | Flask-Login, Flask-Bcrypt                 |
| Storage      | AWS S3 (encrypted documents)              |
| Encryption   | cryptography (AES-256)                    |
| Cloud        | AWS EC2, S3, RDS, CloudFront, SES         |

---

## Project Structure

```
TripVault/
├── app.py                  # Flask application & routes
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore
├── README.md
├── database/               # DB models (Phase 2)
├── routes/                 # Blueprint route modules (Phase 2)
├── services/               # Business logic & AWS services (Phase 2)
├── templates/              # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── destinations.html
│   ├── trip_details.html
│   ├── booking.html
│   ├── my_bookings.html
│   ├── documents.html
│   └── admin_dashboard.html
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/
├── storage/
│   └── encrypted/          # Local encrypted file cache
└── instance/               # Flask instance folder (DB file)
```

---

## Getting Started (Windows PowerShell)

### 1. Clone / navigate to the project

```powershell
cd e:\Tripvault
```

### 2. Create and activate virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> If you get a script execution policy error, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Set environment variables

```powershell
Copy-Item .env.example .env
# Then edit .env with your actual values
```

### 5. Run the application

```powershell
python app.py
```

The app will be available at **http://127.0.0.1:5000**

## Deploy on Render

This repository includes [`render.yaml`](./render.yaml), which provisions a Python web service and a managed PostgreSQL database.

1. Push the project to GitHub/GitLab and create a new Render Blueprint from the repository.
2. Set `PUBLIC_BASE_URL` to the deployed Render URL, for example `https://tripvault.onrender.com`.
3. Add SMTP credentials in Render under Environment. Gmail requires 2FA and an App Password; Mailtrap is useful for testing.
4. Deploy. Render runs `gunicorn app:app`, checks `/healthz`, and the app adds any new sample destinations without deleting existing data.

Required mail variables: `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME`, `MAIL_PASSWORD`, and `MAIL_DEFAULT_SENDER`.

Do not commit `.env` or real SMTP credentials. The included `.env.example` is safe to copy for local setup.

---

## Pages & Routes

| Route                    | Template              | Description                    |
|--------------------------|-----------------------|--------------------------------|
| `/`                      | index.html            | Landing page with hero + search|
| `/login`                 | login.html            | User login form                |
| `/register`              | register.html         | User registration form         |
| `/dashboard`             | dashboard.html        | User dashboard                 |
| `/destinations`          | destinations.html     | Destination catalogue          |
| `/trip/<id>`             | trip_details.html     | Destination detail + booking   |
| `/booking/<id>`          | booking.html          | Traveller details form         |
| `/my-bookings`           | my_bookings.html      | Booking history                |
| `/documents`             | documents.html        | Secure document vault          |
| `/admin`                 | admin_dashboard.html  | Admin panel                    |

---

## Development Phases

### ✅ Phase 1 (Complete) — Frontend
- Project structure
- All HTML templates with Bootstrap 5
- Custom CSS design system
- Client-side JS (filters, validation, price calculator)

### 🔲 Phase 2 — Backend & Authentication
- SQLAlchemy models (User, Booking, Destination, Document)
- Flask-Login session management
- Flask-WTF forms with CSRF
- Password hashing with Flask-Bcrypt
- Admin role middleware

### 🔲 Phase 3 — Cloud Integration
- AWS S3 document upload with pre-signed URLs
- AES-256 client-side encryption via `cryptography`
- AWS RDS (PostgreSQL) for production DB
- AWS SES for booking confirmation emails
- AWS EC2 deployment with Gunicorn + Nginx

---

## License

This project is developed for academic purposes (MCA Cloud Computing).
