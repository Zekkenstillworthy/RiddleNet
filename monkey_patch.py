import eventlet
eventlet.monkey_patch()
# This file exists only to ensure monkey patching happens
# before any other imports
print("Eventlet monkey patching completed successfully")
