from flask import Flask, request, jsonify, send_file
from init import app
from flask_cors import CORS # import CORS
import db # import db
from openai import OpenAI # import OpenAI class
from models.quizModel import createQuiz, getQuiz, getAll, updateQuiz, deleteQuiz # import functions from models.quizModel
from bson import ObjectId 
from datetime import datetime
import os
import uuid
from dotenv import load_dotenv 
from werkzeug.utils import secure_filename # For image file upload handling
from gridfs import GridFS # For file storage
from urllib.parse import unquote # For URL decoding

# For PDF parsing
import PyPDF2
import requests
import io

# Import Anthropic
from anthropic import Anthropic

# Import Google gemini
import google.generativeai as genai


# load environment variables from .env file
load_dotenv()
MONGODB_URI = os.environ.get('MONGODB_URI')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

CORS(app, supports_credentials=True) # enable CORS

# Initialize GPT client
client = OpenAI( # create instance of OpenAI
    api_key=OPENAI_API_KEY
)

# Initialize claude client
claude_client = Anthropic(
    api_key=ANTHROPIC_API_KEY
)

# Configure the Gemini API
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    print("Warning: GOOGLE_API_KEY not found in environment variables")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Initialize GridFS
fs = GridFS(db.quizdb)

# test data
data = {
    "name": "John",
    "age": 30,
    "city": "New York"
}

# test route
@app.route('/')  
def home():
    print("successful connection to Quiz Service")
    return "Quiz Service"

# test route with data
@app.route('/data', methods=['POST'])
def insert_data():
    db.db.collection.insert_one(data)
    return jsonify("Data inserted successfully" + str(data))

# Create a new quiz using POST method and return the quizID in the response
@app.route('/api/quiz', methods=['POST'])
def CreateQuiz():
    try: 
        
        # Pull data from request
        quizData = request.json

        # Validate required fields
        if not quizData.get('title') or not quizData.get('questions'):
            return jsonify({"error": "Title and questions are required"}), 400
        
        quizResponse = createQuiz(quizData)

        quizId = quizResponse['quiz_id']

        # Build quiz object
        newQuiz = {
            '_id': quizId,
            'title': quizData['title'],
            'description': quizData.get('description', ''),
            'category': quizData.get('category', 'Custom'),
            'difficulty': quizData.get('difficulty', 'intermediate'),
            'userId': quizData.get('userId', ''),
            'randomizeQuestions': quizData.get('randomizeQuestions', False), 
            'useQuestionPool': quizData.get('useQuestionPool', False),
            'questionsPerAttempt': quizData.get('questionsPerAttempt'),
            'questions': []
        }

        # Process questions with new IDs
        for question in quizData.get('questions', []):
            questionId = str(uuid.uuid4())
            newQuiz['questions'].append({
                'id': questionId,
                'question': question['question'],
                'options': question['options'],
                'correctAnswer': question['correctAnswer'],
                'imageUrl': question.get('imageUrl'),
                'explanation': question.get('explanation', False),
                'explanation': question.get('explanation', '')
            })


        # Return response
        return jsonify(newQuiz), 201

    except Exception as e:
        print(f"Error creating quiz: {e}")
        return jsonify({"error": "Failed to create quiz", "details": str(e)}), 500
    

# Get a quiz by quizID using GET method and return the quiz in the response
@app.route('/api/quiz/<quizID>', methods=['GET'])
def getQuizByID(quizID):
    print(quizID)
    quiz = getQuiz(quizID)
    if(quiz):
        return jsonify(quiz)
    return jsonify("Error: Quiz not found"), 404

# Get all quizzes using GET method and return the quizzes in the response
@app.route('/api/quizzes', methods=['GET'])
def getAllQuizzes():
    userId = request.args.get('userId')
    quizzes = getAll(userId)
    return jsonify(quizzes)

