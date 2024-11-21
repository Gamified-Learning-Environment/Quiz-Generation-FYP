from flask import Flask, request, jsonify
from flask_cors import CORS # import CORS for cross origin resource sharing
import db
from models.quizModel import createQuiz, getQuiz, getAll, updateQuiz, deleteQuiz
from bson import ObjectId

app = Flask(__name__)

# Apply CORS to this app
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


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
#@app.route('/api/quizzes', methods=['GET'])
#def getAllQuizzes():
#    quizzes = getAll()
#    return jsonify(quizzes)

# get all quizzes modified
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
    

if __name__ == '__main__':
    app.run(debug=True, port=9090) # run the server in debug mode