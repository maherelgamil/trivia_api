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

        response = self.client().delete('/questions/{}'.format(question_id))
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['id'], question_id)

    def test_delete_question_with_invalid_id(self):
        response = self.client().delete('/questions/1000')

        self.assertEqual(response.status_code, 404)

    """
    test insert new question
    """
    def test_create_new_question(self):
        question = {
            "question":"Test Question",
            "answer":"Test Answer",
            "category":1,
            "difficulty":3
        }

        response = self.client().post('/questions', json=question.copy())
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['question']['question'], question.get('question'))
        self.assertEqual(response_data['question']['answer'], question.get('answer'))
        self.assertEqual(response_data['question']['difficulty'], question.get('difficulty'))

    def test_create_new_question_validation(self):
        question = {
            "question":"Test Question",
        }

        response = self.client().post('/questions', json=question.copy())

        self.assertEqual(response.status_code, 422)

    """
    test search for question
    """
    def test_get_questions_by_search_term(self):
        response = self.client().post('/questions', json={'searchTerm': 'title'})
        questions = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(questions['questions']), questions['total_questions'])

    """
    test get questions by category
    """
    def test_get_questions_by_category(self):
        response = self.client().get('/categories/1/questions')
        questions = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(questions['questions']), questions['total_questions'])
        self.assertEqual(questions['current_category']['id'], 1)


    def test_get_questions_by_not_exist_category(self):
        response = self.client().get('/categories/11111/questions')
        questions = json.loads(response.data)

        self.assertEqual(response.status_code, 422)

    def test_get_questions_by_category_with_invalid_page_number(self):
        response = self.client().get('/categories/1/questions?page=0')
        questions = json.loads(response.data)

        self.assertEqual(response.status_code, 422)


    def test_play_quizzes_with_category(self):
        response = self.client().post('/quizzes', json={
            'previous_questions': [1],
            'quiz_category': {
                'id': 1,
                'type': 'Science'
            }
        })
        question = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(question['success'], True)

    def test_play_quizzes_with_no_category(self):
        response = self.client().post('/quizzes', json={
            'previous_questions': [1],
            'quiz_category': 0
        })
        question = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(question['success'], True)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
