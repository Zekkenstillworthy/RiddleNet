#!/usr/bin/env python3
"""
Diagnostic script to check if question groups are assigned to modules
"""
from application import create_app
from instructor.models.module import Module
from instructor.models.question_group import QuestionGroup

app = create_app()

with app.app_context():
    print("=" * 80)
    print("MODULE QUESTION GROUP ASSIGNMENTS DIAGNOSTIC")
    print("=" * 80)
    
    # Get the one question group we found
    question_group = QuestionGroup.query.get(1)
    
    if question_group:
        print(f"\n📚 Question Group: '{question_group.name}' (ID: {question_group.id})")
        print(f"   Questions: {len(question_group.questions or [])}")
        
        # Check if it's assigned to any modules
        try:
            # Check via reverse relationship (if it exists)
            if hasattr(question_group, 'modules'):
                modules = question_group.modules
                print(f"   Assigned to {len(modules)} modules:")
                for mod in modules:
                    print(f"      - Module {mod.id}: '{mod.title}'")
            else:
                print("   ⚠️  Question group has no 'modules' relationship")
        except Exception as e:
            print(f"   ⚠️  Error checking modules relationship: {e}")
        
        # Check from module side
        print(f"\n🔍 Checking all modules for question group assignments...")
        all_modules = Module.query.all()
        print(f"   Total modules: {len(all_modules)}")
        
        modules_with_qg = []
        for mod in all_modules:
            if hasattr(mod, 'question_groups'):
                try:
                    qgroups = list(mod.question_groups)
                    if qgroups:
                        qg_ids = [qg.id for qg in qgroups]
                        if 1 in qg_ids:
                            modules_with_qg.append(mod)
                            print(f"   ✅ Module {mod.id}: '{mod.title}' HAS Question Group 1")
                except Exception as e:
                    print(f"   ⚠️  Error checking module {mod.id}: {e}")
        
        if not modules_with_qg:
            print("\n❌ PROBLEM FOUND: Question Group 1 is NOT assigned to any modules!")
            print("   This is why __lessonQuestions is empty - no module has this question group.")
        else:
            print(f"\n✅ Question Group 1 is assigned to {len(modules_with_qg)} module(s)")
    else:
        print("\n❌ Question Group 1 not found!")
    
    # Check module_question_groups table directly
    print(f"\n🔍 Checking module_question_groups association table...")
    try:
        from __init__ import db
        result = db.session.execute(db.text("SELECT * FROM module_question_groups"))
        rows = result.fetchall()
        print(f"   Total associations: {len(rows)}")
        for row in rows:
            print(f"      Module {row[0]} ↔ Question Group {row[1]}")
        
        if len(rows) == 0:
            print("\n❌ PROBLEM CONFIRMED: module_question_groups table is EMPTY!")
            print("   No question groups are assigned to any modules.")
    except Exception as e:
        print(f"   ⚠️  Error querying module_question_groups: {e}")
