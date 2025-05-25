from flask import render_template, request, redirect, url_for, session, jsonify
# Import db directly from main app
from __init__ import db

# Use a lazy import approach to avoid circular imports
def get_models():
    """Get models lazily to avoid circular imports"""
    from user.models import Score, User
    from admin.models.question import Question
    from admin.models.essay_response import EssayResponse
    return Score, Question, EssayResponse, User

class QuizController:
    def __init__(self, app):
        self.app = app
        self.register_routes()

    def register_routes(self):
        """Register all quiz-related routes"""
        # Quiz submission routes
        self.app.route('/submit_quiz', methods=['POST'])(self.submit_quiz)
        self.app.route('/save_score', methods=['POST'])(self.save_score)
        self.app.route('/save_topology_score', methods=['POST'])(self.save_topology_score)
        self.app.route('/save_crimping_score', methods=['POST'])(self.save_crimping_score)
        self.app.route('/save_troubleshoot_score', methods=['POST'])(self.save_troubleshoot_score)
        
        # Make sure we register both the direct and API routes for essay submission
        self.app.route('/save_essay', methods=['POST'])(self.save_essay)
        
        # Note: We're not registering the API version here since it should come from the API blueprint
        # This avoids conflicts with the blueprint registration
        
        self.app.route('/delete_score/<int:score_id>', methods=['POST'])(self.delete_score)
        
        # Quiz data routes - register both with and without API prefix for fallback
        self.app.route('/questions')(self.get_questions)
        
        # Quiz view routes
        self.app.route('/topology', methods=['GET', 'POST'])(self.topology)
        self.app.route('/troubleshoot', methods=['GET', 'POST'])(self.troubleshoot)
        self.app.route('/crimp', methods=['GET', 'POST'])(self.crimp)

    def submit_quiz(self):
        if 'user_id' not in session:
            return render_template('user/index.html', message='You need to log in first!')

        Score, Question, EssayResponse, User = get_models()
        user_id = session['user_id']
        score = request.form['score']

        new_score = Score(score=score, user_id=user_id)
        db.session.add(new_score)
        db.session.commit()
        return redirect(url_for('dashboard'))

    def save_score(self):
        """Save a quiz score"""
        Score, Question, EssayResponse, User = get_models()
        if 'user_id' in session:
            user_id = session['user_id']
            score = request.form.get('score', 0)
            category = request.form.get('category', 'riddle')
            
            # Create and save new score
            new_score = Score(
                score=score, 
                user_id=user_id, 
                category=category
            )
            db.session.add(new_score)
            db.session.commit()
            
            return jsonify({'status': 'success', 'message': 'Score saved successfully'})
        else:
            print("User not logged in")
            return jsonify({'status': 'error', 'message': 'User not logged in'})

    def save_topology_score(self):
        """Save a topology quiz score"""
        Score, Question, EssayResponse, User = get_models()
        if 'user_id' in session:
            user_id = session['user_id']
            score = request.form.get('score', 0)
            
            # Create and save new score with topology category
            new_score = Score(
                score=score, 
                user_id=user_id, 
                category='topology'
            )
            db.session.add(new_score)
            db.session.commit()
            
            return jsonify({'status': 'success', 'message': 'Topology score saved successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'User not logged in'})
            
    def save_crimping_score(self):
        """Save a crimping quiz score"""
        Score, Question, EssayResponse, User = get_models()
        if 'user_id' in session:
            user_id = session['user_id']
            score = request.form.get('score', 0)
            
            # Create and save new score with crimping category
            new_score = Score(
                score=score, 
                user_id=user_id, 
                category='crimping'
            )
            db.session.add(new_score)
            db.session.commit()
            
            return jsonify({'status': 'success', 'message': 'Crimping score saved successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'User not logged in'})
            
    def save_troubleshoot_score(self):
        """Save a troubleshooting quiz score"""
        Score, Question, EssayResponse, User = get_models()
        if 'user_id' in session:
            user_id = session['user_id']
            score = request.form.get('score', 0)
            
            # Create and save new score with troubleshoot category
            new_score = Score(
                score=score, 
                user_id=user_id, 
                category='troubleshoot'
            )
            db.session.add(new_score)
            db.session.commit()
            
            return jsonify({'status': 'success', 'message': 'Troubleshooting score saved successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'User not logged in'})
            
    def save_essay(self):
        """Save an essay response"""
        Score, Question, EssayResponse, User = get_models()
        if 'user_id' in session:
            user_id = session['user_id']
            question_id = request.form.get('question_id')
            question_text = request.form.get('question_text')
            response_text = request.form.get('response_text')
            category = request.form.get('category', 'riddle')
            
            # Create and save new essay response
            new_response = EssayResponse(
                user_id=user_id,
                question_id=question_id,
                question_text=question_text,
                response_text=response_text,
                category=category
            )
            db.session.add(new_response)
            db.session.commit()
            
            return jsonify({'status': 'success', 'message': 'Essay saved successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'User not logged in'})
            
    def delete_score(self, score_id):
        """Delete a user's score"""
        Score, Question, EssayResponse, User = get_models()
        if 'user_id' not in session:
            return render_template('user/index.html', message='You need to log in first!')
            
        score = Score.query.get(score_id)
        if score and score.user_id == session['user_id']:
            db.session.delete(score)
            db.session.commit()
        return redirect(url_for('user.dashboard'))

    def get_questions(self):
        """Get all questions for quizzes"""
        Score, Question, EssayResponse, User = get_models()
        questions = Question.query.all()
        question_list = []
        
        for q in questions:
            question_dict = {
                'id': q.id,
                'numb': q.numb,
                'question': q.question,
                'answer': q.answer,
                'options': q.options,
                'explanation': q.explanation,
                'category': q.category,
                'type': q.question_type if hasattr(q, 'question_type') else 'multiple_choice'
            }
            question_list.append(question_dict)
            
        return jsonify(question_list)

    def topology(self):
        """Render topology quiz page"""
        return render_template('user/topology-simulation.html', title="topology")
        
    def troubleshoot(self):
        """Render troubleshooting quiz page"""
        return render_template('user/troubleshoot.html', title="troubleshoot")
        
    def crimp(self):
        """Render crimping quiz page"""
        return render_template('user/crimping-simulation.html', title="crimp")
