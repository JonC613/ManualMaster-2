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
- **File Processing**: Support for PDF file reading using PyPDF2 or pdfplumber as fallback options
- **Data Storage**: In-memory storage using Streamlit session state (non-persistent)

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
- **Limitation**: Current implementation uses session state for storage, which means data is not persistent across server restarts
- **Scalability**: Single-user sessions only; no multi-user support in current architecture
- **File Storage**: Files are processed but not permanently stored on disk

### Potential Improvements
- Add persistent database storage (SQLite, PostgreSQL)
- Implement user authentication for multi-user support
- Add file system or cloud storage for uploaded documents
- Implement proper error logging and monitoring

## Notes

The application is designed as a simple, single-user manual management system with basic CRUD operations. The architecture prioritizes simplicity and ease of deployment over advanced features like user management or persistent storage.