import sqlite3
import os
from database import init_db
from flask import Flask,render_template,request,redirect,url_for,flash
from flask_login import LoginManager, login_user, login_required,logout_user,UserMixin,current_user
from database import get_user_by_email, create_company, create_student
from werkzeug.utils import secure_filename
from datetime import datetime

app=Flask(__name__)

app.secret_key = "dsjcn34y7r3fbf9218wdneuf#^%#&@()" # Secret key
 

# Login Manager
login_manager= LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"

class User(UserMixin):
    def __init__(self, id, role):
        self.actual_id = int(id)  # Force integer for DB queries
        self.role = str(role).lower() # Normalize to lowercase
        self.id = f"{self.role}-{self.actual_id}"

@app.route("/") # Home Page
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET","POST"])  # Used to login by students and companies
def login():
    if current_user.is_authenticated:
        return redirect(url_for(f"{current_user.role}_dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user_obj = get_user_by_email(email, password)
        print("LOGIN DEBUG:", user_obj)

        # Error returned from helper
        if user_obj and "error" in user_obj:
            flash(user_obj["error"])
            return render_template("login.html")

        # Invalid login
        if not user_obj:
            flash("Invalid email or password")
            return render_template("login.html")

        # 🚨 COMPANY APPROVAL + BLACKLIST CHECK
        if user_obj["role"] == "company":
            con = sqlite3.connect("placement.db")
            cur = con.cursor()

            cur.execute("""
                SELECT approval_status, is_blacklisted
                FROM companies
                WHERE id=?
            """, (user_obj["id"],))

            company = cur.fetchone()
            con.close()

            if company:
                approval_status, is_blacklisted = company

                if is_blacklisted == 1:
                    flash("Your company account has been blacklisted by the admin.")
                    return render_template("login.html")

                if approval_status != "Approved":
                    flash("Your company account is pending admin approval.")
                    return render_template("login.html")

        # Create User object
        user = User(user_obj["id"], user_obj["role"])

        # Log user into session
        login_user(user)

        # Redirect based on role
        if user.role == "admin":
            return redirect(url_for("admin_dashboard"))
        elif user.role == "student":
            return redirect(url_for("student_dashboard"))
        elif user.role == "company":
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
    con=sqlite3.connect("placement.db")
    cur=con.cursor()
    cur.execute("SELECT COUNT(*) FROM students")
    total_students=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM companies")
    total_companies=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM applications")
    total_applications=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM jobs")
    total_jobs=cur.fetchone()[0]
    con.close()
    return render_template("admin_dashboard.html",total_students=total_students,total_companies=total_companies,total_jobs=total_jobs,total_applications=total_applications)

@app.route("/admin/pending_companies")
@login_required
def pending_companies():
    if current_user.role!="admin":
        flash("Unauthorized access")
        return redirect(url_for("login"))
    con=sqlite3.connect("placement.db")
    cur=con.cursor()
    cur.execute("SELECT * FROM companies WHERE approval_status='Pending'")
    companies=cur.fetchall()
    con.close()
    return render_template("pending_companies.html",companies=companies)

@app.route("/admin/approve_company/<int:id>", methods=["POST"])
@login_required
def approve_company(id):
    if current_user.role != "admin":
        flash("Unauthorized access")
        return redirect(url_for("login"))

    con = sqlite3.connect("placement.db")
    cur = con.cursor()
    cur.execute("UPDATE companies SET approval_status='Approved' WHERE id=?", (id,))
    con.commit()
    con.close()

    flash("Company approved successfully!")
    return redirect(url_for("pending_companies"))

@app.route("/admin/reject_company/<int:id>", methods=["POST"])
@login_required
def reject_company(id):
    if current_user.role != "admin":
        flash("Unauthorized access")
        return redirect(url_for("login"))

    con = sqlite3.connect("placement.db")
    cur = con.cursor()
    cur.execute("UPDATE companies SET approval_status='Rejected' WHERE id=?", (id,))
    con.commit()
    con.close()

    flash("Company rejected successfully!")
    return redirect(url_for("pending_companies"))

@app.route("/admin/pending_jobs")
@login_required
def pending_jobs():
    if current_user.role!="admin":
        flash("Unauthorized access")
        return redirect(url_for("login"))
    con=sqlite3.connect("placement.db")
    cur=con.cursor()
    cur.execute("SELECT * FROM jobs WHERE status='Pending'")
    jobs=cur.fetchall()
    con.close()
    return render_template("pending_jobs.html",jobs=jobs)

@app.route("/admin/approve_job/<int:id>", methods=["POST"])
@login_required
def approve_job(id):
    if current_user.role != "admin":
        flash("Unauthorized access")
        return redirect(url_for("login"))

    con = sqlite3.connect("placement.db")
    cur = con.cursor()
    cur.execute("UPDATE jobs SET status='Approved' WHERE id=?", (id,))
    con.commit()
    con.close()

    flash("Job approved successfully!")
    return redirect(url_for("pending_jobs"))

@app.route("/admin/reject_job/<int:id>", methods=["POST"])
@login_required
def reject_job(id):
    if current_user.role != "admin":
        flash("Unauthorized access")
        return redirect(url_for("login"))

    con = sqlite3.connect("placement.db")
    cur = con.cursor()
    cur.execute("UPDATE jobs SET status='Closed' WHERE id=?", (id,))
    con.commit()
    con.close()

    flash("Job closed successfully!")
    return redirect(url_for("pending_jobs"))

@app.route("/admin/manage_students")
@login_required
def manage_students():
    if current_user.role != "admin":
        flash("Unauthorized access")
        return redirect(url_for("login"))
    
    search_query=request.args.get("search")

    con=sqlite3.connect("placement.db")
    cur=con.cursor()
    if search_query:
        cur.execute("SELECT * FROM students WHERE name LIKE ? OR email LIKE ? OR id LIKE ?",(f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
    else:
        cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    con.close()
    return render_template("manage_students.html", students=students)

@app.route("/admin/deactivate_student/<int:id>", methods=["POST"])
@login_required
def deactivate_student(id):
    if current_user.role != "admin":
        flash("Unauthorized access")
        return redirect(url_for("login"))
    con=sqlite3.connect("placement.db")
    cur=con.cursor()
    cur.execute("UPDATE students SET is_active=0 WHERE id=?",(id,))
    con.commit()
    con.close()
    flash("Student deactivated successfully!")
    return redirect(url_for("manage_students"))

@app.route("/admin/manage_companies")
@login_required
def manage_companies():
    if current_user.role != "admin":
        flash("Unauthorized access")
        return redirect(url_for("login"))
    
    search_query=request.args.get("search")

    con=sqlite3.connect("placement.db")
    cur=con.cursor()
    if search_query:
        cur.execute("""
            SELECT * FROM companies
            WHERE company_name LIKE ?
            OR email LIKE ?
        """, (f"%{search_query}%", f"%{search_query}%"))
    else:
        cur.execute("SELECT * FROM companies")
    companies=cur.fetchall()
    con.close()
    return render_template("manage_companies.html",companies=companies)

@app.route("/admin/blacklist_company/<int:id>", methods=["POST"])
@login_required
def blacklist_company(id):
    if current_user.role != "admin":
       flash("Unauthorized access")
       return redirect(url_for("login"))
    con=sqlite3.connect("placement.db")
    cur=con.cursor()
    cur.execute("UPDATE companies SET is_blacklisted=1 WHERE id=?",(id,))
    con.commit()
    con.close()
    flash("Company blacklisted successfully!")
    return redirect(url_for("manage_companies"))

@app.route("/admin/manage_jobs")
@login_required
def manage_jobs():
    if current_user.role != "admin":
       flash("Unauthorized access")
       return redirect(url_for("login"))
    con=sqlite3.connect("placement.db")
    cur=con.cursor()
    cur.execute("SELECT * FROM jobs JOIN companies ON jobs.company_id=companies.id")
    jobs=cur.fetchall()
    con.close()
    return render_template("manage_jobs.html",jobs=jobs)

@app.route("/admin/manage_applications")
@login_required
def manage_applications():
    if current_user.role != "admin":
       flash("Unauthorized access")
       return redirect(url_for("login"))
    con=sqlite3.connect("placement.db")
    cur=con.cursor()
    cur.execute("""
        SELECT applications.id,students.name,companies.company_name,
                jobs.title,applications.status,applications.applied_on
                FROM applications JOIN students ON applications.student_id =
                students.id JOIN jobs ON applications.job_id = jobs.id
                JOIN companies ON jobs.company_id = companies.id
                
    """)
    applications=cur.fetchall()
    con.close()
    return render_template("manage_applications.html",applications=applications)

@app.route("/admin/placement_tracking")
@login_required
def placement_tracking():
    if current_user.role != "admin":
        flash("Unauthorized access")
        return redirect(url_for("login"))

    con = sqlite3.connect("placement.db")
    cur = con.cursor()

    cur.execute("""
        SELECT students.name,
               companies.company_name,
               jobs.title,
               applications.status,
               applications.applied_on
        FROM applications
        JOIN students ON applications.student_id = students.id
        JOIN jobs ON applications.job_id = jobs.id
        JOIN companies ON jobs.company_id = companies.id
        ORDER BY applications.applied_on DESC
    """)

    applications = cur.fetchall()
    con.close()

    return render_template("admin_application_tracking.html", applications=applications)

@app.route("/student_dashboard")
@login_required
def student_dashboard():
    if current_user.role != "student":
        flash("Unauthorized access")
        return redirect(url_for("login"))

    con = sqlite3.connect("placement.db")
    cur = con.cursor()

    # Total Applications
    cur.execute("""
        SELECT COUNT(*) FROM applications
        WHERE student_id = ?
    """, (current_user.actual_id,))
    total_applied = cur.fetchone()[0]

    # Status Counts
    cur.execute("""
        SELECT COUNT(*) FROM applications
        WHERE student_id = ? AND status = 'Shortlisted'
    """, (current_user.actual_id,))
    shortlisted = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM applications
        WHERE student_id = ? AND status = 'Selected'
    """, (current_user.actual_id,))
    selected = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM applications
        WHERE student_id = ? AND status = 'Rejected'
    """, (current_user.actual_id,))
    rejected = cur.fetchone()[0]

    # 🔔 Notifications (status changed)
    cur.execute("""
        SELECT jobs.title,
               companies.company_name,
               applications.status
        FROM applications
        JOIN jobs ON applications.job_id = jobs.id
        JOIN companies ON jobs.company_id = companies.id
        WHERE applications.student_id = ?
        AND applications.status IN ('Shortlisted','Selected','Rejected')
        ORDER BY applications.applied_on DESC LIMIT 5
    """, (current_user.actual_id,))

    notifications = cur.fetchall()

    con.close()

    return render_template(
        "student_dashboard.html",
        total_applied=total_applied,
        shortlisted=shortlisted,
        selected=selected,
        rejected=rejected,
        notifications=notifications
    )


@app.route("/student/profile", methods=["GET","POST"])
@login_required
def student_profile():
    if current_user.role!="student":
        flash("Unauthorized access")
        return redirect(url_for("login"))
    con=sqlite3.connect("placement.db")
    cur=con.cursor()
    if request.method=="POST":
        branch=request.form.get("branch")
        cgpa=request.form.get("cgpa")
        skills=request.form.get("skills")
        resume=request.files.get("resume")
        resume_path=None

        if resume and resume.filename!="":
            filename = f"{current_user.actual_id}_{secure_filename(resume.filename)}"

            if not filename.lower().endswith(".pdf"):
                flash("Only PDF resumes are allowed.")
                con.close()
                return redirect(url_for("student_profile"))
            
            upload_folder = os.path.join("static", "uploads")
            os.makedirs(upload_folder, exist_ok=True)

            file_path = os.path.join(upload_folder, filename)
            resume.save(file_path)

            # Save relative path for Flask static serving
            resume_path = f"uploads/{filename}"
        
        if resume_path:
            cur.execute("UPDATE students SET branch=?, cgpa=?, skills=?, resume_path=? WHERE id=?",(branch,cgpa,skills,resume_path,current_user.actual_id))
        else:
            cur.execute("UPDATE students SET branch=?, cgpa=?, skills=? WHERE id=?",(branch,cgpa,skills,current_user.actual_id))
        
        con.commit()
        flash("Profile updated successfully!")

    cur.execute("SELECT name,email,branch,cgpa,skills,resume_path FROM students WHERE id=?",(current_user.actual_id,))
    student=cur.fetchone()
    
    con.close()
    return render_template("student_profile.html",student=student)

@app.route("/student/jobs")
@login_required
def student_jobs():
    if current_user.role != "student":
        flash("Unauthorized access")
        return redirect(url_for("login"))

    search_query = request.args.get("search")

    con = sqlite3.connect("placement.db")
    cur = con.cursor()

    if search_query:
        cur.execute("""
            SELECT jobs.id,
                   jobs.title,
                   jobs.description,
                   jobs.eligibility_criteria,
                   jobs.deadline,
                   companies.company_name
            FROM jobs
            JOIN companies ON jobs.company_id = companies.id
            WHERE jobs.status = 'Approved'
            AND (
                companies.company_name LIKE ?
                OR jobs.title LIKE ?
                OR jobs.eligibility_criteria LIKE ?
            )
        """, (
            f"%{search_query}%",
            f"%{search_query}%",
            f"%{search_query}%"
        ))
    else:
        cur.execute("""
            SELECT jobs.id,
                   jobs.title,
                   jobs.description,
                   jobs.eligibility_criteria,
                   jobs.deadline,
                   companies.company_name
            FROM jobs
            JOIN companies ON jobs.company_id = companies.id
            WHERE jobs.status = 'Approved'
        """)

    jobs = cur.fetchall()

    # 🔹 Get jobs already applied by this student
    cur.execute("""
        SELECT job_id
        FROM applications
        WHERE student_id = ?
    """, (current_user.actual_id,))

    applied_jobs = [row[0] for row in cur.fetchall()]

    con.close()

    return render_template(
        "student_jobs.html",
        jobs=jobs,
        applied_jobs=applied_jobs
    )


@app.route("/student/apply/<int:job_id>", methods=["POST"])
@login_required
def apply_job(job_id):
    if current_user.role != "student":
        flash("Unauthorized access")
        return redirect(url_for("login"))

    con = sqlite3.connect("placement.db")
    cur = con.cursor()

    # 1️⃣ Check student is active
    cur.execute("SELECT is_active FROM students WHERE id=?", (current_user.actual_id,))
    student = cur.fetchone()

    if not student or student[0] == 0:
        con.close()
        flash("Your account is not active.")
        return redirect(url_for("student_jobs"))

    # 2️⃣ Check job status and deadline
    cur.execute("""
        SELECT status, deadline
        FROM jobs
        WHERE id=?
    """, (job_id,))
    job = cur.fetchone()

    if not job:
        con.close()
        flash("Job does not exist.")
        return redirect(url_for("student_jobs"))

    job_status, job_deadline = job

    # Must be Approved
    if job_status != "Approved":
        con.close()
        flash("This job is not available.")
        return redirect(url_for("student_jobs"))

    # 3️⃣ Deadline check
    try:
        deadline_date = datetime.strptime(job_deadline, "%Y-%m-%d")
        if deadline_date < datetime.now():
            con.close()
            flash("Application deadline has passed.")
            return redirect(url_for("student_jobs"))
    except:
        # If deadline format is unexpected, block application
        con.close()
        flash("Invalid job deadline.")
        return redirect(url_for("student_jobs"))

    # 4️⃣ Check duplicate application
    cur.execute("""
        SELECT id
        FROM applications
        WHERE student_id=? AND job_id=?
    """, (current_user.actual_id, job_id))

    already_applied = cur.fetchone()

    if already_applied:
        con.close()
        flash("You have already applied for this job.")
        return redirect(url_for("student_jobs"))

    # 5️⃣ Insert application
    cur.execute("""
        INSERT INTO applications (student_id, job_id, status, applied_on)
        VALUES (?, ?, 'Applied', CURRENT_TIMESTAMP)
    """, (current_user.actual_id, job_id))

    con.commit()
    con.close()

    flash("Application submitted successfully!")
    return redirect(url_for("student_jobs"))

@app.route("/student/my_applications")
@login_required
def my_applications():
    if current_user.role != "student":
        flash("Unauthorized access")
        return redirect(url_for("login"))

    con = sqlite3.connect("placement.db")
    cur = con.cursor()

    cur.execute("""
        SELECT jobs.title,
               companies.company_name,
               applications.applied_on,
               applications.status
        FROM applications
        JOIN jobs ON applications.job_id = jobs.id
        JOIN companies ON jobs.company_id = companies.id
        WHERE applications.student_id = ?
        ORDER BY applications.applied_on DESC
    """, (current_user.actual_id,))

    applications = cur.fetchall()
    con.close()

    return render_template("student_my_applications.html", applications=applications)

@app.route("/student/application_history")
@login_required
def student_application_history():
    if current_user.role != "student":
        flash("Unauthorized access")
        return redirect(url_for("login"))

    con = sqlite3.connect("placement.db")
    cur = con.cursor()

    cur.execute("""
        SELECT jobs.title,
               companies.company_name,
               applications.status,
               applications.applied_on
        FROM applications
        JOIN jobs ON applications.job_id = jobs.id
        JOIN companies ON jobs.company_id = companies.id
        WHERE applications.student_id = ?
        ORDER BY applications.applied_on DESC
    """, (current_user.actual_id,))

    applications = cur.fetchall()
    con.close()

    return render_template("student_application_history.html", applications=applications)

@app.route("/company_dashboard")
@login_required
def company_dashboard():
    if current_user.role!="company":
        flash("Unauthorized access")
        return redirect(url_for("login"))
    

    con=sqlite3.connect("placement.db")
    cur=con.cursor()

    cur.execute("SELECT approval_status, is_blacklisted FROM companies WHERE id=?", (current_user.actual_id,))
    company = cur.fetchone()
    if not company or company[0] != "Approved" or company[1] == 1:
            con.close()
            flash("Your company is not allowed to post jobs.")
            return redirect(url_for("company_dashboard"))
    
    cur.execute("SELECT COUNT(*) FROM jobs WHERE company_id=?",(current_user.actual_id,))
    total_jobs=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM jobs WHERE status='Approved' AND company_id=?",(current_user.actual_id,))
    active_jobs=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM jobs WHERE status='Closed' AND company_id=?",(current_user.actual_id,))
    closed_jobs=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM applications JOIN jobs ON applications.job_id=jobs.id WHERE jobs.company_id=?",(current_user.actual_id,))
    total_applications=cur.fetchone()[0]
    con.close()
    return render_template("company_dashboard.html",total_jobs=total_jobs,active_jobs=active_jobs,closed_jobs=closed_jobs,total_applications=total_applications)

@app.route("/company/post_job",methods=["GET","POST"])
@login_required
def post_job():
    if current_user.role!="company":
        flash("Unauthorized access")
        return redirect(url_for("login"))
    if request.method=="POST":
        title=request.form.get("title")
        description=request.form.get("description")
        skills=request.form.get("skills")
        experience=request.form.get("experience")
        salary=request.form.get("salary")
        deadline=request.form.get("deadline")

        con=sqlite3.connect("placement.db")
        cur=con.cursor()
        # Check company approval status
        cur.execute("SELECT approval_status, is_blacklisted FROM companies WHERE id=?", (current_user.actual_id,))
        company = cur.fetchone()

        if not company or company[0] != "Approved" or company[1] == 1:
            con.close()
            flash("Your company is not allowed to post jobs.")
            return redirect(url_for("company_dashboard"))
        
        cur.execute("""INSERT INTO jobs (company_id,title,
                    description,eligibility_criteria,deadline,status,
                    created_at) VALUES(?,?,?,?,?,'Pending',CURRENT_TIMESTAMP)"""
                    ,(current_user.actual_id,title,description,
                      f"Skills: {skills} | Experience: {experience} years | Salary: {salary} LPA",
                      deadline))
        con.commit()
        con.close()
        flash("Job Posted successfully waiting for admin approval.")
        return redirect(url_for("company_dashboard"))
    return render_template("post_job.html")

@app.route("/company/manage_jobs")
@login_required
def company_manage_jobs():
    if current_user.role!="company":
        flash("Unauthorized access")
        return redirect(url_for("login"))
    con=sqlite3.connect("placement.db")
    cur=con.cursor()
    cur.execute("SELECT id, title, deadline, status, created_at FROM jobs WHERE company_id=?",(current_user.actual_id,))
    jobs=cur.fetchall()
    con.close()
    return render_template("company_manage_jobs.html",jobs=jobs)

@app.route("/company/close_job/<int:job_id>",methods=["POST"])
@login_required
def close_job(job_id):
    if current_user.role!="company":
        flash("Unauthorized access")
        return redirect(url_for("login"))
    con=sqlite3.connect("placement.db")
    cur=con.cursor()
    cur.execute("UPDATE jobs SET status='Closed' WHERE id=? AND company_id=?",(job_id,current_user.actual_id))
    con.commit()
    con.close()
    flash("Job closed successfully!")
    return redirect(url_for("company_manage_jobs"))

@app.route("/company/view_applications/<int:job_id>")
@login_required
def view_applications(job_id):
    if current_user.role!="company":
        flash("Unauthorized access")
        return redirect(url_for("login"))
    con=sqlite3.connect("placement.db")
    cur=con.cursor()
    # Security Check: To make sure the job belong to this company
    cur.execute("SELECT id FROM jobs WHERE id=? AND company_id=?",(job_id,current_user.actual_id))
    job=cur.fetchone()

    if not job:
       con.close()
       flash("Unauthorized access to this job.")
       return redirect(url_for("company_manage_jobs"))
    
    cur.execute("""
        SELECT applications.id, students.name, students.cgpa, students.resume_path, applications.status, applications.applied_on
                FROM applications JOIN students ON applications.student_id=students.id JOIN jobs ON applications.job_id=jobs.id
                WHERE applications.job_id=? AND jobs.company_id=?
    """,(job_id, current_user.actual_id))

    applications=cur.fetchall()
    con.close()

    return render_template("company_view_applications.html",applications=applications,job_id=job_id)

@app.route("/company/update_application_status/<int:application_id>/<string:new_status>", methods=["POST"])
@login_required
def update_application_status(application_id, new_status):
    if current_user.role != "company":
        flash("Unauthorized access")
        return redirect(url_for("login"))

    # Allowed statuses
    allowed_status = ["Shortlisted","Interview","Selected","Rejected","Placed"]

    if new_status not in allowed_status:
        flash("Invalid status update.")
        return redirect(url_for("company_dashboard"))

    con = sqlite3.connect("placement.db")
    cur = con.cursor()

    # SECURITY CHECK:
    # Ensure this application belongs to a job of this company
    cur.execute("""
        SELECT applications.id
        FROM applications
        JOIN jobs ON applications.job_id = jobs.id
        WHERE applications.id = ?
        AND jobs.company_id = ?
    """, (application_id, current_user.actual_id))

    application = cur.fetchone()

    if not application:
        con.close()
        flash("Unauthorized access.")
        return redirect(url_for("company_dashboard"))

    # Update status
    cur.execute("""
        UPDATE applications
        SET status = ?
        WHERE id = ?
    """, (new_status, application_id))

    con.commit()
    con.close()

    flash(f"Application marked as {new_status}.")
    return redirect(request.referrer)

@app.route("/company/shortlisted_candidates")
@login_required
def shortlisted_candidates():
    if current_user.role != "company":
        flash("Unauthorized access")
        return redirect(url_for("login"))

    con = sqlite3.connect("placement.db")
    cur = con.cursor()

    cur.execute("""
        SELECT students.id,
               students.name,
               students.cgpa,
               students.resume_path,
               jobs.title,
               applications.applied_on
        FROM applications
        JOIN students ON applications.student_id = students.id
        JOIN jobs ON applications.job_id = jobs.id
        WHERE jobs.company_id = ?
        AND applications.status = 'Shortlisted'
    """, (current_user.actual_id,))

    candidates = cur.fetchall()
    con.close()

    return render_template(
        "company_shortlisted_candidates.html",
        candidates=candidates
    )

@app.route("/company/application_history")
@login_required
def company_application_history():
    if current_user.role != "company":
        flash("Unauthorized access")
        return redirect(url_for("login"))

    con = sqlite3.connect("placement.db")
    cur = con.cursor()

    cur.execute("""
        SELECT students.name,
               jobs.title,
               applications.status,
               applications.applied_on
        FROM applications
        JOIN students ON applications.student_id = students.id
        JOIN jobs ON applications.job_id = jobs.id
        WHERE jobs.company_id = ?
        ORDER BY applications.applied_on DESC
    """, (current_user.actual_id,))

    applications = cur.fetchall()
    con.close()

    return render_template("company_application_overview.html", applications=applications)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@login_manager.user_loader
def load_user(user_id):
    try:
        # Split 'student-1' into ['student', '1']
        role, actual_id = user_id.split("-")
        return User(int(actual_id), role)
    except (ValueError, AttributeError):
        return None

if __name__=="__main__":
    init_db()
    app.run(port=5000,debug=True)