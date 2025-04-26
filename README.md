# Gamified Learning Environment (GLE) - Quiz Generation Microservice

Welcome to the Quiz Generation Microservice Repository for the Gamified Learning Environment (GLE) project! This microservice handles all quiz creation and management operations, supporting both manual quiz creation and AI-powered quiz generation. See the Frontend and the Project Dissertation for greater details.

## Service Overview
This microservice is designed to provide personalized learning experiences through interactive and highly customizable quizzes. It supports the platform's objective to enhance online learning engagement through intuitive quiz creation and management.

## Features

### Core Quiz Generation Features

1. Dynamic Quiz Generation:
   - Manual quiz creation interface
   - AI-powered quiz generation using OpenAI
   - User-friendly AI prompt engineering system
   - Customizable quiz parameters and settings

2. Quiz Management:
   - Quiz object creation and persistence
   - Session state management
   - Quiz operation and flow control
   - Question bank management

3. Data Management:
   - Quiz data persistence
   - Integration with results tracking
   - Dynamic feedback generation
   - Quiz performance analytics

## Technologies Used

### Backend Framework
- Flask: Python-based RESTful API development
- MongoDB: Document-based storage for quiz data
  - JSON format for quiz structures
  - Key-value pair storage for efficient retrieval
- OpenAI Integration: AI-powered quiz generation

## API Endpoints

The service exposes RESTful endpoints for:
- Quiz creation (manual and AI-generated)
- Quiz management and retrieval
- Session state handling
- Quiz results submission
- Analytics data access

## System Architecture

### Microservice Integration
This service is one of four independent microservices in the GLE platform:
- User Management
- Quiz Generation (This service)
- Results Tracking
- Gamification

## Deployment and Running
While you could download, compile and run each of the repositories for this Final Year Project and get a more in depth look into the code, it is also fully deployed on Railway at the following link : https://exper-frontend-production.up.railway.app

Alternatively, here's a QR Code: 

![ExperQRCode](https://github.com/user-attachments/assets/57795718-9c35-462c-b257-03cf354f5bd4)

Should this not be sufficient for grading, please see the instructions below: 

### Prerequisites
Node.js (v18+) and npm/yarn
Python (v3.9+)
MongoDB database
API keys for:
OpenAI
Anthropic Claude (optional)
Google Gemini (optional)

### Setup and Installation
1. Clone each repository for this project.
2. For each microservice repeat these steps
      1. 
         ```
         cd service-directory  # e.g., Quiz-Generation-FYP
         python -m venv venv
         source venv/bin/activate  # On Windows: venv\Scripts\activate
         pip install -r requirements.txt
         ```
         
      2. Environmental Variables
         Create a .env file in each microservice directory with appropriate values:
         ```
            MONGODB_URI=mongodb://localhost:27017/quizdb
            OPENAI_API_KEY=your_openai_key
            ANTHROPIC_API_KEY=your_anthropic_key  # Optional
            GOOGLE_API_KEY=your_gemini_key  # Optional
         ```
         User Management Service
         ```
         MONGODB_URI=mongodb://localhost:27017/userdb
         JWT_SECRET=your_jwt_secret
         ```

         Results Tracking Service
         ```
         MONGODB_URI=mongodb://localhost:27017/resultsdb
         ```
         Gamification Service
         ```
         MONGODB_URI=mongodb://localhost:27017/gamificationdb
         ```

3. Frontend Setup
      ```
      cd Exper-Frontend/experfrontend
      npm install
      ```
      Create a .env.local file with:
      ```
      NEXT_PUBLIC_USER_SERVICE_URL=http://localhost:8080
      NEXT_PUBLIC_QUIZ_SERVICE_URL=http://localhost:9090
      NEXT_PUBLIC_RESULTS_SERVICE_URL=http://localhost:8081
      NEXT_PUBLIC_GAMIFICATION_SERVICE_URL=http://localhost:8082
      ```

4. Running the Application
   1. Start the microservices, run each in a seperate terminal:
      ```
      # Quiz Generation Service
      cd Quiz-Generation-FYP
      source venv/bin/activate  # On Windows: venv\Scripts\activate
      python app.py  # Will run on port 9090
      
      # User Management Service
      cd User-Management-Service
      source venv/bin/activate
      python app.py  # Will run on port 8080
      
      # Results Tracking Service
      cd Results-Tracking-FYP
      source venv/bin/activate
      python app.py  # Will run on port 8081
      
      # Gamification Service
      cd Gamification-FYP
      source venv/bin/activate
      python app.py  # Will run on port 8082
      ```
   2. Start the Frontend
      ```
      cd Exper-Frontend/experfrontend
      npm run dev
      ```
   Visit http://localhost:3000 to access the application.

  
