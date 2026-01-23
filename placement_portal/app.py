# =============================================================================
# FILE: app.py
# PURPOSE: Main application entry point for the Placement Portal
# DESCRIPTION: Configures Flask app, defines routes, handles authentication
# =============================================================================

import os
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime, date
from config import Config
from models import db, User, StudentProfile, CompanyProfile, JobPosting, Application
from forms import (LoginForm, StudentRegistrationForm, CompanyRegistrationForm,
                   JobPostingForm, ApplicationForm, StudentProfileUpdateForm,
                   CompanyProfileUpdateForm)

# =============================================================================
# APPLICATION SETUP AND CONFIGURATION
# =============================================================================

# app: Flask application instance - main app object
app = Flask(__name__)

# Load configuration from Config class
app.config.from_object(Config)

# db_init: Initialize SQLAlchemy with app
db.init_app(app)

# lm: LoginManager instance for handling user sessions
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'  # Redirect to login page if not authenticated
lm.login_message = 'Please log in to access this page.'
lm.login_message_category = 'info'

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@lm.user_loader
def load_user(user_id):
    """
    load_user - Flask-Login user loader callback
    
    Loads user from database given user ID stored in session.
    Required by Flask-Login for session management.
    
    Args:
        user_id: String user ID from session
        
    Returns:
        User object if found, None otherwise
    """
    # qry_user: Query database for user by ID
    return User.query.get(int(user_id))

# =============================================================================
# CUSTOM DECORATORS FOR ROLE-BASED ACCESS CONTROL
# =============================================================================

