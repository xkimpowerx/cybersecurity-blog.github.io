# Cybersecurity Blog

A FastAPI-based blog application with admin functionality, article management, and image upload capabilities.

## Features

- 📝 Article creation, editing, and deletion
- 📤 File upload for articles (Markdown, Text)
- 🖼️ Image upload and management
- 🔐 Admin authentication
- 🎨 Modern cybersecurity-themed UI with scrambled text effects
- 📱 Responsive design

## Requirements

- Python 3.8+
- pip

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd Cursor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create an admin user:
```bash
python3 blog_create_admin.py
```
Enter your desired username and password when prompted.

Alternatively, use command line arguments:
```bash
python3 blog_create_admin.py <username> <password>
```

## Running the Application

Start the development server:
```bash
python3 blog_main.py
```

Or using uvicorn directly:
```bash
uvicorn blog_main:app --host 127.0.0.1 --port 8000 --reload
```

The application will be available at `http://127.0.0.1:8000`

## Usage

### Accessing Admin Panel

Navigate to `http://127.0.0.1:8000/admin` and log in with your admin credentials.

### Creating Articles

1. **Manual Entry**: Go to Admin Dashboard → "Add New Article"
2. **File Upload**: Go to Admin Dashboard → "Upload Article File" (supports .md, .txt, .markdown)
3. **With Images**: Use the "Upload & Insert Image" feature in the article editor

### Image Management

- Upload images via Admin Dashboard → "Upload Image"
- Or use the inline image uploader in the article editor
- Images are stored in `static/uploads/` and accessible at `/static/uploads/<filename>`

## Project Structure

```
.
├── blog_main.py              # Main FastAPI application
├── blog_models.py            # SQLAlchemy models
├── blog_db.py                # Database configuration
├── blog_create_admin.py      # Admin user creation script
├── requirements.txt          # Python dependencies
├── templates/                # Jinja2 templates
│   ├── home.html
│   ├── article_detail.html
│   ├── admin_dashboard.html
│   ├── admin_article_form.html
│   ├── admin_upload.html
│   ├── admin_image_upload.html
│   └── login.html
├── static/                   # Static files
│   ├── style.css
│   ├── scrambled-text.css
│   ├── scrambled-text.js
│   └── uploads/              # Uploaded images
└── blog.db                   # SQLite database (created automatically)
```

## Configuration

- Database: SQLite (default: `blog.db`)
- Session Secret: Change `CHANGE_THIS_SECRET_KEY` in `blog_main.py` for production
- Upload Directory: `static/uploads/` (created automatically)

## Security Notes

⚠️ **Important**: Before deploying to production:

1. Change the session secret key in `blog_main.py`
2. Use a production-grade database (PostgreSQL, MySQL) instead of SQLite
3. Set up proper environment variables for sensitive data
4. Use HTTPS
5. Implement rate limiting
6. Add CSRF protection

## License

This project is open source and available for personal use.

