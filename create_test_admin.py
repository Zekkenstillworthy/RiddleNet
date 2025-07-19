#!/usr/bin/env python3
"""
Create test admin user and sample data for testing the essay system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from admin import db
from admin.models.user import Admin
from admin.models.class_model import Class
from admin.models.essay_response import EssayResponse
from user.models.user import User
from datetime import datetime, timedelta
import random

def create_test_data():
    """Create test admin, classes, users, and essays"""
    try:
        # Create test admin
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(
                username='admin',
                email='admin@riddlenet.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("✅ Created admin user (username: admin, password: admin123)")
        else:
            print("✅ Admin user already exists")

        # Create test classes
        class_names = [
            ("Networking Fundamentals", "NET101", "A"),
            ("Network Security", "SEC201", "B"), 
            ("Advanced Routing", "ADV301", "A"),
            ("Troubleshooting Basics", "TRB101", "C")
        ]
        
        classes = []
        for name, code, section in class_names:
            existing_class = Class.query.filter_by(code=code).first()
            if not existing_class:
                new_class = Class(
                    name=name,
                    code=code,
                    section=section,
                    description=f"Sample class for {name}",
                    created_at=datetime.utcnow()
                )
                db.session.add(new_class)
                classes.append(new_class)
                print(f"✅ Created class: {name} ({code})")
            else:
                classes.append(existing_class)
                print(f"✅ Class already exists: {name}")

        # Create test users/students
        student_names = [
            ("alice", "alice@student.com", "Alice Johnson"),
            ("bob", "bob@student.com", "Bob Smith"),
            ("charlie", "charlie@student.com", "Charlie Brown"),
            ("diana", "diana@student.com", "Diana Prince"),
            ("eve", "eve@student.com", "Eve Davis"),
            ("frank", "frank@student.com", "Frank Miller"),
            ("grace", "grace@student.com", "Grace Lee"),
            ("henry", "henry@student.com", "Henry Wilson")
        ]
        
        students = []
        for username, email, full_name in student_names:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(
                    username=username,
                    email=email,
                    full_name=full_name,
                    created_at=datetime.utcnow()
                )
                new_user.set_password('password123')
                db.session.add(new_user)
                students.append(new_user)
                print(f"✅ Created student: {username}")
            else:
                students.append(existing_user)
                print(f"✅ Student already exists: {username}")

        # Commit users and classes first
        db.session.commit()

        # Assign students to classes
        for i, student in enumerate(students):
            # Assign each student to 1-3 random classes
            num_classes = random.randint(1, 3)
            student_classes = random.sample(classes, num_classes)
            
            for class_obj in student_classes:
                if student not in class_obj.students:
                    class_obj.students.append(student)
                    print(f"✅ Enrolled {student.username} in {class_obj.name}")

        # Create sample essays
        essay_topics = [
            ("What is the OSI model and why is it important?", "topology"),
            ("Explain the difference between TCP and UDP", "riddle"),
            ("How would you troubleshoot a network connectivity issue?", "troubleshoot"),
            ("Describe the process of crimping an Ethernet cable", "crimping"),
            ("What are VLANs and how do they work?", "topology"),
            ("Explain subnetting with an example", "riddle"),
            ("How do you diagnose packet loss?", "troubleshoot"),
            ("What tools are needed for cable crimping?", "crimping")
        ]
        
        sample_answers = [
            "The OSI model is a conceptual framework that describes how data communication occurs between devices...",
            "TCP is connection-oriented while UDP is connectionless. TCP provides reliability through acknowledgments...",
            "To troubleshoot connectivity, I would start by checking physical connections, then verify IP configuration...",
            "Cable crimping requires a crimping tool, RJ45 connectors, and proper cable stripping technique...",
            "VLANs create logical network segments within a physical network, improving security and performance...",
            "Subnetting divides a network into smaller segments. For example, 192.168.1.0/24 can be divided...",
            "Packet loss can be diagnosed using tools like ping, traceroute, and network monitoring software...",
            "Essential tools include wire strippers, crimping tool, cable tester, and RJ45 connectors..."
        ]

        for student in students:
            # Create 2-5 essays per student
            num_essays = random.randint(2, 5)
            for i in range(num_essays):
                topic, category = random.choice(essay_topics)
                answer = random.choice(sample_answers)
                
                # Create essay with random submission date in the past 30 days
                submission_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
                
                essay = EssayResponse(
                    user_id=student.id,
                    question_text=topic,
                    response_text=answer,
                    category=category,
                    submission_date=submission_date,
                    is_graded=random.choice([True, False]),
                    graded_score=random.randint(70, 100) if random.choice([True, False]) else None
                )
                
                db.session.add(essay)
                print(f"✅ Created essay for {student.username}: {topic[:50]}...")

        # Final commit
        db.session.commit()
        print("\n🎉 Test data creation completed successfully!")
        print("\nYou can now log in with:")
        print("Username: admin")
        print("Password: admin123")
        print("\nAnd visit: http://localhost:5001/admin/essays")

    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        db.session.rollback()
        raise

if __name__ == "__main__":
    # Initialize the app context
    from admin.app import AdminApp
    
    admin_app = AdminApp()
    
    with admin_app.app.app_context():
        print("🚀 Creating test data for RiddleNet Essay System...")
        create_test_data()
