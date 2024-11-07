from flask import Flask, request, jsonify
from flask_cors import CORS # import CORS for cross origin resource sharing
import db
from models.quizModel import createQuiz, getQuiz
from bson import ObjectId

app = Flask(__name__)

# Apply CORS to this app
CORS(app)

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

@app.route('/data', methods=['GET'])
def get_data():
    db.db.collection.insert_one(data)
    return jsonify("Data inserted successfully" + str(data))

@app.route('/api/quiz', methods=['POST'])
def createNewQuiz():
    quizData = request.json
    quizResponse = createQuiz(quizData)
    return jsonify("Message: Quiz created successfully" + quizResponse['message']), 201

@app.route('/api/quiz/<quizID>', methods=['GET'])
def getQuizByID(quizID):
    print(quizID)
    quiz = getQuiz(quizID)
    if(quiz):
        return jsonify(quiz)
    return jsonify("Error: Quiz not found"), 404

if __name__ == '__main__':
    app.run(debug=True, port=9090) # run the server in debug mode