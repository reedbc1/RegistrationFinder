# Overview

This application is a web-based tool designed for St. Louis County Library staff to streamline patron registration by automatically determining geographic codes and patron types based on street addresses and ZIP codes. The system validates addresses against US Census data and cross-references location information with county-specific databases to determine library eligibility and appropriate patron classifications.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
The application uses a traditional server-rendered web interface built with Flask templates. The frontend consists of three main HTML templates:
- **index.html** - Simple form interface for address input
- **result.html** - Displays lookup results including geographic codes and patron types
- **error.html** - Error handling page for invalid addresses or system failures

The UI follows a clean, responsive design with inline CSS styling focused on usability for library staff.

## Backend Architecture
Built on **Flask** as the primary web framework with a modular design:
- **app.py** - Main Flask application handling routes, request validation, and error handling
- **regfinder.py** - Core business logic module containing address lookup functions
- **wsgi.py** - WSGI entry point for production deployment

The application implements several security measures:
- Request size limiting (10KB maximum)
- Rate limiting (10 requests per minute via Flask-Limiter)
- Input sanitization using MarkupSafe
- ZIP code format validation with regex

## Data Processing Pipeline
The address lookup follows a multi-step validation process:
1. **Address Verification** - Validates input against US Census Bureau geocoding API
2. **Geographic Classification** - Determines county/city from validated address
3. **Patron Type Assignment** - Uses CSV lookup tables to assign appropriate patron types
4. **Special Cases** - Handles St. Louis County (library districts) and Jefferson County (school districts) with specific logic

## Data Storage
The application uses **CSV files** for patron type mappings stored in a `csv_files/` directory:
- **PatronTypes.csv** - Contains mappings between geographic locations and patron type classifications
- Data is loaded into pandas DataFrames for efficient querying and filtering

# External Dependencies

## Third-Party Services
- **US Census Bureau Geocoding API** - Primary address validation service
- **St. Louis County ArcGIS Services** - Geographic data for library district boundaries
  - Address_Points MapServer
  - AGS_Parcels MapServer
- **Jefferson County ArcGIS Services** - School district boundary data

## Hosting and Deployment
- **Render.com** - Cloud hosting platform for production deployment
- **Gunicorn** - Production WSGI server with configuration for 4 workers

## Python Dependencies
- **Flask 3.1.2+** - Web framework
- **pandas 2.2.3** - Data manipulation and CSV processing
- **requests 2.32.3** - HTTP client for external API calls
- **Flask-Limiter 3.9.2** - Rate limiting functionality
- **MarkupSafe** - Input sanitization (Flask dependency)

## External APIs
- **Census Geocoder** (geocoding.geo.census.gov) - Address validation and geographic coordinate resolution
- **St. Louis County GIS Services** - Real-time parcel and address point data
- **Jefferson County GIS Services** - School district boundary information

The architecture prioritizes reliability and data accuracy by using authoritative government data sources while maintaining simple deployment and maintenance requirements.