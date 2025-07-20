"""
Logging Configuration for A/B Testing Analysis
Captures all console output and analysis results to log files
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

class DualLogger:
    """Logger that writes to both console and file"""
    
    def __init__(self, log_dir="../logs", log_level=logging.INFO):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create timestamp for log files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Setup main logger
        self.logger = logging.getLogger('ABTestAnalysis')
        self.logger.setLevel(log_level)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        simple_formatter = logging.Formatter('%(message)s')
        
        # File handler for detailed logs
        file_handler = logging.FileHandler(
            self.log_dir / f"analysis_detailed_{timestamp}.log",
            encoding='utf-8'
        )
        file_handler.setFormatter(detailed_formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # File handler for console output
        console_log_handler = logging.FileHandler(
            self.log_dir / f"console_output_{timestamp}.log",
            encoding='utf-8'
        )
        console_log_handler.setFormatter(simple_formatter)
        console_log_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(simple_formatter)
        console_handler.setLevel(logging.INFO)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_log_handler)
        self.logger.addHandler(console_handler)
        
        # Store current timestamp for file naming
        self.timestamp = timestamp
        
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
        
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
        
    def error(self, message):
        """Log error message"""
        self.logger.error(message)
        
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
        
    def log_dataframe(self, df, name, sample_rows=10):
        """Log DataFrame information and sample data"""
        self.info(f"\n=== {name} DataFrame ===")
        self.info(f"Shape: {df.shape}")
        self.info(f"Columns: {list(df.columns)}")
        self.info(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
        
        if len(df) > 0:
            self.info(f"\nFirst {min(sample_rows, len(df))} rows:")
            self.info(str(df.head(sample_rows)))
            
            self.info(f"\nData types:")
            self.info(str(df.dtypes))
            
            # Numeric columns summary
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                self.info(f"\nNumeric columns summary:")
                self.info(str(df[numeric_cols].describe()))
        
    def log_analysis_results(self, results_dict):
        """Log analysis results in structured format"""
        self.info("\n" + "="*50)
        self.info("ANALYSIS RESULTS SUMMARY")
        self.info("="*50)
        
        for key, value in results_dict.items():
            self.info(f"\n{key.upper().replace('_', ' ')}:")
            if hasattr(value, 'to_string'):
                self.info(str(value))
            else:
                self.info(str(value))
                
    def save_results_to_file(self, results, filename=None):
        """Save results to a separate results file"""
        if filename is None:
            filename = f"analysis_results_{self.timestamp}.txt"
            
        results_file = self.log_dir / filename
        
        with open(results_file, 'w', encoding='utf-8') as f:
            f.write(f"A/B Testing Analysis Results\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            
            for key, value in results.items():
                f.write(f"{key.upper().replace('_', ' ')}:\n")
                f.write("-" * 30 + "\n")
                if hasattr(value, 'to_string'):
                    f.write(value.to_string())
                else:
                    f.write(str(value))
                f.write("\n\n")
        
        self.info(f"Results saved to: {results_file}")
        
    def get_log_files(self):
        """Return paths to current log files"""
        return {
            'detailed_log': self.log_dir / f"analysis_detailed_{self.timestamp}.log",
            'console_log': self.log_dir / f"console_output_{self.timestamp}.log",
            'log_directory': self.log_dir
        }

# Global logger instance
logger = None

def setup_logging(log_dir="../logs"):
    """Setup global logger"""
    global logger
    logger = DualLogger(log_dir)
    return logger

def get_logger():
    """Get the global logger instance"""
    global logger
    if logger is None:
        logger = setup_logging()
    return logger 