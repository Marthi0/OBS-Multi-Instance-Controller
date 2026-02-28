"""Main application window."""
import logging
from typing import List, Dict
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QMessageBox, QStatusBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from app.obs.controller import OBSController
from app.system.obs_launcher import OBSLauncher
from app.system.watchdog import OBSWatchdog
from app.config.models import AppConfig, CourtConfig
from app.ui.widgets import CourtControlWidget
from app.__version__ import __version__, __title__

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, app_config: AppConfig):
        """Initialize main window.

        Args:
            app_config: Application configuration
        """
        super().__init__()
        self.app_config = app_config
        self.setWindowTitle(f"{__title__} v{__version__}")
        self.setGeometry(100, 100, 1000, 600)

        # Initialize OBS controllers and launchers
        self.obs_controllers: Dict[str, OBSController] = {}
        self.obs_launchers: Dict[str, OBSLauncher] = {}
        self.watchdogs: Dict[str, OBSWatchdog] = {}
        self.court_widgets: Dict[str, CourtControlWidget] = {}

        self._setup_ui()
        self._initialize_obs_instances()
        self._setup_cleanup_timer()

    def _setup_ui(self) -> None:
        """Setup main window UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("OBS Multi Instance Controller")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        # Courts layout
        courts_layout = QHBoxLayout()
        courts_layout.setSpacing(20)

        for court_config in self.app_config.courts:
            obs_controller = OBSController(court_config)
            self.obs_controllers[court_config.name] = obs_controller

            obs_launcher = OBSLauncher(
                self.app_config.obs_executable_path,
                court_config.profile_name,
                court_config.websocket_port,
                court_config.websocket_password
            )
            self.obs_launchers[court_config.name] = obs_launcher

            # Create watchdog
            court_name = court_config.name
            watchdog = OBSWatchdog(
                court_config=court_config,
                obs_launcher=obs_launcher,
                obs_controller=obs_controller,
                check_interval=self.app_config.watchdog_check_interval,
                restart_delay=self.app_config.watchdog_restart_delay,
                on_disconnect=lambda cn=court_name: self._on_obs_disconnected(cn),
                on_reconnect=lambda cn=court_name: self._on_obs_reconnected(cn)
            )
            self.watchdogs[court_config.name] = watchdog

            # Create control widget with watchdog reference
            court_widget = CourtControlWidget(court_config.name, obs_controller, obs_launcher, watchdog)
            court_widget.status_changed.connect(self._on_status_changed)
            court_widget.error_occurred.connect(self._on_error_occurred)
            self.court_widgets[court_config.name] = court_widget

            courts_layout.addWidget(court_widget)

        main_layout.addLayout(courts_layout)
        main_layout.addStretch()

        # Status bar
        self.statusBar().showMessage("Ready")

    def _initialize_obs_instances(self) -> None:
        """Initialize OBS instances and watchdogs."""
        # Watchdogs are already created in _setup_ui, just start them
        for court_config in self.app_config.courts:
            watchdog = self.watchdogs[court_config.name]
            watchdog.start()
            logger.info(f"Initialized {court_config.name}")

    def _setup_cleanup_timer(self) -> None:
        """Setup timer for periodic cleanup."""
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._periodic_cleanup)
        self.cleanup_timer.start(60000)  # Every minute

    def _periodic_cleanup(self) -> None:
        """Periodic cleanup tasks."""
        pass  # Placeholder for future cleanup logic

    def _on_status_changed(self, message: str) -> None:
        """Handle status change message.

        Args:
            message: Status message
        """
        logger.info(message)
        self.statusBar().showMessage(message)

    def _on_error_occurred(self, message: str) -> None:
        """Handle error message.

        Args:
            message: Error message
        """
        logger.error(message)
        self.statusBar().showMessage(f"ERROR: {message}")
        QMessageBox.warning(self, "Error", message)

    def _on_obs_disconnected(self, court_name: str) -> None:
        """Handle OBS disconnection.

        Args:
            court_name: Name of the court
        """
        logger.warning(f"OBS disconnected for {court_name}")
        self.statusBar().showMessage(f"WARNING: {court_name} OBS disconnected - attempting recovery...")

    def _on_obs_reconnected(self, court_name: str) -> None:
        """Handle OBS reconnection.

        Args:
            court_name: Name of the court
        """
        logger.info(f"OBS reconnected for {court_name}")
        self.statusBar().showMessage(f"{court_name} OBS reconnected successfully")

    def closeEvent(self, event):
        """Handle application close event."""
        logger.info("Application closing...")

        # Stop all watchdogs
        for watchdog in self.watchdogs.values():
            watchdog.stop()

        # Cleanup court widgets
        for widget in self.court_widgets.values():
            widget.cleanup()

        # Disconnect controllers
        for controller in self.obs_controllers.values():
            controller.disconnect()

        logger.info("Application closed")
        event.accept()
