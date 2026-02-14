from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =====================
# MODELS
# =====================

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # admin / student / company
    role = db.Column(db.String(20), nullable=False)

    # company approval
    is_approved = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student_profile = db.relationship(
        "StudentProfile", back_populates="user",
    )
    
    company_profile = db.relationship(
        "CompanyProfile", back_populates="user", 
    )


class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    department = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    resume = db.Column(db.String(200))

    user = db.relationship("User", back_populates="student_profile")
    applications = db.relationship("Application", back_populates="student")


class CompanyProfile(db.Model):
    __tablename__ = "company_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    company_name = db.Column(db.String(150))
    industry = db.Column(db.String(100))
    website = db.Column(db.String(150))

    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    company_size = db.Column(db.String(50))

    user = db.relationship("User", back_populates="company_profile")
    jobs = db.relationship("Job", back_populates="company")


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company_profiles.id"))

    title = db.Column(db.String(150))
    skills = db.Column(db.String(200))
    salary = db.Column(db.String(50))

    is_approved = db.Column(db.Boolean, default=False)
    is_closed = db.Column(db.Boolean, default=False)  # 👈 add this

    company = db.relationship("CompanyProfile", back_populates="jobs")
    applications = db.relationship("Application", back_populates="job")


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"))
    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id"))

    status = db.Column(db.String(50), default="Applied")
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    job = db.relationship("Job", back_populates="applications")
    student = db.relationship("StudentProfile", back_populates="applications")







@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]  # student / company

        # block admin registration
        if role == "admin":
            return "Admin cannot be registered"

        if User.query.filter_by(email=email).first():
            return "Email already registered"

        user = User(
            name=name,
            email=email,
            password=password,
            role=role,
            is_approved=False if role == "company" else True
        )

        db.session.add(user)
        db.session.commit()



        if role == "student":
            return "student dashboard"
        else:
            return "company dashbaord"

    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if not user:
            print('186 line ')
            return "No user found"

        
        if not (user.password, password):
            print(user.password,password)
            return "Wrong password" 
        session["user_id"] = user.id
        session["role"] = user.role
        if user.role == "company" and not user.is_approved:
            return "u are not approved"



        if user.role == "Admin":
            return "admin dashboard"

        elif user.role == "company":
            return "company dashboard"

        else:
            return "student dashboard"

    return render_template("login.html")

# =====================
# RUN
# =====================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        existing_admin = User.query.filter_by(name="admin").first()

        if not existing_admin:

            admin_db = User(
                name = 'admin',
                password ='admin',
                email = 'admin@gmail.com',
                role='Admin'
            )
            db.session.add(admin_db)
            db.session.commit()
    app.run(debug=True)