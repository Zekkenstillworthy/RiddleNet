"""
Quick script to reset all active live quiz sessions to 'waiting' status
"""
from application import application
from __init__ import db
from user.models.live_quiz import LiveQuizSession

with application.app_context():
    # Find all active sessions
    sessions = LiveQuizSession.query.filter_by(status='active').all()
    
    print(f'\n{"="*80}')
    print(f'Found {len(sessions)} active session(s)')
    print(f'{"="*80}\n')
    
    if sessions:
        for s in sessions:
            print(f'Session {s.id}:')
            print(f'  Title: {s.title}')
            print(f'  Code: {s.session_code}')
            print(f'  Started at: {s.started_at}')
            print(f'  Status: {s.status} -> waiting')
            
            # Reset to waiting
            s.status = 'waiting'
            s.started_at = None
            s.ended_at = None
            print()
        
        db.session.commit()
        print(f'{"="*80}')
        print(f'✅ Successfully reset {len(sessions)} session(s) to "waiting" status')
        print(f'{"="*80}\n')
    else:
        print('✅ No active sessions found - database is already clean\n')
