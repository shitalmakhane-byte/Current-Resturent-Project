# Annpurana Pure Veg Hotel — Restaurant Management System

A Flask-based restaurant management web app with cart, ordering, and admin panel.

**Developer:** Shital Makhane | Project Portfolio
**Live URL:** https://web-production-86730.up.railway.app
**GitHub Repo:** https://github.com/shitalmakhane-byte/Current-Resturent-Project

---

## Tech Stack

- Python 3.11
- Flask 2.3.3
- Flask-SQLAlchemy (ORM)
- PostgreSQL (Railway) / SQLite (local)
- Gunicorn (production server)
- Bootstrap 4.5 (frontend)

---

## Project Structure

```
├── app.py              # Main Flask app — all routes and business logic
├── models.py           # SQLAlchemy models (User, CartItem, Order, OrderItem)
├── requirements.txt    # Python dependencies
├── Procfile            # Railway/Heroku start command
├── nixpacks.toml       # Railway build config (Python 3.11 + libpq)
├── .env.example        # Environment variable template
├── static/
│   ├── Experiment.css  # Main stylesheet
│   ├── Experiment.js   # Main JS
│   └── images/         # All food and UI images
└── templates/
    ├── home.html
    ├── veg.html
    ├── street-chaat.html
    ├── desserts.html
    ├── ice-cream.html
    ├── Dessert-Icream.html
    ├── gym-food.html
    ├── gym-protein.html
    ├── gym-detox.html
    ├── gym-shakes.html
    ├── cart.html
    ├── checkout.html
    ├── my_orders.html
    ├── order_details.html
    ├── admin_panel.html
    ├── admin_users.html
    ├── admin_orders.html
    └── auth/
        ├── login.html
        └── register.html
```

---

## Database Models

### User
| Field | Type | Notes |
|-------|------|-------|
| id | Integer | Primary key |
| email | String | Stores username (unique) |
| name | String | Display name |
| password_hash | String | Werkzeug hashed |
| is_verified | Boolean | False = blocked |
| created_at | DateTime | Auto |

### CartItem
| Field | Type | Notes |
|-------|------|-------|
| id | Integer | Primary key |
| user_id | FK → users | |
| item_name | String | |
| item_price | Float | Server-side locked |
| quantity | Integer | |
| category | String | |

### Order
| Field | Type | Notes |
|-------|------|-------|
| id | Integer | Primary key |
| user_id | FK → users | |
| total_amount | Float | |
| status | String | Pending/Confirmed/Delivered/Cancelled |
| delivery_address | Text | |
| phone_number | String | |
| created_at / updated_at | DateTime | |

### OrderItem
| Field | Type | Notes |
|-------|------|-------|
| id | Integer | Primary key |
| order_id | FK → orders | cascade delete |
| item_name | String | |
| item_price | Float | Snapshot at order time |
| quantity | Integer | |
| category | String | |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| SECRET_KEY | Yes | Flask session secret |
| DATABASE_URL | Yes | PostgreSQL URL (Railway auto-injects) |
| ADMIN_USERNAMES | Yes | Comma-separated admin usernames e.g. `admin,shivam` |
| DEBUG | No | Set `False` in production |

Copy `.env.example` to `.env` for local setup.

---

## Local Setup

```bash
# 1. Clone
git clone https://github.com/shitalmakhane-byte/Current-Resturent-Project.git
cd Current-Resturent-Project

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
copy .env.example .env
# Edit .env and set SECRET_KEY and ADMIN_USERNAMES

# 5. Run
python app.py
```

App runs on http://localhost:5000 with SQLite by default.

---

## Railway Deployment

1. Push to GitHub (main branch)
2. Create new Railway project → Deploy from GitHub repo
3. Add PostgreSQL plugin
4. Set environment variables in web service Variables tab:
   - `SECRET_KEY`
   - `ADMIN_USERNAMES`
   - `DEBUG=False`
   - `DATABASE_URL` — copy raw URL from PostgreSQL service → Connect tab
5. Railway auto-deploys on every push to main

**Important:** Do not use `${{Postgres.DATABASE_URL}}` reference syntax — paste the raw URL directly to avoid newline injection issues.

---

## Admin Access

- URL: `/admin`
- Login with a username listed in `ADMIN_USERNAMES` env var
- Admin can: view dashboard stats, manage users (ban/unban/delete), update order statuses

To create the first admin user, register normally at `/register` using the username set in `ADMIN_USERNAMES`.

---

## Features

- User registration and login (username-based, no email required)
- Add to cart, update quantity, remove items
- Checkout with delivery address and phone number
- Order history and order details
- Order cancellation (Pending orders only)
- Admin dashboard — users, orders, revenue stats
- Server-side price validation (prevents cart price tampering)
- Full ACID-compliant DB transactions with rollback on failure
- PostgreSQL on Railway, SQLite locally

---

## Menu Categories

| Category | Route |
|----------|-------|
| Pure Veg | /veg |
| Street Chaat | /street-chaat |
| Gym High Protein | /gym-protein |
| Gym Detox Drinks | /gym-detox |
| Gym Shakes | /gym-shakes |
| Desserts | /desserts |
| Ice Cream | /ice-cream |
