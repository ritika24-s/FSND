import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import Category

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# define pagination for questions
def pagination(request,selection):
    page = request.args.get('page',1,int)

    if (page-1)*QUESTIONS_PER_PAGE > len(selection):
        abort(416)

    start = (page-1) * QUESTIONS_PER_PAGE
    end =  start + QUESTIONS_PER_PAGE

    current_questions = selection[start:end]
    current_questions = [question.format() for question in current_questions]

    return current_display
 

#filter categories through id or return all
def __get_categories(category_id=0):
    if category_id != 0:
        categories = Category.query.filter(Category.id==category_id).one_or_none()

        if categories is None:                   #if category not found
            abort(404)

        categories = categories.format()

    else:
        categories = Category.query.order_by(Category.id).all()

        if categories is None:                  #if category not found       
            abort(404)

        categories = [category.format() for category in categories]

    return categories 


#filter questions through id or return all
def __get_questions(question_id=0): 
    if question_id != 0:
        questions = Question.query.filter(Question.id==question_id).one_or_none()

        if questions is None:                   #if question not found
            abort(404)

        questions = questions.format()

    else:
        questions = Question.query.order_by(Question.id).all()

        if questions is None:                   #if question not found
            abort(404)

        questions = [question.format() for question in questions]

    return questions 


#filter questions through category
def __get_questions_through_category(category_id):
    questions = Question.query.filter_by(Question.category==category_id).all()

    if questions is None:
        abort(404)

    return [question.format() for question in questions]



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
  
    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app)


    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response


    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    @app.route('/categories/',methods=['GET','POST'])
    def list_categories():
        if request.method =='GET':

            categories = __get_categories()

            return jsonify({
                'success' : True,
                'categories' : categories
                })

        # add new categories (additional requirement)
        elif request.method =='POST':
            body = request.get_json()
            type = body.get('type',None)
  
            if type is None:
                abort(400)

            try:
                category = Category(type)
                category.insert()

                categories = __get_categories()

                return jsonify({
                'success' : True,
                'categories' : categories
                })

            except:
                abort(422)

        else:
            abort(405)    # methods other than GET and POST not allowed


    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    @app.route('/questions',methods=['GET'])
    def list_questions():
        try:
            selection = __get_questions()

            current_questions = pagination(request,selection)

            categories = __get_categories()

            return jsonify({
                'success': True,
                'questions' : current_questions,
                'total_questions' : len(selection),
                'categories' : categories
                })
        except:
            abort(400)
    

    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = __get_questions(question_id)

            question.delete()
            selection = __get_questions()
            current_questions = pagination(request,selection)

            return jsonify({
                'success': True,
                'deleted_question' : question.id,
                'questions' : current_questions,
                'total_questions' : len(selection),
                'categories' : categories
                })

        except:
            abort(422)


    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()

        new_question = body.get('question',None)
        new_answer = body.get('answer',None)
        new_category = body.get('category',None)
        new_difficulty = body.get('difficulty',None)
        new_rating = body.get('rating',None)
        search = body.get('search',None)
        try:
            if search:
                selection = Question.query.order_by(Question.id).filter_by(Question.question.ilike('%{}%'.format(search)))
                
                if selection is None:
                    abort(404)

                current_questions = pagination(request,selection)

                return jsonify({
                    'success': True,
                    'questions' : current_questions,
                    'total_questions' : len(selection)
                    })

            else:
                if new_question or new_answer or new_category or new_difficulty or new_rating is None:
                    abort(400)

                question = Question(new_question, new_answer, new_category, new_difficulty, new_rating)
                question.insert()

                selection = __get_questions()
                current_questions = pagination(request,selection)

                return jsonify({
                    'success': True,
                    'current_questions': current_questions,
                    'total_questions': len(selection)
                    })
        except:
            abort(422)

    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<int:category_id>/questions',methods=['GET'])
    def get_categorywise_questions(category_id):
        try:
            category = __get_categories(category_id)

            selection = __get_questions_through_category(category_id)

            current_questions = pagination(request,selection)
            
            return jsonify({
                'success': True,
                'questions' : current_questions,
                'totalQuestions' : len(selection),
                'current_category' : category.type
            })

        except:
            abort(404)


    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
    @app.route('/quizzes',methods=['POST'])
    def play_game():
        body = request.get_json()

        if 'pervious_questions' not in body:
            abort(400)
            
        pervious_questions = body.get('pervious_questions',[])
        id = body.get('id',None)

        if id == '':
            abort(400)

        if id is None:                                  #get random questions from all categories
            questions = __get_questions()
        else:
            questions = __get_questions_through_category(id)        #get random questions from a particular category
            
        question = random.choice(questions)
        try:
            while len(questions)>len(pervious_questions):

                question = random.choice(questions)

                if question.id not in pervious_questions:
                    return jsonify({
                        'success': True,
                        'question': question
                    })
            return jsonify({
                        'success': True,
                        'question': question
                    })
        except:
                abort(400)

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
          "success": False, 
          "error": 400,
          "message": "Bad Request"
          }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
          "success": False, 
          "error": 404,
          "message": "resource not found"
          }), 404

    @app.errorhandler(416)
    def beyond_range_request(error):
        return jsonify({
            "success" : False,
            "error" : 416,
            "message" : "Requested Range Not Satisfiable"
            }),416

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success" : False,
            "error" : 422,
            "message" : "Unprocessable Entity"
            }),422

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500


    return app

    