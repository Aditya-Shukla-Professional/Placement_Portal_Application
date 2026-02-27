import sqlite3
from werkzeug.security import generate_password_hash

# Creating the SQL Tables
connection=sqlite3.connect("placement.db")
cursor=connection.cursor()

# Enabling Foreign key in SQLite
connection.execute("PRAGMA foreign_keys = ON")

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
        hashed_password TEXT NOT NULL,
        resume_path TEXT,
        branch TEXT,
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

# Executing the tables
cursor.execute(adminTable)
cursor.execute(companyTable)
cursor.execute(studentTable)
cursor.execute(jobTable)
cursor.execute(applicationTable)
cursor.execute(placementTable)

# This will create a default admin if no other admin is present
cursor.execute("SELECT id from admin WHERE role='admin' LIMIT 1")
if not cursor.fetchone():
    cursor.execute("INSERT INTO admin (name,email,hashed_password,role) VALUES (?,?,?,?)",
                   ("admin","admin@placement.com",generate_password_hash("admin123"),"admin"))
    connection.commit()

connection.commit()
connection.close()
