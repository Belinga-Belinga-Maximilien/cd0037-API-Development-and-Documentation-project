import json
import os
from unicodedata import category
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

    def format_stuff(someObject):
        return [d.format() for d in someObject]

    """
    Set up CORS. Allow '*' for origins. 
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    """
    after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    Endpoint to handle GET requests
    for all available categories.
    endpoint: '/categories'
    method: 'GET'
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        
        formatted_categories = format_stuff(categories)
        return jsonify({
            'success': True,
            'categories': {category['id']:category['type'] for category in formatted_categories}
        })

    """
    Endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = Question.query.all()
        categories = Category.query.all()
        formatted_questions = format_stuff(questions)
        formatted_categories = format_stuff(categories)
        
        if len(formatted_questions[start:end]) == 0:
            abort(404)
        
        return jsonify({
            'success': True,
            'questions':formatted_questions[start:end],
            'categories': {category['id']:category['type'] for category in formatted_categories},
            'currentCategory': None,
            'totalQuestions': len(formatted_questions)
        })
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)

            if question is None:
                abort(400)

            question.delete()
            return jsonify({
                'success': True,
                'message': 'Question {} deleted'.format(question_id)
            })
        except:
            abort(422)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def new_question():
        body = request.get_json()
        try:
            newQuestion = Question(question=body['question'],answer=body['answer'],category=body['category'],difficulty=body['difficulty']
        )

            newQuestion.insert()

            return jsonify({
                'success': True,
                'message': 'Question created',
                'total_questions': len(Question.query.all())
            })
        except:
            abort(422)
        
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/search', methods=['POST'])
    def search():
        searchTerm = request.get_json()
        
        questions = Question.query.filter(Question.question.ilike("%"+searchTerm["searchTerm"]+"%")).all()

        if questions is None:
            abort(404)

        formatted_questions =  format_stuff(questions)
        return jsonify({
            'success': True,
            'questions': formatted_questions
        })
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def getByCategory(id):
        try:
            category = Category.query.get(id)
            formatted_category = category.format()
            questions = Question.query.filter(Question.category == formatted_category['id']).all()

            if questions is None:
                abort(404)

            formatted_questions = format_stuff(questions)
            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'totalQuestions': len(formatted_questions),
                'currentCategory': formatted_category['type']
            })
        except:
            abort(422)
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()
        prevQuestions = body['previous_questions']
        category = body['quiz_category']
        
        previous_questions = Question.query.filter(Question.id.in_([str(pq) for pq in prevQuestions])).all()
        question_by_category = Question.query.filter_by(category=category['id']).all()
        all_questions = Question.query.all()

        if prevQuestions == [] and category['id'] == 0:
            question = random.choice(format_stuff(all_questions))
        elif prevQuestions == [] and category['id'] != 0:
            question = random.choice(format_stuff(question_by_category))
        elif prevQuestions != [] and category['id'] == 0:
            question = random.choice(format_stuff(all_questions))
            if question in format_stuff(previous_questions):
                question = random.choice(format_stuff(all_questions))
        else: 
            question = random.choice(question_by_category) 

        
        return jsonify({
            'success': True,
            'question': question
        })
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def error_not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource was Not Found'
        }), 404

    @app.errorhandler(405)
    def method_unallowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method Not Allowerd for the requested URL'
        }), 405

    @app.errorhandler(422)
    def not_responsive(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessed'
        }), 422

    return app
