# Placement Portal

A comprehensive web-based **Placement Portal** application designed to facilitate campus placements by connecting students, companies, and administrators. Built with Flask and Bootstrap 5 for a modern, responsive user experience.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [User Roles](#user-roles)
- [Screenshots](#screenshots)
- [Security Features](#security-features)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### For Students
- **User Registration & Authentication**: Secure account creation with email and password
- **Profile Management**: Update personal details, academic information, skills, and resume
- **Job Search & Browse**: Search and filter through active job postings
- **One-Click Applications**: Apply to jobs with optional cover letter
- **Application Tracking**: Monitor application status through the recruitment pipeline
- **Dashboard**: View statistics and recent applications at a glance

### For Companies
- **Company Registration**: Create company profile with verification process
- **Job Posting**: Post unlimited job opportunities with detailed requirements
- **Applicant Management**: View, review, and manage candidate applications
- **Status Updates**: Track candidates through recruitment stages (Applied → Review → Shortlisted → Interview → Selected/Rejected)
- **Dashboard**: Overview of posted jobs, applicants, and shortlisted candidates

### For Administrators
- **Platform Dashboard**: View system-wide statistics and metrics
- **User Management**: Activate/deactivate user accounts
- **Company Verification**: Approve company registrations before job posting
- **Reporting**: Access platform analytics and placement statistics

## 🛠 Tech Stack

### Backend
- **Python 3.8+**
- **Flask 2.3.0** - Web framework
- **SQLAlchemy** - ORM for database operations
- **Flask-Login** - User session management
- **Flask-WTF** - Form handling and validation
- **Werkzeug** - Password hashing and security

### Frontend
- **HTML5 & CSS3**
- **Bootstrap 5** - Responsive design framework
- **Bootstrap Icons** - Icon library
- **JavaScript (Vanilla)** - Client-side interactivity

### Database
- **SQLite** - Development database (easily replaceable with PostgreSQL/MySQL for production)

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step-by-Step Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd placement_portal
```

2. **Create and activate virtual environment**
```bash
# On Linux/Mac
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Initialize the database**
```bash
python app.py
```
This will create the database and add a default admin user.

5. **Run the application**
```bash
python app.py
```

6. **Access the application**
Open your browser and navigate to: `http://localhost:5000`

### Default Credentials

**Admin Account:**
- Email: `admin@placementportal.com`
- Password: `admin123`

⚠️ **Important**: Change the admin password immediately after first login in production!

## 🚀 Usage

### For Students

1. **Register**: Go to `/register` and select "Register as Student"
2. **Complete Profile**: Fill in your academic details, skills, and upload resume
3. **Browse Jobs**: Navigate to "Find Jobs" to see available opportunities
4. **Apply**: Click on jobs of interest and submit applications
5. **Track Progress**: Monitor application status in "My Applications"

### For Companies

1. **Register**: Go to `/register` and select "Register as Company"
2. **Wait for Verification**: Admin must verify your company account
3. **Post Jobs**: Once verified, create job postings from your dashboard
4. **Manage Applications**: Review applicants and update their status
5. **Close Positions**: Deactivate job postings when positions are filled

### For Administrators

1. **Login**: Use admin credentials at `/login`
2. **Verify Companies**: Approve pending company registrations
3. **Manage Users**: Activate/deactivate user accounts as needed
4. **Monitor Platform**: View statistics and overall system health

## 📁 Project Structure

```
placement_portal/
├── app.py                      # Main application entry point
├── config.py                   # Configuration settings
├── models.py                   # Database models (User, Student, Company, Job, Application)
├── forms.py                    # WTForms form classes
├── requirements.txt            # Python dependencies
├── placement_portal.db         # SQLite database (created on first run)
├── static/
│   ├── css/
│   │   └── style.css          # Custom styles and Bootstrap overrides
│   ├── js/
│   │   └── main.js            # Custom JavaScript functionality
│   └── uploads/               # Resume and file uploads directory
├── templates/
│   ├── base.html              # Base template with navigation
│   ├── index.html             # Landing page
│   ├── login.html             # Login page
│   ├── register.html          # Registration selection page
│   ├── student/
│   │   ├── register.html      # Student registration form
│   │   ├── dashboard.html     # Student dashboard
│   │   ├── profile.html       # Profile management
│   │   ├── applications.html  # Application history
│   │   └── apply.html         # Job application form
│   ├── company/
│   │   ├── register.html      # Company registration form
│   │   ├── dashboard.html     # Company dashboard
│   │   ├── post_job.html      # Job posting form
│   │   ├── jobs.html          # Company's job listings
│   │   └── applicants.html    # Applicant management
│   ├── admin/
│   │   ├── dashboard.html     # Admin dashboard
│   │   └── manage_users.html  # User management
│   ├── jobs/
│   │   ├── listings.html      # All job listings
│   │   └── detail.html        # Job detail page
│   └── errors/
│       ├── 404.html           # 404 error page
│       └── 500.html           # 500 error page
└── README.md                   # This file
```

## 👥 User Roles

### Student
- Browse and search job listings
- Apply to jobs with cover letters
- Track application status
- Manage profile and resume

### Company
- Post job opportunities (after verification)
- View and manage applications
- Update candidate status
- Schedule interviews

### Administrator
- Verify company accounts
- Manage all users
- View platform statistics
- Monitor system activity

## 📸 Screenshots

> **Note**: Add screenshots of your application here for better visualization:
> - Landing page
> - Student dashboard
> - Company dashboard
> - Admin dashboard
> - Job listings page
> - Application tracking

## 🔒 Security Features

- **Password Hashing**: All passwords are hashed using Werkzeug's secure hashing
- **CSRF Protection**: All forms include CSRF tokens
- **Session Management**: Secure session handling with Flask-Login
- **Role-Based Access Control**: Decorators enforce access restrictions
- **Input Validation**: Server-side validation on all user inputs
- **SQL Injection Prevention**: SQLAlchemy ORM prevents SQL injection
- **XSS Protection**: Template escaping prevents cross-site scripting

## 🔧 Configuration

### Environment Variables

For production deployment, set these environment variables:

```bash
export SECRET_KEY="your-secret-key-here"
export DATABASE_URL="postgresql://user:password@localhost/dbname"
export FLASK_ENV="production"
```

### Email Configuration (Optional)

To enable email notifications:

```bash
export MAIL_SERVER="smtp.gmail.com"
export MAIL_PORT=587
export MAIL_USE_TLS=True
export MAIL_USERNAME="your-email@gmail.com"
export MAIL_PASSWORD="your-app-password"
```

## 🐛 Troubleshooting

### Common Issues

1. **Database locked error**
   - Close all connections to the database
   - Delete `placement_portal.db` and restart the app

2. **Template not found**
   - Ensure you're running the app from the `placement_portal` directory
   - Check that all template files exist in the correct locations

3. **Port already in use**
   - Change the port in `app.py`: `app.run(port=5001)`

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Code Standards

This project follows specific coding conventions:

- **Variable Naming**: Uses abbreviated/vague variable names with detailed comments
- **Comments**: Extensive inline and block comments for code clarity
- **Documentation**: All functions include docstrings explaining purpose and parameters

Example:
```python
# u_pwd_hash: Stores the securely hashed version of user's password
# using werkzeug's generate_password_hash function
u_pwd_hash = generate_password_hash(pwd)
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- Bootstrap team for the amazing CSS framework
- Flask community for excellent documentation
- All contributors who help improve this project

## 📧 Contact

For questions or support, please contact:
- Email: support@placementportal.com
- GitHub Issues: [Project Issues](https://github.com/yourrepo/placement_portal/issues)

---

**Happy Placement Hunting! 🎓💼**
