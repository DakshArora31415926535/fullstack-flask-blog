from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
# Import your forms from the forms.py
from forms import CreatePostForm
from forms import LoginForm
from forms import RegisterForm
from forms import CommentForm

'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


@login_manager.user_loader
def load_user(id):
    return Mainusers.query.get(id)


def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        mainid = current_user.id
        if mainid != 1:
            # If the user is not an admin, redirect to the home page
            return redirect(url_for('get_all_posts'))
        # If the user is an admin, call the decorated function
        return func(*args, **kwargs)

    return wrapper


# CONFIGURE TABLES
class BlogPost(db.Model, UserMixin):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)



class Mainusers(db.Model, UserMixin):
    __tablename__ = "main_users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)


class Comments(db.Model, UserMixin):
    __tablename__ = "comments_by_users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    comment: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer)


with app.app_context():
    db.create_all()



@app.route('/register', methods=["POST", "GET"])
def register():
    mainer = RegisterForm()
    if mainer.validate_on_submit():
        namer = mainer.name.data
        if Mainusers.query.filter_by(name=namer).first():
            print(
                f"Registered user {namer} with hashed password {Mainusers.query.filter_by(name=namer).first().password}")
            print("User already registered")
            return redirect("/login")
        passwo = mainer.password.data
        hashedpass = generate_password_hash(password=passwo, method='pbkdf2:sha256', salt_length=8)
        print(hashedpass)
        newuse = Mainusers(name=namer, password=hashedpass)
        db.session.add(newuse)
        db.session.commit()
        login_user(newuse)
        print(f"Registered user {namer} with hashed password {hashedpass}")
        return redirect("/")
    return render_template("register.html", former=mainer)


@app.route('/login', methods=["GET", "POST"])
def login():
    former = LoginForm()
    if former.validate_on_submit():
        mainname = former.name.data
        password = former.password.data
        user = Mainusers.query.filter_by(name=mainname).first()
        if user:
            print(f"Found user {mainname} with hashed password {user.password}")
            if check_password_hash(user.password, password):
                print("Password correct")
                login_user(user)
                return redirect(url_for("get_all_posts"))
            else:
                print("Incorrect password")
                flash("Login Unsuccessful. Please check your username and password", "danger")
        else:
            print("User not found")
            flash("Login Unsuccessful. Please check your username and password", "danger")
    return render_template("login.html", mainform=former)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/', methods=["GET", "POST"])
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>",methods=["GET","POST"])
@login_required
def show_post(post_id):
    maincommmentform = CommentForm()
    list1=db.session.query(Comments).all()
    finalcomments=[]
    for i in list1:
        if i.user_id==post_id:
            finalcomments.append(i.comment)
    print(finalcomments,"sjdhhddhrhrrh")
    if maincommmentform.validate_on_submit():
        newcomment=maincommmentform.comment.data
        print(newcomment,"hhhhhhhhhhhshhhshsh")
        newe=Comments(user_id=post_id,comment=newcomment)
        db.session.add(newe)
        db.session.commit()
        print("jddddddddddddddddddddddddddddd")
        return redirect(url_for("show_post",post_id=post_id))
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post, form=maincommmentform,commentlist=finalcomments)



@app.route("/new-post", methods=["GET", "POST"])
@login_required
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user.name,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)



@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
@login_required
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
        post.author = current_user.name
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)



@app.route("/delete/<int:post_id>")
@admin_only
@login_required
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
    app.run(debug=True, port=5002)
