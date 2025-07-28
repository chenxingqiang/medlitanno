#!/usr/bin/env python3
"""
Progress monitoring for medical literature annotation
"""

import os
import json
import time
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict

from ..common import BaseProcessor, ProcessingResult


class ProgressMonitor:
    """Progress monitor for annotation processing"""
    
    def __init__(self, data_dir: str = "datatrain"):
        """
        Initialize progress monitor
        
        Args:
            data_dir: Data directory to monitor
        """
        self.data_dir = data_dir
    
    def get_status(self, model_type: str = None) -> Dict[str, Any]:
        """
        Get processing status
        
        Args:
            model_type: Specific model type to check (optional)
            
        Returns:
            Dict[str, Any]: Status information
        """
        total_files = 0
        processed_files = 0
        model_stats = defaultdict(lambda: {"processed": 0, "total_articles": 0, "total_relations": 0})
        
        for root, dirs, files in os.walk(self.data_dir):
            for file in files:
                if file.endswith('.xlsx'):
                    total_files += 1
                    
                    # Check annotation directory
                    annotation_dir = os.path.join(root, 'annotation')
                    if os.path.exists(annotation_dir):
                        base_name = os.path.splitext(file)[0]
                        
                        # Check for different model types
                        models_to_check = [model_type] if model_type else ["deepseek", "deepseek-reasoner", "qianwen"]
                        
                        for model in models_to_check:
                            result_file = os.path.join(annotation_dir, f"{base_name}_annotated_{model}.json")
                            if os.path.exists(result_file):
                                model_stats[model]["processed"] += 1
                                processed_files += 1
                                
                                # Read statistics if available
                                try:
                                    with open(result_file, 'r', encoding='utf-8') as f:
                                        data = json.load(f)
                                    model_stats[model]["total_articles"] += len(data)
                                    for article in data:
                                        model_stats[model]["total_relations"] += len(article.get('relations', []))
                                except:
                                    pass
        
        return {
            "total_files": total_files,
            "processed_files": processed_files,
            "remaining_files": total_files - processed_files,
            "completion_percentage": (processed_files / total_files * 100) if total_files > 0 else 0,
            "model_stats": dict(model_stats),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_recent_files(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recently processed files
        
        Args:
            limit: Maximum number of files to return
            
        Returns:
            List[Dict[str, Any]]: Recent files information
        """
        recent_files = []
        
        for root, dirs, files in os.walk(self.data_dir):
            if 'annotation' in dirs:
                annotation_dir = os.path.join(root, 'annotation')
                for file in os.listdir(annotation_dir):
                    if file.endswith('_annotated_deepseek.json') or file.endswith('_annotated_qianwen.json'):
                        file_path = os.path.join(annotation_dir, file)
                        try:
                            mtime = os.path.getmtime(file_path)
                            recent_files.append({
                                "file_path": file_path,
                                "relative_path": os.path.relpath(file_path, self.data_dir),
                                "modified_time": mtime,
                                "formatted_time": datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                            })
                        except:
                            pass
        
        # Sort by modification time and return top N
        recent_files.sort(key=lambda x: x['modified_time'], reverse=True)
        return recent_files[:limit]
    
    def generate_report(self) -> str:
        """
        Generate a text report of processing status
        
        Returns:
            str: Formatted report
        """
        status = self.get_status()
        recent_files = self.get_recent_files(5)
        
        report = f"""
📊 Medical Literature Annotation Progress Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 Overall Progress:
  Total Files: {status['total_files']}
  Processed: {status['processed_files']}
  Remaining: {status['remaining_files']}
  Completion: {status['completion_percentage']:.1f}%

🤖 Model Statistics:
"""
        
        for model, stats in status['model_stats'].items():
            report += f"""  {model.upper()}:
    Processed Files: {stats['processed']}
    Total Articles: {stats['total_articles']}
    Total Relations: {stats['total_relations']}
"""
        
        if recent_files:
            report += "\n📁 Recently Processed Files:\n"
            for file_info in recent_files:
                report += f"  - {file_info['relative_path']} ({file_info['formatted_time']})\n"
        
        return report


class BatchMonitor:
    """Enhanced batch monitor with real-time capabilities"""
    
    def __init__(self, data_dir: str = "datatrain", refresh_interval: int = 30):
        """
        Initialize batch monitor
        
        Args:
            data_dir: Data directory to monitor
            refresh_interval: Refresh interval in seconds
        """
        self.data_dir = data_dir
        self.refresh_interval = refresh_interval
        self.monitor = ProgressMonitor(data_dir)
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        print("=== Real-time Batch Processing Monitor ===")
        print("Press Ctrl+C to exit")
        print()
        
        try:
            while True:
                # Clear screen
                os.system('clear' if os.name == 'posix' else 'cls')
                
                # Display status
                print(self.monitor.generate_report())
                
                # Wait for next refresh
                time.sleep(self.refresh_interval)
                
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
    
    def check_failed_files(self) -> List[str]:
        """
        Check for failed processing files
        
        Returns:
            List[str]: List of failed files
        """
        failed_files = []
        
        # Check for failed file logs
        for model in ["deepseek", "deepseek-reasoner", "qianwen"]:
            log_file = f"failed_files_{model}.json"
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        failed_data = json.load(f)
                    failed_files.extend(failed_data)
                except:
                    pass
        
        return failed_files
    
    def restart_processing(self, model_type: str):
        """
        Restart processing for a specific model
        
        Args:
            model_type: Model type to restart
        """
        print(f"🚀 Restarting processing for {model_type}...")
        
        # This would typically call the batch processor
        # For now, just print instructions
        print(f"To restart {model_type} processing, run:")
        print(f"  python -c \"from medlitanno import batch_process_directory; batch_process_directory('datatrain', model_type='{model_type}')\"")


def monitor_progress(data_dir: str = "datatrain", refresh_interval: int = 30):
    """
    Start progress monitoring (convenience function)
    
    Args:
        data_dir: Data directory to monitor
        refresh_interval: Refresh interval in seconds
    """
    monitor = BatchMonitor(data_dir, refresh_interval)
    monitor.start_monitoring() 