from flask import Flask,request,redirect,render_template,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String,ForeignKey
from flask_login import login_user,current_user,login_required,logout_user
from flask_login import UserMixin,LoginManager
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'your_secret_key'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Blocks(db.Model):
  id = mapped_column(Integer,autoincrement=True, primary_key=True)
  value = mapped_column(String(100),nullable=False)

class Users(UserMixin,db.Model):
  __tablename__ = "Users"
  id = mapped_column(Integer,autoincrement=True, primary_key=True)
  email = mapped_column(String(50),nullable=False)
  name = mapped_column(String(50),nullable=False)
  password = mapped_column(String(20),nullable=False)

class Post(db.Model):
  __tablename__ = "post"
  id = mapped_column(Integer,autoincrement=True,primary_key=True)
  title = mapped_column(String(20),nullable=False)
  content = mapped_column(String(100),nullable=False)
  user_id = mapped_column(Integer, ForeignKey("Users.id"),nullable=False)
  
with app.app_context():
    db.create_all()

@app.route("/home")
@app.route("/")
def home():
  posts = Post.query.all()
  return render_template("home.html",posts=posts)

@app.route("/user", methods=["GET"])
@login_required
def user_route():
  user = current_user
  return render_template("user.html", email=user.email)

@app.route("/register",methods = ["GET","POST"])
def register():
  if request.method == "GET":
    return render_template("register.html")
  else:
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    pw_hash = bcrypt.generate_password_hash(password)
    x = Users(name = name,email = email,password = pw_hash)
    db.session.add(x)
    db.session.commit()
    return render_template("home.html")
  
@app.route("/login",methods=["GET","POST"])
def login():
  if request.method == "POST":
    email = request.form.get("email")
    password = request.form.get("password")
    user = Users.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password,password):
      login_user(user) 
      return render_template("home.html")
    else:
      flash("wrong password!")
  return render_template("login.html")
  
@app.route("/new_post",methods=["GET","POST"])
@login_required
def new_post():
  if request.method == "POST":
    title = request.form.get("title")
    content = request.form.get("content")
    post = Post(title=title,content=content,user_id=current_user.id)
    db.session.add(post)
    db.session.commit()
    flash("your post is successfully created")
    return redirect(url_for("home"))
  return render_template("new_post.html")

@app.route("/logout")
@login_required
def logout():
  logout_user()
  return redirect(url_for(home))

@app.route("/delete/<int:id>",methods = ["GET","POST"])
def delete(id):
  id = db.get_or_404(Post,id)
  db.session.delete(id)
  db.session.commit()
  return redirect(url_for("home"))
  
@app.route("/update/<int:post_id>",methods = ["GET","POST"])
def update(post_id):
  id = db.get_or_404(Post,post_id)
  if request.method == "POST":
    title = request.form.get("title")
    content = request.form.get("content")
    id.title = title
    id.content = content
    db.session.commit()
    return redirect(url_for("home"))
  return render_template("edit.html")


  

