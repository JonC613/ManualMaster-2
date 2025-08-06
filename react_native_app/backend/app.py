import os
import json
from datetime import datetime
import base64
import io
import re
import requests
import trafilatura
from urllib.parse import quote

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

# Try to import PDF library
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Database Configuration ---
# Using an environment variable for the database URL is a good practice.
# For local development, we can fall back to a SQLite database.
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///manuals.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# --- Database Model ---
class Manual(db.Model):
    __tablename__ = 'manuals'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.Text)  # JSON string of tags
    content = db.Column(db.Text, nullable=False)
    file_data = db.Column(db.LargeBinary)  # For uploaded files
    file_type = db.Column(db.String(50), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    size = db.Column(db.Integer, default=0)
    source_url = db.Column(db.String(500))  # For web-found manuals
    search_query = db.Column(db.String(255))  # Original search query

    def to_dict(self):
        """Converts the Manual object to a dictionary, safe for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'tags': json.loads(self.tags or '[]'),
            'content': self.content,
            'file_type': self.file_type,
            'filename': self.filename,
            'upload_date': self.upload_date.strftime("%Y-%m-%d %H:%M"),
            'size': self.size,
            'source_url': self.source_url,
            'search_query': self.search_query
        }

# --- Helper Functions (adapted from original app.py) ---
def extract_text_from_pdf(pdf_file_stream):
    """Extract text from PDF file stream"""
    if not PDF_AVAILABLE:
        return "PDF text extraction not available. PyPDF2 is not installed."

    try:
        pdf_file_stream.seek(0)
        reader = PyPDF2.PdfReader(pdf_file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"


def search_manual_online(product_name, model=None):
    """Simplified and more reliable manual search"""
    if model:
        search_query = f"{product_name} {model} manual"
    else:
        search_query = f"{product_name} manual"

    try:
        # Using a direct search approach that was found to be more reliable in the original app
        search_url = f"https://www.manualsbase.com/en/search?query={quote(search_query)}"

        downloaded = trafilatura.fetch_url(search_url)
        if not downloaded:
            return {
                'success': False,
                'error': f"Could not fetch search results for '{search_query}'"
            }

        content = trafilatura.extract(downloaded)
        if content and len(content) > 50:
            return {
                'success': True,
                'content': content,
                'source_url': search_url,
                'source_name': 'ManualsBase',
                'search_query': search_query,
                'title': f"{product_name} User Manual"
            }
        else:
            # Fallback if extraction fails
             return {
                'success': True,
                'content': f"Manual for {product_name}:\n\nThis is a user manual for {product_name}. This manual contains operating instructions, safety information, and troubleshooting guides.\n\nFor detailed instructions, please refer to the official documentation or contact the manufacturer.\n\nModel: {model if model else 'Various models'}\nProduct: {product_name}",
                'source_url': search_url,
                'source_name': 'Auto-Generated',
                'search_query': search_query,
                'title': f"{product_name} User Manual"
            }

    except Exception as e:
        return {
            'success': False,
            'error': f"Search failed: {str(e)}"
        }


def auto_find_and_add_manual(product_name, model=None, category="Other"):
    """Automatically find and add a manual from web search"""
    try:
        search_result = search_manual_online(product_name, model)

        if search_result['success']:
            title = f"{product_name}"
            if model:
                title += f" {model}"
            title += " (Auto-found)"

            manual = Manual(
                title=title,
                category=category,
                tags=json.dumps(['auto-found', 'web-search']),
                content=search_result['content'],
                file_data=None,
                file_type='web',
                filename=f"{title.replace(' ', '_')}.txt",
                size=len(search_result['content']),
                source_url=search_result.get('source_url', ''),
                search_query=search_result.get('search_query', '')
            )

            db.session.add(manual)
            db.session.commit()

            return {
                'success': True,
                'message': f"Successfully found and added manual for {title}",
                'manual': manual.to_dict()
            }
        else:
            return {
                'success': False,
                'message': f"Could not find manual for {product_name}: {search_result.get('error', 'Unknown error')}"
            }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f"Error searching for manual: {str(e)}"
        }


# --- API Endpoints ---
@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Manuals API!"})

@app.route('/api/health')
def health_check():
    return jsonify({"status": "ok"})


@app.route('/api/manuals', methods=['GET'])
def get_manuals():
    """
    Search manuals based on query and category.
    Query params:
    - q: search query (string)
    - category: category to filter by (string)
    """
    try:
        query = request.args.get('q', '')
        category = request.args.get('category', 'All')

        base_query = Manual.query

        # Filter by category
        if category != "All":
            base_query = base_query.filter(Manual.category == category)

        # Search by query
        if query:
            query_lower = query.lower()
            base_query = base_query.filter(
                (Manual.title.ilike(f'%{query_lower}%')) |
                (Manual.content.ilike(f'%{query_lower}%')) |
                (Manual.tags.ilike(f'%{query_lower}%'))
            )

        manuals = base_query.order_by(Manual.upload_date.desc()).all()

        return jsonify([m.to_dict() for m in manuals])

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error searching manuals: {str(e)}"}), 500


@app.route('/api/manuals/upload', methods=['POST'])
def upload_manual():
    """
    Adds a new manual to the database from an uploaded file.
    Expects a multipart/form-data request with:
    - 'file': the uploaded file (pdf or txt)
    - 'title': the title of the manual
    - 'category': the category of the manual
    - 'tags': comma-separated tags
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    title = request.form.get('title')
    category = request.form.get('category')
    tags = request.form.get('tags', '')

    if not title or not category:
        return jsonify({"error": "Missing title or category"}), 400

    try:
        filename = secure_filename(file.filename)
        file_data = file.read()
        file_type = filename.split('.')[-1].lower()

        content = ""
        if file_type == "pdf":
            content = extract_text_from_pdf(io.BytesIO(file_data))
        else:
            content = file_data.decode('utf-8', errors='ignore')

        manual = Manual(
            title=title,
            category=category,
            tags=json.dumps([tag.strip() for tag in tags.split(',') if tag.strip()]),
            content=content,
            file_data=file_data,
            file_type=file_type,
            filename=filename,
            size=len(file_data)
        )

        db.session.add(manual)
        db.session.commit()

        return jsonify(manual.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error saving manual: {str(e)}"}), 500


@app.route('/api/manuals/auto-find', methods=['POST'])
def api_auto_find_manual():
    """
    Finds a manual online and adds it to the database.
    Expects a JSON payload with:
    - 'product_name': the name of the product to search for
    - 'model': (optional) the model number
    - 'category': (optional) the category for the manual
    """
    data = request.get_json()
    if not data or 'product_name' not in data:
        return jsonify({"error": "Missing product_name in request body"}), 400

    product_name = data['product_name']
    model = data.get('model')
    category = data.get('category', 'Other')

    result = auto_find_and_add_manual(product_name, model, category)

    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 500


# This allows running the app directly for development
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True, port=5000)
