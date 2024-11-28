from flask import Flask, request, jsonify
from flask_cors import CORS # import CORS for cross origin resource sharing
import db
from openai import OpenAI
from models.quizModel import createQuiz, getQuiz, getAll, updateQuiz, deleteQuiz
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

MONGODB_URI = os.environ.get('MONGODB_URI')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

app = Flask(__name__)

# Configure CORS properly
CORS(app, 
     resources={r"/api/*": {
         "origins": ["http://localhost:3000"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"]
     }},
     supports_credentials=True)

client = OpenAI(
    api_key=OPENAI_API_KEY
)

# test data
data = {
    "name": "John",
    "age": 30,
    "city": "New York"
}

@app.route('/')  # route() decorator to tell Flask what URL should trigger the function
def home():
    print("successful connection to Quiz Service")
    return "Quiz Service"

@app.route('/data', methods=['POST'])
def insert_data():
    db.db.collection.insert_one(data)
    return jsonify("Data inserted successfully" + str(data))

# Create a new quiz using POST method and return the quizID in the response
#@app.route('/api/quiz', methods=['POST'])
#def createNewQuiz():
#    quizData = request.json
#    quizResponse = createQuiz(quizData)
#    return jsonify({
#        "message": "Quiz created successfully",
#        "quizid": quizResponse['quiz_id']
#    }), 201

# create quiz modified
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
        db.quizdb.quizcollection.delete_one({'_id': ObjectId(quizID)})
        return jsonify("Quiz deleted successfully")
    return jsonify("Error: Quiz not found"), 404

# Generate a quiz using POST method and return the quiz in the response
@app.route('/api/generate-quiz', methods=['POST'])
def generate_quiz():
    data = request.json
    notes = data.get('notes')
    parameters = data.get('parameters')
    format_example = data.get('format')

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system", 
                "content": "You are a quiz generator. Generate quiz data in valid Python dictionary format only."
            },
            {
                "role": "user", 
                "content": f"""Generate a quiz in the following Python dictionary format:
                {{
                    'title': 'Quiz Title',
                    'description': 'Quiz Description',
                    'questions': [
                        {{
                            'id': 1,
                            'question': 'Question text',
                            'options': ['option1', 'option2', 'option3', 'option4'],
                            'correctAnswer': 'correct option'
                        }}
                    ]
                }}
                Use these notes: {notes}
                And these parameters: {parameters}"""
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
    

if __name__ == '__main__':
    app.run(debug=True, port=9090) # run the server in debug mode