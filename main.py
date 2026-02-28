#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OBS Multi Instance Controller - Main Entry Point."""
import sys
import logging
from pathlib import Path
from app.config.loader import ConfigLoader
from app.utils import setup_logging
from app.ui import MainWindow
from PyQt5.QtWidgets import QApplication

logger = logging.getLogger(__name__)


def main():
    """Main application entry point."""
    # Initialize logging
    setup_logging(log_dir="logs", log_level=logging.INFO)

    logger.info("=" * 60)
    logger.info("OBS Multi Instance Controller Starting")
    logger.info("=" * 60)

    # Load configuration
    config_path = Path("config.json")
    if not config_path.exists():
        error_msg = (
            f"Configuration file not found: {config_path.absolute()}\n\n"
            "Please create a config.json file using the provided template."
        )
        logger.error(error_msg)
        print(error_msg, file=sys.stderr)
        return 1

    try:
        config_loader = ConfigLoader(str(config_path))
        app_config = config_loader.load()
        logger.info(f"Configuration loaded: {len(app_config.courts)} courts configured")

    except Exception as e:
        error_msg = f"Failed to load configuration: {e}"
        logger.error(error_msg)
        print(error_msg, file=sys.stderr)
        return 1

    # Create and show main window
    try:
        qt_app = QApplication(sys.argv)
        main_window = MainWindow(app_config)
        main_window.show()
        logger.info("Main window displayed")

        result = qt_app.exec()
        logger.info(f"Application exiting with code {result}")
        return result

    except Exception as e:
        error_msg = f"Application error: {e}"
        logger.critical(error_msg, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())


