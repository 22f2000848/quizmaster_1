# =============================================================================
# FILE: forms.py
# PURPOSE: Defines all WTForms form classes for the placement portal
# FORMS: LoginForm, StudentRegistrationForm, CompanyRegistrationForm, 
#        JobPostingForm, ApplicationForm, ProfileUpdateForms
# =============================================================================

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, FloatField, IntegerField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange, ValidationError
from models import User

# =============================================================================
# AUTHENTICATION FORMS
# =============================================================================

class LoginForm(FlaskForm):
    """
    LoginForm - User authentication form
    
    Used for logging in existing users (students, companies, admins).
    Validates email and password credentials.
    
    Fields:
        lf_email: User's email address
        lf_password: User's password
        lf_submit: Form submission button
    """
    
    # lf_email: Email input field with validation
    # validators: Must be provided and must be valid email format
    lf_email = StringField('Email', 
                          validators=[DataRequired(message='Email is required'), 
                                    Email(message='Invalid email address')])
    
    # lf_password: Password input field (masked)
    # validators: Must be provided
    lf_password = PasswordField('Password', 
                               validators=[DataRequired(message='Password is required')])
    
    # lf_submit: Submit button for form
    lf_submit = SubmitField('Login')

class StudentRegistrationForm(FlaskForm):
    """
    StudentRegistrationForm - New student account creation
    
    Comprehensive form for student registration including personal details,
    academic information, and account credentials.
    
    Fields:
        srf_email: Student email (used for login)
        srf_password: Account password
        srf_confirm_pwd: Password confirmation
        srf_full_name: Student's complete name
        srf_college: College/university name
        srf_branch: Academic department
        srf_cgpa: Academic performance
        srf_skills: Technical/soft skills
        srf_submit: Form submission
    """
    
    # srf_email: Email address for login and communication
    # validators: Required, valid email format, unique check in view
    srf_email = StringField('Email Address', 
                           validators=[DataRequired(), Email()])
    
    # srf_password: Password with minimum length requirement
    # validators: Required, minimum 6 characters for security
    srf_password = PasswordField('Password', 
                                validators=[DataRequired(), 
                                          Length(min=6, message='Password must be at least 6 characters')])
    
    # srf_confirm_pwd: Password confirmation field
    # validators: Must match the password field
    srf_confirm_pwd = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), 
                                             EqualTo('srf_password', message='Passwords must match')])
    
    # srf_full_name: Student's complete legal name
    # validators: Required, max 100 characters
    srf_full_name = StringField('Full Name', 
                               validators=[DataRequired(), 
                                         Length(max=100)])
    
    # srf_college: Educational institution name
    # validators: Optional but recommended
    srf_college = StringField('College/University', 
                             validators=[Optional(), Length(max=200)])
    
    # srf_branch: Academic branch/department
    # validators: Optional, max 100 characters
    srf_branch = StringField('Branch/Department', 
                            validators=[Optional(), Length(max=100)])
    
    # srf_cgpa: Cumulative grade point average
    # validators: Optional, must be between 0 and 10 if provided
    srf_cgpa = FloatField('CGPA', 
                         validators=[Optional(), 
                                   NumberRange(min=0, max=10, message='CGPA must be between 0 and 10')])
    
    # srf_skills: Comma-separated list of skills
    # validators: Optional text area for multiple skills
    srf_skills = TextAreaField('Skills (comma-separated)', 
                              validators=[Optional()])
    
    # srf_submit: Submit button
    srf_submit = SubmitField('Register as Student')
    
    def validate_srf_email(self, field):
        """
        validate_srf_email - Custom validator to check email uniqueness
        
        Checks if email already exists in database.
        Raises ValidationError if email is already registered.
        
        Args:
            field: The email field being validated
        """
        # qry_user: Query to find existing user with same email
        qry_user = User.query.filter_by(u_email=field.data).first()
        if qry_user:
            raise ValidationError('Email already registered. Please use a different email or login.')

class CompanyRegistrationForm(FlaskForm):
    """
    CompanyRegistrationForm - New company account creation
    
    Registration form for companies/recruiters to create accounts
    and post job opportunities on the portal.
    
    Fields:
        crf_email: Company contact email
        crf_password: Account password
        crf_confirm_pwd: Password confirmation
        crf_name: Company name
        crf_industry: Business sector
        crf_description: Company details
        crf_website: Company website URL
        crf_submit: Form submission
    """
    
    # crf_email: Company contact email for login
    # validators: Required, valid email format
    crf_email = StringField('Company Email', 
                           validators=[DataRequired(), Email()])
    
    # crf_password: Account password
    # validators: Required, minimum 6 characters
    crf_password = PasswordField('Password', 
                                validators=[DataRequired(), 
                                          Length(min=6, message='Password must be at least 6 characters')])
    
    # crf_confirm_pwd: Password confirmation
    # validators: Must match password field
    crf_confirm_pwd = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), 
                                             EqualTo('crf_password', message='Passwords must match')])
    
    # crf_name: Official company name
    # validators: Required, max 200 characters
    crf_name = StringField('Company Name', 
                          validators=[DataRequired(), Length(max=200)])
    
    # crf_industry: Business industry/sector
    # validators: Optional, max 100 characters
    crf_industry = StringField('Industry', 
                              validators=[Optional(), Length(max=100)])
    
    # crf_description: Detailed company information
    # validators: Optional text area for company profile
    crf_description = TextAreaField('Company Description', 
                                   validators=[Optional()])
    
    # crf_website: Company website URL
    # validators: Optional, max 255 characters
    crf_website = StringField('Website', 
                             validators=[Optional(), Length(max=255)])
    
    # crf_submit: Submit button
    crf_submit = SubmitField('Register as Company')
    
    def validate_crf_email(self, field):
        """
        validate_crf_email - Check email uniqueness
        
        Ensures company email is not already registered.
        
        Args:
            field: The email field being validated
        """
        # qry_user: Check for existing email in database
        qry_user = User.query.filter_by(u_email=field.data).first()
        if qry_user:
            raise ValidationError('Email already registered. Please use a different email or login.')

