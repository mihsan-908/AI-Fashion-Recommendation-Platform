# AI Fashion Recommendation Platform

An AI-powered fashion recommendation platform that helps users create personalized outfits based on their gender, occasion, style, season, preferred colors, budget, text requests and uploaded clothing images.

The application uses Google Gemini for fashion understanding and recommendations and Hugging Face for AI-generated outfit visuals.

## Features

- User registration and login
- Personalized fashion recommendations
- Men and women outfit recommendations
- Occasion-based styling
- Style preference selection
- Season selection
- Preferred color selection
- Budget preference
- Clothing image upload and analysis
- AI-generated outfit recommendations
- AI-generated fashion visuals
- Save outfits to a personal collection
- Delete saved outfits
- PostgreSQL database for persistent user and outfit data
- Responsive and modern web interface

## Tech Stack

**Backend**
- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- PostgreSQL

**AI**
- Google Gemini API
- Hugging Face Inference API

**Frontend**
- HTML
- CSS
- JavaScript
- Tailwind CSS
- Lucide Icons

**Other**
- Python-dotenv
- Werkzeug
- Pillow
- Requests

## How It Works

1. The user creates an account or logs in.
2. The user opens the AI Fashion Recommendation Platform.
3. The user provides fashion preferences such as gender, occasion, style, season, preferred colors and budget.
4. The user can also describe what they are looking for or upload a clothing image.
5. Google Gemini analyzes the request and creates a complete outfit recommendation.
6. Hugging Face generates a visual representation of the recommended outfit.
7. The user can review the outfit and save it to their collection.
8. Saved outfits can be viewed or deleted from the Saved Looks page.

## Project Structure

```
AI Fashion Website/
│
├── services/
│   ├── __init__.py
│   └── image_generator.py
│
├── static/
│   ├── generated/
|
├── templates/
│   ├── base.html
│   ├── chat.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── saved.html
│
├── uploads/
├── instance/
├── .gitignore
├── app.py
├── models.py
├── requirements.txt
└── README.md
```

## Requirements

Make sure you have the following installed:

- Python 3.10+
- PostgreSQL
- Git

You also need API credentials for:

- Google Gemini
- Hugging Face

## Installation

**1. Clone the repository**

```
git clone https://github.com/your-username/your-repository.git
cd AI-Fashion-Recommendation-Platform
```

**2. Create a virtual environment**

```
python -m venv venv
```

**3. Activate the virtual environment (Windows PowerShell)**

```
.\venv\Scripts\Activate.ps1
```

**4. Install dependencies**

```
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://postgres:your_password@localhost/fashion_ai
GEMINI_API_KEY=your_gemini_api_key
HF_TOKEN=your_huggingface_token
```

Do not commit the `.env` file to GitHub.

## Database

Create a PostgreSQL database named:

```
fashion_ai
```

The application uses SQLAlchemy to create the required database tables when the application starts.

## Run the Application

Activate the virtual environment and run:

```
python app.py
```

The application will be available at:

```
http://127.0.0.1:5000
```

## Main Application Flow

```
User
  |
  |-- Register / Login
  |
  v
AI Fashion Recommendation Platform
  |
  |-- Select preferences
  |-- Enter fashion request
  |-- Upload clothing image
  |
  v
Google Gemini
  |
  |-- Understands request and creates outfit recommendation
  |
  v
Hugging Face
  |
  |-- Generates outfit visual
  |
  v
User
  |
  |-- View recommendation
  |-- Save outfit
       |
       v
   PostgreSQL
       |
       |-- View saved looks
       |-- Delete saved looks
```

## Security

- Passwords are securely hashed before being stored.
- User sessions are managed with Flask-Login.
- API keys are stored in environment variables.
- User outfits are associated with their individual accounts.
- Users can only delete their own saved outfits.
- Sensitive configuration files are excluded through `.gitignore`.

## AI Architecture

The project separates the AI responsibilities between two services.

**Google Gemini**

Gemini acts as the fashion intelligence layer. It is responsible for:

- Understanding the user's request
- Analyzing uploaded clothing images
- Understanding fashion preferences
- Creating complete outfit recommendations
- Generating structured outfit information

**Hugging Face**

Hugging Face handles the visual generation layer. It is responsible for:

- Generating visual representations of recommended outfits
- Creating full-body fashion visuals
- Rendering the recommended clothing combination

This separation keeps the application simple while allowing each AI service to focus on a specific task.