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

def search_manual_online(product_name, model=None):
    """Search for manuals online using web scraping"""
    try:
        # Construct search query
        query = f"{product_name} manual"
        if model:
            query += f" {model}"
        
        # Search on ManualsOnline - a reliable source for manuals
        search_url = f"https://www.manualslib.com/search/{quote(query)}"
        
        # Attempt to get manual content
        downloaded = trafilatura.fetch_url(search_url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            return {
                'success': True,
                'content': text[:3000] if text else "No content found",
                'source_url': search_url,
                'search_query': query
            }
        else:
            return {
                'success': False,
                'error': 'Could not fetch search results',
                'search_query': query
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'search_query': query if 'query' in locals() else product_name
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
                'tags': json.loads(manual.tags),
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
                'tags': json.loads(manual.tags) if manual.tags else [],
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
    tab1, tab2, tab3 = st.tabs(["📱 Browse Manuals", "➕ Add Manual", "🔍 Auto-Find Manual"])
    
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
            col1, col2 = st.columns([2, 1])
            
            with col1:
                product_name = st.text_input(
                    "Product Name *",
                    placeholder="e.g., Samsung TV, Toyota Camry, iPhone",
                    help="Enter the product name you need a manual for"
                )
            
            with col2:
                model_number = st.text_input(
                    "Model Number",
                    placeholder="e.g., UN55TU8000",
                    help="Optional: Enter model number for better results"
                )
            
            category = st.selectbox(
                "Category",
                options=[cat for cat in CATEGORIES if cat != "All"],
                index=9,  # Default to "Other" (index 9 in filtered list)
                help="Select the category for this product"
            )
            
            find_button = st.form_submit_button("🔍 Search for Manual", use_container_width=True)
            
            if find_button:
                if product_name.strip():
                    with st.spinner(f"Searching the web for {product_name} manual..."):
                        result = auto_find_and_add_manual(
                            product_name.strip(), 
                            model_number.strip() if model_number.strip() else None,
                            category
                        )
                        
                        if result['success']:
                            st.success(f"✅ {result['message']}")
                            st.balloons()
                            # Show preview of found manual
                            with st.expander("📖 Preview of Found Manual", expanded=True):
                                manual = result['manual']
                                st.write(f"**Title:** {manual['title']}")
                                st.write(f"**Category:** {manual['category']}")
                                st.write(f"**Source:** {manual.get('source_url', 'N/A')}")
                                st.text_area(
                                    "Content Preview:",
                                    manual['content'][:500] + "..." if len(manual['content']) > 500 else manual['content'],
                                    height=200,
                                    disabled=True
                                )
                        else:
                            st.error(f"❌ {result['message']}")
                            st.info("💡 Try different keywords or check the product name spelling.")
                else:
                    st.error("❌ Please enter a product name to search for.")
        
        st.divider()
        
        # Tips for better results
        with st.expander("💡 Tips for Better Search Results"):
            st.markdown("""
            **To get the best results:**
            - Use the exact product name and brand (e.g., "Samsung Galaxy S21" not just "phone")
            - Include model numbers when available
            - Try variations if first search doesn't work
            - Some products may not have manuals available online
            
            **Examples of good searches:**
            - LG 55NANO90UNA TV
            - KitchenAid Stand Mixer KSM150
            - Honda Civic 2020
            """)
    
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
                            db_session.rollback()

if __name__ == "__main__":
    main()
