MindEase Health

AI-Based Student Mental Wellness Platform (Flask)

 Overview

MindEase Health is a web-based platform designed to support student mental wellbeing through mood tracking, AI-based emotional analysis, and accessible support tools.

The system allows users to monitor their emotional state, reflect on patterns, and take proactive steps toward better mental health.

 Features
 User Authentication (Register / Login / Logout)
 Mood Detection (text-based emotional analysis)
 Dashboard with Statistics & Chart Visualization
 Smart Alert System (detects negative mood patterns)
 Session Booking System
 Wellness Notes (personal reflections)
 Support Resources Page
 Live Demo

   https://temurrr.pythonanywhere.com

 Tech Stack
Backend: Flask (Python)
Frontend: HTML, CSS
Database: SQLite
Visualization: Chart.js
Deployment: PythonAnywhere
 Project Structure
MindEase-Health/
│
├── app.py
├── requirements.txt
├── mood.db
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── mood.html
│   ├── history.html
│   ├── support.html
│   ├── book.html
│   └── notes.html
│
├── static/
│   └── style.css
⚙️ How to Run Locally
Clone the repository:
git clone https://github.com/your-username/MindEase-Health.git
Navigate into the project:
cd MindEase-Health
Install dependencies:
pip install -r requirements.txt
Run the app:
python app.py
Open in browser:
http://127.0.0.1:5000
 Key Functionality
Detects mood using keyword-based analysis
Stores mood history for tracking
Displays insights through charts
Provides recommendations based on emotional state
Alerts users when negative patterns are detected
 Limitations
Basic rule-based mood detection (not full AI model)
SQLite database (not scalable for production)
No real-time therapist integration
 Future Improvements
Machine Learning-based sentiment analysis
Email notifications for bookings
Mobile-responsive enhancements
Cloud database integration 

 Author

Developed as part of a student project in Digital Enterprise / Information Systems.
