#!/usr/bin/env python3
"""
Simple validation script for enhanced template generator key features
"""

def validate_template_features():
    print("🔍 Validating Enhanced Class Template Generator Changes...")
    
    # Read the enhanced generator file
    try:
        with open('admin/services/enhanced_class_template_generator.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Successfully read enhanced_class_template_generator.py")
        
        # Check for key features
        features_to_check = [
            ("Admin/User dual inheritance", "{% if user_context and user_context.get('is_admin') %}"),
            ("Admin base template", "{% extends \"admin/base.html\" %}"),
            ("User base template", "{% extends \"user/learning_base.html\" %}"),
            ("Admin navigation button", "Back to Admin"),
            ("User navigation button", "Back to Classes"),
            ("Admin badge", "Admin View"),
            ("Cyber-themed styling", "var(--cyber-glow)"),
            ("Learning container styling", ".learning-container"),
            ("Card-based layout", ".content-card"),
            ("Tab navigation", ".nav-tabs"),
            ("Progress stats", ".progress-stats"),
            ("Responsive design", "@media (max-width: 768px)"),
            ("Empty modules placeholder", "Create Your First Module"),
            ("Admin access indicators", "Admin Access Required"),
            ("Chart.js integration", "chart.js"),
            ("CSS animations", "@keyframes"),
        ]
        
        found_features = []
        missing_features = []
        
        for feature_name, search_text in features_to_check:
            if search_text in content:
                found_features.append(feature_name)
            else:
                missing_features.append(feature_name)
        
        print(f"\n✅ Found {len(found_features)} key features:")
        for feature in found_features:
            print(f"   ✓ {feature}")
        
        if missing_features:
            print(f"\n⚠️  Missing {len(missing_features)} features:")
            for feature in missing_features:
                print(f"   ✗ {feature}")
        
        # Check method updates
        method_checks = [
            ("General template method", "_generate_general_template"),
            ("Integrated template method", "_generate_integrated_template"),
            ("Static templates map", "static_templates_map"),
            ("Class type detection", "_detect_class_type"),
        ]
        
        print(f"\n🔧 Method Validation:")
        for method_name, search_text in method_checks:
            if search_text in content:
                print(f"   ✓ {method_name}")
            else:
                print(f"   ✗ {method_name}")
        
        # Validate template structure
        template_structure_checks = [
            ("Dual inheritance block", "{% if user_context and user_context.get('is_admin') %}"),
            ("Head block with CSS", "{% block head %}"),
            ("Content block structure", "{% block content %}"),
            ("Navigation handling", "back-to-classes"),
            ("Admin badge conditional", "admin-badge"),
        ]
        
        print(f"\n📋 Template Structure Validation:")
        for structure_name, search_text in template_structure_checks:
            if search_text in content:
                print(f"   ✓ {structure_name}")
            else:
                print(f"   ✗ {structure_name}")
        
        # Calculate overall score
        total_checks = len(features_to_check) + len(method_checks) + len(template_structure_checks)
        passed_checks = len(found_features) + sum(1 for _, search in method_checks if search in content) + sum(1 for _, search in template_structure_checks if search in content)
        
        score = (passed_checks / total_checks) * 100
        
        print(f"\n🎯 Overall Validation Score: {score:.1f}% ({passed_checks}/{total_checks})")
        
        if score >= 90:
            print("🎉 Excellent! Enhanced template generator is fully updated with all key features!")
        elif score >= 75:
            print("✅ Good! Most features implemented, minor items may need attention.")
        else:
            print("⚠️  Some key features are missing and need to be implemented.")
        
        return score >= 75
        
    except FileNotFoundError:
        print("❌ Could not find enhanced_class_template_generator.py file")
        return False
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return False

if __name__ == "__main__":
    success = validate_template_features()
    if success:
        print("\n✅ Validation completed successfully!")
    else:
        print("\n❌ Validation failed - please check the issues above.")
