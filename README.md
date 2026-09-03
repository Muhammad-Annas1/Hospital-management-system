# 🏥 Hospital Management System (Python + Streamlit)

A complete **Intermediate-Level Hospital Management System** built with **Python, Streamlit, SQLite, Pandas, and Plotly**. The application runs **100% locally and offline** with zero external API dependencies or cloud backends.

---

## 🌟 Key Features

### 🔐 Authentication & Role-Based Access Control
* **Admin Dashboard**: Full administrative power to manage patients, doctors, appointment scheduling, billing invoices, reports, and database settings.
* **Patient Portal**: Isolated access for patients to view personal health records, search doctors by symptoms/disease, book non-conflicting appointment slots, view appointment history, and inspect invoices.
* **Salted Password Hashing**: Hashed local credentials using standard library `hashlib.pbkdf2_hmac`.

### 🩺 Disease-to-Specialization Rule Engine
* Rule-based algorithm mapping symptoms (e.g. *"Chest pain"*, *"Skin rash"*, *"Migraine"*) to medical departments (*Cardiologist*, *Dermatologist*, *Neurologist*, etc.).
* Medical disclaimer footer embedded on patient guidance views.

### 📅 Smart Appointment Booking Engine
* **Dynamic Slot Generation**: Automatically generates available 30-minute consultation slots based on doctor working hours and active working days.
* **Double Booking Prevention**: Enforces database-level checks to prevent overlapping doctor bookings or duplicate patient schedules.

### 💳 Billing & Financial Invoicing
* Automatic total computation formula:
  $$\text{Subtotal} = \text{Consultation Fee} + \text{Medicine} + \text{Laboratory} + \text{Other Charges}$$
  $$\text{Total} = \max(0.0, \text{Subtotal} - \text{Discount} + \text{Tax})$$
* Payment status tracking (`Paid`, `Pending`, `Partially Paid`) across `Cash`, `Card`, and `Bank Transfer`.

### 📊 Analytics & Reporting
* **Interactive Dashboards**: Real-time KPI summary cards and Plotly interactive visualizations (Appointments by status, doctor specialization breakdown, revenue by status, and patient growth line charts).
* **CSV Exports**: Export Patient Registrations, Appointments, and Financial Revenue reports for custom date ranges.

---

## 🛠️ Technology Stack

### 🐍 Backend / Language
| Technology | Version | Role |
|---|---|---|
| **Python** | 3.9+ | Core programming language |
| **SQLite3** | Built-in | Relational database (`hospital.db`) |
| **JSON** | Built-in | Patient data backup (`registered_patients.json`) |
| **hashlib** | Built-in | Salted password hashing (`pbkdf2_hmac`) |
| **datetime / re** | Built-in | Date validation & regex utilities |

### 🖥️ Frontend / UI Framework
| Technology | Version | Role |
|---|---|---|
| **Streamlit** | ≥ 1.31.0 | Web app framework — UI rendering & routing |
| **Vanilla CSS** | — | Custom design system (`assets/styles.css`) |
| **HTML** (inline) | — | Custom banners, badges & layouts |
| **Plus Jakarta Sans** | Google Fonts | Premium UI typography |

### 📊 Data & Visualization
| Technology | Version | Role |
|---|---|---|
| **Pandas** | ≥ 2.0.0 | Data manipulation, filtering & CSV export |
| **Plotly Express** | ≥ 5.18.0 | Interactive pie charts & bar graphs |
| **Plotly Graph Objects** | ≥ 5.18.0 | Advanced chart customization |

### 📁 Project Architecture

```
hospital-mangement/
├── app.py                      # Main Streamlit app launcher & role router
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── hospital.db                 # SQLite database (auto-created on startup)
├── registered_patients.json    # JSON backup of registered patients
├── database/
│   ├── db.py                   # SQLite connection manager & foreign key enforcer
│   ├── schema.py               # DDL table creation scripts
│   └── seed.py                 # Demo data seeder (10 patients, 8 doctors, appts, bills)
├── services/
│   ├── auth_service.py         # Login, registration, password hashing
│   ├── patient_service.py      # Patient CRUD operations & filters
│   ├── doctor_service.py       # Doctor CRUD operations & schedule manager
│   ├── appointment_service.py  # Slot availability algorithm & appointment booking
│   └── billing_service.py      # Invoice creation & payment status calculations
├── utils/
│   ├── validators.py           # Email, phone, DOB, non-negative validators
│   ├── appointment_utils.py    # Time slot generators & day matcher
│   ├── helpers.py              # Status badges, currency formatters
│   └── disease_rules.py        # Rule-based disease matching dictionary & disclaimer
└── assets/
    ├── styles.css              # Custom CSS design system (dark sidebar, cards, animations)
    └── background.png          # App background image
```

### 🏗️ Architecture Layers

| Layer | Files | Responsibility |
|---|---|---|
| **UI / Controller** | `app.py` | Page routing, form rendering, session state |
| **Database** | `database/` | Connection, schema creation, seed data |
| **Business Logic** | `services/` | CRUD operations, booking rules, billing calculations |
| **Utilities** | `utils/` | Validation, formatting, disease-specialization rules |
| **Assets** | `assets/` | CSS styling, background image |


---

## 🚀 Getting Started

### Prerequisites
* Python 3.9 or higher installed on your local machine.

### Installation

1. **Clone or Navigate to the project folder**:
   ```bash
   cd hospital-mangement
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   streamlit run app.py
   ```
   *The database `hospital.db` will automatically initialize and populate with sample data on first run!*

---

## 🔑 Demo Credentials

### 👨‍💼 Hospital Administrator
* **Username**: `admin`
* **Password**: `admin123`

### 👤 Sample Patient Account
* **Username**: `john_doe`
* **Password**: `pass123`

*(Additional demo patient accounts: `alice_smith` / `pass123`, `michael_brown` / `pass123`)*

---

## 📸 Screenshots

*(Add screenshots of your Admin Dashboard, Patient Booking, and Billing screens here for your portfolio presentation)*

---

## 🔮 Future Enhancements
* Multi-branch hospital support.
* PDF invoice generation and download.
* Email/SMS notification simulation logs.
* Prescription & lab test results storage.

---

## 📄 License

**Copyright (c) 2026 Muhammad Annas. All Rights Reserved.**

This project and all of its source code, files, designs, and associated materials are proprietary and protected by copyright.

No permission is granted to copy, modify, distribute, reproduce, publish, sublicense, sell, or use this project or any part of it for commercial or personal purposes without prior written permission from the copyright holder.

The project is provided for **portfolio and demonstration purposes only**.

For permission to use any part of this project, please contact the copyright holder.

See the [`LICENSE`](./LICENSE) file for full details.

---

*Built with ❤️ by Muhammad Annas*
