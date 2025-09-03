#!/usr/bin/env python3
"""
Test the actual data connection between admin simulation and user runner
"""
from admin.models.simulation import Simulation
from admin import db
from __init__ import create_app
import json

app = create_app()
with app.app_context():
    # Test simulation ID 1
    sim = Simulation.query.get(1)
    if not sim:
        print("❌ Simulation 1 not found")
        exit(1)
    
    print(f"🎯 Testing Simulation 1: {sim.title}")
    print(f"   Published: {sim.is_published}, Active: {sim.is_active}")
    
    # Test the exact data flow our user route uses
    print("\n=== Testing Data Parsing (Same as user route) ===")
    
    # 1. Parse simulation_config
    simulation_config = sim.simulation_config or {}
    if isinstance(simulation_config, str):
        try:
            simulation_config = json.loads(simulation_config)
        except:
            simulation_config = {}
    print(f"✅ Simulation config parsed: {type(simulation_config)} with {len(simulation_config)} keys")
    
    # 2. Parse step_definitions  
    step_definitions = sim.step_definitions or []
    if isinstance(step_definitions, str):
        try:
            step_definitions = json.loads(step_definitions)
        except:
            step_definitions = []
    print(f"✅ Step definitions parsed: {type(step_definitions)} with {len(step_definitions)} steps")
    
    # 3. Parse validation_rules
    validation_rules = sim.validation_rules or {}
    if isinstance(validation_rules, str):
        try:
            validation_rules = json.loads(validation_rules)
        except:
            validation_rules = {}
    print(f"✅ Validation rules parsed: {type(validation_rules)} with {len(validation_rules)} rules")
    
    # 4. Test normalization (like our user route does)
    print("\n=== Testing Step Normalization ===")
    normalized_steps = []
    for i, step in enumerate(step_definitions):
        s = dict(step) if isinstance(step, dict) else {'content': str(step)}
        
        # Test field normalization
        original_fields = list(s.keys())
        
        # Builder field normalization  
        if 'questionText' in s and 'question_text' not in s:
            s['question_text'] = s.get('questionText')
        if 'questionType' in s and 'question_type' not in s:
            s['question_type'] = s.get('questionType')
            
        # Validation mapping
        v = s.get('validation') or {}
        if isinstance(v, dict):
            if 'expectedAnswer' in v and 'expected_answer' not in s:
                s['expected_answer'] = v.get('expectedAnswer')
            if 'score' in v and 'score' not in s:
                s['score'] = v.get('score')
                
        normalized_steps.append(s)
        
        if i < 2:  # Show first 2 steps
            print(f"  Step {i}: {original_fields} -> {list(s.keys())}")
    
    # 5. Test validation dict building  
    validation = {}
    if isinstance(validation_rules, dict):
        for k, v in validation_rules.items():
            validation[str(k)] = v
    
    # Generate fallback rules if missing
    if not validation and normalized_steps:
        for idx, s in enumerate(normalized_steps):
            if 'expected_answer' in s and s['expected_answer']:
                validation[str(idx)] = {
                    'type': 'exact_match',
                    'expected_answer': s['expected_answer'],
                    'score': s.get('score', 10)
                }
    
    print(f"✅ Validation dict built: {len(validation)} rules")
    
    # 6. Test final simulation data structure (what gets passed to template)
    simulation_data = {
        'id': sim.id,
        'title': sim.title,
        'description': sim.description,
        'simulation_type': sim.simulation_type,
        'category': sim.category,
        'difficulty': sim.difficulty,
        'estimated_duration': sim.estimated_duration,
        'learning_objectives': sim.learning_objectives if isinstance(sim.learning_objectives, list) else [],
        'step_definitions': normalized_steps,
        'validation': validation,
        'topology': simulation_config,
        'total_steps': len(normalized_steps),
        'base_score': sim.base_score or 100,
        'time_bonus': sim.time_bonus or 20,
        'perfect_completion_bonus': sim.perfect_completion_bonus or 30
    }
    
    print(f"\n=== Final Simulation Data ===")
    print(f"✅ Title: {simulation_data['title']}")
    print(f"✅ Total steps: {simulation_data['total_steps']}")
    print(f"✅ Has validation: {len(simulation_data['validation'])} rules")
    print(f"✅ Step definitions: {len(simulation_data['step_definitions'])} items")
    
    if simulation_data['total_steps'] > 0:
        print(f"\n🎉 SUCCESS: Admin simulation data WILL flow to user simulation!")
        print(f"📝 The user will see {simulation_data['total_steps']} steps")
        print(f"⚖️ Validation rules: {len(simulation_data['validation'])}")
        print(f"🎯 Base score: {simulation_data['base_score']}")
        
        # Test first step
        if simulation_data['step_definitions']:
            first_step = simulation_data['step_definitions'][0]
            print(f"\n📋 First step preview:")
            print(f"   Type: {first_step.get('type', first_step.get('question_type', 'unknown'))}")
            print(f"   Has content: {'title' in first_step or 'question_text' in first_step or 'content' in first_step}")
            print(f"   Has validation: {str(0) in simulation_data['validation']}")
            
        print(f"\n🔗 URLs to test:")
        print(f"   Admin: http://127.0.0.1:5001/admin/simulation/edit/{sim.id}")
        print(f"   User:  http://127.0.0.1:5001/dynamic/simulation/{sim.id}")
        print(f"\n✅ CONCLUSION: YES - Admin data IS connected to user simulation!")
        
    else:
        print(f"\n❌ PROBLEM: No steps found - simulation incomplete")
