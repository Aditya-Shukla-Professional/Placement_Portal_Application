import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Creating all the required tables
# Creating admin table
adminTable=""" 
    CREATE TABLE IF NOT EXISTS admin(
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        role TEXT DEFAULT 'admin'
    )
"""

# Creating company table
companyTable="""
    CREATE TABLE IF NOT EXISTS companies(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        hr_contact TEXT NOT NULL,
        website TEXT,
        approval_status TEXT CHECK(approval_status IN ('Pending','Approved','Rejected')) DEFAULT 'Pending' NOT NULL,
        is_blacklisted INTEGER DEFAULT 0 NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""

# Creating student table
studentTable="""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT CHECK(gender in ('Male','Female','Other')) NOT NULL,
        hashed_password TEXT NOT NULL,
        resume_path TEXT,
        skills TEXT,
        branch TEXT NOT NULL,
        cgpa REAL CHECK(cgpa BETWEEN 0 AND 10) DEFAULT 0,
        is_active INTEGER DEFAULT 1 NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""

# Creating job table
jobTable="""
    CREATE TABLE IF NOT EXISTS jobs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        eligibility_criteria TEXT NOT NULL,
        deadline TEXT NOT NULL,
        required_skills TEXT,
        experience_required TEXT,
        salary_range TEXT,
        job_type TEXT CHECK(job_type IN ('Full-time','Internship','Contract')) DEFAULT 'Full-time',
        location TEXT,
        status TEXT CHECK(status in ('Pending','Approved','Closed')) DEFAULT 'Pending' NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES companies(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    )
"""

# Creating application table
applicationTable="""
    CREATE TABLE IF NOT EXISTS applications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        job_id INTEGER NOT NULL,
        applied_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT CHECK(status in ('Applied','Shortlisted','Selected','Rejected')) DEFAULT 'Applied' NOT NULL,
        UNIQUE(student_id, job_id),
        FOREIGN KEY (student_id) REFERENCES students(id)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
        FOREIGN KEY (job_id) REFERENCES jobs(id)
        ON DELETE CASCADE 
        ON UPDATE CASCADE
    )
"""

# Creating placement table
placementTable="""
    CREATE TABLE IF NOT EXISTS placements(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        company_id INTEGER NOT NULL,
        job_id INTEGER NOT NULL,
        salary_package REAL NOT NULL,
        placement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
        FOREIGN KEY (company_id) REFERENCES companies(id)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
        FOREIGN KEY (job_id) REFERENCES jobs(id)
        ON DELETE CASCADE 
        ON UPDATE CASCADE
    )
"""

def init_db():
    connection = sqlite3.connect("placement.db")
    cursor = connection.cursor()

    connection.execute("PRAGMA foreign_keys = ON")

    cursor.execute(adminTable)
    cursor.execute(companyTable)
    cursor.execute(studentTable)
    cursor.execute(jobTable)
    cursor.execute(applicationTable)
    cursor.execute(placementTable)

    cursor.execute("SELECT id FROM admin WHERE role='admin' LIMIT 1")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO admin (name,email,hashed_password,role) VALUES (?,?,?,?)",
            ("admin","admin@placement.com",generate_password_hash("admin123"),"admin")
        )

    connection.commit()
    connection.close()


# Login % Register Logic

# Checking admin,student or company by email and password
def get_user_by_email(email,password):
    con=sqlite3.connect("placement.db")
    cursor=con.cursor()

    # Check Admin
    cursor.execute("SELECT id, hashed_password FROM admin WHERE email=?",(email,))
    admin=cursor.fetchone()
    if admin and check_password_hash(admin[1],password):
        con.close()
        return {"id":admin[0],"role":"admin"}
    
    # Check Student
    cursor.execute("SELECT id, hashed_password, is_active FROM students WHERE email=?",(email,))
    student=cursor.fetchone()
    if student:
        if student[2]==0:
            con.close()
            return {"error":"Student is not Active"}
        if check_password_hash(student[1],password):
            con.close()
            return {"id":student[0],"role":"student"}
    
    # Check Company
    cursor.execute("SELECT id, hashed_password, approval_status, is_blacklisted FROM companies WHERE email=?",(email,))
    company=cursor.fetchone()
    if company:
        if company[3] == 1:
            con.close()
            return {"error": "Company is blacklisted"}
        if company[2]!="Approved":
            con.close()
            return {"error":"Company not approved yet"}
        if check_password_hash(company[1],password):
            con.close()
            return {"id":company[0],"role":"company"}
        con.close()
        return None
    con.close()
    return None
    
# Creating Student
def create_student(name,email,age,gender,password,branch,cgpa):
    try:
        con = sqlite3.connect("placement.db")
        cursor = con.cursor()

        cursor.execute("""
        INSERT INTO students(name,email,age,gender,hashed_password,branch,cgpa)
        VALUES(?,?,?,?,?,?,?)
        """,(name,email,age,gender,generate_password_hash(password),branch,cgpa))

        con.commit()
        con.close()

        return True

    except sqlite3.IntegrityError:
        return False

# Creating Company
def create_company(company_name,email,password,contact,website):
    try:
        con = sqlite3.connect("placement.db")
        cursor = con.cursor()

        cursor.execute("""
        INSERT INTO companies(company_name,email,hashed_password,hr_contact,website)
        VALUES(?,?,?,?,?)
        """,(company_name,email,generate_password_hash(password),contact,website))

        con.commit()
        con.close()

        return True

    except sqlite3.IntegrityError:
        return False