def student_required(f):
    """
    student_required - Decorator to restrict access to students only
    
    Wraps route functions to ensure only logged-in students can access.
    Redirects non-students to home page with error message.
    
    Args:
        f: Function to be wrapped
        
    Returns:
        Wrapped function with student access check
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated and has student role
        if not current_user.is_authenticated or current_user.u_role != 'student':
            flash('Access denied. Student access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def company_required(f):
    """
    company_required - Decorator to restrict access to companies only
    
    Ensures only verified company accounts can access certain routes.
    
    Args:
        f: Function to be wrapped
        
    Returns:
        Wrapped function with company access check
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated and has company role
        if not current_user.is_authenticated or current_user.u_role != 'company':
            flash('Access denied. Company access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    admin_required - Decorator to restrict access to admins only
    
    Protects administrative routes from unauthorized access.
    
    Args:
        f: Function to be wrapped
        
    Returns:
        Wrapped function with admin access check
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated and has admin role
        if not current_user.is_authenticated or current_user.u_role != 'admin':
            flash('Access denied. Administrator access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# =============================================================================
# PUBLIC ROUTES - Accessible to all users
# =============================================================================

@app.route('/')
def index():
    """
    index - Landing page route
    
    Displays the homepage with hero section and features overview.
    Redirects authenticated users to their respective dashboards.
    
    Returns:
        Rendered index.html template or redirect to dashboard
    """
    # If user is already logged in, redirect to appropriate dashboard
    if current_user.is_authenticated:
        if current_user.u_role == 'student':
            return redirect(url_for('student_dashboard'))
        elif current_user.u_role == 'company':
            return redirect(url_for('company_dashboard'))
        elif current_user.u_role == 'admin':
            return redirect(url_for('admin_dashboard'))
    
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    login - User authentication route
    
    Handles user login for all user types (student/company/admin).
    Validates credentials and creates session on success.
    
    Returns:
        Login form template or redirect to dashboard on success
    """
    # If already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # frm: LoginForm instance for handling form data
    frm = LoginForm()
    
    if frm.validate_on_submit():
        # Get form data
        email = frm.lf_email.data
        pwd = frm.lf_password.data
        
        # qry_user: Query to find user by email
        qry_user = User.query.filter_by(u_email=email).first()
        
        # Validate user exists and password is correct
        if qry_user and check_password_hash(qry_user.u_pwd_hash, pwd):
            # Check if account is active
            if not qry_user.u_is_active:
                flash('Your account has been deactivated. Please contact admin.', 'danger')
                return redirect(url_for('login'))
            
            # Log user in using Flask-Login
            login_user(qry_user)
            flash('Login successful! Welcome back.', 'success')
            
            # nxt_page: Get the page user was trying to access before login
            nxt_page = request.args.get('next')
            if nxt_page:
                return redirect(nxt_page)
            
            # Redirect based on user role
            if qry_user.u_role == 'student':
                return redirect(url_for('student_dashboard'))
            elif qry_user.u_role == 'company':
                return redirect(url_for('company_dashboard'))
            elif qry_user.u_role == 'admin':
                return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    
    return render_template('login.html', form=frm)

@app.route('/register')
def register():
    """
    register - Registration page selector
    
    Shows options for student or company registration.
    
    Returns:
        Registration selection template
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/register/student', methods=['GET', 'POST'])
def register_student():
    """
    register_student - Student registration route
    
    Handles student account creation with profile details.
    Creates User and StudentProfile records in database.
    
    Returns:
        Student registration form or redirect to login on success
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # frm: StudentRegistrationForm instance
    frm = StudentRegistrationForm()
    
    if frm.validate_on_submit():
        # pwd_hash: Generate secure password hash
        pwd_hash = generate_password_hash(frm.srf_password.data)
        
        # new_user: Create new User record with student role
        new_user = User(
            u_email=frm.srf_email.data,
            u_pwd_hash=pwd_hash,
            u_role='student',
            u_is_active=True
        )
        
        # Add user to session and commit to get user ID
        db.session.add(new_user)
        db.session.commit()
        
        # new_profile: Create StudentProfile linked to new user
        new_profile = StudentProfile(
            sp_user_id=new_user.u_id,
            sp_full_name=frm.srf_full_name.data,
            sp_college=frm.srf_college.data,
            sp_branch=frm.srf_branch.data,
            sp_cgpa=frm.srf_cgpa.data,
            sp_skills=frm.srf_skills.data
        )
        
        db.session.add(new_profile)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('student/register.html', form=frm)

@app.route('/register/company', methods=['GET', 'POST'])
def register_company():
    """
    register_company - Company registration route
    
    Handles company account creation.
    Creates User and CompanyProfile records.
    Companies require admin verification before posting jobs.
    
    Returns:
        Company registration form or redirect to login on success
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # frm: CompanyRegistrationForm instance
    frm = CompanyRegistrationForm()
    
    if frm.validate_on_submit():
        # pwd_hash: Generate secure password hash
        pwd_hash = generate_password_hash(frm.crf_password.data)
        
        # new_user: Create new User record with company role
        new_user = User(
            u_email=frm.crf_email.data,
            u_pwd_hash=pwd_hash,
            u_role='company',
            u_is_active=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # new_profile: Create CompanyProfile linked to new user
        # cp_is_verified set to False - requires admin approval
        new_profile = CompanyProfile(
            cp_user_id=new_user.u_id,
            cp_name=frm.crf_name.data,
            cp_industry=frm.crf_industry.data,
            cp_description=frm.crf_description.data,
            cp_website=frm.crf_website.data,
            cp_is_verified=False
        )
        
        db.session.add(new_profile)
        db.session.commit()
        
        flash('Registration successful! Your account will be verified by admin. Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('company/register.html', form=frm)

@app.route('/logout')
@login_required
def logout():
    """
    logout - User logout route
    
    Logs out current user and clears session.
    
    Returns:
        Redirect to index page
    """
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

# =============================================================================
# STUDENT ROUTES - Protected by student_required decorator
# =============================================================================

@app.route('/student/dashboard')
@login_required
@student_required
def student_dashboard():
    """
    student_dashboard - Student dashboard route
    
    Displays overview of student's applications, upcoming interviews,
    and recent job postings.
    
    Returns:
        Rendered student dashboard template
    """
    # sp: Get StudentProfile for current user
    sp = StudentProfile.query.filter_by(sp_user_id=current_user.u_id).first()
    
    # qry_apps: Get all applications by this student
    qry_apps = Application.query.filter_by(a_student_id=sp.sp_id).order_by(Application.a_applied_at.desc()).all()
    
    # cnt_total: Total applications submitted
    cnt_total = len(qry_apps)
    
    # cnt_pending: Applications still under review
    cnt_pending = len([a for a in qry_apps if a.a_status in ['applied', 'reviewing']])
    
    # cnt_shortlisted: Applications that reached shortlist/interview stage
    cnt_shortlisted = len([a for a in qry_apps if a.a_status in ['shortlisted', 'interview']])
    
    # recent_apps: Last 5 applications for dashboard display
    recent_apps = qry_apps[:5]
    
    return render_template('student/dashboard.html',
                         profile=sp,
                         total_apps=cnt_total,
                         pending_apps=cnt_pending,
                         shortlisted_apps=cnt_shortlisted,
                         recent_applications=recent_apps)

@app.route('/student/profile', methods=['GET', 'POST'])
@login_required
@student_required
def student_profile():
    """
    student_profile - Student profile management route
    
    Allows students to view and update their profile information.
    
    Returns:
        Profile form template or redirect on successful update
    """
    # sp: Get StudentProfile for current user
    sp = StudentProfile.query.filter_by(sp_user_id=current_user.u_id).first()
    
    # frm: StudentProfileUpdateForm instance
    frm = StudentProfileUpdateForm()
    
    if frm.validate_on_submit():
        # Update profile fields from form data
        sp.sp_full_name = frm.spuf_full_name.data
        sp.sp_college = frm.spuf_college.data
        sp.sp_branch = frm.spuf_branch.data
        sp.sp_cgpa = frm.spuf_cgpa.data
        sp.sp_skills = frm.spuf_skills.data
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student_profile'))
    
    # Pre-populate form with current data
    if request.method == 'GET':
        frm.spuf_full_name.data = sp.sp_full_name
        frm.spuf_college.data = sp.sp_college
        frm.spuf_branch.data = sp.sp_branch
        frm.spuf_cgpa.data = sp.sp_cgpa
        frm.spuf_skills.data = sp.sp_skills
    
    return render_template('student/profile.html', form=frm, profile=sp)

@app.route('/student/applications')
@login_required
@student_required
def student_applications():
    """
    student_applications - View all student applications
    
    Shows complete list of applications with status and details.
    
    Returns:
        Applications list template
    """
    # sp: Get StudentProfile for current user
    sp = StudentProfile.query.filter_by(sp_user_id=current_user.u_id).first()
    
    # qry_apps: Get all applications with related job and company info
    qry_apps = Application.query.filter_by(a_student_id=sp.sp_id).order_by(Application.a_applied_at.desc()).all()
    
    return render_template('student/applications.html', applications=qry_apps)

@app.route('/jobs')
@login_required
def job_listings():
    """
    job_listings - Display all active job postings
    
    Shows list of all active jobs with search and filter options.
    Available to students and companies (companies to see competition).
    
    Returns:
        Job listings template
    """
    # search_term: Get search query from URL parameters
    search_term = request.args.get('search', '')
    
    # qry_jobs: Query active jobs, filter by search if provided
    qry_jobs = JobPosting.query.filter_by(jp_is_active=True)
    
    if search_term:
        # Filter by title or location containing search term
        qry_jobs = qry_jobs.filter(
            db.or_(
                JobPosting.jp_title.contains(search_term),
                JobPosting.jp_location.contains(search_term)
            )
        )
    
    # Sort by most recent first
    qry_jobs = qry_jobs.order_by(JobPosting.jp_created_at.desc()).all()
    
    return render_template('jobs/listings.html', jobs=qry_jobs, search=search_term)

@app.route('/jobs/<int:job_id>')
@login_required
def job_detail(job_id):
    """
    job_detail - Display detailed information about a job
    
    Shows full job description, requirements, company info, etc.
    
    Args:
        job_id: ID of the job posting to display
        
    Returns:
        Job detail template or 404 if not found
    """
    # job: Get job posting by ID or return 404
    job = JobPosting.query.get_or_404(job_id)
    
    # has_applied: Check if current student has already applied
    has_applied = False
    if current_user.u_role == 'student':
        sp = StudentProfile.query.filter_by(sp_user_id=current_user.u_id).first()
        if sp:
            existing_app = Application.query.filter_by(a_student_id=sp.sp_id, a_job_id=job_id).first()
            has_applied = existing_app is not None
    
    return render_template('jobs/detail.html', job=job, has_applied=has_applied)

@app.route('/jobs/<int:job_id>/apply', methods=['GET', 'POST'])
@login_required
@student_required
def apply_to_job(job_id):
    """
    apply_to_job - Submit application for a job
    
    Allows students to apply to jobs with optional cover letter.
    
    Args:
        job_id: ID of the job to apply for
        
    Returns:
        Application form or redirect to applications on success
    """
    # job: Get job posting or 404
    job = JobPosting.query.get_or_404(job_id)
    
    # sp: Get current student's profile
    sp = StudentProfile.query.filter_by(sp_user_id=current_user.u_id).first()
    
    # Check if already applied
    existing_app = Application.query.filter_by(a_student_id=sp.sp_id, a_job_id=job_id).first()
    if existing_app:
        flash('You have already applied to this job.', 'warning')
        return redirect(url_for('job_detail', job_id=job_id))
    
    # Check if deadline has passed
    if job.jp_deadline and job.jp_deadline < date.today():
        flash('Application deadline has passed for this job.', 'danger')
        return redirect(url_for('job_detail', job_id=job_id))
    
    # frm: ApplicationForm instance
    frm = ApplicationForm()
    
    if frm.validate_on_submit():
        # new_app: Create new application record
        new_app = Application(
            a_student_id=sp.sp_id,
            a_job_id=job_id,
            a_status='applied',
            a_cover_letter=frm.af_cover_letter.data
        )
        
        db.session.add(new_app)
        db.session.commit()
        
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('student_applications'))
    
    return render_template('student/apply.html', job=job, form=frm)

# =============================================================================
# COMPANY ROUTES - Protected by company_required decorator
# =============================================================================

@app.route('/company/dashboard')
@login_required
@company_required
def company_dashboard():
    """
    company_dashboard - Company dashboard route
    
    Displays company statistics including posted jobs, total applicants,
    and recent applications.
    
    Returns:
        Rendered company dashboard template
    """
    # cp: Get CompanyProfile for current user
    cp = CompanyProfile.query.filter_by(cp_user_id=current_user.u_id).first()
    
    # Check if company is verified
    if not cp.cp_is_verified:
        flash('Your company account is pending verification by admin.', 'warning')
    
    # qry_jobs: Get all jobs posted by this company
    qry_jobs = JobPosting.query.filter_by(jp_company_id=cp.cp_id).all()
    
    # cnt_jobs: Total jobs posted
    cnt_jobs = len(qry_jobs)
    
    # cnt_active: Active jobs currently accepting applications
    cnt_active = len([j for j in qry_jobs if j.jp_is_active])
    
    # cnt_applicants: Total applications across all jobs
    cnt_applicants = 0
    for job in qry_jobs:
        cnt_applicants += Application.query.filter_by(a_job_id=job.jp_id).count()
    
    # cnt_shortlisted: Applications in shortlisted/interview stage
    cnt_shortlisted = 0
    for job in qry_jobs:
        cnt_shortlisted += Application.query.filter_by(a_job_id=job.jp_id).filter(
            Application.a_status.in_(['shortlisted', 'interview'])
        ).count()
    
    # recent_jobs: Last 5 jobs posted
    recent_jobs = JobPosting.query.filter_by(jp_company_id=cp.cp_id).order_by(
        JobPosting.jp_created_at.desc()
    ).limit(5).all()
    
    return render_template('company/dashboard.html',
                         company=cp,
                         total_jobs=cnt_jobs,
                         active_jobs=cnt_active,
                         total_applicants=cnt_applicants,
                         shortlisted=cnt_shortlisted,
                         recent_jobs=recent_jobs)

@app.route('/company/post-job', methods=['GET', 'POST'])
@login_required
@company_required
def company_post_job():
    """
    company_post_job - Post new job opening
    
    Allows verified companies to create new job postings.
    
    Returns:
        Job posting form or redirect to dashboard on success
    """
    # cp: Get CompanyProfile for current user
    cp = CompanyProfile.query.filter_by(cp_user_id=current_user.u_id).first()
    
    # Verify company is approved
    if not cp.cp_is_verified:
        flash('Your company must be verified before posting jobs. Please wait for admin approval.', 'warning')
        return redirect(url_for('company_dashboard'))
    
    # frm: JobPostingForm instance
    frm = JobPostingForm()
    
    if frm.validate_on_submit():
        # new_job: Create new job posting record
        new_job = JobPosting(
            jp_company_id=cp.cp_id,
            jp_title=frm.jpf_title.data,
            jp_description=frm.jpf_description.data,
            jp_requirements=frm.jpf_requirements.data,
            jp_salary_min=frm.jpf_salary_min.data,
            jp_salary_max=frm.jpf_salary_max.data,
            jp_location=frm.jpf_location.data,
            jp_deadline=frm.jpf_deadline.data,
            jp_is_active=True
        )
        
        db.session.add(new_job)
        db.session.commit()
        
        flash('Job posted successfully!', 'success')
        return redirect(url_for('company_dashboard'))
    
    return render_template('company/post_job.html', form=frm)

@app.route('/company/jobs')
@login_required
@company_required
def company_jobs():
    """
    company_jobs - View all company's job postings
    
    Shows list of all jobs posted by the company.
    
    Returns:
        Company jobs list template
    """
    # cp: Get CompanyProfile for current user
    cp = CompanyProfile.query.filter_by(cp_user_id=current_user.u_id).first()
    
    # qry_jobs: Get all jobs for this company
    qry_jobs = JobPosting.query.filter_by(jp_company_id=cp.cp_id).order_by(
        JobPosting.jp_created_at.desc()
    ).all()
    
    return render_template('company/jobs.html', jobs=qry_jobs)

@app.route('/company/jobs/<int:job_id>/applicants')
@login_required
@company_required
def company_applicants(job_id):
    """
    company_applicants - View applicants for a specific job
    
    Shows all applications received for a job with filtering options.
    
    Args:
        job_id: ID of the job to view applicants for
        
    Returns:
        Applicants list template or 404 if job not found
    """
    # job: Get job posting or 404
    job = JobPosting.query.get_or_404(job_id)
    
    # cp: Get current company profile
    cp = CompanyProfile.query.filter_by(cp_user_id=current_user.u_id).first()
    
    # Verify this job belongs to current company
    if job.jp_company_id != cp.cp_id:
        flash('Access denied. This job does not belong to your company.', 'danger')
        return redirect(url_for('company_dashboard'))
    
    # status_filter: Get status filter from URL parameters
    status_filter = request.args.get('status', 'all')
    
    # qry_apps: Get applications for this job
    qry_apps = Application.query.filter_by(a_job_id=job_id)
    
    if status_filter != 'all':
        qry_apps = qry_apps.filter_by(a_status=status_filter)
    
    qry_apps = qry_apps.order_by(Application.a_applied_at.desc()).all()
    
    return render_template('company/applicants.html', job=job, applications=qry_apps, status_filter=status_filter)

@app.route('/company/application/<int:app_id>/update-status', methods=['POST'])
@login_required
@company_required
def company_update_status(app_id):
    """
    company_update_status - Update application status
    
    Allows companies to change status of applications
    (review, shortlist, schedule interview, select, reject).
    
    Args:
        app_id: ID of the application to update
        
    Returns:
        Redirect to applicants page
    """
    # app: Get application or 404
    app = Application.query.get_or_404(app_id)
    
    # Verify application belongs to company's job
    cp = CompanyProfile.query.filter_by(cp_user_id=current_user.u_id).first()
    if app.job_applied.jp_company_id != cp.cp_id:
        flash('Access denied.', 'danger')
        return redirect(url_for('company_dashboard'))
    
    # new_status: Get new status from form
    new_status = request.form.get('status')
    
    # Validate status value
    valid_statuses = ['applied', 'reviewing', 'shortlisted', 'interview', 'selected', 'rejected']
    if new_status in valid_statuses:
        app.a_status = new_status
        app.a_updated_at = datetime.utcnow()
        db.session.commit()
        flash(f'Application status updated to {new_status}.', 'success')
    else:
        flash('Invalid status value.', 'danger')
    
    return redirect(url_for('company_applicants', job_id=app.a_job_id))

@app.route('/company/jobs/<int:job_id>/toggle-active')
@login_required
@company_required
def company_toggle_job(job_id):
    """
    company_toggle_job - Activate/deactivate job posting
    
    Allows companies to close or reopen job postings.
    
    Args:
        job_id: ID of the job to toggle
        
    Returns:
        Redirect to company jobs page
    """
    # job: Get job posting or 404
    job = JobPosting.query.get_or_404(job_id)
    
    # cp: Get current company profile
    cp = CompanyProfile.query.filter_by(cp_user_id=current_user.u_id).first()
    
    # Verify job belongs to this company
    if job.jp_company_id != cp.cp_id:
        flash('Access denied.', 'danger')
        return redirect(url_for('company_dashboard'))
    
    # Toggle active status
    job.jp_is_active = not job.jp_is_active
    db.session.commit()
    
    status = 'activated' if job.jp_is_active else 'deactivated'
    flash(f'Job posting {status} successfully.', 'success')
    
    return redirect(url_for('company_jobs'))

# =============================================================================
# ADMIN ROUTES - Protected by admin_required decorator
# =============================================================================

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """
    admin_dashboard - Administrator dashboard route
    
    Displays platform-wide statistics and pending approvals.
    
    Returns:
        Rendered admin dashboard template
    """
    # cnt_students: Total registered students
    cnt_students = StudentProfile.query.count()
    
    # cnt_companies: Total registered companies
    cnt_companies = CompanyProfile.query.count()
    
    # cnt_verified: Verified companies
    cnt_verified = CompanyProfile.query.filter_by(cp_is_verified=True).count()
    
    # cnt_pending: Companies pending verification
    cnt_pending = CompanyProfile.query.filter_by(cp_is_verified=False).count()
    
    # cnt_jobs: Total job postings
    cnt_jobs = JobPosting.query.count()
    
    # cnt_active_jobs: Active job postings
    cnt_active_jobs = JobPosting.query.filter_by(jp_is_active=True).count()
    
    # cnt_applications: Total applications submitted
    cnt_applications = Application.query.count()
    
    # pending_companies: List of companies awaiting verification
    pending_companies = CompanyProfile.query.filter_by(cp_is_verified=False).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_students=cnt_students,
                         total_companies=cnt_companies,
                         verified_companies=cnt_verified,
                         pending_companies_count=cnt_pending,
                         total_jobs=cnt_jobs,
                         active_jobs=cnt_active_jobs,
                         total_applications=cnt_applications,
                         pending_companies=pending_companies)

@app.route('/admin/users')
@login_required
@admin_required
def admin_manage_users():
    """
    admin_manage_users - User management page
    
    Shows all users with ability to activate/deactivate accounts.
    
    Returns:
        User management template
    """
    # role_filter: Get role filter from URL parameters
    role_filter = request.args.get('role', 'all')
    
    # qry_users: Get users based on filter
    qry_users = User.query
    
    if role_filter != 'all':
        qry_users = qry_users.filter_by(u_role=role_filter)
    
    qry_users = qry_users.order_by(User.u_created_at.desc()).all()
    
    return render_template('admin/manage_users.html', users=qry_users, role_filter=role_filter)

@app.route('/admin/users/<int:user_id>/toggle-active')
@login_required
@admin_required
def admin_toggle_user(user_id):
    """
    admin_toggle_user - Activate/deactivate user account
    
    Args:
        user_id: ID of the user to toggle
        
    Returns:
        Redirect to user management page
    """
    # user: Get user or 404
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deactivating themselves
    if user.u_id == current_user.u_id:
        flash('You cannot deactivate your own account.', 'warning')
        return redirect(url_for('admin_manage_users'))
    
    # Toggle active status
    user.u_is_active = not user.u_is_active
    db.session.commit()
    
    status = 'activated' if user.u_is_active else 'deactivated'
    flash(f'User account {status} successfully.', 'success')
    
    return redirect(url_for('admin_manage_users'))

@app.route('/admin/companies/<int:company_id>/verify')
@login_required
@admin_required
def admin_verify_company(company_id):
    """
    admin_verify_company - Verify company account
    
    Approves company to post jobs on the platform.
    
    Args:
        company_id: ID of the company to verify
        
    Returns:
        Redirect to dashboard
    """
    # cp: Get company profile or 404
    cp = CompanyProfile.query.get_or_404(company_id)
    
    # Set verified status
    cp.cp_is_verified = True
    db.session.commit()
    
    flash(f'Company "{cp.cp_name}" has been verified successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found_error(error):
    """
    not_found_error - 404 error handler
    
    Displays custom 404 page when route is not found.
    
    Args:
        error: Error object
        
    Returns:
        404 error template with 404 status code
    """
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """
    internal_error - 500 error handler
    
    Displays custom 500 page on server errors.
    Rolls back database session to prevent corruption.
    
    Args:
        error: Error object
        
    Returns:
        500 error template with 500 status code
    """
    # Rollback any failed database transactions
    db.session.rollback()
    return render_template('errors/500.html'), 500

# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

def init_db():
    """
    init_db - Initialize database and create tables
    
    Creates all database tables and adds default admin user
    if not already present.
    """
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin_user = User.query.filter_by(u_email='admin@placementportal.com').first()
        
        if not admin_user:
            # Create default admin account
            admin_pwd = generate_password_hash('admin123')
            admin_user = User(
                u_email='admin@placementportal.com',
                u_pwd_hash=admin_pwd,
                u_role='admin',
                u_is_active=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print('Default admin user created: admin@placementportal.com / admin123')

# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    
    # Run Flask development server
    # debug: Enable debug mode for development (set to False in production)
    app.run(debug=True, host='0.0.0.0', port=5000)