# get quizzes by category
@app.route('/api/quizzes/category/<category>', methods=['GET'])
def getQuizzesByCategory(category):
    try:
        quizzes = db.quizdb.quizcollection.find({'category': category})
        quiz_list = []
        for quiz in quizzes:
            quiz['_id'] = str(quiz['_id'])
            quiz_list.append(quiz)
        return jsonify(quiz_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update a quiz by quizID using PUT method and return the response
@app.route('/api/quiz/<quizID>', methods=['PUT'])
def updateQuizByID(quizID):
    quizData = request.json
    quiz = getQuiz(quizID)
    if(quiz):
        updateQuiz(quizID, quizData)
        return jsonify("Quiz updated successfully")
    return jsonify("Error: Quiz not found"), 404

# Delete a quiz by quizID using DELETE method and return the response
@app.route('/api/quiz/<quizID>', methods=['DELETE'])
def deleteQuizByID(quizID):
    quiz = getQuiz(quizID)
    if(quiz):
        deleteQuiz(quizID)
        return jsonify("Quiz deleted successfully")
    return jsonify("Error: Quiz not found"), 404

# Validate a quiz using POST method and return the validation result in the response
def validate_quiz_questions(quiz_data, parameters):

    # Extract difficulty from parameters
    difficulty = parameters.get('difficulty', 'intermediate')

    validation_response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"""You are a quiz validator. Review quiz questions for {difficulty} level difficultly and provide a quality assessment. 
                
                Validation criteria:
                1. Question clarity and structure
                2. Option quality and distinctiveness
                3. Correct answer appropriateness
                4. Difficulty level alignment
                5. Educational value
                
                For {difficulty} difficulty expectations:
                - Beginner: Basic concepts, simple language
                - Intermediate: Applied knowledge, moderate complexity
                - Expert: Advanced concepts, complex analysis
                """
            
            },
            {
                "role": "user",
                "content": f"""Review these quiz questions for {difficulty} level:
                {quiz_data}
                
                Provide assessment in the following JSON format:
                {{
                    'score': <0-100>,
                    'feedback': [
                        {{
                            'question_id': <id>,
                            'score': <0-100>,
                            'difficulty_rating': <'too_easy'|'appropriate'|'too_hard'>,
                            'issues': ['issue1', 'issue2'],
                            'suggestions': ['suggestion1', 'suggestion2']
                        }}
                    ],
                    'difficulty_alignment': <0-100>,
                    'overall_feedback': <summary>
                }}"""
            }
        ],
        model="gpt-3.5-turbo",
    )
    
    # Parse and clean validation result
    validation_result = validation_response.choices[0].message.content.strip()
    # Remove any text before the first '{' and after the last '}'
    start = validation_result.find('{')
    end = validation_result.rfind('}') + 1
    if start == -1 or end == 0:
        raise ValueError("No valid dictionary found in GPT validation response")
    validation_result = validation_result[start:end]

    validation = eval(validation_result[start:end])
    
    # Define difficulty threshold
    difficulty_threshold = {
        'beginner': 70,
        'intermediate': 75,
        'expert': 80
    }

    # Update the generate_quiz route to consider difficulty alignment
    if validation['difficulty_alignment'] < difficulty_threshold[difficulty]:
        validation['score'] = min(validation['score'], validation['difficulty_alignment'])
        validation['overall_feedback'] = f"Quiz difficulty ({validation['difficulty_alignment']}/100) does not align well with {difficulty} level. {validation['overall_feedback']}"

    return validation

# Validate quiz questions using Anthropic Claude model
# def validate_with_claude(quiz_data, difficulty):
#     completion = claude_client.messages.create(
#         model="claude-3-7-sonnet-20250219",
#         messages=[{
#             "role": "user",
#             "content": f"""You are a quiz validator. Review these quiz questions for {difficulty} level difficulty:
#             {quiz_data}
            
#             Apply these validation criteria:
#             1. Question clarity and structure
#             2. Option quality and distinctiveness 
#             3. Correct answer appropriateness
#             4. Difficulty level alignment
#             5. Educational value
            
#             For {difficulty} difficulty expectations:
#             - Beginner: Basic concepts, simple language
#             - Intermediate: Applied knowledge, moderate complexity
#             - Expert: Advanced concepts, complex analysis
            
#             Provide assessment in the following exact Python dictionary format:
#             {{
#                 'score': <0-100>,
#                 'feedback': [
#                     {{
#                         'question_id': <id>,
#                         'score': <0-100>,
#                         'difficulty_rating': <'too_easy'|'appropriate'|'too_hard'>,
#                         'issues': ['issue1', 'issue2'],
#                         'suggestions': ['suggestion1', 'suggestion2']
#                     }}
#                 ],
#                 'difficulty_alignment': <0-100>,
#                 'overall_feedback': <summary>
#             }}
            
#             Return only the Python dictionary, nothing else."""
#         }],
#         max_tokens=4000,
#     )

