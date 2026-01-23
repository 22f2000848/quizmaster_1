# =============================================================================
# FILE: config.py
# PURPOSE: Contains all configuration settings for the placement portal application
# USAGE: Imported by app.py to configure Flask app instance
# =============================================================================

import os

class Config:
    """
    Configuration Class - Contains all app settings
    
    This class holds all configuration variables used throughout the application
    including secret keys, database URIs, upload settings, and feature flags.
    """
    
    # sk: Secret key for session encryption and CSRF protection
    # Should be set via environment variable in production for security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'placement_portal_dev_secret_key_2024'
    
    # db_uri: Database connection string for SQLAlchemy
    # Uses SQLite database file stored in instance folder
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'placement_portal.db')
    
    # db_track: Disable modification tracking to save resources
    # SQLAlchemy event system can be resource-intensive if enabled
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # upload_folder: Directory path for storing uploaded files (resumes, documents)
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
    
    # max_file_size: Maximum allowed file size for uploads (5MB in bytes)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    
    # allowed_ext: Permitted file extensions for resume uploads
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    
    # items_per_page: Default number of items shown per page in pagination
    ITEMS_PER_PAGE = 10
    
    # mail_server: Email server configuration for notifications (optional)
    # Configure these if you want to enable email notifications
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # admin_email: Default admin email for system notifications
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@placementportal.com'
