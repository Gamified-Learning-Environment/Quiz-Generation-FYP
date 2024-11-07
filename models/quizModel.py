from db import db
from datetime import datetime

class Quiz: 
    # constructor
    def __init__(self, title, questions): # Self is a reference to current instance, title and questions are parameters
        self.title = title
        self.questions = questions
        self.created_at = datetime.now()

    def to_dict(self): # Convert the object to a dictionary
        return {
            'title': self.title,
            'questions': self.questions,
            'created_at': self.created_at
        }
def createQuiz(quizData):
    quiz = Quiz(
        title = quizData['title'], 
        questions = quizData['questions']
    )
    db.quizcollection.insert_one(quiz.to_dict())
    return {'message': 'Quiz created successfully!' + quizData['title'] + ' ' + quizData['questions']}

def getQuiz(quizID):
    return db.quizcollection.find_one({'_id': quizID})