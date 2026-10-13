# 🐾 FurFind — Pet Search & Recovery System

FurFind is a desktop application for reporting, searching, and reuniting **lost and found pets**. Pet owners and finders submit reports with photos, an automated matching engine suggests likely pairs, and **human admins verify every match** before a case is closed.

Built with **Python (Tkinter)** and **MySQL** (via XAMPP), using a layered architecture (Views → Controllers → Repositories → Database).

---

## Table of Contents

1. [Features](#features)
2. [Roles and Privileges](#roles-and-privileges)
3. [Tech Stack](#tech-stack)
4. [Architecture](#architecture)
5. [Project Structure](#project-structure)
6. [How Matching Works](#how-matching-works)
7. [Database Schema](#database-schema)
8. [Installation Guide (Run on Another Device)](#installation-guide-run-on-another-device)
9. [Sharing One Database Across Multiple Devices](#sharing-one-database-across-multiple-devices-optional)
10. [Default Accounts](#default-accounts)
11. [Running the Tests](#running-the-tests)
12. [Troubleshooting](#troubleshooting)
13. [Security Notes](#security-notes)
14. [Known Limitations](#known-limitations)

---

## Features

- Submit **Lost** or **Found** pet reports with descriptive details and a **required photo**
- **Unified search** with filters (species, report type, status, keyword)
- **Automated match suggestions** scored by a weighted algorithm
- **Claim / dispute** requests tied to a suggested match
- **Admin verification queue**: approve or reject matches (no case closes automatically)
- Edit and **soft-delete** reports (records are hidden, never destroyed)
- **Audit trail** of logins, report changes, claims, and admin decisions
- **Exports**: single report to PDF, audit logs to CSV/PDF, dashboard statistics to CSV
- **User management** for Super Admins: create accounts, assign roles, lock/unlock

---

## Roles and Privileges

| Capability | Pet Owner | Admin | Super Admin |
|---|:---:|:---:|:---:|
| Register an account (self-service) | ✅ | — | — |
| Submit Lost / Found reports (photo required) | ✅ | — | — |
| Unified search and filtering | ✅ | ✅ | ✅ |
| View match suggestions for own reports | ✅ | — | — |
| Submit claim / dispute requests | ✅ | — | — |
| Edit own profile | ✅ | — | — |
| Edit / soft-delete any report | — | ✅ | ✅ |
| Approve / reject matches (verification queue) | — | ✅ | ✅ |
| View audit logs and export (CSV / PDF) | — | ✅ | ✅ |
| Export dashboard statistics | — | ✅ | ✅ |
| Create / edit accounts, assign roles | — | — | ✅ |
| Lock / unlock accounts | — | — | ✅ |

Admin and Super Admin accounts **cannot** be self-registered; a Super Admin creates them.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| GUI | Tkinter / ttk |
| Database | MySQL or MariaDB (XAMPP) |
| DB driver | `mysql-connector-python` |
| Images | `Pillow` |
| PDF export | `reportlab` |
| Testing | `pytest`, `unittest.mock` |

---

## Architecture

```
┌──────────┐   ┌──────────────┐   ┌───────────────┐   ┌─────────────────┐
│  Views   │ → │ Controllers  │ → │ Repositories  │ → │ DatabaseManager │ → MySQL
│ (Tkinter)│   │ (business    │   │ (parameterized│   │ (Singleton)     │
│          │   │  rules)      │   │  SQL / DAO)   │   │                 │
└──────────┘   └──────────────┘   └───────────────┘   └─────────────────┘
        Models (User ► PetOwner/Admin/SuperAdmin, PetReport, MatchResult, AuditLog)
        Utils  (MatchingEngine, Validator, PDFExporter)
        Core   (DatabaseManager, custom exceptions)
```

OOP concepts used: abstraction and polymorphism (`User` base class with role subclasses), encapsulation (properties/setters), Singleton (`DatabaseManager`), DAO/Repository pattern, and a custom exception hierarchy (`FurFindException` and subclasses).

---

## Project Structure

```
FurFind/
├── main.py                     # Entry point: initializes DB, then launches the GUI
├── app.py                      # Tk root, login/logout flow, wires views to controllers
├── requirements.txt
├── config/
│   ├── init.py                 # Reads database.ini, creates DB, runs schema + seed
│   ├── database.ini            # MySQL connection settings
│   └── pytest.ini
├── core/
│   ├── db_manager.py           # Singleton connection + cursor context manager
│   └── exceptions.py
├── database/
│   ├── schema.sql              # Tables
│   └── dummy.sql               # Seed users, sample reports, sample match
├── models/                     # user.py, pet_report.py, match_result.py, audit_log.py
├── repositories/               # user, report, match, claim, audit (DAO layer)
├── controllers/                # auth, report, match, claim, user, audit, dashboard
├── utils/                      # matching_engine.py, validator.py, pdf_exporter.py
├── views/
│   ├── login_and_register_view.py
│   ├── main_window.py          # Shell + role-guarded routing
│   ├── dashboard_view.py
│   ├── report_form_view.py     # Pet Owner
│   ├── search_view.py          # All roles
│   ├── my_reports_view.py      # Pet Owner (matches, claims, disputes)
│   ├── profile_view.py         # Pet Owner
│   ├── match_queue_view.py     # Admin / Super Admin
│   ├── pet_mgmt_view.py        # Admin / Super Admin
│   ├── audit_logs_view.py      # Admin / Super Admin
│   ├── user_mgmt_view.py       # Super Admin
│   └── components/             # navbar.py, ui_kit.py, report_browser.py
├── tests/
└── uploads/                    # Created automatically; stores submitted pet photos
```

---

## How Matching Works

When a report is submitted, it is compared against all **active reports of the opposite type** (Lost vs. Found) from **other users**. Each pair gets a score from 0 to 100:

| Factor | Weight | Notes |
|---|---:|---|
| Species | 30 | Hard rule: different species = score 0 |
| Breed | 20 | Half credit for partial text match |
| Gender | 15 | "Unknown" matches anything |
| Color | 15 | Half credit if primary color appears in the other's secondary |
| Location | 10 | Half credit for partial text match |
| Date proximity | 10 | Full ≤ 1 day, 70% ≤ 7 days, 30% ≤ 30 days |

Pairs scoring **50 or higher** are saved as `Pending Admin Verification`. An admin reviews both reports side by side (photos, details, claims) and explicitly **approves** (both reports become `Resolved`) or **rejects** (with a required reason).

---

## Database Schema

| Table | Purpose |
|---|---|
| `tbl_roles` | Pet Owner (1), Admin (2), Super Admin (3) |
| `tbl_users` | Accounts, salted password hash, status (`Active` / `Suspended`) |
| `tbl_reports` | Lost/Found reports, photo path, status, `is_deleted` soft-delete flag |
| `tbl_matches` | Suggested pairs, score, verification status, admin notes |
| `tbl_claims` | Claim and dispute requests attached to a match |
| `tbl_audit_log` | Timestamped activity trail |

The database, tables, and seed data are created **automatically** on first launch.

---

## Installation Guide (Run on Another Device)

These steps assume a clean Windows machine (the project targets XAMPP). macOS/Linux notes are at the end of this section.

### Step 1: Install the prerequisites

| Software | Notes |
|---|---|
| **Python 3.10 or newer** | From python.org. On Windows, tick **"Add python.exe to PATH"** in the installer. Tkinter is included. |
| **XAMPP** | From apachefriends.org. Only the **MySQL** module is required. |
| **Git** *(optional)* | Only needed if you clone instead of copying a ZIP. |

Verify Python:

```
python --version
```

### Step 2: Get the project onto the device

Either clone it:

```
git clone <your-repository-url> FurFind
cd FurFind
```

or copy the project folder (USB, ZIP, cloud drive) and open a terminal inside it.

### Step 3: Start MySQL

1. Open the **XAMPP Control Panel**.
2. Click **Start** next to **MySQL**. (Apache is not needed.)
3. Wait until the module turns green.

### Step 4: Create a virtual environment and install dependencies

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

On macOS/Linux, activate with `source venv/bin/activate`.

### Step 5: Check the database settings

Open `config/database.ini`. XAMPP's defaults already match:

```ini
[mysql]
host = localhost
port = 3306
user = root
password =
database = furfind_db
auth_plugin = mysql_native_password
```

Only change these if your MySQL uses a different port, user, or password (see [Troubleshooting](#troubleshooting)).

### Step 6: Run the app

Always run from the **project root folder**:

```
python main.py
```

On the first run FurFind will:

1. Create the `furfind_db` database,
2. Create all tables from `database/schema.sql`,
3. Insert demo data from `database/dummy.sql`,
4. Open the login window.

Log in with one of the [default accounts](#default-accounts).

### Resetting the database

To return to a clean state with fresh seed data, drop the database in phpMyAdmin (`http://localhost/phpmyadmin`) or run the following, then start the app again:

```sql
DROP DATABASE furfind_db;
```

Delete the `uploads/` folder as well if you want to remove previously uploaded photos.

### macOS / Linux notes

- **Linux:** Tkinter may be a separate package: `sudo apt install python3-tk`.
- **MySQL:** use XAMPP for Linux, or install MariaDB/MySQL (`sudo apt install mariadb-server`) and set matching credentials in `config/database.ini`.
- **macOS:** use MAMP, XAMPP for macOS, or Homebrew's `mysql`. The UI uses the *Segoe UI* font, so another system font is substituted automatically and spacing may differ slightly.

---

## Sharing One Database Across Multiple Devices (Optional)

By default each device has its own local database. To have several devices use **one shared database** (for example, an admin PC and owner laptops on the same Wi-Fi):

1. **On the host device** (the one running XAMPP MySQL), find its IP address (`ipconfig` on Windows, e.g. `192.168.1.20`).
2. Create a dedicated user in phpMyAdmin → SQL (avoid exposing `root`):
   ```sql
   CREATE USER 'furfind'@'%' IDENTIFIED BY 'choose-a-strong-password';
   GRANT ALL PRIVILEGES ON furfind_db.* TO 'furfind'@'%';
   FLUSH PRIVILEGES;
   ```
3. Allow inbound TCP **port 3306** through the host's firewall.
4. **On every other device**, edit `config/database.ini`:
   ```ini
   host = 192.168.1.20
   user = furfind
   password = choose-a-strong-password
   ```
5. Start `python main.py` on each device.

> **Photo caveat:** uploaded photos are copied to each device's local `uploads/` folder and stored in the database by absolute path. Photos uploaded on one device **will not display on another** unless `uploads/` is shared (for example, a network folder mapped to the same path). Reports and matches themselves are shared normally.

Only do this on a trusted network. Don't expose MySQL to the internet.

---

## Default Accounts

All seeded accounts use the password **`Password123!`**.

| Role | Email |
|---|---|
| Super Admin | `superadmin@furfind.com` |
| Admin | `admin@furfind.com` |
| Pet Owner | `john@furfind.com` |
| Pet Owner | `jane@furfind.com` |

The seed data includes one lost dog (John) and one found dog (Jane) with a pending match, so the admin verification queue has something to review immediately. **Change or remove these accounts before any real deployment.**

---

## Running the Tests

From the project root with the virtual environment active:

```
python -m pytest
```

Tests cover models, repositories (with a mocked database), controllers, the matching engine, the validator, and PDF export. They do not need MySQL running.

---

## Troubleshooting

| Problem | Cause and fix |
|---|---|
| `Can't connect to MySQL server` / connection refused | MySQL isn't running. Start it in the XAMPP Control Panel. |
| MySQL won't start in XAMPP (port in use) | Another MySQL service already uses port 3306. Stop that service, or change XAMPP's MySQL port (Config → `my.ini`) and set the same `port` in `config/database.ini`. |
| `Access denied for user` | The username or password in `config/database.ini` doesn't match your MySQL. XAMPP defaults to `root` with an empty password. |
| `ModuleNotFoundError: No module named 'config'` (or `core`, `views`) | You launched from the wrong folder. Run `python main.py` from the project root. |
| `ModuleNotFoundError: mysql` / `PIL` / `reportlab` | Dependencies aren't installed in the active environment. Activate the venv and run `pip install -r requirements.txt`. |
| `No module named '_tkinter'` / `tkinter` | Linux: `sudo apt install python3-tk`. Windows: re-run the Python installer and enable *tcl/tk*. |
| `Table 'tbl_...' doesn't exist` or odd column errors | The database was created from an older schema. Drop `furfind_db` and restart the app. |
| `python` not recognized | Python isn't on PATH. Reinstall with *Add to PATH* ticked, or use `py main.py` on Windows. |
| Login says "Account is locked" | A Super Admin locked the account. Another Super Admin can unlock it in User Management. |
| Photos not showing after moving machines | Photo paths are stored per device. See the photo caveat above. |
| Details of any startup failure | Check `furfind_app.log` in the project folder. |

---

## Security Notes

- Passwords are stored as **salted SHA-256** hashes. This is fine for a coursework project, but for production use a slow password hasher such as bcrypt or Argon2.
- All SQL uses **parameterized queries**. Column names in dynamic updates come from a fixed whitelist.
- Role checks are enforced in the view router (`MainWindow.ACCESS`) and the navigation bar. Controllers don't re-verify the caller's role, so add `AuthController.require_role(...)` checks if you expose the controllers through another interface.
- `config/database.ini` contains credentials. If you use a real password, **don't commit it**; add the file to `.gitignore` and share a sample copy instead.
- Public self-registration only creates **Pet Owner** accounts.

---

## Known Limitations

- Desktop-only and single-process; there's no web or mobile client.
- Matching is rule-based text comparison (no image recognition). Free-text fields such as "Quezon City" vs. "QC" won't match.
- Photo storage is local to each device (see the multi-device section).
- No password reset or email notifications.
- Report status values in use are `Active`, `Resolved`, and `Closed`.

---

## License

Add your license here (e.g., MIT) or state that the project is for academic use.