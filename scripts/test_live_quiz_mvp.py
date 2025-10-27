"""
Test Live Quiz MVP Flow
Tests the complete end-to-end live quiz system:
1. Instructor creates quiz
2. Student joins quiz
3. Instructor starts quiz
4. Student submits answers
5. Leaderboard updates
6. Quiz ends with final results
"""
import os
import requests
import time
import json
from requests import RequestException

BASE_URL = "http://127.0.0.1:5001"
LIVE_QUIZ_MVP_BASE = f"{BASE_URL}/api/live-quiz-mvp"

# Test data (override with env vars for local creds)
INSTRUCTOR_CREDENTIALS = {
    "email": os.getenv("RIDDLENET_INSTRUCTOR_EMAIL", "admin@example.com"),
    "password": os.getenv("RIDDLENET_INSTRUCTOR_PASSWORD", "admin")
}

STUDENT_CREDENTIALS = {
    "email": os.getenv("RIDDLENET_STUDENT_EMAIL", "student@example.com"),
    "password": os.getenv("RIDDLENET_STUDENT_PASSWORD", "password")
}

TEST_CLASS_ID = 7
TEST_MODULE_ID = 1
TEST_QUESTION_GROUP_ID = 1  # Update with actual question group ID


class LiveQuizTester:
    def __init__(self):
        self.instructor_session = requests.Session()
        self.student_session = requests.Session()
        self.quiz_session_id = None
        self.session_code = None
        self.participant_id = None
        
    @staticmethod
    def _was_redirected_to(response, path_fragment: str) -> bool:
        """True if the response or redirect history includes the target path."""
        fragment = path_fragment.lower()
        if fragment in response.url.lower():
            return True
        for hop in response.history:
            location = hop.headers.get('Location', '').lower()
            if fragment in location:
                return True
        return False

    def login_instructor(self):
        """Login as instructor"""
        print("\n1️⃣ Logging in as Instructor...")
        try:
            response = self.instructor_session.post(
                f"{BASE_URL}/instructor/login",
                data=INSTRUCTOR_CREDENTIALS,
                allow_redirects=True,
                timeout=15
            )
        except RequestException as exc:
            print(f"[ERROR] Instructor login request failed: {exc}")
            return False

        print(f"   [DEBUG] Instructor login final URL: {response.url}")
        if response.status_code >= 400:
            print(f"[ERROR] Instructor login failed with status {response.status_code}")
            return False

        if self._was_redirected_to(response, '/instructor/dashboard'):
            print("[OK] Instructor logged in successfully")
            return True

        if self._was_redirected_to(response, '/instructor/login') or 'Invalid admin credentials' in response.text:
            print("[ERROR] Instructor credentials were rejected. Update RIDDLENET_INSTRUCTOR_EMAIL/PASSWORD.")
            return False

        print("[WARNING] Instructor login returned an unexpected page; verify credentials and 2FA status.")
        return False
    
    def login_student(self):
        """Login as student"""
        print("\n2️⃣ Logging in as Student...")
        try:
            response = self.student_session.post(
                f"{BASE_URL}/login",
                data=STUDENT_CREDENTIALS,
                allow_redirects=True,
                timeout=15
            )
        except RequestException as exc:
            print(f"[ERROR] Student login request failed: {exc}")
            return False

        print(f"   [DEBUG] Student login final URL: {response.url}")
        if response.status_code >= 400:
            print(f"[ERROR] Student login failed with status {response.status_code}")
            return False

        if self._was_redirected_to(response, '/dashboard'):
            print("[OK] Student logged in successfully")
            return True

        if self._was_redirected_to(response, '/login') or 'Invalid email' in response.text:
            print("[ERROR] Student credentials were rejected. Update RIDDLENET_STUDENT_EMAIL/PASSWORD.")
            return False

        print("[WARNING] Student login returned an unexpected page; verify credentials or OTP requirements.")
        return False
    
    def create_quiz(self):
        """Instructor creates a live quiz"""
        print("\n3️⃣ Creating Live Quiz Session...")
        
        payload = {
            "question_group_id": TEST_QUESTION_GROUP_ID,
            "class_id": TEST_CLASS_ID,
            "module_id": TEST_MODULE_ID,
            "title": "MVP Test Live Quiz",
            "time_per_question": 30,
            "show_leaderboard": True,
            "allow_join_after_start": True,
            "randomize_questions": False,
            "randomize_answers": False
        }
        
        response = self.instructor_session.post(
            f"{BASE_URL}/instructor/api/live-quiz/create",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                self.quiz_session_id = data['session']['id']
                self.session_code = data['session']['session_code']
                print(f"[OK] Quiz created with ID: {self.quiz_session_id}")
                print(f"   Session Code: {self.session_code}")
                return True
            else:
                print(f"[ERROR] Quiz creation failed: {data.get('error')}")
                return False
        else:
            print(f"[ERROR] Quiz creation request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def student_join_quiz(self):
        """Student joins the live quiz"""
        print(f"\n4️⃣ Student Joining Quiz (ID: {self.quiz_session_id})...")
        
        payload = {
            "quiz_id": self.quiz_session_id
        }
        
        response = self.student_session.post(
            f"{LIVE_QUIZ_MVP_BASE}/join",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                self.participant_id = data['participant']['id']
                print(f"[OK] Student joined successfully")
                print(f"   Participant ID: {self.participant_id}")
                return True
            else:
                print(f"[ERROR] Join failed: {data.get('error')}")
                return False
        else:
            print(f"[ERROR] Join request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def instructor_start_quiz(self):
        """Instructor starts the quiz"""
        print(f"\n5️⃣ Instructor Starting Quiz (ID: {self.quiz_session_id})...")
        
        # Test both URL formats
        urls = [
            f"{BASE_URL}/instructor/api/live-quiz/{self.quiz_session_id}/start",
            f"{BASE_URL}/instructor/api/live-quiz/session/{self.quiz_session_id}/start"
        ]
        
        for url in urls:
            print(f"   Testing URL: {url}")
            response = self.instructor_session.post(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"[OK] Quiz started successfully via {url}")
                    return True
                else:
                    print(f"[WARNING] Start failed: {data.get('error')}")
            else:
                print(f"[WARNING] Start request failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
        
        return False
    
    def get_quiz_questions(self):
        """Student gets quiz questions"""
        print(f"\n6️⃣ Student Getting Quiz Questions...")
        
        response = self.student_session.get(
            f"{LIVE_QUIZ_MVP_BASE}/questions/{self.quiz_session_id}"
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                questions = data.get('questions', [])
                print(f"[OK] Retrieved {len(questions)} questions")
                return questions
            else:
                print(f"[ERROR] Failed to get questions: {data.get('error')}")
                return []
        else:
            print(f"[ERROR] Questions request failed: {response.status_code}")
            return []
    
    def submit_answer(self, question_id, answer):
        """Student submits an answer"""
        print(f"   [NOTE] Submitting answer for question {question_id}...")
        
        payload = {
            "session_id": self.quiz_session_id,
            "question_id": question_id,
            "selected_answer": answer,
            "response_time": 5.0
        }
        
        response = self.student_session.post(
            f"{LIVE_QUIZ_MVP_BASE}/submit-answer",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                is_correct = data.get('is_correct')
                points = data.get('points_awarded', 0)
                print(f"   {'[OK] Correct' if is_correct else '[ERROR] Incorrect'} - {points} points")
                return True
            else:
                print(f"   [WARNING] Submit failed: {data.get('error')}")
                return False
        else:
            print(f"   [WARNING] Submit request failed: {response.status_code}")
            return False
    
    def get_leaderboard(self):
        """Get current leaderboard"""
        print(f"\n7️⃣ Getting Leaderboard...")
        
        response = self.instructor_session.get(
            f"{BASE_URL}/instructor/api/live-quiz/{self.quiz_session_id}/leaderboard"
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                leaderboard = data.get('leaderboard', [])
                print(f"[OK] Leaderboard retrieved ({len(leaderboard)} participants):")
                for entry in leaderboard[:5]:
                    print(f"   #{entry['rank']} - {entry['display_name']}: {entry['total_score']} pts ({entry['total_correct']} correct)")
                return True
            else:
                print(f"[ERROR] Leaderboard failed: {data.get('error')}")
                return False
        else:
            print(f"[ERROR] Leaderboard request failed: {response.status_code}")
            return False
    
    def instructor_end_quiz(self):
        """Instructor ends the quiz"""
        print(f"\n8️⃣ Instructor Ending Quiz...")
        
        response = self.instructor_session.post(
            f"{BASE_URL}/instructor/api/live-quiz/{self.quiz_session_id}/end"
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"[OK] Quiz ended successfully")
                final_leaderboard = data.get('leaderboard', [])
                print(f"\n🏆 Final Leaderboard ({len(final_leaderboard)} participants):")
                for entry in final_leaderboard[:10]:
                    medal = "🥇" if entry['rank'] == 1 else "🥈" if entry['rank'] == 2 else "🥉" if entry['rank'] == 3 else f"#{entry['rank']}"
                    print(f"   {medal} {entry['display_name']}: {entry['total_score']} pts")
                return True
            else:
                print(f"[ERROR] End quiz failed: {data.get('error')}")
                return False
        else:
            print(f"[ERROR] End quiz request failed: {response.status_code}")
            return False
    
    def run_full_test(self):
        """Run complete MVP test flow"""
        print("=" * 60)
        print("🚀 LIVE QUIZ MVP TEST")
        print("=" * 60)
        
        # Step 1: Login instructor
        if not self.login_instructor():
            print("\n[ERROR] Test failed at instructor login")
            return False
        
        # Step 2: Login student
        if not self.login_student():
            print("\n[ERROR] Test failed at student login")
            return False
        
        # Step 3: Create quiz
        if not self.create_quiz():
            print("\n[ERROR] Test failed at quiz creation")
            return False
        
        # Step 4: Student joins
        if not self.student_join_quiz():
            print("\n[ERROR] Test failed at student join")
            return False
        
        # Step 5: Start quiz
        if not self.instructor_start_quiz():
            print("\n[ERROR] Test failed at quiz start")
            return False
        
        # Step 6: Get questions
        questions = self.get_quiz_questions()
        if not questions:
            print("\n[ERROR] Test failed at getting questions")
            return False
        
        # Step 7: Submit answers
        print(f"\n7️⃣ Student Submitting Answers...")
        for i, question in enumerate(questions[:3], 1):  # Test first 3 questions
            print(f"\n   Question {i}/{min(3, len(questions))}: {question.get('question', '')[:50]}...")
            # Submit the first option as answer (for testing)
            answer = question.get('options', ['A'])[0] if question.get('options') else 'A'
            self.submit_answer(question['id'], answer)
            time.sleep(1)  # Small delay between submissions
        
        # Step 8: Check leaderboard
        if not self.get_leaderboard():
            print("\n[WARNING] Leaderboard check failed, continuing...")
        
        # Step 9: End quiz
        if not self.instructor_end_quiz():
            print("\n[ERROR] Test failed at quiz end")
            return False
        
        print("\n" + "=" * 60)
        print("[OK] LIVE QUIZ MVP TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        return True


if __name__ == "__main__":
    tester = LiveQuizTester()
    success = tester.run_full_test()
    
    if not success:
        exit(1)
