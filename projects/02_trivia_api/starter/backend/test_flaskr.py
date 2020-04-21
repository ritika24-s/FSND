import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgres://{}@{}/{}".format('postgres:password123','localhost:5432', database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_list_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    
    def test_post_categories(self):
        res = self.client().post('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])


    def test_405_invalid_method_for_categories(self):
        res = self.client().patch('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 405)
        self.assertEqual(data["message"], "method not allowed")


    def test_get_pagination(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['current_questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))


    def test_416_error_requesting_beyond_valid_page_range_for_questions(self):
        res = self.client().get("/questions?page=10000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 416)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 416)
        self.assertEqual(data["message"], "Requested Range Not Satisfiable")

    def test_delete_question(self):
        self.question.insert()
        question_id = self.question.id

        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == question_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_question'], question_id)
        self.assertEqual(question, None)
        self.assertTrue(data['total_questions'])

    def test_delete_question_doesnot_exist(self):
        res = self.client().delete('/questions/9000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'Unprocessable Entity')

    def test_add_new_question(self):
        question = {
            'question': self.question.question,
            'answer': self.question.answer,
            'category': self.question.category,
            'difficulty': self.question.difficulty
        }
        res = self.client().post('/questions', json=question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["current_questions"]))
        self.assertTrue(data["total_questions"])

    def test_question_add_not_allowed(self):
        question = {
            'question': self.question.question,
            'answer': self.question.answer,
            'category': self.question.category,
            'difficulty': self.question.difficulty
        }
        res = self.client().post("/questions/45", json=question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")

    def test_422_if_question_is_not_processable(self):
        question = {
            "question": self.question.question,
            "category": self.question.category,
            "answer": None,
            "difficulty": self.question.difficulty,
        }
        res = self.client().post("/questions", json=question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable Entity")

    def test_question_search_with_results(self):
        search = {"search": "title"}
        res = self.client().post("/questions", json=search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertEqual(len(data["questions"]), 3)
        self.assertEqual(data["total_questions"], 1)

    def test_get_question__search_without_results(self):
        search = {"search": "jog"}
        res = self.client().post("/questions", json=search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["questions"]), 0)
        self.assertEqual(data["total_questions"], 0)

    def test_get_question_through_category(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["questions"]), 8)
        self.assertEqual(data["total_questions"], 8)
        self.assertEqual(data["current_category"], "Science")

    def test_400_if_the_category_is_not_valid(self):
        res = self.client().get("/categories/1000/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 400)
        self.assertEqual(data["message"], "Bad Request")

    def test_get_quiz(self):
        posted_data = {"previous_questions": [], "id": "1"}  
        res = self.client().post("/quizzes", json=posted_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_400_post_invalid_category_for_quiz(self):
        posted_data = {"previous_questions": [], "id": ""}  
        res = self.client().post("/quizzes", json=posted_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 400)
        self.assertEqual(data["message"], "Bad Request")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()