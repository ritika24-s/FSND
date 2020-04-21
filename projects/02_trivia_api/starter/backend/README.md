# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

ENDPOINTS UNDERSTANDING

1. GET '/categories'
	General:
		Endpoint to get list of all the categories
		Request Arguments: None
	Returns:
		An object with success, categories.
		'categories' key contains a list of category objects with:
		
		{
                'success' : True,
                'categories' : categories
        }
	Sample - 
		Fixed categories -
		{
		  "categories": [
			{
			  "id": 1,
			  "type": "Science"
			},
			{
			  "id": 2,
			  "type": "Art"
			},
			{
			  "id": 3,
			  "type": "Geography"
			},
			{
			  "id": 4,
			  "type": "History"
			},
			{
			  "id": 5,
			  "type": "Entertainment"
			},
			{
			  "id": 6,
			  "type": "Sports"
			}
		  ],
		  "success": true
		}

2. POST '/categories'
	General:
		Endpoint to create a new category
		Request Arguments: type of the category
			json={'type':'Art'}
	Returns:
		An object with success, categories.
		'categories' key contains a list of category objects with:
		{
                'success' : True,
                'categories' : categories
        }

3. GET '/questions'
	General:
		Endpoint to get list of all the questions
		Request Arguments: None
	Returns:
		An object with success, questions, total_questions and categories.
		{
                'success': True,
                'questions' : current_questions,
                'total_questions' : total_questions
                'categories' : categories
        }

4. DELETE '/questions/<int:question_id>'
	General:
		Endpoint to delete a question by its id
		Request Arguments: question_id
	Returns:
		An object with success, deleted_questions, questions, total_questions and categories.
		{
                'success': True,
                'deleted_question' : question_id,
                'questions' : current_questions,
                'total_questions' : total_questions,
				'categories' : categories
        }

5. POST '/questions'
	General:
		Endpoint to create a new question using the submitted question, answer, category, difficulty and rating 
		Request Arguments: json={"question":"What is the shape of earth?", "answer":"Spherical", "category":"3", "difficulty":"2","rating":"1"}'

	Returns:
		An object with success, questions and total_questions.
               {
                    'success': True,
                    'current_questions': current_questions,
                    'total_questions': total_questions
               }
	
	General:
		This endpoint can also be used to search for a particular question 
		Request Arguments: json={"search":"title"}

	Returns:
		An object with success, questions and total_questions.
		{
                'success': True,
				'questions' : current_questions,
                'total_questions' : total_questions
        }
	
6. GET '/categories/<int:category_id>/questions'
	General:
		Endpoint to get questions for particular category 
		Request Arguments: category_id

	Returns:
		An object with success, questions, total_questions and current_category.
		{
                'success': True,
                'questions' : current_questions,
                'totalQuestions' : len(selection),
                'current_category' : category.type
        }

7. POST '/quizzes'
	General:
		Endpoint to play the trivia game. This endpoint help yu generate random questions from a particular category or all. 
		Request Arguments: list of previous_questions and category_id(optional)

	Returns:
		An object with success, question.
		{
                'success': True,
				'question' : question
        }
## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```