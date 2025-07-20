# Nate's Manual App

## Overview

This is a Streamlit-based manual management application that allows users to upload, organize, and search through various types of manuals (appliance, car, tech, etc.). The application provides a simple web interface for document management with categorization and search functionality.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit - A Python-based web framework that creates interactive web apps from Python scripts
- **Layout**: Wide layout with collapsible sidebar for better content viewing
- **State Management**: Streamlit session state for maintaining user data across interactions

### Backend Architecture
- **Language**: Python
- **Framework**: Streamlit (handles both frontend and backend logic)
- **Database**: PostgreSQL with SQLAlchemy ORM for persistent data storage
- **File Processing**: Support for PDF file reading using PyPDF2 or pdfplumber as fallback options
- **Data Storage**: PostgreSQL database for persistent manual storage (replaces session state)

## Key Components

### File Upload and Processing
- PDF file upload capability with fallback library support
- Error handling for missing PDF libraries
- Document parsing and text extraction

### Auto-Find Manual Feature (NEW)
- Web scraping functionality using Trafilatura library
- Automatic manual search from online sources
- Support for product name and model number searches
- Integration with ManualsLib.com for manual content

### Categorization System
- Predefined categories including: Appliance, Car, Tech, Home & Garden, Tools, Electronics, Kitchen, HVAC
- Category-based filtering system
- "All" category for viewing all manuals

### Search Functionality
- Text-based search through manual contents
- Search state persistence across sessions

### Data Management
- Manual storage in session state
- JSON serialization support for data export/import
- Base64 encoding for file handling
- Support for web-sourced manuals (no file data storage)

## Data Flow

1. **Upload**: User uploads PDF files through Streamlit file uploader
2. **Auto-Find**: User searches for manuals automatically via web scraping
3. **Processing**: PDF content is extracted using available PDF libraries OR web content is extracted using Trafilatura
4. **Storage**: Manual data is stored in session state with metadata (title, category, upload date, source URL)
5. **Search/Filter**: Users can search and filter manuals by category or text content
6. **Display**: Manuals are presented in a user-friendly interface with source attribution

## External Dependencies

### Required Libraries
- `streamlit` - Web application framework
- `pandas` - Data manipulation and analysis
- `base64` - File encoding/decoding
- `requests` - HTTP requests for web scraping
- `trafilatura` - Web content extraction and text processing
- `beautifulsoup4` - HTML parsing support
- `psycopg2-binary` - PostgreSQL database adapter
- `sqlalchemy` - ORM for database operations

### Optional Libraries (with fallback handling)
- `PyPDF2` - Primary PDF processing library
- `pdfplumber` - Fallback PDF processing library

### Standard Libraries
- `json` - Data serialization
- `datetime` - Timestamp management
- `io` - Input/output operations
- `re` - Regular expressions for text processing
- `urllib.parse` - URL encoding for search queries

## Deployment Strategy

### Local Development
- Single-file application (`app.py`) for easy deployment
- Streamlit's built-in development server
- No database setup required (uses in-memory storage)

### Production Considerations
- **Data Persistence**: PostgreSQL database ensures data persists across server restarts
- **Scalability**: Single-user sessions with shared database; no user authentication in current architecture
- **File Storage**: Binary files stored in database as BLOB data
- **Database**: Automatic table creation on first run using SQLAlchemy migrations

### Recent Improvements (2025-07-20)
- Implemented PostgreSQL database with SQLAlchemy ORM
- Added persistent storage for manuals and metadata
- Replaced session state with database queries for data retrieval
- Enhanced data integrity with proper database schema
- **Enhanced Manual Search Functionality:**
  - Added URL validation to ensure all found links are accessible
  - Implemented multiple search sources (ManualsLib, Manualzilla, ManualsOnline)
  - Added real-time link validation during manual preview
  - Enhanced content quality assessment and user feedback
  - Improved error handling with specific troubleshooting tips
  - Added suggested alternative search terms for failed searches
  - **New Smart Search Features:**
    - Enhanced query variations with better search patterns
    - Multiple search strategies (Quick, Smart, Preview-only)
    - Instant manual suggestions with popular products
    - Preview-before-save functionality for better user control
    - Improved BeautifulSoup parsing for better manual link detection
    - Support for direct PDF links and manual page links
  - **QR Code Integration:**
    - Added QR code scanning capability for product identification
    - Automatic manual search from scanned QR codes
    - QR code generation for existing manuals
    - Support for product codes, URLs, and custom text in QR codes
    - Smart product information extraction from QR data

### Potential Future Improvements
- Implement user authentication for multi-user support
- Add file system or cloud storage for larger files
- Implement proper error logging and monitoring
- Add database connection pooling for better performance

## Notes

The application is designed as a simple, single-user manual management system with basic CRUD operations. The architecture prioritizes simplicity and ease of deployment over advanced features like user management or persistent storage.