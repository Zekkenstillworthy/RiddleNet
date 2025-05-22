"""
Utilities for monitoring WebSocket connection health and performance
"""
import time
import threading
import logging
from flask import request, current_app

# Configure logging
logger = logging.getLogger(__name__)

class SocketConnectionMonitor:
    """
    Monitor WebSocket connections and performance
    """
    def __init__(self):
        self.active_connections = {}
        self.connection_counts = {
            'total': 0,
            'active': 0,
            'disconnected': 0,
            'errors': 0
        }
        self.event_counts = {}
        self.latency_stats = {
            'min': float('inf'),
            'max': 0,
            'avg': 0,
            'samples': 0
        }
        
        # Start background monitoring
        self.monitoring_active = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start the background monitoring thread"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info("Socket connection monitoring started")
    
    def stop_monitoring(self):
        """Stop the background monitoring thread"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
            self.monitor_thread = None
        
        logger.info("Socket connection monitoring stopped")
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Clean up stale connections
                now = time.time()
                stale_connections = []
                
                for sid, conn_info in self.active_connections.items():
                    # Check if connection is stale (no activity for 2 minutes)
                    if now - conn_info['last_activity'] > 120:
                        stale_connections.append(sid)
                
                # Remove stale connections
                for sid in stale_connections:
                    logger.warning(f"Removing stale connection: {sid}")
                    self.connection_counts['disconnected'] += 1
                    self.connection_counts['active'] -= 1
                    del self.active_connections[sid]
                
                # Log current status if connections changed
                if stale_connections:
                    logger.info(f"Connection status: {self.get_connection_stats()}")
                
                # Sleep for 30 seconds before next check
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(60)  # Longer sleep after error
    
    def register_connection(self, sid, user_id=None):
        """Register a new WebSocket connection"""
        self.active_connections[sid] = {
            'user_id': user_id,
            'connected_at': time.time(),
            'last_activity': time.time(),
            'events_sent': 0,
            'events_received': 0,
            'ip': request.remote_addr if request else None
        }
        
        self.connection_counts['total'] += 1
        self.connection_counts['active'] += 1
        
        logger.info(f"New connection: {sid} (User: {user_id})")
    
    def update_activity(self, sid):
        """Update last activity time for a connection"""
        if sid in self.active_connections:
            self.active_connections[sid]['last_activity'] = time.time()
    
    def register_disconnect(self, sid):
        """Register a WebSocket disconnection"""
        if sid in self.active_connections:
            conn_info = self.active_connections[sid]
            duration = time.time() - conn_info['connected_at']
            
            logger.info(f"Connection closed: {sid} (Duration: {duration:.1f}s)")
            
            self.connection_counts['disconnected'] += 1
            self.connection_counts['active'] -= 1
            
            del self.active_connections[sid]
    
    def register_error(self, sid, error):
        """Register a WebSocket error"""
        self.connection_counts['errors'] += 1
        
        if sid in self.active_connections:
            logger.error(f"WebSocket error for {sid}: {str(error)}")
    
    def register_event(self, event_type, direction='in'):
        """Register an event sent or received"""
        key = f"{direction}:{event_type}"
        self.event_counts[key] = self.event_counts.get(key, 0) + 1
    
    def register_latency(self, latency_ms):
        """Register round-trip latency measurement"""
        # Update latency statistics
        self.latency_stats['min'] = min(self.latency_stats['min'], latency_ms)
        self.latency_stats['max'] = max(self.latency_stats['max'], latency_ms)
        
        # Update running average
        total = self.latency_stats['avg'] * self.latency_stats['samples']
        self.latency_stats['samples'] += 1
        self.latency_stats['avg'] = (total + latency_ms) / self.latency_stats['samples']
    
    def get_connection_stats(self):
        """Get current connection statistics"""
        return {
            'connections': self.connection_counts.copy(),
            'active_count': len(self.active_connections),
            'events': self.event_counts.copy(),
            'latency': {
                'min': self.latency_stats['min'] if self.latency_stats['min'] != float('inf') else 0,
                'max': self.latency_stats['max'],
                'avg': self.latency_stats['avg'],
                'samples': self.latency_stats['samples']
            }
        }


# Singleton instance
socket_monitor = SocketConnectionMonitor()

# Start monitoring when imported
if not socket_monitor.monitoring_active:
    socket_monitor.start_monitoring()
