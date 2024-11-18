from datetime import datetime

class Quiz: 
    # constructor
    def __init__(self, title, description, questions): # Self is a reference to current instance, title and questions are parameters
        self.title = title
        self.description = description
        self.questions = questions
        self.created_at = datetime.now()

    def to_dict(self): # Convert the object to a dictionary
        return {
            'title': self.title,
            'description': self.description,
            'questions': [
                {
                    'id': question['id'],
                    'question': question['question'],
                    'options': question['options'],
                    'correctAnswer': question['correctAnswer']
                } for question in self.questions
            ],
            'created_at': self.created_at
        }
def createQuiz(quizData):
    from db import quizdb
    quiz = Quiz(
        title = quizData['title'], 
        description = quizData['description'],
        questions = quizData['questions']
    )
    result = quizdb.quizcollection.insert_one(quiz.to_dict())
    quizID = str(result.inserted_id)
    return {'message': ' QuizID: ' + quizID,
        'quiz_id': quizID,
        'title': quizData['title'],
        'description': quizData['description'],
        'questions': str(quizData['questions'])
    }

def getQuiz(quizID):
    from db import quizdb
    from bson import ObjectId
    quiz = quizdb.quizcollection.find_one({'_id': ObjectId(quizID)})
    if quiz:
        quiz['_id'] = str(quiz['_id'])  # Convert ObjectId to string
    return quiz