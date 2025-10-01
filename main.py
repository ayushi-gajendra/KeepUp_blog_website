from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm




app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLES

# Parent of BlogPost, Comment
class User(UserMixin, db.Model):
    __tablename__="users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Parent relationship
    posts: Mapped["BlogPost"]= relationship(back_populates="author")
    comments: Mapped["Comment"]= relationship(back_populates="comment_author")


# Parent of Comment, Child of User
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    # Child relationship
    author_id: Mapped[int]= mapped_column(ForeignKey("users.id"))
    author: Mapped["User"]= relationship(back_populates="posts")
    # Parent relationship
    comments: Mapped["Comment"]= relationship(back_populates="parent_post")


# Child of User, BlogPost
class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int]= mapped_column(Integer, primary_key=True)
    text: Mapped[str]= mapped_column(String(1000), nullable=False)
    # Child relationship with User
    author_id: Mapped[int]= mapped_column(ForeignKey("users.id"))
    comment_author:Mapped["User"]= relationship(back_populates="comments")
    # Child relationship with BlogPost
    post_id: Mapped[int]= mapped_column(ForeignKey("blog_posts.id"))
    parent_post: Mapped["BlogPost"]= relationship(back_populates="comments")



with app.app_context():
    db.create_all()


#callback function Flask-Login will call to reload the logged-in user
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


#admin only decorator function
def admin_only(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        if current_user.id==1:
            return func(*args, **kwargs)
        else:
            return abort(code=403, description="You are not allowed to access this page.")
    return decorated_func


@app.route('/register', methods=["GET", "POST"])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        # check if user exists in db
        result= db.session.execute(db.select(User).where(User.email==form.email.data))
        already_a_user= result.scalar()
        if already_a_user:
            flash("You are already registered with us, login instead.")
            return redirect(url_for("login"))
        # otherwise, register a new user
        else:
            hash_and_salted_password= generate_password_hash(
                form.password.data,
                method='pbkdf2:sha256',
                salt_length=8
            )
            user= User(
                email= form.email.data,
                password= hash_and_salted_password,
                name= form.name.data
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("get_all_posts"))
    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        password=form.password.data
        email=form.email.data
        user=db.session.execute(db.select(User).where(User.email==email)).scalar()
        if not user:
            flash("Email doesn't exist, try a different one")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            flash("Wrong password, try again")
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))
    return render_template("login.html", form=form)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    form = CommentForm()
    comments = db.session.execute(db.select(Comment).where(Comment.post_id==post_id)).scalars().all()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            new_comment= Comment(
                text= form.text.data,
                comment_author= current_user,
                parent_post= requested_post
            )
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for("show_post", post_id=post_id))
        else:
            flash("You need to login to comment")
            return redirect(url_for("login"))
    return render_template("post.html", post=requested_post, comment_form=form, comments=comments)


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            date=date.today().strftime("%B %d, %Y"),
            author_id= current_user.id,
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True,port=5001)
