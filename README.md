# White House Briefing Room News App

A modern web application that scrapes and displays the latest articles from the White House Briefing Room.

## Features

- Automatic scraping of White House Briefing Room articles
- Beautiful Material-UI based interface
- Local storage using SQLite database
- Real-time article refresh functionality
- Responsive design for all devices

## Prerequisites

- Python 3.7+
- Node.js 14+
- npm or yarn

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
```

## Running the Application

1. Start the Flask backend:
```bash
python app.py
```

2. In a new terminal, start the React frontend:
```bash
cd frontend
npm start
```

3. Open your browser and navigate to `http://localhost:3000`

## Usage

- The application will automatically load the latest articles when you first open it
- Click the refresh button in the top-right corner to fetch new articles
- Click "Read More" on any article to view the full article on the White House website

## Technologies Used

- Backend: Flask, SQLAlchemy, BeautifulSoup4
- Frontend: React, Material-UI
- Database: SQLite
- HTTP Client: Axios
