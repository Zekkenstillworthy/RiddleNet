"""
Live Leaderboard Integration Examples
This module shows how to integrate the live leaderboard system 
with existing scoring and challenge completion systems.
"""

from socket_manager import socketio
from flask import current_app
from datetime import datetime
import json

class LiveLeaderboardIntegration:
    """Integration class for connecting existing systems to live leaderboard"""
    
    @staticmethod
    def handle_quiz_completion(user_id, username, quiz_data, score_percentage):
        """
        Handle quiz completion and trigger live leaderboard update
        
        Args:
            user_id (int): User ID who completed the quiz
            username (str): Username for display purposes
            quiz_data (dict): Quiz metadata (category, type, etc.)
            score_percentage (float): Score as percentage (0-100)
        """
        try:
            # Extract category from quiz data
            category = quiz_data.get('category', 'networking')
            quiz_type = quiz_data.get('type', 'quiz')
            difficulty = quiz_data.get('difficulty', 'medium')
            
            # Trigger live leaderboard update
            socketio.emit('score_achieved', {
                'user_id': user_id,
                'username': username,
                'score': score_percentage,
                'category': category,
                'challenge_type': quiz_type,
                'difficulty': difficulty,
                'timestamp': datetime.utcnow().isoformat()
            }, room='leaderboard')
            
            print(f"✅ Live leaderboard updated: {username} scored {score_percentage}% in {category}")
            
        except Exception as e:
            print(f"❌ Error updating live leaderboard: {e}")
    
    @staticmethod
    def handle_simulation_completion(user_id, username, simulation_data, performance_metrics):
        """
        Handle simulation completion and trigger live leaderboard update
        
        Args:
            user_id (int): User ID who completed the simulation
            username (str): Username for display purposes
            simulation_data (dict): Simulation metadata
            performance_metrics (dict): Performance data including score
        """
        try:
            category = simulation_data.get('category', 'troubleshooting')
            scenario_type = simulation_data.get('scenario_type', 'network_troubleshooting')
            score_percentage = performance_metrics.get('overall_score', 0)
            
            # Additional metrics for rich notifications
            completion_time = performance_metrics.get('completion_time_seconds', 0)
            steps_completed = performance_metrics.get('steps_completed', 0)
            total_steps = performance_metrics.get('total_steps', 0)
            
            # Trigger live leaderboard update with additional context
            socketio.emit('score_achieved', {
                'user_id': user_id,
                'username': username,
                'score': score_percentage,
                'category': category,
                'challenge_type': 'simulation',
                'scenario_type': scenario_type,
                'completion_time': completion_time,
                'steps_completed': steps_completed,
                'total_steps': total_steps,
                'timestamp': datetime.utcnow().isoformat()
            }, room='leaderboard')
            
            print(f"✅ Simulation completion broadcast: {username} - {score_percentage}% in {category}")
            
        except Exception as e:
            print(f"❌ Error broadcasting simulation completion: {e}")
    
    @staticmethod
    def handle_collaboration_completion(participants, session_data, team_score):
        """
        Handle collaborative session completion
        
        Args:
            participants (list): List of user dictionaries with id and username
            session_data (dict): Collaboration session metadata
            team_score (float): Team score percentage
        """
        try:
            category = 'collaboration'
            session_type = session_data.get('type', 'team_troubleshooting')
            
            # Broadcast for each participant
            for participant in participants:
                socketio.emit('score_achieved', {
                    'user_id': participant['id'],
                    'username': participant['username'],
                    'score': team_score,
                    'category': category,
                    'challenge_type': 'collaboration',
                    'session_type': session_type,
                    'team_size': len(participants),
                    'participants': [p['username'] for p in participants],
                    'timestamp': datetime.utcnow().isoformat()
                }, room='leaderboard')
            
            # Special team achievement notification
            socketio.emit('team_achievement', {
                'participants': participants,
                'team_score': team_score,
                'session_type': session_type,
                'timestamp': datetime.utcnow().isoformat()
            }, room='leaderboard')
            
            print(f"✅ Team achievement broadcast: {len(participants)} participants - {team_score}%")
            
        except Exception as e:
            print(f"❌ Error broadcasting team achievement: {e}")

