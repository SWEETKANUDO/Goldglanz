<h1 align="center">✨ Goldglanz ✨</h1>
<p align="center">
  <i>A modern Jewellery E-commerce Store built with Flask + MySQL</i><br>
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Flask-2.x-black?style=for-the-badge&logo=flask" />
  <img src="https://img.shields.io/badge/MySQL-8.x-orange?style=for-the-badge&logo=mysql" />
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" />
</p>

---

## 🎯 Overview
Goldglanz is a **full-stack jewellery store** application created as a college project.  
It includes product listings, shopping cart, admin dashboard, and a responsive UI.  
Perfect for **learning Flask + MySQL integration** and building real-world e-commerce prototypes.

---

<p align="center">
## 🧭 Quick demo / preview
> https://goldglanz.vercel.app/

</p>

---

## ✨ Features
- 🛍️ Product catalog with categories & details  
- 🛒 Shopping cart with add/remove functionality  
- 👩‍💻 Admin dashboard for managing products & orders  
- 🎨 Responsive templates with CSS/JS  
- 💾 Database migrations included  

---

## 🛠 Tech Stack
- **Backend:** Flask (Python)  
- **Database:** MySQL (via SQLAlchemy ORM)  
- **Frontend:** Jinja2 templates + static CSS/JS  
- **Tools:** Flask-Migrate, Vercel/Heroku deploy configs  

---

## ⚡ Quickstart
```bash
# Clone repo
git clone https://github.com/SWEETKANUDO/Goldglanz.git
cd Goldglanz

# Setup venv & install
python3 -m venv venv
source venv/bin/activate     # Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
export DATABASE_URL="mysql+pymysql://user:pass@localhost/goldglanz_db"
export FLASK_APP=app.py
export FLASK_ENV=development

# Run migrations (if present)
python migrate.py   # or flask db upgrade

# Start server
flask run
