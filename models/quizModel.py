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
# create a new quiz using the quizData
#def createQuiz(quizData):
#    from db import quizdb
#    quiz = Quiz(
#        title = quizData['title'], 
#        description = quizData['description'],
#        questions = quizData['questions']
#    )
#    # Insert the quiz into the database
#    result = quizdb.quizcollection.insert_one(quiz.to_dict())
#    
#    # convert the ObjectId to string and return the quiz
#    quizID = str(result.inserted_id)
#    return {'message': ' QuizID: ' + quizID,
#        'quiz_id': quizID,
#        'title': quizData['title'],
#        'description': quizData['description'],
#        'questions': str(quizData['questions'])
#    }

# create quiz modified
def createQuiz(quizData):
    from db import quizdb
    quiz = Quiz(
        title=quizData['title'], 
        description=quizData['description'],
        questions=quizData['questions']
    )
    quiz_dict = quiz.to_dict()
    quiz_dict['userId'] = quizData['userId']  # Add userId to the quiz data
    result = quizdb.quizcollection.insert_one(quiz_dict)
    
    # convert the ObjectId to string and return the quiz
    quizID = str(result.inserted_id)
    return {
        'message': 'QuizID: ' + quizID,
        'quiz_id': quizID,
        'title': quizData['title'],
        'description': quizData['description'],
        'questions': str(quizData['questions']),
        #'created_at': quizData['created_at']
    }

# get a quiz by quizID
def getQuiz(quizID):
    from db import quizdb
    from bson import ObjectId
    quiz = quizdb.quizcollection.find_one({'_id': ObjectId(quizID)})
    if quiz:
        quiz['_id'] = str(quiz['_id'])  # Convert ObjectId to string
    return quiz

# get all quizzes
#def getAll():
    #from db import quizdb
    #quizzes = quizdb.quizcollection.find()
    #quiz_list = []
   # for quiz in quizzes:
  #      quiz['_id'] = str(quiz['_id'])  # Convert ObjectId to string
 #       quiz_list.append(quiz)
#    return quiz_list

# Get all quizzes modified
def getAll(userId=None):
    from db import quizdb
    query = {}
    if userId:
        query['userId'] = userId
    quizzes = quizdb.quizcollection.find(query)
    quiz_list = []
    for quiz in quizzes:
        quiz['_id'] = str(quiz['_id'])  # Convert ObjectId to string
        quiz_list.append(quiz)
    return quiz_list

# update a quiz by quizID
def updateQuiz(quizID, quizData):
    from db import quizdb
    from bson import ObjectId
    quiz = quizdb.quizcollection.find_one({'_id': ObjectId(quizID)})
    if quiz:
        quizdb.quizcollection.update_one({'_id': ObjectId(quizID)}, {'$set': quizData})
        return {'message': 'Quiz updated successfully'}
    return {'message': 'Error: Quiz not found'}

# delete a quiz by quizID
def deleteQuiz(quizID):
    from db import quizdb
    from bson import ObjectId
    quiz = quizdb.quizcollection.find_one({'_id': ObjectId(quizID)})
    if quiz:
        quizdb.quizcollection.delete_one({'_id': ObjectId(quizID)})
        return {'message': 'Quiz deleted successfully'}
    return {'message': 'Error: Quiz not found'}