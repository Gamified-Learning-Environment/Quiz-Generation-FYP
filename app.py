from flask import Flask, request, jsonify
from flask_cors import CORS # import CORS for cross origin resource sharing
import json
import db

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

if __name__ == '__main__':
    app.run(debug=True, port=9090) # run the server in debug mode