# 🎬  Production-Expense-Analytics Web Application

A full-stack web application that automates the **entire ETL pipeline** for film production expense management through a clean browser-based UI. Users upload raw department CSVs, the app validates and cleans them, generates a financial analytics dashboard, and pushes the final data into MySQL — all in one flow.


---

## 🖥️ Live Demo

> *Run locally — see setup instructions below*

---

## ✨ Features

- 📂 **Drag & drop file upload** for 4 departments (Camera, Catering, Transport, Talent)
- ✅ **Automated column validation** — instantly flags missing or incorrect columns
- 🧹 **Auto data cleaning** — computes derived costs per department
- 📊 **Interactive analytics dashboard** — total spend, average spend, top spender, department-wise bar chart
- 🗄️ **One-click MySQL push** — loads combined expenses into database
- 🔄 **4-step progress tracker** in the UI (Upload → Validate → Combine → Push to DB)

---

## 🗂️ Project Structure

```
BoomTown-WebApp/
│
├── app.py                  # Flask backend — all API routes + frontend HTML
├── save.py                 # Combine logic reference
├── requirements.txt        # Python dependencies
│
├── PROCESSED_DATA/         # Auto-created — stores cleaned CSVs
├── Combined_Record/        # Auto-created — stores combined_expenses.csv
│
└── README.md
```

---

## 🔁 How It Works

```
User Uploads 4 CSVs
        ↓
  /api/validate  →  Validates columns, cleans data, saves to PROCESSED_DATA/
        ↓
  /api/combine   →  Merges all departments → Combined_Record/combined_expenses.csv
                    Returns dashboard metrics (total, avg, top dept)
        ↓
  /api/load_db   →  Inserts combined data into MySQL BoomTown.expenses table
```

---

## 🧪 Raw Data Format

Each uploaded CSV must contain these columns:

| Department | Required Columns |
|-----------|-----------------|
| Catering | `Date, Vendor, Meal_Type, Headcount, Price_Per_Head` |
| Camera | `Date, Item_Name, Daily_Rate, Days, Total_Cost` |
| Transport | `Date, Vehicle_Type, Fuel_AED, Salik_Tolls, Driver_OT_Hours` |
| Talent | `Actor_Name, Role, Agency, Contract_Fee, Status` |

---

## 🔢 Business Logic

| Department | Cost Calculation |
|-----------|-----------------|
| Camera | `Total_Cost = Daily_Rate × Days` |
| Catering | `Total_Spend = Headcount × Price_Per_Head` |
| Transport | `Total = Fuel_AED + Salik_Tolls + (Driver_OT_Hours × 50 AED)` |
| Talent | `Contract_Fee` (excludes rows where Status = "pending") |

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/Toufiq1806/Production-Expense-Analytics.git
cd Production-Expense-Analytics
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up MySQL database
```sql
CREATE DATABASE BoomTown;
```
> The `expenses` table is created automatically when you push data.

### 4. Update database credentials in `app.py`
```python
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "YOUR_PASSWORD",   # <-- change this to your password
    "database": "BoomTown",
}
```

### 5. Run the app
```bash
python app.py
```

Then open your browser and go to:
```
http://localhost:5000
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the web UI |
| `POST` | `/api/validate` | Validates and cleans uploaded CSVs |
| `POST` | `/api/combine` | Merges departments, returns dashboard metrics |
| `POST` | `/api/load_db` | Pushes combined data into MySQL |
| `GET` | `/api/expenses` | Retrieves all expenses from the database |

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask, Flask-CORS
- **Data Processing:** Pandas
- **Database:** MySQL, PyMySQL
- **Frontend:** Vanilla HTML, CSS, JavaScript (served by Flask)

---

## 📋 requirements.txt

```
flask
flask-cors
pandas
pymysql
```

---

## 👤 Author

Made by **[Your Name]** — feel free to connect on [LinkedIn](https://linkedin.com/in/your-profile)
