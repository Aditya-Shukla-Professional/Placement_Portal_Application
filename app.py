import sqlite3
from datetime import date
from flask import Flask,render_template,request,redirect,url_for,flash
from flask_login import LoginManager, login_user, login_required,logout_user,UserMixin,current_user
from database import get_user_by_email, create_company, create_student
from werkzeug.security import check_password_hash

app=Flask(__name__)

app.secret_key = "dsjcn34y7r3fbf9218wdneuf#^%#&@()" # Secret key

# Login Manager
login_manager= LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"

class User(UserMixin):
    def __init__(self, id, role):
        self.id = f"{role}-{id}"
        self.role = role
        self.actual_id=id

@app.route("/") # Home Page
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET","POST"]) # Used to login by students and companies
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")

        user_obj=get_user_by_email(email,password)

        if user_obj and "error" in user_obj:
            flash("Company not yet approved")
            return render_template("login.html")
        if not user_obj:
            flash("Invalid email or password")
            return render_template("login.html")
        
        # Create User object
        user = User(user_obj["id"], user_obj["role"])
        
        # Log user into session
        login_user(user)
        
        if user.role=="admin":
            return redirect(url_for("admin_dashboard"))
        elif user.role=="student":
            return redirect(url_for("student_dashboard"))
        elif user.role=="company":
            return redirect(url_for("company_dashboard"))
        
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/student_register",methods=["GET","POST"]) # Used to register new students
def student_register():
    if request.method=="POST":
        name=request.form.get("name")
        email=request.form.get("email")
        age=request.form.get("age")
        gender=request.form.get("gender")
        password=request.form.get("password")
        branch=request.form.get("branch")
        cgpa=request.form.get("cgpa")

        create_student(name,email,age,gender,password,branch,cgpa)
        flash("Registration successful! You can now login.")
        return redirect(url_for("login"))
    
    return render_template("student_register.html")

@app.route("/company_register", methods=["GET","POST"]) # Used to register a new company
def company_register():
    if request.method=="POST":
        company_name=request.form.get("name")
        email=request.form.get("email")
        password=request.form.get("password")
        contact=request.form.get("contact")
        website=request.form.get("website")

        create_company(company_name,email,password,contact,website)
        flash("Registration successful! You can now login.")
        return redirect(url_for("login"))
    return render_template("company_register.html")

@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    if current_user.role!="admin":
        flash("Unauthorized access")
        return redirect(url_for("login"))
    return render_template("admin_dashboard.html")

@app.route("/student_dashboard")
@login_required
def student_dashboard():
    if current_user.role!="student":
        flash("Unauthorized access")
        return redirect(url_for("login"))
    return render_template("student_dashboard.html")

@app.route("/company_dashboard")
@login_required
def company_dashboard():
    if current_user.role!="company":
        flash("Unauthorized access")
        return redirect(url_for("login"))
    return render_template("company_dashboard.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))






@login_manager.user_loader
def load_user(user_id):
    try:
        role,actual_id=user_id.split("-")
        actual_id=int(actual_id)
    except:
        return None
    return User(actual_id,role)

if __name__=="__main__":
    app.run(port=5000,debug=True)