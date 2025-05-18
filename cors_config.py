from flask import Flask
from flask_cors import CORS

def enable_cors_for_apis(app):
    """
    Enable CORS for the topology and troubleshooting API endpoints.
    This will allow the endpoints to be accessed from the frontend even when the user is not logged in.
    """
    # Create a CORS instance specifically for these routes
    cors = CORS(app, resources={
        r"/admin/topology/*": {"origins": "*"},
        r"/admin/troubleshooting/*": {"origins": "*"}
    })
    print("CORS enabled for /admin/topology/* and /admin/troubleshooting/* routes")
    return cors

# Import this function in run.py and call it after creating the app:
# from cors_config import enable_cors_for_apis
# enable_cors_for_apis(app)
