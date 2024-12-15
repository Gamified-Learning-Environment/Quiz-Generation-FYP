from flask import Flask, request, jsonify, send_file
from init import app
from flask_cors import CORS # import CORS
import db # import db
from openai import OpenAI # import OpenAI class
from models.quizModel import createQuiz, getQuiz, getAll, updateQuiz, deleteQuiz # import functions from models.quizModel
from bson import ObjectId 
from datetime import datetime
import os
from dotenv import load_dotenv 
from werkzeug.utils import secure_filename # For image file upload handling
from gridfs import GridFS # For file storage

# For PDF parsing
import PyPDF2
import requests
import io

# load environment variables from .env file
load_dotenv()
MONGODB_URI = os.environ.get('MONGODB_URI')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

client = OpenAI( # create instance of OpenAI
    api_key=OPENAI_API_KEY
)

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
def createNewQuiz():
    quizData = request.json
    quizResponse = createQuiz(quizData)
    return jsonify({
        "message": "Quiz created successfully",
        "quizid": quizResponse['quiz_id']
    }), 201

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

# Generate a quiz using POST method and return the quiz in the response
@app.route('/api/generate-quiz', methods=['POST'])
def generate_quiz():
    data = request.json
    notes = data.get('notes')
    pdf_url = data.get('pdfUrl')
    parameters = data.get('parameters')
    format_example = data.get('format')

    # Process PDF if URL is provided
    pdf_content = ""
    if pdf_url:
        pdf_content = extract_text_from_pdf(pdf_url) or ""

    # Combine notes and PDF content
    combined_content = f"{notes}\n{pdf_content}"

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system", 
                "content": "You are a quiz generator. Generate quiz data in valid Python dictionary format only based on provided notes and/or PDF content."
            },
            {
                "role": "user", 
                "content": f"""Generate a quiz based on the following content:
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
        print(quiz_data)
        return jsonify(quiz_data)
    except Exception as e:
        return jsonify({"error": "Failed to parse quiz data", "details": str(e)}), 400

def parse_generated_quiz(generated_text):
    # Remove any text before the first '{' and after the last '}'
    start = generated_text.find('{')
    end = generated_text.rfind('}') + 1
    if start == -1 or end == 0:
        raise ValueError("No valid dictionary found in response")
    dict_text = generated_text[start:end]
    
    # Safely evaluate the dictionary string
    quiz_data = eval(dict_text)
    return quiz_data


def extract_text_from_pdf(pdf_path):
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
            # Open local file directly
            pdf_file = open(pdf_path, 'rb')

        # Read PDF content
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

        # Close the file if it's a local file
        if not isinstance(pdf_file, io.BytesIO):
            pdf_file.close()

        print(f"Extracted text from PDF: {text}")
        return text
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return None
    
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

if __name__ == '__main__':
    app.run(debug=True, port=9090) # run the server in debug mode