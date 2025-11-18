from fastapi import FastAPI, Request, Form, Depends, Response, status, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import uvicorn
from typing import Optional
from blog_db import SessionLocal, init_db
from blog_models import Article, AdminUser
from passlib.context import CryptContext
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime
from pathlib import Path
from uuid import uuid4

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key='CHANGE_THIS_SECRET_KEY')

app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

init_db()

UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'}


async def save_uploaded_image(file: UploadFile) -> str:
    filename = file.filename or ""
    file_ext = Path(filename).suffix.lower()
    if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError("Invalid file type. Please upload PNG, JPG, JPEG, GIF, WEBP, or SVG.")

    file_bytes = await file.read()
    if not file_bytes:
        raise ValueError("Uploaded file is empty.")

    safe_stem = Path(filename).stem.replace(" ", "_").replace("/", "_")[:50] or "image"
    unique_name = f"{safe_stem}_{uuid4().hex[:8]}{file_ext}"
    file_path = UPLOAD_DIR / unique_name
    with file_path.open("wb") as buffer:
        buffer.write(file_bytes)

    return f"/static/uploads/{unique_name}"


def get_uploaded_images(limit: int = 12):
    if not UPLOAD_DIR.exists():
        return []
    files = sorted(
        [p for p in UPLOAD_DIR.iterdir() if p.is_file()],
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    images = []
    for file_path in files[:limit]:
        images.append({
            "url": f"/static/uploads/{file_path.name}",
            "name": file_path.name
        })
    return images

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def is_logged_in(request: Request) -> bool:
    return request.session.get("admin") is True

@app.get('/', response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    articles = db.query(Article).order_by(Article.date.desc()).all()
    return templates.TemplateResponse('home.html', {"request": request, "articles": articles})

@app.get('/article/{article_id}', response_class=HTMLResponse)
def article_detail(request: Request, article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        return Response(content="Article Not Found", status_code=404)
    return templates.TemplateResponse('article_detail.html', {"request": request, "article": article})

@app.get('/login', response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse('login.html', {"request": request, "error": None})

@app.post('/login', response_class=HTMLResponse)
def login_post(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    error = None
    if user:
        # Try passlib verification first, fallback to bcrypt directly
        try:
            verified = pwd_context.verify(password, user.hashed_password)
        except Exception:
            # Fallback to bcrypt direct verification
            import bcrypt
            password_bytes = password.encode('utf-8')
            hash_bytes = user.hashed_password.encode('utf-8') if isinstance(user.hashed_password, str) else user.hashed_password
            verified = bcrypt.checkpw(password_bytes, hash_bytes)
        
        if verified:
            request.session['admin'] = True
            return RedirectResponse(url="/admin", status_code=302)
    
    if not error:
        error = "Invalid credentials"
    return templates.TemplateResponse('login.html', {"request": request, "error": error})

@app.get('/logout')
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

@app.get('/admin', response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    if not is_logged_in(request):
        return RedirectResponse(url="/login", status_code=302)
    articles = db.query(Article).order_by(Article.date.desc()).all()
    return templates.TemplateResponse('admin_dashboard.html', {"request": request, "articles": articles})

@app.get('/admin/new', response_class=HTMLResponse)
def admin_new_article(request: Request):
    if not is_logged_in(request):
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(
        'admin_article_form.html',
        {"request": request, "article": None, "uploaded_images": get_uploaded_images()}
    )

@app.post('/admin/new', response_class=HTMLResponse)
def admin_create_article(request: Request, title: str = Form(...), summary: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    if not is_logged_in(request):
        return RedirectResponse(url="/login", status_code=302)
    article = Article(title=title, summary=summary, content=content, date=datetime.utcnow())
    db.add(article)
    db.commit()
    return RedirectResponse(url="/admin", status_code=302)

@app.get('/admin/edit/{article_id}', response_class=HTMLResponse)
def admin_edit_article_get(request: Request, article_id: int, db: Session = Depends(get_db)):
    if not is_logged_in(request):
        return RedirectResponse(url="/login", status_code=302)
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        return Response(content="Article Not Found", status_code=404)
    return templates.TemplateResponse(
        'admin_article_form.html',
        {"request": request, "article": article, "uploaded_images": get_uploaded_images()}
    )

@app.post('/admin/edit/{article_id}', response_class=HTMLResponse)
def admin_edit_article_post(request: Request, article_id: int, title: str = Form(...), summary: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    if not is_logged_in(request):
        return RedirectResponse(url="/login", status_code=302)
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        return Response(content="Article Not Found", status_code=404)
    article.title = title
    article.summary = summary
    article.content = content
    db.commit()
    return RedirectResponse(url="/admin", status_code=302)

@app.get('/admin/delete/{article_id}')
def admin_delete_article(request: Request, article_id: int, db: Session = Depends(get_db)):
    if not is_logged_in(request):
        return RedirectResponse(url="/login", status_code=302)
    article = db.query(Article).filter(Article.id == article_id).first()
    if article:
        db.delete(article)
        db.commit()
    return RedirectResponse(url="/admin", status_code=302)

@app.get('/admin/upload', response_class=HTMLResponse)
def admin_upload_get(request: Request):
    if not is_logged_in(request):
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse('admin_upload.html', {"request": request, "message": None, "error": None})

@app.post('/admin/upload', response_class=HTMLResponse)
async def admin_upload_post(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not is_logged_in(request):
        return RedirectResponse(url="/login", status_code=302)
    
    error = None
    message = None
    
    # Check file extension
    allowed_extensions = {'.md', '.txt', '.markdown'}
    file_ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        error = f"Invalid file type. Please upload a .md, .txt, or .markdown file."
        return templates.TemplateResponse('admin_upload.html', {"request": request, "message": None, "error": error})
    
    try:
        # Read file content
        content_bytes = await file.read()
        content_text = content_bytes.decode('utf-8')
        
        # Parse the file content
        # For markdown files, try to extract title from first # heading
        # For text files, use filename as title
        title = None
        summary = None
        content = content_text
        
        if file_ext in {'.md', '.markdown'}:
            # Try to extract title from first # heading
            lines = content_text.split('\n')
            for idx, line in enumerate(lines[:10]):  # Check first 10 lines
                if line.strip().startswith('# '):
                    title = line.strip()[2:].strip()
                    # Remove title from content
                    content = '\n'.join(lines[idx + 1:])
                    break
            
            # If no title found, use filename
            if not title:
                title = file.filename.rsplit('.', 1)[0]
            
            # Extract summary from first paragraph or first few lines
            content_lines = [l.strip() for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]
            if content_lines:
                summary = content_lines[0][:300]
            else:
                summary = "No summary available"
        else:
            # For .txt files, use filename as title
            title = file.filename.rsplit('.', 1)[0]
            # Extract summary from first line or first 300 chars
            first_line = content_text.split('\n')[0].strip()
            summary = first_line[:300] if len(first_line) > 0 else "No summary available"
        
        # Create article
        article = Article(
            title=title,
            summary=summary,
            content=content,
            date=datetime.utcnow()
        )
        db.add(article)
        db.commit()
        
        message = f"Article '{title}' uploaded successfully!"
        
    except UnicodeDecodeError:
        error = "Error reading file. Please ensure the file is UTF-8 encoded."
    except Exception as e:
        error = f"Error processing file: {str(e)}"
    
    return templates.TemplateResponse('admin_upload.html', {"request": request, "message": message, "error": error})

@app.get('/admin/upload-image', response_class=HTMLResponse)
def admin_upload_image_get(request: Request):
    if not is_logged_in(request):
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(
        'admin_image_upload.html',
        {"request": request, "message": None, "error": None, "image_url": None}
    )

@app.post('/admin/upload-image', response_class=HTMLResponse)
async def admin_upload_image_post(request: Request, file: UploadFile = File(...)):
    if not is_logged_in(request):
        return RedirectResponse(url="/login", status_code=302)
    try:
        image_url = await save_uploaded_image(file)
        message = "Image uploaded successfully!"
        return templates.TemplateResponse(
            'admin_image_upload.html',
            {"request": request, "message": message, "error": None, "image_url": image_url}
        )
    except ValueError as exc:
        error = str(exc)
        return templates.TemplateResponse(
            'admin_image_upload.html',
            {"request": request, "message": None, "error": error, "image_url": None}
        )
    except Exception as exc:
        error = f"Error uploading image: {exc}"
        return templates.TemplateResponse(
            'admin_image_upload.html',
            {"request": request, "message": None, "error": error, "image_url": None}
        )


@app.post('/admin/upload-image-inline')
async def admin_upload_image_inline(request: Request, file: UploadFile = File(...)):
    if not is_logged_in(request):
        return JSONResponse(status_code=403, content={"error": "Not authenticated"})
    try:
        image_url = await save_uploaded_image(file)
        return JSONResponse({"image_url": image_url, "message": "Image uploaded successfully."})
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": f"Error uploading image: {exc}"})

if __name__ == "__main__":
    uvicorn.run("blog_main:app", host="127.0.0.1", port=8000, reload=True)
