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
        self.database_account = 'postgres'
        self.database_password = 'postgres'
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(self.database_account, self.database_password, 'localhost:5432', self.database_name)
        self.cat_id = 1
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
    def test_get_categories(self):
        res = self.client().get('/categories')
        self.assertEqual(res.status_code, 200)

    def test_get_questions_pagination(self):
        res = self.client().get('/questions')
        self.assertEqual(res.status_code, 200)

    def test_error_qet_questions_pagination(self):
        res = self.client().get('/questions?page=100')

        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_delete_question(self):
        res = self.client().delete('/questions/5')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_new_question(self):
        res = self.client().post("/questions", json=({
                                                        'question':  'Voici une chaîne de nouvelle question',
                                                        'answer':  'Voici une chaîne de nouvelle réponse',
                                                        'difficulty': 1,
                                                        'category': 3,
                                                    }))
        self.assertEqual(res.status_code, 200)
    
    def test_search(self):
        res = self.client().post("/search", json=({
                                                    'searchTerm': 'Which'
                                                    }))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])

    def test_getByCategory(self):
        res = self.client().get("/categories/1/questions")  
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_unresponsive_422(self):
        res = self.client().get("/categories/10/questions")
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 422)

    def test_play_quiz(self):
        res = self.client().post("/quizzes", json=({
                                                'previous_questions': [],
                                                'quiz_category': {'id':'1', 'type':'Science'}
                                                }))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()