#     generated_text = completion.content
#     if isinstance(generated_text, list) and len(generated_text) > 0:
#         generated_text = generated_text[0].text

#     # Parse and clean validation result
#     start = generated_text.find('{')
#     end = generated_text.rfind('}') + 1
#     if start == -1 or end == 0:
#         raise ValueError("No valid dictionary found in Claude validation response")
    
#     validation_result = generated_text[start:end]
#     validation = eval(validation_result)
#     return apply_difficulty_threshold(validation, difficulty)

# Validate quiz questions using Google Gemini model
# def validate_with_gemini(quiz_data, difficulty):
#     model = genai.GenerativeModel('gemini-1.5-pro')

#     prompt = f"""You are a quiz validator. Review these quiz questions for {difficulty} level difficulty:
#     {quiz_data}
    
#     Apply these validation criteria:
#     1. Question clarity and structure
#     2. Option quality and distinctiveness 
#     3. Correct answer appropriateness
#     4. Difficulty level alignment
#     5. Educational value
    
#     For {difficulty} difficulty expectations:
#     - Beginner: Basic concepts, simple language
#     - Intermediate: Applied knowledge, moderate complexity
#     - Expert: Advanced concepts, complex analysis
    
#     Provide assessment in the following exact Python dictionary format:
#     {{
#         'score': <0-100>,
#         'feedback': [
#             {{
#                 'question_id': <id>,
#                 'score': <0-100>,
#                 'difficulty_rating': <'too_easy'|'appropriate'|'too_hard'>,
#                 'issues': ['issue1', 'issue2'],
#                 'suggestions': ['suggestion1', 'suggestion2']
#             }}
#         ],
#         'difficulty_alignment': <0-100>,
#         'overall_feedback': <summary>
#     }}
    
#     Return only the Python dictionary, nothing else."""
    
#     response = model.generate_content(prompt)
#     generated_text = response.text

#     # Parse and clean validation result
#     start = generated_text.find('{')
#     end = generated_text.rfind('}') + 1
#     if start == -1 or end == 0:
#         raise ValueError("No valid dictionary found in Gemini validation response")
    
#     validate_result = generated_text[start:end]
#     validation = eval(validate_result)
#     return apply_difficulty_threshold(validation, difficulty)

@app.route('/api/validate-quiz', methods=['POST'])
def validate_quiz():
    try:
        data = request.json
        questions = data.get('questions', [])
        parameters = data.get('parameters', {})
        
        # Validate the model type to prevent injection
        if model_type not in ['gpt', 'claude', 'gemini']:
            model_type = 'gpt'  # Default to GPT if invalid model specified
            
        print(f"Validating quiz with {model_type.upper()} model")

        validation = validate_quiz_questions({
            'questions': questions,  
            'title': '',  
            'description': ''
        }, parameters, model_type)
        
        return jsonify({
            'validation': validation,
            'model_used': model_type
        })
        
    except Exception as e:
        print(f"Validation error: {str(e)}")
        return jsonify({
            "error": "Failed to validate quiz",
            "details": str(e)
        }), 400
    
