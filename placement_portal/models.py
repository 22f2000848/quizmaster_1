# =============================================================================
# FILE: models.py
# PURPOSE: Defines all database models for the placement portal application
# MODELS: User, StudentProfile, CompanyProfile, JobPosting, Application
# =============================================================================

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# db: SQLAlchemy database instance - handles all database operations
db = SQLAlchemy()

# =============================================================================
# USER MODEL - Base authentication model for all user types
# =============================================================================

class User(db.Model, UserMixin):
    """
    User Model - Base authentication model for all user types
    
    This model handles the core authentication data for students,
    companies, and administrators. Role-based access is determined
    by the u_role field.
    
    Attributes:
        u_id: Unique identifier for each user (auto-incremented)
        u_email: User's email address (used for login)
        u_pwd_hash: Securely hashed password (never store plain text)
        u_role: User type - 'student', 'company', or 'admin'
        u_created_at: Timestamp when account was created
        u_is_active: Boolean flag to enable/disable accounts
    """
    
    # tbl_name: Specifies the table name in database
    __tablename__ = 'users'
    
    # u_id: Primary key - unique identifier for database operations
    u_id = db.Column(db.Integer, primary_key=True)
    
    # u_email: Stores user email - must be unique across all users
    # Used as the primary login credential
    u_email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    
    # u_pwd_hash: Hashed password using werkzeug security
    # Never stores plain text passwords for security
    u_pwd_hash = db.Column(db.String(256), nullable=False)
    
    # u_role: Defines user type for role-based access control
    # Values: 'student', 'company', 'admin'
    u_role = db.Column(db.String(20), nullable=False)
    
    # u_created_at: Timestamp of account creation
    # Automatically set to current time when record is created
    u_created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # u_is_active: Flag to activate/deactivate user accounts
    # Used by admin to manage user access
    u_is_active = db.Column(db.Boolean, default=True)
    
    # rel_student: One-to-one relationship with StudentProfile
    # backref creates 'student_user' attribute on StudentProfile
    rel_student = db.relationship('StudentProfile', backref='student_user', uselist=False, cascade='all, delete-orphan')
    
    # rel_company: One-to-one relationship with CompanyProfile
    # backref creates 'company_user' attribute on CompanyProfile
    rel_company = db.relationship('CompanyProfile', backref='company_user', uselist=False, cascade='all, delete-orphan')
    
    def get_id(self):
        """
        get_id - Required by Flask-Login for session management
        Returns: String representation of user ID
        """
        return str(self.u_id)
    
    def __repr__(self):
        """String representation of User object for debugging"""
        return f'<User {self.u_email} ({self.u_role})>'

# =============================================================================
# STUDENT PROFILE MODEL - Extended profile for students
# =============================================================================

