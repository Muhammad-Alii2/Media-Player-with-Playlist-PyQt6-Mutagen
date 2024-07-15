from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout,
                             QStyle, QSlider, QFileDialog, QListWidget, QListWidgetItem, QSizePolicy)
from PyQt6.QtGui import QPalette, QIcon
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from mutagen import File
import time
import sys


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Media Player')  # Set window title
        self.setWindowIcon(QIcon(r'..\Input Files\favicon.ico'))  # Set window icon

        palette = self.palette()  # Get the current palette
        palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.black)  # Set window background color to black
        self.setPalette(palette)

        self.current_playing_index = -1  # Initialize the index of the currently playing media

        self.createPlayer()  # Create the media player components

    def createPlayer(self):
        # Initialize media player and audio output
        self.media_player = QMediaPlayer()
        self.video_widget = QVideoWidget()  # Video widget to display video
        self.video_widget.setFixedSize(650, 450)  # Set fixed size for video widget
        self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)  # Set audio output for media player

        # Create buttons for media controls
        self.open_btn = QPushButton('Open Video')
        self.open_btn.clicked.connect(self.openFile)  # Connect button to openFile method

        self.seek_backward_btn = QPushButton()
        self.seek_backward_btn.setEnabled(False)  # Initially disabled
        self.seek_backward_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekBackward))
        self.seek_backward_btn.clicked.connect(self.seekBackward)  # Connect button to seekBackward method

        self.play_btn = QPushButton()
        self.play_btn.setEnabled(False)  # Initially disabled
        self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_btn.clicked.connect(self.playVideo)  # Connect button to playVideo method

        self.stop_btn = QPushButton()
        self.stop_btn.setEnabled(False)  # Initially disabled
        self.stop_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.stop_btn.clicked.connect(self.stopVideo)  # Connect button to stopVideo method

        self.seek_forward_btn = QPushButton()
        self.seek_forward_btn.setEnabled(False)  # Initially disabled
        self.seek_forward_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward))
        self.seek_forward_btn.clicked.connect(self.seekForward)  # Connect button to seekForward method

        # Create slider for media position
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)  # Initially no range
        self.slider.sliderMoved.connect(self.setPosition)  # Connect slider to setPosition method

        # Create volume button and slider
        self.volume_btn = QPushButton()
        self.volume_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
        self.volume_btn.clicked.connect(self.toggleVolumeSlider)  # Connect button to toggleVolumeSlider method

        self.volume_slider = QSlider(Qt.Orientation.Vertical)
        self.volume_slider.setRange(0, 100)  # Volume range 0 to 100
        self.volume_slider.setValue(50)  # Set initial volume to 50
        self.volume_slider.setVisible(False)  # Initially hidden
        self.volume_slider.setFixedSize(30, 100)  # Set size for volume slider
        self.volume_slider.valueChanged.connect(self.setVolume)  # Connect slider to setVolume method

        # Create horizontal layout for control buttons
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)

        # Add buttons and slider to horizontal layout
        hbox.addWidget(self.open_btn)
        hbox.addWidget(self.seek_backward_btn)
        hbox.addWidget(self.play_btn)
        hbox.addWidget(self.stop_btn)
        hbox.addWidget(self.seek_forward_btn)
        hbox.addWidget(self.slider)
        hbox.addWidget(self.volume_btn)
        hbox.addWidget(self.volume_slider)

        # Create vertical layout for video widget and control layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.video_widget)
        vbox.addLayout(hbox)

        # Create playlist widget
        self.playlist = QListWidget()
        vbox.addWidget(self.playlist)

        # Create buttons for playlist control
        self.add_btn = QPushButton('Add')
        self.add_btn.setFixedSize(100, 25)
        self.add_btn.clicked.connect(self.addToPlaylist)  # Connect button to addToPlaylist method

        self.run_btn = QPushButton('Run Playlist')
        self.run_btn.setFixedSize(100, 25)
        self.run_btn.clicked.connect(self.playSelectedItem)  # Connect button to playSelectedItem method

        self.remove_btn = QPushButton('Remove')
        self.remove_btn.setFixedSize(100, 25)
        self.remove_btn.clicked.connect(self.removeFromPlaylist)  # Connect button to removeFromPlaylist method

        # Create horizontal layout for playlist control buttons
        self.playlist_control = QHBoxLayout()
        self.playlist_control.setContentsMargins(0, 0, 0, 0)

        # Add playlist control buttons to horizontal layout
        self.playlist_control.addWidget(self.add_btn)
        self.playlist_control.addWidget(self.run_btn)
        self.playlist_control.addWidget(self.remove_btn)

        # Add playlist control layout to vertical layout
        vbox.addLayout(self.playlist_control)

        # Set video output to video widget
        self.media_player.setVideoOutput(self.video_widget)

        self.setLayout(vbox)  # Set main layout to vertical layout

        # Connect media player signals to corresponding methods
        self.media_player.playbackStateChanged.connect(self.mediaStateChanged)
        self.media_player.positionChanged.connect(self.positionChanged)
        self.media_player.durationChanged.connect(self.durationChanged)
        self.playlist.itemDoubleClicked.connect(self.playSelectedItem)
        self.media_player.mediaStatusChanged.connect(self.checkMediaStatus)

    def openFile(self):
        # File dialog to open a video or audio file
        file_filter = "Video Files (*.mp4 *.avi *.mkv *.mov);;Audio Files (*.mp3 *.wav *.ogg)"
        filepath, _ = QFileDialog.getOpenFileName(self, "Open File", "", file_filter)

        if filepath:
            self.stopVideo()  # Stop any currently playing video
            self.playlist.clear()  # Clear the playlist
            time.sleep(0.1)
            self.media_player.setSource(QUrl.fromLocalFile(filepath))  # Set media player source to selected file
            self.addToPlaylist(filepath)  # Add file to playlist
            self.playVideo()  # Play the selected video

    def seekBackward(self):
        # Seek backward by 5 seconds
        current_position = self.media_player.position()
        self.media_player.setPosition(max(0, current_position - 5000))

    def playVideo(self):
        # Toggle play/pause state
        self.play_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.seek_backward_btn.setEnabled(True)
        self.seek_forward_btn.setEnabled(True)
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def stopVideo(self):
        # Stop video playback
        self.play_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.seek_backward_btn.setEnabled(False)
        self.seek_forward_btn.setEnabled(False)
        self.media_player.stop()

    def seekForward(self):
        # Seek forward by 5 seconds
        current_position = self.media_player.position()
        duration = self.media_player.duration()
        self.media_player.setPosition(min(duration, current_position + 5000))

    def toggleVolumeSlider(self):
        # Show/hide volume slider
        self.volume_slider.setVisible(not self.volume_slider.isVisible())

    def setVolume(self, volume):
        # Set volume level
        self.audio_output.setVolume(volume / 100.0)
        if volume == 0:
            self.volume_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolumeMuted))
        else:
            self.volume_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))

    def addToPlaylist(self, filepath=None):
        # Add file to playlist
        if not filepath:
            file_filter = "Video Files (*.mp4 *.avi *.mkv *.mov);;Audio Files (*.mp3 *.wav *.ogg)"
            filepath, _ = QFileDialog.getOpenFileName(self, "Open File", "", file_filter)
        if filepath:
            filename = filepath.split('/')[-1]  # Extract filename from filepath
            duration = self.getMediaInfo(filepath)  # Get media duration
            item_text = f"{filename}                --            {duration} seconds"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, filepath)
            self.playlist.addItem(item)  # Add item to playlist


    def removeFromPlaylist(self):
        # Remove selected item from playlist
        current_row = self.playlist.currentRow()
        if current_row != -1:
            if current_row == self.current_playing_index:
                self.stopVideo()  # Stop video if currently playing
                self.playlist.takeItem(current_row)
                self.playNextItem()  # Play next item in playlist
            self.playlist.takeItem(current_row)

    def getMediaInfo(self, file_path):
        # Get media duration using mutagen
        try:
            media_file = File(file_path)
            return media_file.info.length
        except Exception as e:
            print(f"Error getting media info: {e}")
            return 0

    def playSelectedItem(self):
        # Play selected item from playlist
        current_row = self.playlist.currentRow()
        print(current_row)
        if current_row < 0:
            current_row = 0
            self.playlist.setCurrentRow(0)
        item = self.playlist.item(current_row)
        if item:
            filepath = item.data(Qt.ItemDataRole.UserRole)
            self.media_player.setSource(QUrl.fromLocalFile(filepath))
            self.current_playing_index = current_row
            self.playVideo()

    def playNextItem(self):
        # Play next item in playlist
        current_row = self.playlist.currentRow()
        if current_row < self.playlist.count() - 1:
            self.playlist.setCurrentRow(current_row + 1)
            self.playSelectedItem()
        else:
            self.playlist.setCurrentRow(0)
            self.playSelectedItem()

    def mediaStateChanged(self):
        # Change play button icon based on media state
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def checkMediaStatus(self, status):
        # Check media status and play next item if end of media
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.playNextItem()

    def positionChanged(self, position):
        # Update slider position
        self.slider.setValue(position)

    def durationChanged(self, duration):
        # Update slider range based on media duration
        self.slider.setRange(0, duration)

    def setPosition(self, position):
        # Set media position
        self.media_player.setPosition(position)


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())
