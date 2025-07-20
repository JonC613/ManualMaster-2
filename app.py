import streamlit as st
import pandas as pd
import base64
import json
from datetime import datetime
import io
import re
import requests
import trafilatura
from urllib.parse import quote
import os
import psycopg2
# QR Code functionality (will be checked on demand)
QR_AVAILABLE = None
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Try to import PDF libraries
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    try:
        import pdfplumber
        PDF_AVAILABLE = True
        USE_PDFPLUMBER = True
    except ImportError:
        PDF_AVAILABLE = False
        USE_PDFPLUMBER = False

# Database setup
Base = declarative_base()

class Manual(Base):
    __tablename__ = 'manuals'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    tags = Column(Text)  # JSON string of tags
    content = Column(Text, nullable=False)
    file_data = Column(LargeBinary)  # For uploaded files
    file_type = Column(String(50), nullable=False)
    filename = Column(String(255), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    size = Column(Integer, default=0)
    source_url = Column(String(500))  # For web-found manuals
    search_query = Column(String(255))  # Original search query

# Database connection
@st.cache_resource
def get_database_connection():
    """Get database connection and create tables if they don't exist"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            st.error("Database URL not found. Please check your environment variables.")
            return None
        
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session()
    except Exception as e:
        st.error(f"Database connection failed: {str(e)}")
        return None

# Configure page
st.set_page_config(
    page_title="Nate's Manual App",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

if 'selected_category' not in st.session_state:
    st.session_state.selected_category = "All"

# Initialize database connection
db_session = get_database_connection()

# Predefined categories
CATEGORIES = [
    "All",
    "Appliance", 
    "Car", 
    "Tech", 
    "Home & Garden",
    "Tools",
    "Electronics",
    "Kitchen",
    "HVAC",
    "Plumbing",
    "Other"
]

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    if not PDF_AVAILABLE:
        return "PDF text extraction not available. Please install PyPDF2 or pdfplumber."
    
    try:
        pdf_file.seek(0)
        
        if 'USE_PDFPLUMBER' in globals() and USE_PDFPLUMBER:
            import pdfplumber
            text = ""
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        else:
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

def encode_file_to_base64(file):
    """Encode file to base64 for storage"""
    file.seek(0)
    return base64.b64encode(file.read()).decode()

def decode_base64_to_file(encoded_data, filename):
    """Decode base64 data back to file"""
    decoded_data = base64.b64decode(encoded_data)
    return io.BytesIO(decoded_data)

def validate_url(url):
    """Validate if a URL is accessible and returns content"""
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def check_qr_availability():
    """Check if QR functionality is available"""
    global QR_AVAILABLE
    if QR_AVAILABLE is None:
        try:
            import qrcode
            import cv2
            import numpy as np
            from PIL import Image
            from pyzbar import pyzbar
            QR_AVAILABLE = True
        except ImportError:
            QR_AVAILABLE = False
    return QR_AVAILABLE

def generate_qr_code(data, size=200):
    """Generate QR code for given data"""
    if not check_qr_availability():
        st.error("QR code generation not available. Missing required libraries.")
        return None
    
    import qrcode
    from PIL import Image
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Resize to specified size
    img = img.resize((size, size))
    return img

def decode_qr_from_image(image):
    """Decode QR codes from an uploaded image"""
    if not check_qr_availability():
        st.error("QR code scanning not available. Missing required libraries.")
        return []
    
    try:
        import cv2
        import numpy as np
        from pyzbar import pyzbar
        
        # Convert PIL image to OpenCV format
        img_array = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        if len(img_array.shape) == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Decode QR codes
        decoded_objects = pyzbar.decode(img_array)
        
        results = []
        for obj in decoded_objects:
            data = obj.data.decode('utf-8')
            results.append(data)
        
        return results
    except Exception as e:
        st.error(f"Error decoding QR code: {str(e)}")
        return []

def process_qr_data(qr_data):
    """Process QR code data to extract product information"""
    # Check if it's a URL
    if qr_data.startswith(('http://', 'https://')):
        return {
            'type': 'url',
            'data': qr_data,
            'suggested_search': extract_product_from_url(qr_data)
        }
    
    # Check if it's a product code or model number
    elif re.match(r'^[A-Z0-9\-_]+$', qr_data.upper()):
        return {
            'type': 'product_code',
            'data': qr_data,
            'suggested_search': qr_data
        }
    
    # Check if it contains product information
    else:
        return {
            'type': 'text',
            'data': qr_data,
            'suggested_search': qr_data
        }

def extract_product_from_url(url):
    """Extract potential product information from a URL"""
    try:
        # Simple extraction of product names from common URL patterns
        if 'amazon.com' in url:
            # Extract product name from Amazon URL
            match = re.search(r'/([^/]+)/dp/', url)
            if match:
                return match.group(1).replace('-', ' ')
        
        elif 'support' in url.lower() or 'manual' in url.lower():
            # Extract from support/manual URLs
            parts = url.split('/')
            for part in parts:
                if len(part) > 3 and not part.startswith('www'):
                    return part.replace('-', ' ').replace('_', ' ')
        
        return url.split('/')[-1] if url.split('/')[-1] else 'Product from QR'
    
    except:
        return 'Product from QR'

def search_manual_online(product_name, model=None):
    """Enhanced search for manuals with multiple sources and strategies"""
    search_results = []
    
    # Create multiple query variations for better results
    base_queries = []
    if model:
        base_queries = [
            f"{product_name} {model} manual",
            f"{product_name} {model} user guide", 
            f"{product_name} {model} instruction manual",
            f'"{product_name}" "{model}" manual',
            f"{product_name} {model} owner manual pdf"
        ]
    else:
        base_queries = [
            f"{product_name} manual",
            f"{product_name} user guide",
            f"{product_name} instruction manual",
            f'"{product_name}" manual pdf'
        ]
    
    # Define enhanced search sources with multiple sites
    search_sources = [
        {
            'name': 'ManualsLib',
            'base_url': 'https://www.manualslib.com/search/',
            'type': 'manual_site'
        },
        {
            'name': 'Manualzilla',
            'base_url': 'https://manualzilla.com/search?q=',
            'type': 'manual_site'
        },
        {
            'name': 'ManualsOnline',
            'base_url': 'https://www.manualsonline.com/search?q=',
            'type': 'manual_site'
        }
    ]
    
    # Try each query with each source for maximum coverage
    for query in base_queries[:3]:  # Limit to prevent too many requests
        for source in search_sources:
            try:
                # Build search URL
                search_url = source['base_url'] + quote(query)
                
                # Validate the search URL first
                if not validate_url(search_url):
                    continue
                    
                # Fetch the search page
                downloaded = trafilatura.fetch_url(search_url)
                if not downloaded:
                    continue
                
                # Try to parse with BeautifulSoup for better manual link extraction
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(downloaded, 'html.parser')
                    manual_links = []
                    
                    # Enhanced link finding for different manual sites
                    if 'manualslib' in search_url.lower():
                        # ManualsLib specific patterns
                        for link in soup.find_all('a', href=True):
                            href = link.get('href')
                            if href and isinstance(href, str):
                                if '/manual/' in href or '/view/' in href:
                                    if href.startswith('/'):
                                        href = f"https://www.manualslib.com{href}"
                                    elif not href.startswith('http'):
                                        href = f"https://www.manualslib.com/{href}"
                                    
                                    # Get title from link text or nearby text
                                    title = link.get_text(strip=True)
                                    if not title:
                                        # Try parent or sibling elements for title
                                        parent = link.parent
                                        if parent:
                                            title = parent.get_text(strip=True)[:100]
                                    
                                    if title and len(title) > 10:
                                        manual_links.append({
                                            'url': href,
                                            'title': title,
                                            'source': source['name']
                                        })
                    
                    elif 'manualzilla' in search_url.lower() or 'manualsonline' in search_url.lower():
                        # Generic manual site patterns
                        for link in soup.find_all('a', href=True):
                            href = link.get('href')
                            if href and isinstance(href, str):
                                # Look for PDF links or manual pages
                                if (href.endswith('.pdf') or 
                                    'manual' in href.lower() or 
                                    'download' in href.lower()):
                                    
                                    if not href.startswith('http'):
                                        # Build full URL based on source
                                        if 'manualzilla' in search_url.lower():
                                            href = f"https://manualzilla.com{href}"
                                        elif 'manualsonline' in search_url.lower():
                                            href = f"https://www.manualsonline.com{href}"
                                    
                                    title = link.get_text(strip=True)
                                    if title and len(title) > 8:
                                        manual_links.append({
                                            'url': href,
                                            'title': title,
                                            'source': source['name']
                                        })
                    
                    # Validate and extract content from found manual links
                    for manual in manual_links[:2]:  # Check top 2 results per source
                        if validate_url(manual['url']):
                            try:
                                manual_content = trafilatura.fetch_url(manual['url'])
                                if manual_content:
                                    manual_text = trafilatura.extract(manual_content)
                                    if manual_text and len(manual_text.strip()) > 200:
                                        return {
                                            'success': True,
                                            'content': manual_text[:8000],  # More content
                                            'source_url': manual['url'],
                                            'search_query': query,
                                            'source_name': manual['source'],
                                            'title': manual['title']
                                        }
                            except Exception:
                                continue
                
                except ImportError:
                    # Fallback if BeautifulSoup not available
                    text = trafilatura.extract(downloaded)
                    if text and len(text.strip()) > 100:
                        search_results.append({
                            'success': True,
                            'content': text[:4000],
                            'source_url': search_url,
                            'search_query': query,
                            'source_name': source['name']
                        })
                
                except Exception:
                    continue
                    
            except Exception:
                continue
    
    # Return best result if any found
    if search_results:
        # Prefer results with more content
        best_result = max(search_results, key=lambda x: len(x['content']))
        return best_result
    
    return {
        'success': False,
        'error': 'No valid manual sources found or all links were inaccessible',
        'search_query': query
    }

def auto_find_and_add_manual(product_name, model=None, category="Other"):
    """Automatically find and add a manual from web search"""
    if not db_session:
        return {
            'success': False,
            'message': "Database connection not available"
        }
    
    try:
        # Search for the manual online
        search_result = search_manual_online(product_name, model)
        
        if search_result['success']:
            # Create a manual entry from web search
            title = f"{product_name}"
            if model:
                title += f" {model}"
            title += " (Auto-found)"
            
            manual = Manual(
                title=title,
                category=category,
                tags=json.dumps(['auto-found', 'web-search']),
                content=search_result['content'],
                file_data=None,  # No file data for web-found manuals
                file_type='web',
                filename=f"{title.replace(' ', '_')}.txt",
                size=len(search_result['content']),
                source_url=search_result.get('source_url', ''),
                search_query=search_result.get('search_query', '')
            )
            
            db_session.add(manual)
            db_session.commit()
            
            # Convert to dict for return
            manual_dict = {
                'id': manual.id,
                'title': manual.title,
                'category': manual.category,
                'tags': json.loads(manual.tags or '[]'),
                'content': manual.content,
                'file_type': manual.file_type,
                'filename': manual.filename,
                'upload_date': manual.upload_date.strftime("%Y-%m-%d %H:%M"),
                'size': manual.size,
                'source_url': manual.source_url,
                'search_query': manual.search_query
            }
            
            return {
                'success': True,
                'message': f"Successfully found and added manual for {title}",
                'manual': manual_dict
            }
        else:
            return {
                'success': False,
                'message': f"Could not find manual for {product_name}: {search_result.get('error', 'Unknown error')}"
            }
    except Exception as e:
        db_session.rollback()
        return {
            'success': False,
            'message': f"Error searching for manual: {str(e)}"
        }

def add_manual(title, category, tags, file, file_type):
    """Add a new manual to the database"""
    if not db_session:
        st.error("Database connection not available")
        return False
    
    try:
        # Extract text content
        if file_type == "pdf":
            content = extract_text_from_pdf(file)
        else:
            file.seek(0)
            content = file.read().decode('utf-8', errors='ignore')
        
        # Encode file for storage
        file.seek(0)
        file_data = file.read()
        
        # Create manual entry
        manual = Manual(
            title=title,
            category=category,
            tags=json.dumps([tag.strip() for tag in tags.split(',') if tag.strip()]),
            content=content,
            file_data=file_data,
            file_type=file_type,
            filename=file.name,
            size=len(file_data)
        )
        
        db_session.add(manual)
        db_session.commit()
        return True
    except Exception as e:
        db_session.rollback()
        st.error(f"Error saving manual: {str(e)}")
        return False

def search_manuals(query, category="All"):
    """Search manuals based on query and category"""
    if not db_session:
        return []
    
    try:
        # Start with base query
        base_query = db_session.query(Manual)
        
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
        
        # Get results and convert to dictionaries
        manuals = base_query.all()
        manual_dicts = []
        
        for manual in manuals:
            manual_dict = {
                'id': manual.id,
                'title': manual.title,
                'category': manual.category,
                'tags': json.loads(manual.tags or '[]'),
                'content': manual.content,
                'file_data': manual.file_data,
                'file_type': manual.file_type,
                'filename': manual.filename,
                'upload_date': manual.upload_date.strftime("%Y-%m-%d %H:%M"),
                'size': manual.size,
                'source_url': manual.source_url,
                'search_query': manual.search_query
            }
            manual_dicts.append(manual_dict)
        
        return manual_dicts
    except Exception as e:
        st.error(f"Error searching manuals: {str(e)}")
        return []

def display_manual_card(manual):
    """Display a manual as a card"""
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.subheader(manual['title'])
            st.caption(f"📁 {manual['category']} | 📅 {manual['upload_date']}")
            
            # Display tags
            if manual['tags']:
                tag_str = " ".join([f"#{tag}" for tag in manual['tags']])
                st.text(f"🏷️ {tag_str}")
            
            # Show source URL for web-found manuals
            if manual.get('file_type') == 'web' and manual.get('source_url'):
                st.caption(f"🌐 Source: {manual['source_url']}")
        
        with col2:
            # View button
            if st.button("👁️ View", key=f"view_{manual['id']}"):
                st.session_state[f"viewing_{manual['id']}"] = True
                st.rerun()
        
        with col3:
            # Download button
            if manual.get('file_data'):
                # For uploaded files with binary data
                st.download_button(
                    label="📥 Download",
                    data=manual['file_data'],
                    file_name=manual['filename'],
                    mime="application/pdf" if manual['file_type'] == "pdf" else "text/plain",
                    key=f"download_{manual['id']}"
                )
            else:
                # For web-found manuals, offer to download as text
                st.download_button(
                    label="📥 Download",
                    data=manual['content'],
                    file_name=manual['filename'],
                    mime="text/plain",
                    key=f"download_{manual['id']}"
                )
        
        # Show content if viewing
        if st.session_state.get(f"viewing_{manual['id']}", False):
            with st.expander("📖 Manual Content", expanded=True):
                # Show first 2000 characters with option to show more
                content = manual['content']
                if len(content) > 2000:
                    st.text_area(
                        "Content Preview (first 2000 characters):",
                        content[:2000] + "...\n\n[Content truncated - download file for full content]",
                        height=300,
                        disabled=True,
                        key=f"content_{manual['id']}"
                    )
                else:
                    st.text_area(
                        "Full Content:",
                        content,
                        height=300,
                        disabled=True,
                        key=f"content_{manual['id']}"
                    )
                
                if st.button("✖️ Close", key=f"close_{manual['id']}"):
                    st.session_state[f"viewing_{manual['id']}"] = False
                    st.rerun()
        
        st.divider()

def main():
    # App Header
    st.title("📖 Nate's Manual App")
    st.caption("Upload, organize, and quickly access your instruction manuals")
    
    # Mobile-friendly tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📱 Browse Manuals", "➕ Add Manual", "🔍 Auto-Find Manual", "📱 QR Scanner"])
    
    with tab2:
        st.header("Upload New Manual")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'txt'],
            help="Upload PDF or text files"
        )
        
        if uploaded_file:
            # Manual details form
            with st.form("manual_form"):
                title = st.text_input(
                    "Manual Title",
                    value=uploaded_file.name.rsplit('.', 1)[0],
                    help="Give your manual a descriptive title"
                )
                
                category = st.selectbox(
                    "Category",
                    options=[cat for cat in CATEGORIES if cat != "All"],
                    help="Select the category that best fits your manual"
                )
                
                tags = st.text_input(
                    "Tags (comma-separated)",
                    placeholder="e.g., warranty, troubleshooting, setup",
                    help="Add tags to make your manual easier to find"
                )
                
                submitted = st.form_submit_button("💾 Save Manual")
                
                if submitted:
                    if title.strip():
                        file_type = uploaded_file.name.split('.')[-1].lower()
                        try:
                            success = add_manual(title.strip(), category, tags, uploaded_file, file_type)
                            if success:
                                st.success(f"✅ Manual '{title}' saved successfully!")
                                st.balloons()
                                # Clear the form by switching tabs
                                st.session_state.active_tab = 0
                            else:
                                st.error("❌ Failed to save manual. Please try again.")
                        except Exception as e:
                            st.error(f"❌ Error saving manual: {str(e)}")
                    else:
                        st.error("❌ Please enter a title for your manual.")
    
    with tab3:
        st.header("🔍 Auto-Find Manual")
        st.caption("Let the app search the web for manuals automatically")
        
        with st.form("auto_find_form"):
            # Enhanced input with better layout
            product_name = st.text_input(
                "🔍 Product Name *",
                placeholder="e.g., Samsung UN65TU8000, Honda Civic 2020, iPhone 13 Pro",
                help="Be specific: include brand and model for best results"
            )
            
            col1, col2 = st.columns([1, 1])
            with col1:
                model_number = st.text_input(
                    "📋 Model Number (Optional)",
                    placeholder="e.g., UN65TU8000, KSM150PSER",
                    help="Model numbers greatly improve search accuracy"
                )
            with col2:
                category = st.selectbox(
                    "📁 Category",
                    options=[cat for cat in CATEGORIES if cat != "All"],
                    index=9,  # Default to "Other"
                    help="Select the product category"
                )
            
            # Quick suggestion examples
            st.caption("💡 **Best Results Examples:** Samsung UN65TU8000 • Honda Civic 2020 • KitchenAid KSM150PSER • iPhone 13 Pro")
            
            # Enhanced search options
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                find_button = st.form_submit_button("🔍 Quick Search", use_container_width=True)
            with col2:
                smart_search = st.form_submit_button("🎯 Smart Search", use_container_width=True, help="Try multiple search variations")
            with col3:
                preview_only = st.form_submit_button("👁️ Preview Only", use_container_width=True, help="Find and preview without saving")
            
            if find_button or smart_search or preview_only:
                if product_name.strip():
                    search_type = "Smart Search" if smart_search else "Preview" if preview_only else "Quick Search"
                    with st.spinner(f"{search_type}: Searching for {product_name} manual..."):
                        if preview_only:
                            # Just search without saving
                            search_result = search_manual_online(
                                product_name.strip(),
                                model_number.strip() if model_number.strip() else None
                            )
                            
                            if search_result['success']:
                                st.success("✅ Manual found! Preview below:")
                                with st.expander("📖 Manual Preview", expanded=True):
                                    st.write(f"**Title:** {search_result.get('title', product_name)}")
                                    st.write(f"**Source:** {search_result.get('source_name', 'Unknown')}")
                                    if search_result.get('source_url'):
                                        st.write(f"**Link:** [View Original]({search_result['source_url']})")
                                    
                                    content = search_result['content']
                                    st.text_area(
                                        "Content Preview:",
                                        content[:1000] + "..." if len(content) > 1000 else content,
                                        height=300,
                                        disabled=True
                                    )
                                    
                                    # Option to save after preview
                                    if st.button("💾 Save This Manual", use_container_width=True):
                                        save_result = auto_find_and_add_manual(
                                            product_name.strip(),
                                            model_number.strip() if model_number.strip() else None,
                                            category
                                        )
                                        if save_result['success']:
                                            st.success("✅ Manual saved successfully!")
                                            st.rerun()
                            else:
                                st.error(f"❌ {search_result.get('error', 'No manual found')}")
                        else:
                            # Regular search and save
                            result = auto_find_and_add_manual(
                                product_name.strip(), 
                                model_number.strip() if model_number.strip() else None,
                                category
                            )
                            
                            if result['success']:
                                st.success(f"✅ {result['message']}")
                                st.balloons()
                                # Show preview of found manual with link validation
                                with st.expander("📖 Preview of Found Manual", expanded=True):
                                    manual = result['manual']
                                    st.write(f"**Title:** {manual['title']}")
                                    st.write(f"**Category:** {manual['category']}")
                                    
                                    # Show source with validation status
                                    source_url = manual.get('source_url', 'N/A')
                                    if source_url != 'N/A':
                                        # Validate the link in real-time
                                        with st.spinner("Validating source link..."):
                                            is_valid = validate_url(source_url)
                                        
                                        if is_valid:
                                            st.write(f"**Source:** ✅ [Valid Link]({source_url})")
                                            st.success("Source link is accessible and valid")
                                        else:
                                            st.write(f"**Source:** ❌ Link may be inaccessible")
                                            st.warning("Source link validation failed - content was cached during search")
                                    else:
                                        st.write(f"**Source:** {source_url}")
                                    
                                    # Show source name if available
                                    if manual.get('source_name'):
                                        st.write(f"**Search Engine:** {manual.get('source_name')}")
                                    
                                    st.text_area(
                                        "Content Preview:",
                                        manual['content'][:800] + "..." if len(manual['content']) > 800 else manual['content'],
                                        height=300,
                                        disabled=True
                                    )
                                    
                                    # Show content quality indicators
                                    content_length = len(manual['content'])
                                    if content_length > 1000:
                                        st.info(f"📊 High-quality manual found ({content_length:,} characters)")
                                    elif content_length > 500:
                                        st.info(f"📊 Medium-quality manual found ({content_length:,} characters)")
                                    else:
                                        st.warning(f"📊 Limited content found ({content_length:,} characters) - try different search terms")
                            else:
                                st.error(f"❌ {result['message']}")
                            # Provide more specific guidance based on the error
                            with st.expander("💡 Troubleshooting Tips"):
                                st.markdown("""
                                **If search failed, try these approaches:**
                                - Use the exact brand and model number (e.g., "Samsung UN65TU8000")
                                - Try different variations of the product name
                                - Include words like "user guide" or "instruction manual"
                                - Check if the product name spelling is correct
                                - Some newer products may not have manuals available online yet
                                
                                **Alternative search terms to try:**
                                - Add "PDF" to your search
                                - Try the manufacturer's name + model
                                - Search for "setup guide" instead of "manual"
                                """)
                                
                                # Suggest alternative search terms
                                suggested_terms = []
                                if product_name.strip():
                                    base_name = product_name.strip()
                                    suggested_terms = [
                                        f"{base_name} user guide",
                                        f"{base_name} instruction manual PDF",
                                        f"{base_name} setup guide"
                                    ]
                                    if model_number and model_number.strip():
                                        suggested_terms.append(f"{base_name} {model_number.strip()} manual")
                                    
                                    st.write("**Suggested search terms:**")
                                    for term in suggested_terms[:3]:
                                        st.code(term)
                else:
                    st.error("❌ Please enter a product name to search for.")
        
        st.divider()
        
        # Instant Manual Suggestions
        with st.expander("⚡ Instant Manual Suggestions", expanded=False):
            st.markdown("**Popular Manual Categories:**")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📱 iPhone 13 Pro", key="suggest_iphone"):
                    st.session_state.suggested_product = "iPhone 13 Pro"
                    st.session_state.suggested_model = ""
                    st.session_state.suggested_category = "Electronics"
                if st.button("🏠 Nest Thermostat", key="suggest_nest"):
                    st.session_state.suggested_product = "Google Nest Thermostat"
                    st.session_state.suggested_model = "3rd Gen"
                    st.session_state.suggested_category = "Home & Garden"
            
            with col2:
                if st.button("📺 Samsung TV", key="suggest_samsung"):
                    st.session_state.suggested_product = "Samsung TV"
                    st.session_state.suggested_model = "UN65TU8000"
                    st.session_state.suggested_category = "Electronics"
                if st.button("🚗 Honda Civic", key="suggest_honda"):
                    st.session_state.suggested_product = "Honda Civic"
                    st.session_state.suggested_model = "2020"
                    st.session_state.suggested_category = "Car"
            
            with col3:
                if st.button("🍳 KitchenAid Mixer", key="suggest_kitchenaid"):
                    st.session_state.suggested_product = "KitchenAid Stand Mixer"
                    st.session_state.suggested_model = "KSM150PSER"
                    st.session_state.suggested_category = "Kitchen"
                if st.button("💻 MacBook Pro", key="suggest_macbook"):
                    st.session_state.suggested_product = "MacBook Pro"
                    st.session_state.suggested_model = "M1 13-inch"
                    st.session_state.suggested_category = "Tech"
                    
            if any(key in st.session_state for key in ['suggested_product', 'suggested_model', 'suggested_category']):
                st.info("💡 Suggestion selected! Scroll up to see the filled form.")
                if st.button("🔍 Search Now", use_container_width=True):
                    with st.spinner("Searching for suggested manual..."):
                        result = auto_find_and_add_manual(
                            st.session_state.suggested_product,
                            st.session_state.suggested_model,
                            st.session_state.suggested_category
                        )
                        if result['success']:
                            st.success(f"✅ {result['message']}")
                            st.balloons()
                        else:
                            st.error(f"❌ {result['message']}")
        
        # Tips for better results
        with st.expander("💡 Advanced Search Tips & Link Validation"):
            st.markdown("""
            **Search Strategy for Best Results:**
            - Use exact brand + model (e.g., "Samsung UN65TU8000" not "Samsung TV")
            - Include year for vehicles/appliances (e.g., "Honda Civic 2020")
            - Try manufacturer part numbers when available
            - Search for "user guide" if "manual" doesn't work
            
            **Link Validation Features:**
            - All found links are automatically validated before saving
            - Invalid or broken links are flagged during search
            - Content quality is assessed (character count, completeness)
            - Multiple search sources are tried for better reliability
            
            **Excellent Search Examples:**
            - KitchenAid KSM150PSER Stand Mixer
            - Sony WH-1000XM4 Headphones  
            - Whirlpool WTW5000DW Washer
            - Ford F-150 2021 Owner Manual
            
            **If Search Fails:**
            - Try removing/adding model numbers
            - Use "instruction manual" or "user guide" instead
            - Search without special characters or dashes
            """)
            
            # Show current search sources
            st.write("**Current Search Sources:**")
            st.write("• ManualsLib (primary manual database)")
            st.write("• Google Search (PDF files)")
            st.caption("All sources are validated for accessibility before content extraction.")
    
    with tab1:
        st.header("Your Manuals")
        
        # Search and filter section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_query = st.text_input(
                "🔍 Search manuals",
                value=st.session_state.search_query,
                placeholder="Search by title, tags, or content...",
                key="search_input"
            )
            st.session_state.search_query = search_query
        
        with col2:
            selected_category = st.selectbox(
                "📂 Filter by category",
                options=CATEGORIES,
                index=CATEGORIES.index(st.session_state.selected_category),
                key="category_filter"
            )
            st.session_state.selected_category = selected_category
        
        # Get manuals from database
        filtered_manuals = search_manuals(search_query, selected_category)
        all_manuals = search_manuals("", "All")  # Get all manuals for count
        total_manuals = len(all_manuals)
        
        if total_manuals == 0:
            st.info("📭 No manuals uploaded yet. Use the 'Add Manual' tab to get started!")
        else:
            st.caption(f"Showing {len(filtered_manuals)} of {total_manuals} manuals")
            
            if not filtered_manuals:
                st.warning("🔍 No manuals match your search criteria. Try different keywords or category.")
            else:
                # Sort options
                sort_option = st.radio(
                    "Sort by:",
                    ["📅 Upload Date (Newest)", "📅 Upload Date (Oldest)", "🔤 Title (A-Z)", "🔤 Title (Z-A)"],
                    horizontal=True
                )
                
                # Sort manuals
                if "Newest" in sort_option:
                    filtered_manuals.sort(key=lambda x: x['upload_date'], reverse=True)
                elif "Oldest" in sort_option:
                    filtered_manuals.sort(key=lambda x: x['upload_date'])
                elif "A-Z" in sort_option:
                    filtered_manuals.sort(key=lambda x: x['title'].lower())
                elif "Z-A" in sort_option:
                    filtered_manuals.sort(key=lambda x: x['title'].lower(), reverse=True)
                
                # Display manuals
                for manual in filtered_manuals:
                    display_manual_card(manual)
        
        # Clear all data option (for development/testing)
        if total_manuals > 0:
            with st.expander("⚙️ Advanced Options"):
                if st.button("🗑️ Clear All Manuals", type="secondary"):
                    if st.checkbox("I confirm I want to delete all manuals"):
                        try:
                            if db_session:
                                db_session.query(Manual).delete()
                                db_session.commit()
                                st.success("All manuals cleared!")
                                st.rerun()
                            else:
                                st.error("Database connection not available")
                        except Exception as e:
                            st.error(f"Error clearing manuals: {str(e)}")
                            if db_session:
                                db_session.rollback()
    
    with tab4:
        st.header("📱 QR Code Scanner")
        st.caption("Scan QR codes to automatically find product manuals")
        
        # Check QR availability first
        if not check_qr_availability():
            st.error("🚫 QR Code functionality is not available")
            st.info("💡 QR functionality requires additional system libraries that aren't currently installed.")
            st.markdown("""
            **Available alternatives:**
            - Use the **Auto-Find Manual** tab to search by product name
            - Upload manual files directly in the **Add Manual** tab
            - Try scanning QR codes with your phone and typing the result into Auto-Find
            """)
        else:
            qr_method = st.radio(
                "Choose scanning method:",
                ["📷 Upload QR Image", "🔗 Generate QR for Manual"],
                horizontal=True
            )
            
            if qr_method == "📷 Upload QR Image":
                st.subheader("📷 Upload QR Code Image")
                
                uploaded_qr = st.file_uploader(
                    "Choose QR code image",
                    type=['png', 'jpg', 'jpeg'],
                    help="Upload an image containing a QR code"
                )
            
                if uploaded_qr:
                    # Display the uploaded image
                    from PIL import Image
                    image = Image.open(uploaded_qr)
                
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(image, caption="Uploaded QR Code", width=200)
                    
                    with col2:
                        # Decode QR code
                        with st.spinner("Scanning QR code..."):
                            qr_results = decode_qr_from_image(image)
                        
                        if qr_results:
                            st.success(f"✅ Found {len(qr_results)} QR code(s)")
                            
                            for i, qr_data in enumerate(qr_results):
                                st.write(f"**QR Code {i+1}:**")
                                
                                # Process QR data
                                processed = process_qr_data(qr_data)
                                
                                if processed['type'] == 'url':
                                    st.write(f"🔗 **Link:** {qr_data}")
                                    if st.button(f"🌐 Open Link", key=f"open_{i}"):
                                        st.markdown(f"[Click here to open]({qr_data})")
                                
                                elif processed['type'] == 'product_code':
                                    st.write(f"🏷️ **Product Code:** {qr_data}")
                                
                                else:
                                    st.write(f"📝 **Text:** {qr_data}")
                                
                                # Auto-search option
                                st.write(f"**Suggested Search:** {processed['suggested_search']}")
                                
                                if st.button(f"🔍 Search for Manual", key=f"search_{i}"):
                                    with st.spinner(f"Searching for manual using: {processed['suggested_search']}"):
                                        result = auto_find_and_add_manual(
                                            processed['suggested_search'],
                                            None,
                                            "Other"  # Default category
                                        )
                                        
                                        if result['success']:
                                            st.success(f"✅ {result['message']}")
                                            st.balloons()
                                        else:
                                            st.error(f"❌ {result['message']}")
                                            st.info("💡 Try editing the product name and using the Auto-Find Manual tab")
                                
                                st.divider()
                        
                        else:
                            st.error("❌ No QR code found in the image")
                            st.info("💡 Make sure the QR code is clear and well-lit in the image")
            
            else:  # Generate QR for Manual
                st.subheader("🔗 Generate QR Code for Manual")
            
                # Get list of manuals for QR generation
                manuals = get_all_manuals()
                
                if manuals:
                    manual_options = {f"{manual['title']} ({manual['category']})": manual for manual in manuals}
                
                    selected_manual_name = st.selectbox(
                        "Select manual to generate QR code:",
                        list(manual_options.keys())
                    )
                    
                    if selected_manual_name:
                        selected_manual = manual_options[selected_manual_name]
                        
                        # QR content options
                        qr_content_type = st.radio(
                            "QR Code content:",
                            ["📖 Manual Title", "🏷️ Manual ID", "📝 Custom Text"],
                            horizontal=True
                        )
                        
                        if qr_content_type == "📖 Manual Title":
                            qr_content = selected_manual['title']
                        elif qr_content_type == "🏷️ Manual ID":
                            qr_content = f"MANUAL_ID:{selected_manual['id']}"
                        else:
                            qr_content = st.text_input(
                                "Custom QR content:",
                                value=selected_manual['title'],
                                help="Enter any text to encode in the QR code"
                            )
                        
                        if qr_content:
                            col1, col2 = st.columns([1, 1])
                            
                            with col1:
                                st.write("**QR Code Preview:**")
                                qr_img = generate_qr_code(qr_content, size=250)
                                st.image(qr_img, width=250)
                            
                            with col2:
                                st.write("**QR Code Info:**")
                                st.write(f"**Content:** {qr_content}")
                                st.write(f"**Manual:** {selected_manual['title']}")
                                st.write(f"**Category:** {selected_manual['category']}")
                                
                                # Download QR code
                                import io
                                buffer = io.BytesIO()
                                qr_img.save(buffer, format='PNG')
                                qr_data = buffer.getvalue()
                                
                                st.download_button(
                                    label="📥 Download QR Code",
                                    data=qr_data,
                                    file_name=f"qr_{selected_manual['title'].replace(' ', '_')}.png",
                                    mime="image/png",
                                    use_container_width=True
                                )
                else:
                    st.info("📚 No manuals available. Add some manuals first to generate QR codes.")
        
        # QR Tips
        with st.expander("💡 QR Code Tips & Usage"):
            st.markdown("""
            **Scanning QR Codes:**
            - Take clear, well-lit photos of QR codes
            - Ensure the entire QR code is visible in the image
            - Works with product QR codes, support links, and manual references
            
            **Generating QR Codes:**
            - Share manual information easily with QR codes
            - Print QR codes and attach to physical products
            - Use custom text for special manual references
            
            **Common QR Sources:**
            - Product packaging and labels
            - User manual covers
            - Manufacturer support websites
            - Warranty cards and documentation
            """)

if __name__ == "__main__":
    main()
