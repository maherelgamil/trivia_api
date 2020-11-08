import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={'/': {'origins': '*'}})
  '''
  Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
      return response

  '''
  Create an endpoint to handle GET requests
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
      categories = [category.format() for category in Category.query.all()]

      return jsonify({
          "success": True,
          "categories": categories,
          "total_categories": len(categories)
      })

  '''
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions_by_category_id():
      # get questions
      questions = Question.query.all()

      # pagination
      page = request.args.get('page', 1, type=int)

      # page parameter validation
      if page <= 0:
          return abort(422)

      start = (page - 1) * QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE

      questions = [question.format() for question in questions]
      questions = questions[start:end]

      if len(questions) == 0:
          return abort(422)

      # get all categories
      categories = Category.query.all()
      categories_formatted = {}
      for category in categories:
          categories_formatted[category.id] = category.type

      return jsonify({
          'success': True,
          'questions': questions,
          'total_questions': len(questions),
          'current_category': None,
          'categories': categories_formatted
      })

  '''
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''

  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):

      # first we need to get the question record
      question = Question.query.filter(Question.id == id).one_or_none()

      # if question not exist
      if question == None:
          return abort(404)

      try:
        question.delete()

        return jsonify({
            "success": True,
            "id": id
        }), 200

      except:
        return abort(500)

  '''
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
  @app.route('/questions', methods=['POST'])
  def create_post():

      question_data = request.get_json()

      if question_data.get('searchTerm'):
          query = question_data.get('searchTerm')

          # get questions by search term
          questions = Question.query.filter(
              Question.question.ilike(f'%{query}%')
          ).all()

          # pagination
          page = request.args.get('page', 1, type=int)

          # page parameter validation
          if page <= 0:
              return abort(422)

          start = (page - 1) * QUESTIONS_PER_PAGE
          end = start + QUESTIONS_PER_PAGE

          questions = [question.format() for question in questions]
          questions = questions[start:end]

          if len(questions) == 0:
              return abort(422)

          # get all categories
          categories = Category.query.all()
          categories_formatted = {}
          for category in categories:
              categories_formatted[category.id] = category.type

          return jsonify({
              'success': True,
              'questions': questions,
              'total_questions': len(questions),
              'current_category': None,
              'categories': categories_formatted
          })
      else:
          # Validation
          if 'question' not in question_data.keys() or \
              question_data.get('question') == None or \
              question_data.get('question') == '' or \
              'answer' not in question_data.keys() or \
              question_data.get('answer') == None or \
              question_data.get('answer') == '' or \
              'difficulty' not in question_data.keys() or \
              question_data.get('difficulty') == None or \
              question_data.get('difficulty') == '' or \
              'category' not in question_data.keys() or \
              question_data.get('category') == None or \
              question_data.get('category') == '':
              return abort(422)

          question = Question(
              question=question_data.get('question'),
              answer=question_data.get('answer'),
              difficulty=question_data.get('difficulty'),
              category=question_data.get('category'),
          )
          question.insert()

          return jsonify({
              "success": True,
              "message": "Question Created Successfully",
              'question': question.format()
          }), 200

  '''
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

  '''
  Create error handlers for all expected errors
  including 404 and 422.
  '''
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": 'Entity Not Found'
      }), 404

  @app.errorhandler(422)
  def validation_error(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "Validation Error"
      }), 422

  @app.errorhandler(500)
  def internal_server_error(error):
      return jsonify({
          "success": False,
          "error": 500,
          "message": "Internal Server Error"
      }), 500

  # Let's run our app
  return app

