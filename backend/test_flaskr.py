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
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
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
    test to get all available categories
    """
    def test_get_all_available_categories(self):
        response = self.client().get('/categories')
        categories = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(categories['success'], True)

    """
    test get questions
    """
    def test_get_questions_list(self):
        response = self.client().get('/questions?page=1')
        questions = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(questions['questions']), questions['total_questions'])

    """
    test get question by invalid page
    """
    def test_get_question_by_invalid_page(self):
        response = self.client().get('/questions?page=0')

        self.assertEqual(response.status_code, 422)

    def test_get_question_by_below_zero_page(self):
        response = self.client().get('/questions?page=-1')
        self.assertEqual(response.status_code, 422)

    def test_get_question_by_none_exist_page(self):
        response = self.client().get('/questions?page=10')
        self.assertEqual(response.status_code, 422)

    def test_delete_question(self):
        # create new question
        question = Question(
            question="Test Question",
            answer="Test Answer",
            category=1,
            difficulty=3
        )
        question.insert()

        question_id = question.id

        response = self.client().delete('/questions?id={}'.format(question_id))
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['id'], question_id)

    def test_delete_question_with_422_error(self):
        response = self.client().delete('/questions')

        self.assertEqual(response.status_code, 422)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