@app.route('/api/generate-quiz-gemini', methods=['POST'])
def generate_quiz_gemini():
    data = request.json
    notes = data.get('notes')
    pdf_url = data.get('pdfUrl')
    parameters = data.get('parameters')
    question_count = data['parameters'].get('questionCount', 1)
    difficulty = parameters.get('difficulty', 'intermediate')

    # Process PDF if URL is provided
    pdf_content = ""
    if pdf_url:
        pdf_content = extract_text_from_pdf(pdf_url) or ""

    # Combine notes and PDF content
    combined_content = f"{notes}\n{pdf_content}"

    try:
        # Configure the model
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Create prompt for Gemini
        prompt = f"""Generate a {difficulty} level quiz with {question_count} questions based on:

        Content: {combined_content}

        Format response as a valid JSON dictionary with exactly this structure:
        {{
            "title": "Quiz Title",
            "description": "Brief description",
            "questions": [
                {{
                    "id": "1",
                    "question": "Question text",
                    "options": ["option1", "option2", "option3", "option4"],
                    "correctAnswer": "correct option",
                    "explanation": "Brief explanation"
                }}
            ]
        }}

        Important: Use double quotes for all keys and string values. Return only the JSON object without any additional text or code formatting."""

        # Generate content
        response = model.generate_content(prompt)
        
        # Extract the text from the response
        generated_text = response.text
        
        # Clean and parse the response
        quiz_data = parse_generated_quiz(generated_text)
        
        print("GEMINI AI RESPONSE ", quiz_data)

        # Validate quiz questions
        validation = validate_quiz_questions(quiz_data, parameters)
        quiz_data['validation'] = validation

        # Add AI model to the quiz data
        quiz_data['aiModel'] = 'gemini'

        return jsonify(quiz_data)
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    
# Route for Claude generation
@app.route('/api/generate-quiz-claude', methods=['POST'])
def generate_quiz_claude():
    data = request.json
    notes = data.get('notes')
    pdf_url = data.get('pdfUrl')
    parameters = data.get('parameters')
    question_count = data['parameters'].get('questionCount', 1)
    difficulty = parameters.get('difficulty', 'intermediate')

    # Process PDF if URL is provided
    pdf_content = ""
    if pdf_url:
        pdf_content = extract_text_from_pdf(pdf_url) or ""

    # Combine notes and PDF content
    combined_content = f"{notes}\n{pdf_content}"

    try:
        # Claude API expects system content as a top-level parameter
        completion = claude_client.messages.create(
            model="claude-3-7-sonnet-20250219",
            messages=[{
                "role": "user",
                "content": f"""Generate a {difficulty} level quiz with {question_count} questions based on:

                Content: {combined_content}

                Format response as a Python dictionary with this EXACT structure:
                {{
                    'title': 'Quiz Title',
                    'description': 'Brief description',
                    'questions': [
                        {{
                            'id': '1',
                            'question': 'Question text',
                            'options': ['option1', 'option2', 'option3', 'option4'],
                            'correctAnswer': 'correct option',
                            'explanation': 'Brief explanation'
                        }}
                    ]
                }}"""
            }],
            temperature=1, 
        ) 
        
        # Get the response text from Claude's new response structure
        generated_text = completion.content
        if isinstance(generated_text, list) and len(generated_text) > 0:
            generated_text = generated_text[0].text

        # Clean and parse the response
        quiz_data = parse_generated_quiz(generated_text)

        print("Claude AI RESPONSE ", quiz_data)

        validation = validate_quiz_questions(quiz_data, parameters)
        quiz_data['validation'] = validation

        # Add AI model to the quiz data
        quiz_data['aiModel'] = 'claude'

        return jsonify(quiz_data)
    except Exception as e:
        print(f"Claude API Error: {str(e)}") 
        return jsonify({"error": str(e)}), 400

# Generate a quiz using POST method and return the quiz in the response
@app.route('/api/generate-quiz', methods=['POST'])
def generate_quiz():
    data = request.json
    notes = data.get('notes')
    pdf_url = data.get('pdfUrl')
    parameters = data.get('parameters')
    format_example = data.get('format')
    question_count = data['parameters'].get('questionCount', 1)
    difficulty = parameters.get('difficulty', 'intermediate')

    # Process PDF if URL is provided
    pdf_content = ""
    if pdf_url:
        pdf_content = extract_text_from_pdf(pdf_url) or ""

    # For larger question counts, use batching
    if question_count > 20:
        return generate_questions_in_batches(notes, pdf_content, parameters, question_count, difficulty)

        # Original code for smaller question counts - Combine notes and PDF content
    combined_content = f"{notes}\n{pdf_content}"

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system", 
                "content": """You are a quiz generator. Generate quiz data in valid Python dictionary format only based on provided notes and/or PDF content. Include short, concise explanations for correct answers."""
            },
            {
                "role": "user", 
                "content": f"""Generate a {difficulty} level quiz with {question_count} questions based on the following content:
                {combined_content}

                Use these parameters:
                {parameters}

                Return the quiz in the following Python dictionary format:
                {{
                    'title': 'Quiz Title',
                    'description': 'Quiz Description',
                    'questions': [
                        {{
                            'id': 1,
                            'question': 'Question text',
                            'options': ['option1', 'option2', 'option3', 'option4'],
                            'correctAnswer': 'correct option',
                            'explanation': 'Short explanation of why this is the correct answer',
                            'imageUrl': None  # Optional image URL
                        }}
                    ]
                }}"""
            }
        ],
        model="gpt-3.5-turbo",
    )

    generated_text = chat_completion.choices[0].message.content.strip()
    
    try:
        quiz_data = parse_generated_quiz(generated_text)
        print("OPEN AI RESPONSE ", quiz_data)

        # Validate quiz questions
        validation = validate_quiz_questions(quiz_data, parameters)

        # Check both overall quality and difficulty alignment
        if validation['score'] < 70 or validation['difficulty_alignment'] < parameters.get('difficulty_threshold', 70):
            quiz_data['validation'] = validation
            quiz_data['warning'] = "Quiz may not meet quality or difficulty requirements"
            return jsonify(quiz_data)  # Return the whole quiz data object
            
        # Add validation results to quiz data
        quiz_data['validation'] = validation

        print("Quiz validation passed successfully with score:", validation['score'])

        # Add AI model to the quiz data
        quiz_data['aiModel'] = 'gpt'

        return jsonify(quiz_data)
    except Exception as e:
        print(f"Generation error: {str(e)}") 
        return jsonify({"error": "Failed to generate/validate quiz", "details": str(e)}), 400

