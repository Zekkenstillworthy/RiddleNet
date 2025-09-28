from __init__ import create_app, db
from admin.models.collaboration import CollaborationSetting

app = create_app()
with app.app_context():
    settings = CollaborationSetting.query.filter_by(simulation_id=70).first()
    if settings:
        print('Collaboration settings found for simulation 70:')
        print(f'  Enabled: {settings.collaboration_enabled}')
        print(f'  Team size: {settings.team_size}')
        print(f'  Chat enabled: {settings.chat_enabled}')
    else:
        print('No collaboration settings found for simulation 70')
    
    # Check for simulation 1 as well
    settings = CollaborationSetting.query.filter_by(simulation_id=1).first()
    if settings:
        print('Collaboration settings found for simulation 1:')
        print(f'  Enabled: {settings.collaboration_enabled}')
        print(f'  Team size: {settings.team_size}')
        print(f'  Chat enabled: {settings.chat_enabled}')
    else:
        print('No collaboration settings found for simulation 1')