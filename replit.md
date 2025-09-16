# Subtitle Viewer

## Overview
A simple web application that displays subtitle (.srt) files in a clean, web-based interface. The application parses SRT subtitle files and presents them in a readable format with timing information.

## Current State
- ✅ Fully functional and running
- ✅ Dependencies installed (Express, OpenAI)
- ✅ Configured for Replit environment
- ✅ Deployment configuration set up

## Project Architecture
- **Backend**: Node.js with Express server on port 5000
- **Frontend**: Server-rendered HTML with inline CSS
- **Data**: SRT subtitle files (en.srt, es.srt)
- **API**: RESTful endpoint at `/api/subtitles` for JSON data

## Key Features
- Displays subtitle files in a clean web interface
- Shows subtitle index, timing, and text
- Provides both HTML view and JSON API
- Responsive design with modern styling
- Error handling for file loading issues

## File Structure
- `server.js` - Main application server
- `package.json` - Node.js dependencies and scripts
- `en.srt` - English subtitle file
- `es.srt` - Spanish subtitle file
- `attached_assets/` - Additional subtitle files

## Configuration
- Server runs on `0.0.0.0:5000` (Replit compatible)
- Trust proxy enabled for Replit environment
- Deployment target: autoscale (stateless web app)

## Recent Changes (2025-09-16)
- Imported from GitHub repository
- Installed Node.js dependencies (Express, OpenAI)
- Verified application functionality
- Configured deployment for Replit autoscale