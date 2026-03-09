<!DOCTYPE html>
<html>

<body>

<h1 align="center">🎓 Placement Portal Application</h1>

<p align="center">
A full-stack web application designed to streamline the campus placement process.
</p>

<p align="center">
<b>Built using Flask, SQLite, Bootstrap, and Jinja2</b>
</p>

<hr>

<h2>📌 Project Overview</h2>

<p>
The <b>Placement Portal Application</b> is a web-based system that simulates a real-world university placement management platform.
It allows students to apply for jobs, companies to post placement drives, and administrators to manage the entire placement workflow.
</p>

<p>
The system ensures secure access through role-based authentication and maintains complete application tracking from submission to final placement.
</p>

<hr>

<h2>🚀 Technologies Used</h2>

<table border="1" cellpadding="10">
<tr>
<th>Category</th>
<th>Technology</th>
</tr>

<tr>
<td>Backend</td>
<td>Python, Flask</td>
</tr>

<tr>
<td>Frontend</td>
<td>HTML, CSS, Bootstrap, Jinja2</td>
</tr>

<tr>
<td>Database</td>
<td>SQLite</td>
</tr>

<tr>
<td>Authentication</td>
<td>Flask-Login</td>
</tr>

<tr>
<td>File Upload</td>
<td>Werkzeug</td>
</tr>

<tr>
<td>Version Control</td>
<td>Git & GitHub</td>
</tr>
</table>

<hr>

<h2>🧩 System Architecture</h2>

<pre>
                +---------------------+
                |        Admin        |
                +---------------------+
                        |
                        | manages
                        ▼
+-------------+     +-------------+     +-------------+
|   Students  | --> | Placement   | <-- |  Companies  |
|             |     |   Portal    |     |             |
+-------------+     +-------------+     +-------------+
       |                    |
       | applies for        | posts
       ▼                    ▼
  Job Applications      Placement Drives
</pre>

<hr>

<h2>👥 User Roles</h2>

<table border="1" cellpadding="10">
<tr>
<th>Role</th>
<th>Description</th>
</tr>

<tr>
<td>Admin</td>
<td>Controls and monitors the entire placement system</td>
</tr>

<tr>
<td>Student</td>
<td>Searches for jobs and applies for placement drives</td>
</tr>

<tr>
<td>Company</td>
<td>Posts job opportunities and evaluates applicants</td>
</tr>
</table>

<hr>

<h2>🔐 Authentication and Security</h2>

<ul>
<li>Role-based access control</li>
<li>Secure login using Flask-Login</li>
<li>Duplicate application prevention</li>
<li>Company approval verification</li>
<li>Student activity validation</li>
<li>Job ownership validation</li>
</ul>

<hr>

<h2>🎓 Student Module</h2>

<p>The student module provides tools for managing the placement journey.</p>

<h3>Features</h3>

<ul>
<li>Register and login</li>
<li>Update profile information</li>
<li>Upload resume</li>
<li>Search placement drives</li>
<li>Apply for jobs</li>
<li>Track application status</li>
<li>View application history</li>
<li>Receive placement notifications</li>
</ul>

<h3>Student Dashboard Displays</h3>

<ul>
<li>Total applications submitted</li>
<li>Shortlisted applications</li>
<li>Selected offers</li>
<li>Rejected applications</li>
<li>Placement notifications</li>
</ul>

<hr>

<h2>🏢 Company Module</h2>

<p>The company module allows organizations to create and manage placement drives.</p>

<h3>Features</h3>

<ul>
<li>Company registration</li>
<li>Admin approval verification</li>
<li>Create job postings</li>
<li>View student applications</li>
<li>Shortlist candidates</li>
<li>Conduct interview stages</li>
<li>Select or reject applicants</li>
<li>View shortlisted candidates</li>
</ul>

<h3>Company Dashboard Displays</h3>

<ul>
<li>Total jobs posted</li>
<li>Active placement drives</li>
<li>Closed placement drives</li>
<li>Total applications received</li>
</ul>

<hr>

<h2>🛠 Admin Module</h2>

<p>The admin panel provides complete control over the placement system.</p>

<h3>Features</h3>

<ul>
<li>Approve or reject companies</li>
<li>Approve or reject job postings</li>
<li>Manage student accounts</li>
<li>Blacklist companies</li>
<li>Deactivate students</li>
<li>Monitor all job postings</li>
<li>Track placement statistics</li>
</ul>

<hr>

<h2>📊 Placement Tracking System</h2>

<p>The system tracks the entire lifecycle of job applications.</p>

<ul>
<li>Applied</li>
<li>Shortlisted</li>
<li>Interview</li>
<li>Selected</li>
<li>Rejected</li>
<li>Placed</li>
</ul>

<p>
Every status update is recorded in the database and displayed on dashboards for students, companies, and administrators.
</p>

<hr>

<h2>🗂 Database Design</h2>

<table border="1" cellpadding="10">
<tr>
<th>Table</th>
<th>Description</th>
</tr>

<tr>
<td>students</td>
<td>Stores student profile information</td>
</tr>

<tr>
<td>companies</td>
<td>Stores company information</td>
</tr>

<tr>
<td>jobs</td>
<td>Stores placement drive details</td>
</tr>

<tr>
<td>applications</td>
<td>Tracks student job applications</td>
</tr>
</table>

<hr>

<h2>📁 Project Structure</h2>

<pre>
Placement_Portal_Application
│
├── app.py
├── database.py
│
├── placement.db
│
├── templates
│   ├── admin_dashboard.html
│   ├── student_dashboard.html
│   ├── company_dashboard.html
│   ├── login.html
│   └── register.html
│
├── static
│   ├── css
│   ├── uploads
│   └── images
│
└── README.md
</pre>

<hr>

<h2>⚙ Installation Guide</h2>

<h3>1. Clone the Repository</h3>

<pre>
git clone https://github.com/yourusername/Placement_Portal_Application.git
</pre>

<h3>2. Navigate to Project Folder</h3>

<pre>
cd Placement_Portal_Application
</pre>

<h3>3. Install Dependencies</h3>

<pre>
pip install flask
pip install flask-login
</pre>

<h3>4. Run the Application</h3>

<pre>
python app.py
</pre>

<h3>5. Open the Application</h3>

<pre>
http://127.0.0.1:5000
</pre>

<hr>

<h2>📈 Future Improvements</h2>

<ul>
<li>Email notification system</li>
<li>Resume parsing</li>
<li>AI-based candidate recommendations</li>
<li>Interview scheduling system</li>
<li>Advanced analytics dashboards</li>
<li>Cloud deployment</li>
</ul>

<hr>

<h2>👨‍💻 Author</h2>

<p>
<b>Aditya Shukla</b><br>
Student – IIT Madras BS Degree Program<br>
Computer Science and Data Science Enthusiast
</p>

<hr>

<p align="center">
⭐ If you found this project useful, consider giving it a star on GitHub.
</p>

</body>
</html>