# Generate a large number of questions by making multiple smaller requests
def generate_questions_in_batches(notes, pdf_content, parameters, total_question_count, difficulty):
    combined_content = f"{notes}\n{pdf_content}"
    all_questions = []
    batch_size = 10  # Reduce batch size from 15 to 10
    
    # If content is very large, we need to split it
    if len(combined_content) > 30000:  # ~7500 tokens
        # Take just enough content for context in each batch
        content_chunks = []
        chunk_size = 25000  # ~6250 tokens
        for i in range(0, len(combined_content), chunk_size):
            content_chunks.append(combined_content[i:i+chunk_size])
    else:
        content_chunks = [combined_content]
    
    batches_needed = (total_question_count + batch_size - 1) // batch_size
    
    for batch in range(batches_needed):
        questions_in_batch = min(batch_size, total_question_count - len(all_questions))
        if questions_in_batch <= 0:
            break
            
        # Select which content chunk to use (rotate through chunks)
        content_to_use = content_chunks[batch % len(content_chunks)]
        
        print(f"Generating batch {batch+1}/{batches_needed} with {questions_in_batch} questions")
        
        # Generate batch of questions
        batch_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": """You are a quiz generator. Generate quiz data in valid Python dictionary format only."""
                },
                {
                    "role": "user", 
                    "content": f"""Generate a {difficulty} level quiz with EXACTLY {questions_in_batch} questions based on the following content.
                    These will be part {batch+1} of {batches_needed} in a larger quiz, so make them diverse:
                    {content_to_use}
                    
                    Return the quiz in the following Python dictionary format:
                    {{
                        'title': 'Quiz Part {batch+1}',
                        'description': 'Generated quiz questions part {batch+1}',
                        'questions': [
                            {{
                                'id': '{batch*batch_size+1}',
                                'question': 'Question text',
                                'options': ['option1', 'option2', 'option3', 'option4'],
                                'correctAnswer': 'correct option',
                                'explanation': 'Short explanation of why this is the correct answer'
                            }}
                        ]
                    }}"""
                }
            ],
            model="gpt-3.5-turbo",
            max_tokens=3000  # Reduced from 4000
        )
        
        # Parse batch results
        generated_text = batch_completion.choices[0].message.content.strip()
        batch_data = parse_generated_quiz(generated_text)
        
        # Add to combined results
        all_questions.extend(batch_data.get('questions', []))
        
        # If this is the first batch, get the title and description
        if batch == 0:
            title = batch_data.get('title', f"{difficulty.capitalize()} Quiz")
            description = batch_data.get('description', f"A {difficulty} level quiz with {total_question_count} questions")
    
    # Create combined result
    combined_quiz = {
        "title": title,
        "description": description,
        "questions": all_questions[:total_question_count],  # Only take the requested number
        "aiModel": "gpt"
    }
    
    # Validate combined quiz
    validation = validate_quiz_questions(combined_quiz, parameters)
    combined_quiz['validation'] = validation
    
    return combined_quiz

def parse_generated_quiz(generated_text):

    # Clean up the response text
    text = generated_text.strip()

    # Remove any text before the first '{' and after the last '}'
    start = text.find('{')
    end = text.rfind('}') + 1

    if start == -1 or end == 0:
        raise ValueError("No valid dictionary found in response")
    
    dict_text = text[start:end]

    # Remove any markdown formatting
    dict_text = dict_text.replace('```python', '').replace('```', '')
    dict_text = dict_text.strip()
    
    # Safely evaluate the dictionary string
    quiz_data = eval(dict_text)
    return quiz_data

# Extract text from PDF using PyPDF2 and handle both URLs and local file paths
def extract_text_from_pdf(pdf_path, check_size=True):
    try:
        # Handle both URLs and local file paths
        if pdf_path.startswith(('http://', 'https://')):
            # For URLs
            response = requests.get(pdf_path)
            response.raise_for_status()
            pdf_file = io.BytesIO(response.content)
        else:
            # For local files - remove file:// prefix if present
            if pdf_path.startswith('file:///'):
                pdf_path = pdf_path[8:]  # Remove 'file:///'

            # Decode URL-encoded characters in the path
            pdf_path = unquote(pdf_path)

            # Open local file directly
            pdf_file = open(pdf_path, 'rb')

        # Read PDF content
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        total_pages = len(pdf_reader.pages)
        print(f"Extracting text from {total_pages} pages of PDF")

        # For smaller PDFs, proceed with normal extraction
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        # Check if PDF is large
        if check_size and len(text) > 60000:
            if not isinstance(pdf_file, io.BytesIO):
                pdf_file.close()
            # Return a signal that this PDF is too large
            return "PDF_TOO_LARGE"

        # Close the file if it's a local file
        if not isinstance(pdf_file, io.BytesIO):
            pdf_file.close()

        # Check if total text is too large (approx 15,000 tokens ~= 60,000 chars)
        if check_size and len(text) > 60000:
            return "PDF_TOO_LARGE"

        print(f"EXTRACTED TEST START: {text[:100]}...") # Print first 200 characters
        print(f"EXTRACTED TEXT END: {text[-100:]}...") # Print last 200 characters
        print(f"TOTAL CHARACTERS: {len(text)} characters")
        return text # Return extracted text
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return None

# Upload PDF file to GridFS and return the URL to access it
@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files: # Check if 'pdf' part is in the request
        return jsonify({"error": "No pdf part"}), 400
        
    file = request.files['pdf'] # Get the file from the request
    if file.filename == '': # Check if filename is empty
        return jsonify({"error": "No selected file"}), 400
    
    try: # Try to process the file
        # Store file in GridFS
        filename = secure_filename(file.filename) # Secure the filename
        file_id = fs.put( 
            file, 
            filename=filename,
            content_type=file.content_type
        ) # Store the file in GridFS
        
        # Generate URL to access the PDF
        # Use environment variable for production URL
        base_url = os.environ.get('SERVICE_URL', 'http://localhost:9090')
        pdf_url = f"{base_url}/pdfs/{str(file_id)}"
        
        return jsonify({"pdfUrl": pdf_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/pdfs/<file_id>')
def serve_pdf(file_id):
    try:
        # Find file in GridFS
        file_data = fs.get(ObjectId(file_id))
        
        # Create response with proper content type
        response = send_file(
            file_data,
            mimetype='application/pdf',
            as_attachment=False,
            download_name=file_data.filename
        )
        
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 404

# Process large PDFs in seperate batches, generating questions based on extracted key concepts
def process_large_pdf(pdf_path, question_count, difficulty): 
    try: 
        # Open pdf using same method as extract_text_from_pdf
        if pdf_path.startswith(('http://', 'https://')):
            # For URLs
            response = requests.get(pdf_path)
            response.raise_for_status()
            pdf_file = io.BytesIO(response.content)
        else:
            # For local files - remove file:// prefix if present
            if pdf_path.startswith('file:///'):
                pdf_path = pdf_path[8:]  # Remove 'file:///'

            # Decode URL-encoded characters in the path
            pdf_path = unquote(pdf_path)

            # Open local file directly
            pdf_file = open(pdf_path, 'rb')

        # Read PDF content
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        total_pages = len(pdf_reader.pages)

        print("Processing large PDF with {total_pages} pages")

        # Step 1: Process PDF in batches and extract key concepts
        batch_size = min(5, total_pages) # Process 5 pages at a time
        all_concepts = []

        for start_page in range(0, total_pages, batch_size):
            # Get text from this batch of pages
            batch_text = ""
            end_page = min(start_page + batch_size, total_pages)

            for i in range(start_page, end_page):
                page_text = pdf_reader.pages[i].extract_text() or ""
                batch_text += page_text + "\n"

            # Skip empty batches
            if not batch_text.strip():
                continue

            # Extract key concepts from the batch using AI
            concepts_per_batch = max(1, question_count //  ((total_pages // batch_size) + 1))
            print(f"Extracting {concepts_per_batch} concepts from pages {start_page + 1} to {end_page}")

            concept_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract the most important concepts, terms, and facts from this text that would be good for quiz questions."},
                    {"role": "user", "content": f"Identify {concepts_per_batch} key concepts from this text that would make excellent quiz questions at {difficulty} level. Format each concept as a single sentence with the main term or idea clearly stated:\n\n{batch_text}"}
                ]
            )

            # Parse concepts
            concepts_text = concept_response.choices[0].message.content.strip()
            concepts = [c.strip() for c in concepts_text.split('\n') if c.strip()]
            all_concepts.extend(concepts)

            print(f"Extracted {len(concepts)} concepts from batch")

        if not isinstance(pdf_file, io.BytesIO):
            pdf_file.close()

        # Step 2: Generate quiz questions based on extracted concepts
        concept_text = "\n".join(all_concepts)
        print(f"Generating quiz based on {len(all_concepts)} extracted concepts")

        # Generate the quiz using the concepts
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": f"You are a quiz generator specializing in creating {difficulty} level questions based on key concepts provided."
                },
                {
                    "role": "user", 
                    "content": f"""Create a {difficulty} level quiz with exactly {question_count} questions based on these key concepts extracted from a document:
                    
                    {concept_text}
                    
                    Make sure each question is challenging but fair for {difficulty} level students.
                    
                    Return the quiz in this Python dictionary format:
                    {{
                        'title': 'Quiz Title Based on Document Content',
                        'description': 'Brief description of quiz content and focus',
                        'questions': [
                            {{
                                'id': '1',
                                'question': 'Question text',
                                'options': ['option1', 'option2', 'option3', 'option4'],
                                'correctAnswer': 'correct option',
                                'explanation': 'Brief explanation of the answer'
                            }}
                        ]
                    }}
                    """
                }
            ]
        )

        generated_text = chat_completion.choices[0].message.content.strip()
        quiz_data = parse_generated_quiz(generated_text)
        
        # Add metadata to indicate this was processed using the large PDF method
        quiz_data["processingMethod"] = "large-pdf-two-stage"

        return quiz_data
    except Exception as e:
        print(f"Error processing large PDF: {str(e)}")
        return {"error": str(e)}
    
# Categories management
@app.route('/api/categories', methods=['GET'])
def getCategories():
    try:
        # Get custom categories from database
        custom_categories = db.quizdb.categories.distinct('name')
        # Combine with default categories
        all_categories = list(set(DEFAULT_CATEGORIES + custom_categories))
        return jsonify(all_categories)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/categories', methods=['POST'])
def addCategory():
    try:
        category_data = request.json
        new_category = category_data.get('name')
        if new_category:
            db.quizdb.categories.insert_one({'name': new_category})
            return jsonify({"message": "Category added successfully"})
        return jsonify({"error": "Category name is required"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Predefined categories
DEFAULT_CATEGORIES = [
    "Programming",
    "Mathematics",
    "Science",
    "History",
    "Language",
    "General Knowledge",
    "Custom"
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({"error": "No image part"}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        try:
            # Store file in GridFS
            filename = secure_filename(file.filename)
            file_id = fs.put(
                file,
                filename=filename,
                content_type=file.content_type
            )
            
            # Generate URL using file_id
            image_url = f"http://localhost:9090/images/{str(file_id)}"
            
            return jsonify({"imageUrl": image_url})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Invalid file type"}), 400

# Serve images from GridFS
@app.route('/images/<file_id>')
def serve_image(file_id):
    try:
        # Find file in GridFS
        file_data = fs.get(ObjectId(file_id))
        
        # Create response with proper content type
        response = send_file(
            file_data,
            mimetype=file_data.content_type,
            as_attachment=False,
            download_name=file_data.filename
        )
        
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 404
    
@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        "status": "ok",
        "environment": os.environ.get('RAILWAY_ENVIRONMENT', 'local'),
        "memory_limit": os.environ.get('RAILWAY_MEMORY_LIMIT', 'unknown'),
        "cpu_limit": os.environ.get('RAILWAY_CPU_LIMIT', 'unknown'),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, port=9090) # run the server in debug mode