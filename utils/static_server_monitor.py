"""
Static server monitor utility - ensures static server is available
"""
import requests
import time
import logging
import threading

# Configure logging
logger = logging.getLogger(__name__)

class StaticServerMonitor:
    """Monitor static server availability and health"""
    
    def __init__(self, url="http://localhost:5001/health", check_interval=30):
        self.static_server_url = url
        self.check_interval = check_interval
        self.available = False
        self.last_check_time = 0
        self.monitor_thread = None
        self.running = False
    
    def check_availability(self):
        """Check if static server is available"""
        try:
            response = requests.get(self.static_server_url, timeout=2)
            self.available = response.status_code == 200
            self.last_check_time = time.time()
            return self.available
        except Exception as e:
            logger.warning(f"Static server not available: {e}")
            self.available = False
            self.last_check_time = time.time()
            return False
    
    def start_monitoring(self):
        """Start monitoring thread"""
        if self.monitor_thread and self.monitor_thread.is_alive():
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def _monitor_loop(self):
        """Monitoring loop"""
        while self.running:
            status = self.check_availability()
            if not status:
                logger.warning("⚠️ Static file server is not available! Media files may not load correctly.")
                print("⚠️ WARNING: Static file server is not available! Media files may not load correctly.")
            else:
                logger.debug("Static file server is available")
            
            # Sleep for the check interval
            time.sleep(self.check_interval)
    
    def stop_monitoring(self):
        """Stop monitoring thread"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)


# Create a singleton instance
static_server_monitor = StaticServerMonitor()
