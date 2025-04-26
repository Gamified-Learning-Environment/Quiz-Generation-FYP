# Gamified Learning Environment (GLE) - Quiz Generation Microservice

Welcome to the Quiz Generation Microservice Repository for the Gamified Learning Environment (GLE) project! This microservice handles all quiz creation and management operations, supporting both manual quiz creation and AI-powered quiz generation. See the Frontend and the Project Dissertation for greater details.

## Service Overview
This microservice is designed to provide personalized learning experiences through interactive and highly customizable quizzes. It supports the platform's objective to enhance online learning engagement through intuitive quiz creation and management.
The Quiz Generation microservice is the core for creating quizzes, managing them and delivering them to users. It supports both manual quiz question creation and AI powered generation through the use of APIs. This hopefully makes it flexible in its implementation. It possesses the ability to generate quizzes from either Open AI's Chatgpt, Anthropic's Claude or Google's Gemini, so its never reliant on just one and gives the users options for question generation. 
   - Quiz Data Model: It has a flexible schema that is designed with support for either multi-choice answers or 1 in 4 answers, difficulty levels and categories of study. All quizzes are stored in MongoDB with IDs for efficient retrieval. Quizzes possess both a QuizID and a UserId of the user that created them.
   - Manual Quiz Creation: Questions, answers and metadeta can be manually inputted by the user and sent RESTfully to the backend for quiz object creation. This includes image support.
   - Randomised Question Pools: In the later days of the project, question randomisation was implemented into the question creation process. This allows a quiz creator to have the quiz randomise questions upon an attempt, rather than be in a set sequential order. Additionally, question pools were implemented to complement this. This allows a quiz creator to create a larger pool of questions and have a select amount be pulled from on an attempt, similar to seen on platforms like Moodle.
   - AI-Powered Generation with Prompt Engineering: Integrates with either OpenAI's ChatGPT, Anthropic's Claude or Google's Gemini for generative AI quiz creation. This is done through several methods that utilize prompt engineering. The prompt varies in approach based on the required AI's API structure with extensive testing on results giving.

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

  
