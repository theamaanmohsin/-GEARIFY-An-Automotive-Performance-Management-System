# -GEARIFY-An-Automotive-Performance-Management-System
# Gearify

An integrated automotive performance and maintenance management system built for automotive workshops — replacing paper-based service records with a digital, role-based platform for vehicle service tracking, maintenance scheduling, and business operations.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Framework-Flask-black)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow)

## Overview

Gearify digitizes core workshop operations: capturing vehicle and service details, calculating costs automatically from live pricing data, generating professional digital receipts, and maintaining a searchable service history — all while enforcing role-based access between mechanics, managers, and admins.

**Problems it solves:**
- Lost/damaged paper records and inconsistent documentation
- Manual billing calculation errors
- No audit trail or role-based access control
- Slow retrieval of service history
- Lack of visibility into revenue trends and service popularity

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.8+, Flask |
| Templating | Jinja2 |
| Frontend | HTML, CSS, JavaScript (responsive) |
| Data Storage | JSON-based flat-file persistence |

## Features

- **Role-Based Access** — separate flows for Mechanics (Users), Workshop Managers/Owners (Admins), and read-only receipt access for Customers
- **Service Entry** — capture vehicle info (registration no., make, model, year, current KM), select parts from a live inventory dropdown
- **Automatic Cost Calculation** — parts and labor totals computed from current pricing data, removing manual arithmetic errors
- **Predictive Maintenance** — automatically calculates the next service interval (KM) based on the current entry
- **Digital Receipts** — professional, printable receipts generated per service, replacing handwritten slips
- **Service History & Search** — search past records by registration number, make, or date
- **Admin Console** — price configuration, user governance (view/delete users), secret-key-gated admin registration, system-wide search

**Supported vehicle types:** cars, light commercial vehicles, motorcycles
**Supported services (v1):** oil changes (multiple brands), air filter replacement, oil filter replacement — designed to be extended

## Architecture

```
Browser (HTML/CSS/JS)
        ↓
Flask Web Framework Layer     — routing, session management, before_request auth guard
        ↓
Business Logic Layer          — cost calculation engine, parts selection, predictive maintenance, receipt generation
        ↓
Data Persistence Layer        — JSON file operations, validation, file-system safety checks
        ↓
Data Storage Layer            — users.json · history.json · prices.json · cars.json · settings.json
```

**Example flow — new service entry:**
1. Mechanic clicks "New Service" → Flask renders `maintenance.html`
2. Parts Selection Module loads current prices from `prices.json`
3. Mechanic submits the form (`POST /maintenance`)
4. Cost Calculation Engine computes the total; Predictive Maintenance Module calculates the next service KM
5. Receipt is generated and appended to `history.json`
6. Flask renders `receipt.html` with the transaction details

## Project Structure

```
Gearify/
├── app.py              # Flask app entry point & routes
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── maintenance.html
│   └── receipt.html
├── static/              # CSS, JS, assets
└── data/
    ├── users.json
    ├── history.json
    ├── prices.json
    ├── cars.json
    └── settings.json
```

## Prerequisites

- Python 3.8 or higher
- pip
- A modern browser (Chrome 90+, Firefox 88+, Safari 14+, or Edge 90+)

## Getting Started

1. **Clone the repo**
   ```bash
   git clone <repo-url>
   cd Gearify
   ```

2. **Install dependencies**
   ```bash
   pip install flask
   ```

3. **Run the app**
   ```bash
   python app.py
   ```

4. **Open in browser**
   ```
   http://localhost:5000
   ```

### First-time setup

1. Go to `http://localhost:5000/register`
2. Create an admin account (Role: Admin), using the system's admin secret key
3. Log in with the admin credentials

> ⚠️ Change the default admin secret key before any real deployment — don't ship the sample key from development.

## Known Limitations (v1.0)

- JSON flat-file storage — not optimized for more than ~5 concurrent users or ~10,000 service records
- Local network deployment only, no cloud-native architecture
- No third-party integrations (accounting software, POS, diagnostics tools)
- Records transactions but does not process payments (cash-only workflow assumed)
- Tracks parts usage but not stock levels — no automated reorder alerts
- Responsive web design, not a native mobile app

## Roadmap (out of scope for v1.0)

- [ ] Customer-facing booking portal
- [ ] Automated SMS/email service reminders
- [ ] Multi-location franchise management
- [ ] Vehicle diagnostic tool integration
- [ ] Real-time parts ordering from suppliers
- [ ] Accounting software sync

## License

Add your license here.
