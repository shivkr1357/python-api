import os
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List

class CleanupService:
    def __init__(self):
        self.pdf_dir = "outputs/pdfs"
        self.pptx_dir = "outputs/pptx"
        self.cleanup_interval_hours = 24  # Default: 24 hours
        self.is_running = False
        self.cleanup_thread = None
        
        # Create directories if they don't exist
        os.makedirs(self.pdf_dir, exist_ok=True)
        os.makedirs(self.pptx_dir, exist_ok=True)
    
    def start_cleanup_service(self):
        """Start the automatic cleanup service"""
        if not self.is_running:
            self.is_running = True
            self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self.cleanup_thread.start()
            return True
        return False
    
    def stop_cleanup_service(self):
        """Stop the automatic cleanup service"""
        self.is_running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        return True
    
    def get_cleanup_status(self) -> Dict:
        """Get the current status of the cleanup service"""
        return {
            "running": self.is_running,
            "pdf_directory": self.pdf_dir,
            "pptx_directory": self.pptx_dir,
            "cleanup_interval_hours": self.cleanup_interval_hours,
            "last_cleanup": getattr(self, '_last_cleanup', 'Never')
        }
    
    def manual_cleanup(self) -> Dict:
        """Perform manual cleanup of old files"""
        deleted_files = self._cleanup_old_files()
        self._last_cleanup = datetime.now().isoformat()
        return {
            "total_deleted": len(deleted_files),
            "deleted_files": deleted_files,
            "timestamp": self._last_cleanup
        }
    
    def _cleanup_loop(self):
        """Main cleanup loop that runs in background"""
        while self.is_running:
            try:
                self._cleanup_old_files()
                self._last_cleanup = datetime.now().isoformat()
                time.sleep(self.cleanup_interval_hours * 3600)  # Convert hours to seconds
            except Exception as e:
                print(f"Error in cleanup loop: {e}")
                time.sleep(3600)  # Wait 1 hour before retrying
    
    def _cleanup_old_files(self) -> List[str]:
        """Clean up old files from both directories"""
        deleted_files = []
        cutoff_time = datetime.now() - timedelta(hours=self.cleanup_interval_hours)
        
        # Clean PDF directory
        if os.path.exists(self.pdf_dir):
            for filename in os.listdir(self.pdf_dir):
                file_path = os.path.join(self.pdf_dir, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_time:
                        try:
                            os.remove(file_path)
                            deleted_files.append(f"PDF: {filename}")
                        except Exception as e:
                            print(f"Error deleting {filename}: {e}")
        
        # Clean PPTX directory
        if os.path.exists(self.pptx_dir):
            for filename in os.listdir(self.pptx_dir):
                file_path = os.path.join(self.pptx_dir, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_time:
                        try:
                            os.remove(file_path)
                            deleted_files.append(f"PPTX: {filename}")
                        except Exception as e:
                            print(f"Error deleting {filename}: {e}")
        
        return deleted_files