# Example integration with existing quiz system
def integrate_with_quiz_system():
    """Example of how to integrate with existing quiz completion handler"""
    
    def enhanced_quiz_completion_handler(user, quiz, user_answers, score_data):
        """Enhanced quiz completion handler with live leaderboard integration"""
        
        # Existing quiz completion logic
        score_percentage = calculate_quiz_score(quiz, user_answers)
        save_quiz_result(user.id, quiz.id, score_percentage)
        
        # NEW: Live leaderboard integration
        LiveLeaderboardIntegration.handle_quiz_completion(
            user_id=user.id,
            username=user.username,
            quiz_data={
                'category': quiz.category,
                'type': quiz.quiz_type,
                'difficulty': quiz.difficulty,
                'question_count': len(quiz.questions)
            },
            score_percentage=score_percentage
        )
        
        return score_percentage

# Example integration with simulation system
def integrate_with_simulation_system():
    """Example of how to integrate with existing simulation completion handler"""
    
    def enhanced_simulation_completion_handler(user, simulation, performance_data):
        """Enhanced simulation completion handler with live leaderboard integration"""
        
        # Existing simulation completion logic
        final_score = calculate_simulation_score(simulation, performance_data)
        save_simulation_result(user.id, simulation.id, final_score, performance_data)
        
        # NEW: Live leaderboard integration
        LiveLeaderboardIntegration.handle_simulation_completion(
            user_id=user.id,
            username=user.username,
            simulation_data={
                'category': simulation.category,
                'scenario_type': simulation.scenario_type,
                'difficulty': simulation.difficulty
            },
            performance_metrics={
                'overall_score': final_score,
                'completion_time_seconds': performance_data.get('total_time', 0),
                'steps_completed': performance_data.get('completed_steps', 0),
                'total_steps': simulation.total_steps,
                'errors_made': performance_data.get('error_count', 0)
            }
        )
        
        return final_score

# Example integration with collaboration system
def integrate_with_collaboration_system():
    """Example of how to integrate with existing collaboration completion handler"""
    
    def enhanced_collaboration_completion_handler(session, participants, session_results):
        """Enhanced collaboration completion handler with live leaderboard integration"""
        
        # Existing collaboration completion logic
        team_score = calculate_team_score(session, session_results)
        save_collaboration_results(session.id, participants, team_score, session_results)
        
        # NEW: Live leaderboard integration
        participant_data = [
            {'id': p.user_id, 'username': p.username} 
            for p in participants
        ]
        
        LiveLeaderboardIntegration.handle_collaboration_completion(
            participants=participant_data,
            session_data={
                'type': session.session_type,
                'scenario': session.scenario_name,
                'duration_minutes': session.duration_minutes
            },
            team_score=team_score
        )
        
        return team_score

# Utility functions for integration
def calculate_quiz_score(quiz, user_answers):
    """Calculate quiz score percentage"""
    correct_answers = 0
    total_questions = len(quiz.questions)
    
    for question in quiz.questions:
        if user_answers.get(str(question.id)) == question.correct_answer:
            correct_answers += 1
    
    return (correct_answers / total_questions) * 100 if total_questions > 0 else 0

def calculate_simulation_score(simulation, performance_data):
    """Calculate simulation score based on performance metrics"""
    # Example scoring algorithm
    base_score = performance_data.get('base_score', 0)
    time_bonus = performance_data.get('time_bonus', 0)
    error_penalty = performance_data.get('error_penalty', 0)
    
    final_score = base_score + time_bonus - error_penalty
    return max(0, min(100, final_score))  # Clamp between 0 and 100

def calculate_team_score(session, session_results):
    """Calculate team collaboration score"""
    # Example team scoring algorithm
    individual_scores = [result.individual_score for result in session_results]
    team_coordination_bonus = session_results[0].coordination_score if session_results else 0
    
    average_individual = sum(individual_scores) / len(individual_scores) if individual_scores else 0
    final_team_score = (average_individual * 0.8) + (team_coordination_bonus * 0.2)
    
    return final_team_score

def save_quiz_result(user_id, quiz_id, score):
    """Save quiz result to database"""
    # Implementation would save to Score model
    pass

def save_simulation_result(user_id, simulation_id, score, performance_data):
    """Save simulation result to database"""
    # Implementation would save to Score model with additional metadata
    pass

def save_collaboration_results(session_id, participants, team_score, session_results):
    """Save collaboration results to database"""
    # Implementation would save individual and team scores
    pass

# Example usage
if __name__ == "__main__":
    print("🏆 Live Leaderboard Integration Examples")
    print("This module shows how to integrate the live leaderboard system")
    print("with your existing scoring and challenge completion systems.")
    print()
    print("Key Integration Points:")
    print("1. Quiz completion handlers")
    print("2. Simulation completion handlers") 
    print("3. Collaboration session handlers")
    print("4. Real-time WebSocket events")
    print("5. Database score tracking")
    print()
    print("See the functions above for detailed implementation examples.")
