#!/usr/bin/env python3
"""Quick script to check WebSocket monitor status"""

try:
    from utils.socket_monitor import socket_monitor
    print('Socket Monitor Status:')
    print(f'Total connections: {socket_monitor.total_connections}')
    print(f'Active connections: {len(socket_monitor.active_connections)}')
    print(f'Total errors: {len(socket_monitor.errors)}')
    
    if socket_monitor.errors:
        print('\nRecent errors:')
        for i, error in enumerate(socket_monitor.errors[-5:], 1):
            print(f'  {i}. {error}')
    
    if socket_monitor.active_connections:
        print('\nActive connections:')
        for sid, info in socket_monitor.active_connections.items():
            print(f'  {sid}: User {info.get("user_id", "Unknown")}')
            
except Exception as e:
    print(f"Error checking status: {e}")
