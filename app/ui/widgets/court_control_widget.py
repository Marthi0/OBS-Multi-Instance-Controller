"""Court control widget for UI."""
import logging
import time
from typing import Optional, Callable
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QFont
from app.obs.controller import OBSController
from app.system.obs_launcher import OBSLauncher
from app.system.watchdog import OBSWatchdog

logger = logging.getLogger(__name__)


class CourtControlWidget(QWidget):
    """Widget for controlling a single court's OBS instance."""

    # Signals
    status_changed = pyqtSignal(str)  # Emits status string
    error_occurred = pyqtSignal(str)  # Emits error message

    def __init__(self, court_name: str, obs_controller: OBSController, obs_launcher: Optional[OBSLauncher] = None, watchdog: Optional[OBSWatchdog] = None):
        """Initialize court control widget.

        Args:
            court_name: Name of the court
            obs_controller: OBSController instance for this court
            obs_launcher: OBSLauncher instance for this court (optional)
            watchdog: OBSWatchdog instance for this court (optional)
        """
        super().__init__()
        self.court_name = court_name
        self.obs_controller = obs_controller
        self.obs_launcher = obs_launcher
        self.watchdog = watchdog
        self.is_streaming = False
        self.is_recording = False

        self._setup_ui()
        self._setup_status_timer()

    def _setup_ui(self) -> None:
        """Setup widget UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Court name label
        name_label = QLabel(self.court_name)
        name_font = QFont()
        name_font.setPointSize(14)
        name_font.setBold(True)
        name_label.setFont(name_font)
        layout.addWidget(name_label)

        # Status indicator and connection status
        status_layout = QHBoxLayout()
        self.status_indicator = QFrame()
        self.status_indicator.setFixedSize(20, 20)
        self.status_indicator.setStyleSheet("background-color: red; border-radius: 10px;")
        status_layout.addWidget(self.status_indicator)

        self.status_label = QLabel("Disconnected")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        # OBS control buttons
        obs_layout = QHBoxLayout()
        self.start_obs_btn = QPushButton("Start OBS")
        self.start_obs_btn.clicked.connect(self._on_start_obs_clicked)
        obs_layout.addWidget(self.start_obs_btn)

        self.stop_obs_btn = QPushButton("Stop OBS")
        self.stop_obs_btn.clicked.connect(self._on_stop_obs_clicked)
        self.stop_obs_btn.setEnabled(False)
        obs_layout.addWidget(self.stop_obs_btn)
        layout.addLayout(obs_layout)

        # Streaming buttons
        stream_layout = QHBoxLayout()
        self.start_stream_btn = QPushButton("Start Stream")
        self.start_stream_btn.clicked.connect(self._on_start_stream_clicked)
        self.start_stream_btn.setEnabled(False)
        stream_layout.addWidget(self.start_stream_btn)

        self.stop_stream_btn = QPushButton("Stop Stream")
        self.stop_stream_btn.clicked.connect(self._on_stop_stream_clicked)
        self.stop_stream_btn.setEnabled(False)
        stream_layout.addWidget(self.stop_stream_btn)
        layout.addLayout(stream_layout)

        # Recording buttons
        record_layout = QHBoxLayout()
        self.start_record_btn = QPushButton("Start Record")
        self.start_record_btn.clicked.connect(self._on_start_record_clicked)
        self.start_record_btn.setEnabled(False)
        record_layout.addWidget(self.start_record_btn)

        self.stop_record_btn = QPushButton("Stop Record")
        self.stop_record_btn.clicked.connect(self._on_stop_record_clicked)
        self.stop_record_btn.setEnabled(False)
        record_layout.addWidget(self.stop_record_btn)
        layout.addLayout(record_layout)

        # Status display
        self.stream_status_label = QLabel("Stream: Stopped")
        layout.addWidget(self.stream_status_label)

        self.record_status_label = QLabel("Record: Stopped")
        layout.addWidget(self.record_status_label)

        layout.addStretch()

    def _setup_status_timer(self) -> None:
        """Setup timer for periodic status updates."""
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(2000)  # Update every 2 seconds

    def _update_status(self) -> None:
        """Update status display."""
        is_connected = self.obs_controller.is_connected()

        # Update indicator color
        if is_connected:
            self.status_indicator.setStyleSheet("background-color: green; border-radius: 10px;")
            self.status_label.setText("Connected")
        else:
            self.status_indicator.setStyleSheet("background-color: red; border-radius: 10px;")
            self.status_label.setText("Disconnected")

        # Update button states
        self.start_obs_btn.setEnabled(not is_connected)
        self.stop_obs_btn.setEnabled(is_connected)
        self.start_stream_btn.setEnabled(is_connected)
        self.stop_stream_btn.setEnabled(is_connected)
        self.start_record_btn.setEnabled(is_connected)
        self.stop_record_btn.setEnabled(is_connected)

        # Update streaming/recording status
        if is_connected:
            self.is_streaming = self.obs_controller.get_streaming_status()
            self.is_recording = self.obs_controller.get_recording_status()

            self.stream_status_label.setText(
                "Stream: Active" if self.is_streaming else "Stream: Stopped"
            )
            self.record_status_label.setText(
                "Record: Active" if self.is_recording else "Record: Stopped"
            )

            # Disable start buttons if already active
            self.start_stream_btn.setEnabled(not self.is_streaming)
            self.stop_stream_btn.setEnabled(self.is_streaming)
            self.start_record_btn.setEnabled(not self.is_recording)
            self.stop_record_btn.setEnabled(self.is_recording)

    def _on_start_obs_clicked(self) -> None:
        """Handle start OBS button click."""
        # Launch OBS process if launcher is available
        if self.obs_launcher:
            if not self.obs_launcher.launch():
                self.error_occurred.emit(f"{self.court_name}: Failed to launch OBS process")
                return
            # Wait for OBS to initialize
            time.sleep(3)

        # Now try to connect
        if self.obs_controller.connect():
            self.status_changed.emit(f"{self.court_name}: OBS connected")
        else:
            self.error_occurred.emit(f"{self.court_name}: Failed to connect to OBS")

    def _on_stop_obs_clicked(self) -> None:
        """Handle stop OBS button click."""
        # Mark as manually stopped so watchdog doesn't auto-restart
        if self.watchdog:
            self.watchdog.mark_as_manually_stopped()

        # Stop the OBS process if launcher is available
        if self.obs_launcher:
            if self.obs_launcher.stop():
                self.status_changed.emit(f"{self.court_name}: OBS stopped")
            else:
                self.error_occurred.emit(f"{self.court_name}: Failed to stop OBS process")
        else:
            # Fallback to just disconnecting
            self.obs_controller.disconnect()
            self.status_changed.emit(f"{self.court_name}: OBS disconnected")

    def _on_start_stream_clicked(self) -> None:
        """Handle start stream button click."""
        if self.obs_controller.start_streaming():
            self.status_changed.emit(f"{self.court_name}: Streaming started")
        else:
            self.error_occurred.emit(f"{self.court_name}: Failed to start streaming")

    def _on_stop_stream_clicked(self) -> None:
        """Handle stop stream button click."""
        if self.obs_controller.stop_streaming():
            self.status_changed.emit(f"{self.court_name}: Streaming stopped")
        else:
            self.error_occurred.emit(f"{self.court_name}: Failed to stop streaming")

    def _on_start_record_clicked(self) -> None:
        """Handle start record button click."""
        if self.obs_controller.start_recording():
            self.status_changed.emit(f"{self.court_name}: Recording started")
        else:
            self.error_occurred.emit(f"{self.court_name}: Failed to start recording")

    def _on_stop_record_clicked(self) -> None:
        """Handle stop record button click."""
        if self.obs_controller.stop_recording():
            self.status_changed.emit(f"{self.court_name}: Recording stopped")
        else:
            self.error_occurred.emit(f"{self.court_name}: Failed to stop recording")

    def cleanup(self) -> None:
        """Cleanup resources."""
        self.status_timer.stop()
