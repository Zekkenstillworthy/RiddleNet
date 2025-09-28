from __init__ import create_app, db
from admin.models.user import Admin

app = create_app()
with app.app_context():
    admins = Admin.query.all()
    print(f"Found {len(admins)} admin(s):")
    for admin in admins:
        print(f"  ID: {admin.id}, Username: {admin.username}")
    
    if admins:
        admin_id = admins[0].id
        print(f"Using admin ID: {admin_id}")
        
        from admin.models.collaboration import CollaborationSetting
        
        # Create collaboration settings for simulation 70
        setting = CollaborationSetting(
            simulation_id=70,
            class_id=None,  # Allow all classes
            collaboration_enabled=True,
            team_size=2,
            shared_terminal=False,
            individual_terminals=True,
            follow_leader=False,
            chat_enabled=True,
            transcript_logging=False,
            allow_late_join=True,
            require_instructor=False,
            time_window=None,
            roles=['Leader', 'Observer', 'Operator'],
            created_by=admin_id
        )
        
        db.session.add(setting)
        
        # Also create for simulation 1
        setting2 = CollaborationSetting(
            simulation_id=1,
            class_id=None,  # Allow all classes
            collaboration_enabled=True,
            team_size=2,
            shared_terminal=False,
            individual_terminals=True,
            follow_leader=False,
            chat_enabled=True,
            transcript_logging=False,
            allow_late_join=True,
            require_instructor=False,
            time_window=None,
            roles=['Leader', 'Observer', 'Operator'],
            created_by=admin_id
        )
        
        db.session.add(setting2)
        
        try:
            db.session.commit()
            print("✅ Successfully created collaboration settings for simulations 70 and 1")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating collaboration settings: {e}")
    else:
        print("❌ No admin users found in database")