class StudentProfile(db.Model):
    """
    StudentProfile Model - Stores detailed student information
    
    Extended profile containing academic and personal details for students.
    Linked to User model via foreign key relationship.
    
    Attributes:
        sp_id: Primary key for student profile
        sp_user_id: Foreign key linking to User model
        sp_full_name: Student's complete name
        sp_college: Name of the college/university
        sp_branch: Academic branch/department (e.g., CS, EC, ME)
        sp_cgpa: Cumulative Grade Point Average
        sp_skills: Comma-separated list of skills
        sp_resume_path: File path to uploaded resume
    """
    
    __tablename__ = 'student_profiles'
    
    # sp_id: Primary key for student profile table
    sp_id = db.Column(db.Integer, primary_key=True)
    
    # sp_user_id: Foreign key linking to User.u_id
    # Creates one-to-one relationship with User model
    sp_user_id = db.Column(db.Integer, db.ForeignKey('users.u_id'), nullable=False, unique=True)
    
    # sp_full_name: Stores student's complete name
    sp_full_name = db.Column(db.String(100), nullable=False)
    
    # sp_college: Name of educational institution
    sp_college = db.Column(db.String(200))
    
    # sp_branch: Academic department/specialization
    sp_branch = db.Column(db.String(100))
    
    # sp_cgpa: Academic performance indicator (0.0 to 10.0)
    sp_cgpa = db.Column(db.Float)
    
    # sp_skills: Comma-separated string of technical/soft skills
    # Example: "Python, JavaScript, Communication, Leadership"
    sp_skills = db.Column(db.Text)
    
    # sp_resume_path: File system path to uploaded resume document
    # Stored in UPLOAD_FOLDER defined in config.py
    sp_resume_path = db.Column(db.String(255))
    
    # rel_applications: One-to-many relationship with Application model
    # One student can have multiple job applications
    rel_applications = db.relationship('Application', backref='applicant_student', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        """String representation for debugging"""
        return f'<StudentProfile {self.sp_full_name}>'

# =============================================================================
# COMPANY PROFILE MODEL - Extended profile for companies
# =============================================================================

class CompanyProfile(db.Model):
    """
    CompanyProfile Model - Stores company/recruiter information
    
    Extended profile for companies recruiting through the portal.
    Contains business details and verification status.
    
    Attributes:
        cp_id: Primary key for company profile
        cp_user_id: Foreign key linking to User model
        cp_name: Official company name
        cp_industry: Industry/sector (IT, Manufacturing, etc.)
        cp_description: Detailed company description
        cp_website: Company website URL
        cp_is_verified: Admin approval status
    """
    
    __tablename__ = 'company_profiles'
    
    # cp_id: Primary key for company profile table
    cp_id = db.Column(db.Integer, primary_key=True)
    
    # cp_user_id: Foreign key linking to User.u_id
    # Creates one-to-one relationship with User model
    cp_user_id = db.Column(db.Integer, db.ForeignKey('users.u_id'), nullable=False, unique=True)
    
    # cp_name: Official registered company name
    cp_name = db.Column(db.String(200), nullable=False)
    
    # cp_industry: Business sector/domain
    # Examples: "Information Technology", "Finance", "Healthcare"
    cp_industry = db.Column(db.String(100))
    
    # cp_description: Detailed information about the company
    # Used for company profile page and job listings
    cp_description = db.Column(db.Text)
    
    # cp_website: Company's official website URL
    cp_website = db.Column(db.String(255))
    
    # cp_is_verified: Admin verification flag
    # Companies must be verified before posting jobs
    cp_is_verified = db.Column(db.Boolean, default=False)
    
    # rel_jobs: One-to-many relationship with JobPosting model
    # One company can post multiple job openings
    rel_jobs = db.relationship('JobPosting', backref='posting_company', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        """String representation for debugging"""
        return f'<CompanyProfile {self.cp_name}>'

# =============================================================================
# JOB POSTING MODEL - Job listings by companies
# =============================================================================

class JobPosting(db.Model):
    """
    JobPosting Model - Stores job opening details
    
    Contains all information about job opportunities posted by companies.
    Includes job details, requirements, salary range, and application deadline.
    
    Attributes:
        jp_id: Primary key for job posting
        jp_company_id: Foreign key to CompanyProfile
        jp_title: Job position title
        jp_description: Detailed job description
        jp_requirements: Required qualifications/skills
        jp_salary_min: Minimum salary offered
        jp_salary_max: Maximum salary offered
        jp_location: Job location (city/state)
        jp_deadline: Last date to apply
        jp_is_active: Whether job is currently accepting applications
        jp_created_at: When job was posted
    """
    
    __tablename__ = 'job_postings'
    
    # jp_id: Primary key for job posting table
    jp_id = db.Column(db.Integer, primary_key=True)
    
    # jp_company_id: Foreign key linking to CompanyProfile.cp_id
    # Associates job with the company that posted it
    jp_company_id = db.Column(db.Integer, db.ForeignKey('company_profiles.cp_id'), nullable=False)
    
    # jp_title: Job position name/title
    # Examples: "Software Engineer", "Data Analyst", "Product Manager"
    jp_title = db.Column(db.String(200), nullable=False)
    
    # jp_description: Comprehensive job description
    # Includes responsibilities, work environment, etc.
    jp_description = db.Column(db.Text, nullable=False)
    
    # jp_requirements: Required qualifications and skills
    # Lists education, experience, technical skills needed
    jp_requirements = db.Column(db.Text)
    
    # jp_salary_min: Minimum salary offered (in currency units)
    jp_salary_min = db.Column(db.Integer)
    
    # jp_salary_max: Maximum salary offered (in currency units)
    jp_salary_max = db.Column(db.Integer)
    
    # jp_location: Geographic location of job
    # Format: "City, State" or "Remote"
    jp_location = db.Column(db.String(100))
    
    # jp_deadline: Last date for accepting applications
    # Students cannot apply after this date
    jp_deadline = db.Column(db.Date)
    
    # jp_is_active: Flag to activate/deactivate job posting
    # Companies can close positions early by setting to False
    jp_is_active = db.Column(db.Boolean, default=True)
    
    # jp_created_at: Timestamp when job was posted
    # Automatically set to current time
    jp_created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # rel_applications: One-to-many relationship with Application model
    # One job can receive multiple applications
    rel_applications = db.relationship('Application', backref='job_applied', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        """String representation for debugging"""
        return f'<JobPosting {self.jp_title} by {self.posting_company.cp_name}>'

# =============================================================================
# APPLICATION MODEL - Student job applications
# =============================================================================

class Application(db.Model):
    """
    Application Model - Tracks student applications to jobs
    
    Records all job applications submitted by students.
    Tracks application status through the recruitment process.
    
    Attributes:
        a_id: Primary key for application
        a_student_id: Foreign key to StudentProfile
        a_job_id: Foreign key to JobPosting
        a_status: Current application status
        a_cover_letter: Optional cover letter text
        a_applied_at: Timestamp of application submission
        a_updated_at: Last status update timestamp
    
    Status Flow:
        applied -> reviewing -> shortlisted -> interview -> selected/rejected
    """
    
    __tablename__ = 'applications'
    
    # a_id: Primary key for application table
    a_id = db.Column(db.Integer, primary_key=True)
    
    # a_student_id: Foreign key linking to StudentProfile.sp_id
    # Identifies which student submitted the application
    a_student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.sp_id'), nullable=False)
    
    # a_job_id: Foreign key linking to JobPosting.jp_id
    # Identifies which job the student applied for
    a_job_id = db.Column(db.Integer, db.ForeignKey('job_postings.jp_id'), nullable=False)
    
    # a_status: Current stage of application in recruitment process
    # Possible values: 'applied', 'reviewing', 'shortlisted', 'interview', 'selected', 'rejected'
    a_status = db.Column(db.String(20), default='applied')
    
    # a_cover_letter: Optional personalized message from student
    # Allows students to explain why they're interested in the role
    a_cover_letter = db.Column(db.Text)
    
    # a_applied_at: Timestamp when application was submitted
    # Automatically set to current time on creation
    a_applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # a_updated_at: Timestamp of last status change
    # Updated whenever application status is modified
    a_updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint: Student can only apply once per job
    # Prevents duplicate applications
    __table_args__ = (db.UniqueConstraint('a_student_id', 'a_job_id', name='unique_student_job_application'),)
    
    def __repr__(self):
        """String representation for debugging"""
        return f'<Application {self.a_id}: Student {self.a_student_id} -> Job {self.a_job_id} ({self.a_status})>'
