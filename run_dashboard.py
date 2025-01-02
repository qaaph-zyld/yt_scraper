"""
Run the metrics dashboard.
"""
from src.ui.dashboard import MetricsDashboard
from loguru import logger
import sys

def main():
    """Run the dashboard."""
    # Configure logging
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>"
    )
    
    # Create and run dashboard
    dashboard = MetricsDashboard()
    dashboard.run(debug=True)

if __name__ == "__main__":
    main()