# =============================================================================
# JOB POSTING FORMS
# =============================================================================

class JobPostingForm(FlaskForm):
    """
    JobPostingForm - Create/edit job postings
    
    Form used by companies to post new job opportunities
    or edit existing job listings.
    
    Fields:
        jpf_title: Job position title
        jpf_description: Detailed job description
        jpf_requirements: Required qualifications
        jpf_salary_min: Minimum salary
        jpf_salary_max: Maximum salary
        jpf_location: Job location
        jpf_deadline: Application deadline
        jpf_submit: Form submission
    """
    
    # jpf_title: Job position title
    # validators: Required, max 200 characters
    jpf_title = StringField('Job Title', 
                           validators=[DataRequired(), Length(max=200)])
    
    # jpf_description: Comprehensive job description
    # validators: Required text area
    jpf_description = TextAreaField('Job Description', 
                                   validators=[DataRequired()])
    
    # jpf_requirements: Required skills and qualifications
    # validators: Optional text area
    jpf_requirements = TextAreaField('Requirements', 
                                    validators=[Optional()])
    
    # jpf_salary_min: Minimum salary offered
    # validators: Optional, must be positive if provided
    jpf_salary_min = IntegerField('Minimum Salary', 
                                 validators=[Optional(), 
                                           NumberRange(min=0, message='Salary must be positive')])
    
    # jpf_salary_max: Maximum salary offered
    # validators: Optional, must be positive if provided
    jpf_salary_max = IntegerField('Maximum Salary', 
                                 validators=[Optional(), 
                                           NumberRange(min=0, message='Salary must be positive')])
    
    # jpf_location: Geographic location of job
    # validators: Optional, max 100 characters
    jpf_location = StringField('Location', 
                              validators=[Optional(), Length(max=100)])
    
    # jpf_deadline: Last date to accept applications
    # validators: Required date field
    jpf_deadline = DateField('Application Deadline', 
                            validators=[DataRequired()], 
                            format='%Y-%m-%d')
    
    # jpf_submit: Submit button
    jpf_submit = SubmitField('Post Job')

# =============================================================================
# APPLICATION FORMS
# =============================================================================

class ApplicationForm(FlaskForm):
    """
    ApplicationForm - Student job application submission
    
    Simple form for students to apply to jobs with optional cover letter.
    
    Fields:
        af_cover_letter: Optional personalized message
        af_submit: Form submission
    """
    
    # af_cover_letter: Optional personalized message to company
    # validators: Optional text area, allows students to explain interest
    af_cover_letter = TextAreaField('Cover Letter (Optional)', 
                                   validators=[Optional()])
    
    # af_submit: Submit button
    af_submit = SubmitField('Submit Application')

# =============================================================================
# PROFILE UPDATE FORMS
# =============================================================================

class StudentProfileUpdateForm(FlaskForm):
    """
    StudentProfileUpdateForm - Update student profile
    
    Allows students to update their profile information
    after registration.
    
    Fields:
        spuf_full_name: Updated name
        spuf_college: Updated college
        spuf_branch: Updated branch
        spuf_cgpa: Updated CGPA
        spuf_skills: Updated skills
        spuf_submit: Form submission
    """
    
    # spuf_full_name: Student's current name
    # validators: Required, max 100 characters
    spuf_full_name = StringField('Full Name', 
                                validators=[DataRequired(), Length(max=100)])
    
    # spuf_college: Current college/university
    # validators: Optional, max 200 characters
    spuf_college = StringField('College/University', 
                              validators=[Optional(), Length(max=200)])
    
    # spuf_branch: Current branch/department
    # validators: Optional, max 100 characters
    spuf_branch = StringField('Branch/Department', 
                             validators=[Optional(), Length(max=100)])
    
    # spuf_cgpa: Current CGPA
    # validators: Optional, range 0-10
    spuf_cgpa = FloatField('CGPA', 
                          validators=[Optional(), 
                                    NumberRange(min=0, max=10, message='CGPA must be between 0 and 10')])
    
    # spuf_skills: Updated skills list
    # validators: Optional text area
    spuf_skills = TextAreaField('Skills (comma-separated)', 
                               validators=[Optional()])
    
    # spuf_submit: Submit button
    spuf_submit = SubmitField('Update Profile')

class CompanyProfileUpdateForm(FlaskForm):
    """
    CompanyProfileUpdateForm - Update company profile
    
    Allows companies to update their profile information.
    
    Fields:
        cpuf_name: Updated company name
        cpuf_industry: Updated industry
        cpuf_description: Updated description
        cpuf_website: Updated website
        cpuf_submit: Form submission
    """
    
    # cpuf_name: Company name
    # validators: Required, max 200 characters
    cpuf_name = StringField('Company Name', 
                           validators=[DataRequired(), Length(max=200)])
    
    # cpuf_industry: Business sector
    # validators: Optional, max 100 characters
    cpuf_industry = StringField('Industry', 
                               validators=[Optional(), Length(max=100)])
    
    # cpuf_description: Company details
    # validators: Optional text area
    cpuf_description = TextAreaField('Company Description', 
                                    validators=[Optional()])
    
    # cpuf_website: Website URL
    # validators: Optional, max 255 characters
    cpuf_website = StringField('Website', 
                              validators=[Optional(), Length(max=255)])
    
    # cpuf_submit: Submit button
    cpuf_submit = SubmitField('Update Profile')
