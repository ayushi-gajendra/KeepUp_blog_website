# 📝 Flask Blog App

A full-featured Flask Blog Application with:
- User authentication (register, login, logout)
- Post creation, editing, and deletion
- Rich-text editing with CKEditor
- Responsive design with Bootstrap 5
- Secure password hashing (Werkzeug)
- SQLite database with SQLAlchemy ORM

---

## 📸 Screenshotsgit

Add some images of your blog pages here (Home, Post, Login).

---

## 🚀 Features

- User registration & login (with hashed passwords)
- Create, edit, delete blog posts (admin only)
- View all posts and individual posts
- Comment functionality (to be added)
- Responsive UI using Flask-Bootstrap
- Rich-text editing with Flask-CKEditor
- Database models with SQLAlchemy ORM

---

## 🛠️ Tech Stack

- Backend: Flask

- Database: SQLite (via SQLAlchemy ORM)

- Frontend: Bootstrap 5 + Jinja Templates

- Authentication: Flask-Login

- Forms & Validation: Flask-WTF

- Password Security: Werkzeug

---

## 📂 Project Structure

flask-blog/
│── static/ 			# CSS, images, JS
│── templates/ 			# HTML templates
│ ├── index.html
│ ├── register.html
│ ├── login.html
│ ├── post.html
│ ├── make-post.html
│ ├── about.html
│ └── contact.html
│── forms.py 			# Flask-WTF form classes
│── app.py 				# Main Flask application
│── posts.db 			# SQLite database
│── requirements.txt 	# Dependencies
│── README.md 			# Project documentation

## ⚡ Installation & Setup

1. Clone the repo

```
git clone https://github.com/your-username/flask-blog.git
cd flask-blog
```

2. Create a virtual environment & activate it
```
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. Run the app
```
python app.py
```

Flask will start at: 👉 http://127.0.0.1:5001

## 📦 Requirements

Add these to your requirements.txt:

- Flask
- Flask-Bootstrap
- Flask-CKEditor
- Flask-WTF
- Flask-Login
- Flask-SQLAlchemy
- Werkzeug

## 🔑 Admin Controls (to implement)

Only admin users can:
- Create new posts
- Edit posts
- Delete posts
