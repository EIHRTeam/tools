import sys
import os
import time
import subprocess
import platform
import re
import base64
import webbrowser
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QSlider, QFileDialog, QLineEdit, 
                             QProgressBar, QFrame, QMessageBox, QGroupBox, QRadioButton, 
                             QButtonGroup, QScrollArea, QStyle, QCheckBox, QDialog)
from PyQt6.QtCore import Qt, QUrl, QThread, pyqtSignal, QTime, QSize, QTimer
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtGui import QIcon, QPixmap, QFont, QPalette, QColor, QAction

STYLESHEET = """
QMainWindow, QWidget {
    background-color: #1a2a3a;
    color: #ecf0f1;
    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
}

QGroupBox {
    background-color: rgba(30, 40, 50, 0.8);
    border: 1px solid #34495e;
    border-radius: 10px;
    margin-top: 20px;
    padding-top: 20px;
    font-weight: bold;
    color: #3498db;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 10px;
    left: 10px;
}

QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 8px 15px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #1f618d;
}

QPushButton:disabled {
    background-color: #7f8c8d;
    color: #bdc3c7;
}

/* 特殊按钮样式 */
QPushButton#convertBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498db, stop:1 #2ecc71);
    font-size: 16px;
    padding: 12px;
    border-radius: 8px;
}

QPushButton#convertBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2ecc71, stop:1 #3498db);
}

QPushButton#frameBtn {
    background-color: #2ecc71;
}

QPushButton#frameBtn:hover {
    background-color: #27ae60;
}

/* 滑块样式 */
QSlider::groove:horizontal {
    border: 1px solid #34495e;
    height: 8px;
    background: #34495e;
    margin: 2px 0;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #3498db;
    border: 2px solid #2c3e50;
    width: 18px;
    height: 18px;
    margin: -7px 0;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background: #2ecc71;
}

/* 输入框 */
QLineEdit {
    background-color: #34495e;
    border: 2px solid #3498db;
    border-radius: 5px;
    color: #ecf0f1;
    padding: 5px;
}

QLineEdit:focus {
    border-color: #2ecc71;
}

/* 进度条 */
QProgressBar {
    border: none;
    background-color: #34495e;
    border-radius: 5px;
    text-align: center;
    color: white;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498db, stop:1 #2ecc71);
    border-radius: 5px;
}

QLabel#headerLabel {
    font-size: 24px;
    font-weight: bold;
    color: #3498db;
    padding: 10px;
}

QLabel#subHeaderLabel {
    color: #bdc3c7;
    font-size: 12px;
    margin-bottom: 10px;
}

QLabel#timeLabel {
    font-size: 18px;
    font-weight: bold;
    color: #2ecc71;
}
"""

def get_ffmpeg_path():
    if os.path.exists('ffmpeg.exe'):
        return os.path.abspath('ffmpeg.exe')
    elif os.path.exists(os.path.join(os.getcwd(), 'ffmpeg.exe')):
        return os.path.join(os.getcwd(), 'ffmpeg.exe')
    return 'ffmpeg'

def get_video_resolution(video_path):
    ffmpeg_cmd = get_ffmpeg_path()
    try:
        result = subprocess.run([ffmpeg_cmd, '-i', video_path], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
        match = re.search(r'Video:.*?,.*? (\d{2,})x(\d{2,})', result.stderr)
        if match:
            return int(match.group(1)), int(match.group(2))
    except Exception as e:
        print(f"获取分辨率失败: {e}")
    return 0, 0

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a2a3a;
                color: #ecf0f1;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 14px;
            }
            QLabel#title {
                font-size: 24px;
                font-weight: bold;
                color: #3498db;
            }
            QLabel#author {
                color: #bdc3c7;
                font-style: italic;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        # 图标/标题
        title_label = QLabel("神奇妙妙小工具")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        version_label = QLabel("版本: v1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # 作者信息 (带彩蛋)
        self.author_label = QLabel("作者: Oculto")
        self.author_label.setObjectName("author")
        self.author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.author_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.author_label.mousePressEvent = self.on_author_click
        layout.addWidget(self.author_label)
        
        # 提示
        hint_label = QLabel("铃兰小姐就是我们的光——")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint_label)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        self.click_count = 0
        self.last_click_time = 0
        
        self._d = "6ZOD5YWw5bCP5aeQ5q+P5pep5LiD54K55oyJ5pe26LW35bqK5Y+g6KKr5a2Q5Yi354mZ5pmo6K+75Y2B5YiG6ZKf6K+X5q2M6YCJ6ZuG5ZCO5YmN5b6A5Yy755aX6YOo6Zeo6K6k55yf5a2m5Lmg5rqQ55+z5oqA6Im655qE5L2/55So5bm256ev5p6B5biu5Yqp5YW25LuW5ZCM6b6E5Lq65oSf5p+T6ICF5aSE55CG5oOF57uq5a+55q+P5LiA5L2N5Y+C5LiO5bel5L2c55qE5Yy755aX5bmy5ZGY6YO96K+a5oGz5oWw6Zeu5Lit5Y2I5LiA5a6a6KaB5bCP552h5LiA5Liq5bCP5pe2552h6YaS5LmL5ZCO5LiA5a6a5Lya5Zad5LiA5p2v6Iqd5aOr5ben5YWL5Yqb5bCx566X5pyJ5bmy5ZGY56eB5LiL5aGe57uZ57OW5p6c5ZKM5bCP56S854mp5aW55Lmf5Lya56S86LKM5ouS57ud5q+P5b2T6YGH5Yiw5aWH5oCq55qE6ZmM55Sf5Lq65bCx5Lya5oCv55Sf55Sf5Zyw56uZ5Zyo5bmy5ZGY55qE6Lqr5ZCO5L2O5aS05ZCR5YmN6LWw5LiL5Y2I5Lya6K6k55yf5peB5ZCs5Lya6K6u5oiW6ICF5Y2O5rOV55Cz55qE5Yy755aX5bmy5ZGY6K6y5bqn5ZCM5pe25Lya57uG5b+D5Zyw5omT5omr5Lya6K6u546w5Zy65pyA5ZCO5LiA5Liq5YWz54Gv56a75byA5pma5LiK5Z+65pys6Lqy5Zyo5oi/6Ze06YeM55yL5Lmm57Sv5LqG55qE6K+d5Lya5Li75Yqo5o+Q5Ye65biu5Yqp5ZCO5Yuk5bmy5ZGY5YGa5LiA5Lqb5p2C5rS756iN5b6u5aS45aWW5aW55Lik5Y+l5bCx5Lya5a6z576e5pma5LiK5Y2B54K55LmL5YmN5LiA5a6a5Lya5LiK5bqK552h6KeJ5YG25bCU5Lya5ZKM5rOh5pmu5Y2h5ZKM5ber5oGL5bCP5aeQ5b6F5Zyo5LiA6LW36K+36K6w5L2P6ZOD5YWw5bCP5aeQ5bCx5piv5oiR5Lus55qE5YWJ4oCU4oCU"
        self._u = "aHR0cHM6Ly9wcnRzLndpa2kvdy8lRTklOTMlODMlRTUlODUlQjA="

    def on_author_click(self, event):
        current_time = time.time()
        if current_time - self.last_click_time > 2.0:
            self.click_count = 0
        
        self.click_count += 1
        self.last_click_time = current_time
        
        if self.click_count >= 5:
            self.trigger_egg()
            self.click_count = 0

    def trigger_egg(self):
        try:
            msg = base64.b64decode(self._d).decode('utf-8')
            url = base64.b64decode(self._u).decode('utf-8')
            
            QMessageBox.information(self, "✨", msg)
            webbrowser.open(url)
        except Exception as e:
            print(f"Error: {e}")

class ConversionThread(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str, str) # success, message, output_path
    
    def __init__(self, params):
        super().__init__()
        self.params = params
        self.is_running = True

    def run(self):
        try:
            input_path = self.params['input_path']
            output_path = self.params['output_path']
            start_time = self.params['start_time']
            duration = self.params['duration']
            quality = self.params['quality']
            fade_in = self.params['fade_in']
            fade_out = self.params['fade_out']
            fmt = self.params['format']
            target_width = self.params.get('width', 0)
            target_height = self.params.get('height', 0)

            # 确定ffmpeg路径
            ffmpeg_cmd = get_ffmpeg_path()

            # 检查FFmpeg是否存在
            try:
                subprocess.run([ffmpeg_cmd, '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.finished_signal.emit(False, "未找到FFmpeg，请确保已安装并添加到系统环境变量中，或者将ffmpeg.exe放在程序同级目录下。", "")
                return

            # 构建滤镜
            filters = []
            fps = int(5 + (quality / 100) * 15)
            
            # 渐入渐出
            if fade_in > 0:
                fade_in_duration = fade_in / fps
                filters.append(f"fade=t=in:st=0:d={fade_in_duration:.3f}")
            
            if fade_out > 0:
                fade_out_duration = fade_out / fps
                fade_out_start = max(0, duration - fade_out_duration)
                filters.append(f"fade=t=out:st={fade_out_start:.3f}:d={fade_out_duration:.3f}")

            # 缩放
            if target_width > 0 and target_height > 0:
                scale = f"{target_width}:{target_height}"
            elif duration > 30:
                scale = "640:360"
            elif duration > 15:
                scale = "720:405"
            else:
                scale = "800:450"
            filters.append(f"scale={scale}:flags=lanczos")

            filter_str = ",".join(filters)

            # 临时调色板文件 (仅GIF需要)
            palette_path = output_path + "_palette.png"
            
            if fmt == 'gif':
                colors = int(32 + (quality / 100) * 224)
                
                # 1. 生成调色板
                palette_filters = f"{filter_str},palettegen=max_colors={colors}:stats_mode=full"
                cmd_palette = [
                    ffmpeg_cmd, '-y', 
                    '-ss', str(start_time), 
                    '-t', str(duration),
                    '-i', input_path,
                    '-vf', palette_filters,
                    palette_path
                ]
                
                self.progress_signal.emit(20)
                subprocess.run(cmd_palette, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # 2. 生成GIF
                gif_filters = f"{filter_str},fps={fps} [x]; [x][1:v] paletteuse=dither=floyd_steinberg"
                cmd_gif = [
                    ffmpeg_cmd, '-y',
                    '-ss', str(start_time),
                    '-t', str(duration),
                    '-i', input_path,
                    '-i', palette_path,
                    '-filter_complex', gif_filters,
                    '-gifflags', '+transdiff',
                    output_path
                ]
                
                self.progress_signal.emit(60)
                subprocess.run(cmd_gif, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # 清理调色板
                if os.path.exists(palette_path):
                    os.remove(palette_path)

            elif fmt == 'webp':
                # WebP 转换
                cmd_webp = [
                    ffmpeg_cmd, '-y',
                    '-ss', str(start_time),
                    '-t', str(duration),
                    '-i', input_path,
                    '-vf', filter_str,
                    '-c:v', 'libwebp',
                    '-quality', str(quality),
                    '-preset', 'default',
                    '-loop', '0',
                    '-r', str(fps), # 控制帧率
                    output_path
                ]
                self.progress_signal.emit(50)
                subprocess.run(cmd_webp, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            self.progress_signal.emit(100)
            
            # 检查文件大小并返回结果
            if os.path.exists(output_path):
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                msg = f"转换成功！\n文件大小: {size_mb:.2f} MB"
                if size_mb > 20:
                    msg += "\n注意：文件超过20MB。"
                self.finished_signal.emit(True, msg, output_path)
            else:
                self.finished_signal.emit(False, "输出文件未生成", "")

        except subprocess.CalledProcessError as e:
            self.finished_signal.emit(False, f"FFmpeg执行错误: {e}", "")
        except Exception as e:
            self.finished_signal.emit(False, f"发生错误: {str(e)}", "")

class VideoConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("神奇妙妙小工具 - By Oculto")
        self.resize(1000, 800)
        self.setStyleSheet(STYLESHEET)
        
        # 变量初始化
        self.video_path = None
        self.duration = 0
        self.start_time = 0
        self.end_time = 0
        self.is_playing = False
        self.original_width = 0
        self.original_height = 0
        self.aspect_ratio = 0
        
        self.setAcceptDrops(True)
        self.init_menu()
        self.init_ui()
        self.init_media_player()

    def init_menu(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #1a2a3a;
                color: #ecf0f1;
            }
            QMenuBar::item:selected {
                background-color: #3498db;
            }
            QMenu {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
            }
            QMenu::item:selected {
                background-color: #3498db;
            }
        """)
        
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            # 过滤非视频文件
            video_exts = ['.mp4', '.avi', '.mov', '.webm', '.mkv']
            video_file = next((f for f in files if os.path.splitext(f)[1].lower() in video_exts), None)
            if video_file:
                self.load_video(video_file)
            else:
                QMessageBox.warning(self, "提示", "请拖入有效的视频文件")

    def init_media_player(self):
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.errorOccurred.connect(self.handle_errors)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content_widget = QWidget()
        scroll.setWidget(content_widget)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # 1. 头部
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title = QLabel("神奇妙妙小工具")
        title.setObjectName("headerLabel")
        header_layout.addWidget(title)
        content_layout.addLayout(header_layout)

        # 2. 视频预览区
        preview_group = QGroupBox("视频上传与预览")
        preview_layout = QVBoxLayout()
        
        # 上传按钮
        self.upload_btn = QPushButton("选择视频文件 (MP4, AVI, MOV, WebM)")
        self.upload_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        self.upload_btn.clicked.connect(self.open_file)
        self.upload_btn.setMinimumHeight(50)
        preview_layout.addWidget(self.upload_btn)
        
        # 视频播放器
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(400)
        self.video_widget.setStyleSheet("background-color: black; border-radius: 10px;")
        preview_layout.addWidget(self.video_widget)
        
        # 播放控制
        controls_layout = QHBoxLayout()
        self.play_btn = QPushButton("播放")
        self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_btn.clicked.connect(self.play_video)
        self.play_btn.setEnabled(False)
        
        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.sliderMoved.connect(self.set_position)
        self.seek_slider.setEnabled(False)
        
        self.time_label = QLabel("00:00 / 00:00")
        
        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.seek_slider)
        controls_layout.addWidget(self.time_label)
        preview_layout.addLayout(controls_layout)
        
        # 剪辑控制
        trim_layout = QHBoxLayout()
        
        self.mark_start_btn = QPushButton("标记开始点")
        self.mark_start_btn.clicked.connect(lambda: self.mark_time('start'))
        self.mark_start_btn.setEnabled(False)
        
        self.mark_end_btn = QPushButton("标记结束点")
        self.mark_end_btn.clicked.connect(lambda: self.mark_time('end'))
        self.mark_end_btn.setEnabled(False)
        
        self.prev_frame_btn = QPushButton("前一帧")
        self.prev_frame_btn.setObjectName("frameBtn")
        self.prev_frame_btn.clicked.connect(lambda: self.step_frame(-1))
        self.prev_frame_btn.setEnabled(False)
        
        self.next_frame_btn = QPushButton("后一帧")
        self.next_frame_btn.setObjectName("frameBtn")
        self.next_frame_btn.clicked.connect(lambda: self.step_frame(1))
        self.next_frame_btn.setEnabled(False)
        
        trim_layout.addWidget(self.mark_start_btn)
        trim_layout.addWidget(self.mark_end_btn)
        trim_layout.addWidget(self.prev_frame_btn)
        trim_layout.addWidget(self.next_frame_btn)
        preview_layout.addLayout(trim_layout)
        
        # 时间显示
        markers_layout = QHBoxLayout()
        self.start_marker_label = QLabel("开始: 0.00s")
        self.start_marker_label.setObjectName("timeLabel")
        self.end_marker_label = QLabel("结束: 0.00s")
        self.end_marker_label.setObjectName("timeLabel")
        self.duration_marker_label = QLabel("时长: 0.00s")
        self.duration_marker_label.setObjectName("timeLabel")
        
        markers_layout.addWidget(self.start_marker_label)
        markers_layout.addWidget(self.end_marker_label)
        markers_layout.addWidget(self.duration_marker_label)
        preview_layout.addLayout(markers_layout)
        
        preview_group.setLayout(preview_layout)
        content_layout.addWidget(preview_group)

        # 3. 设置区
        settings_group = QGroupBox("转换设置")
        settings_layout = QVBoxLayout()
        
        # 渐入渐出
        fade_layout = QHBoxLayout()
        fade_layout.addWidget(QLabel("渐入帧数:"))
        self.fade_in_slider = QSlider(Qt.Orientation.Horizontal)
        self.fade_in_slider.setRange(0, 30)
        self.fade_in_slider.setValue(10)
        self.fade_in_label = QLabel("10")
        self.fade_in_slider.valueChanged.connect(lambda v: self.fade_in_label.setText(str(v)))
        
        fade_layout.addWidget(self.fade_in_slider)
        fade_layout.addWidget(self.fade_in_label)
        
        fade_layout.addWidget(QLabel("  渐出帧数:"))
        self.fade_out_slider = QSlider(Qt.Orientation.Horizontal)
        self.fade_out_slider.setRange(0, 30)
        self.fade_out_slider.setValue(10)
        self.fade_out_label = QLabel("10")
        self.fade_out_slider.valueChanged.connect(lambda v: self.fade_out_label.setText(str(v)))
        
        fade_layout.addWidget(self.fade_out_slider)
        fade_layout.addWidget(self.fade_out_label)
        settings_layout.addLayout(fade_layout)
        
        # 质量
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("质量等级 (1-100):"))
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(80)
        self.quality_label = QLabel("80")
        self.quality_slider.valueChanged.connect(lambda v: self.quality_label.setText(str(v)))
        
        quality_layout.addWidget(self.quality_slider)
        quality_layout.addWidget(self.quality_label)
        settings_layout.addLayout(quality_layout)
        
        # 尺寸设置
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("输出尺寸:"))
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("宽")
        self.width_input.setFixedWidth(80)
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("高")
        self.height_input.setFixedWidth(80)
        self.lock_ratio_cb = QCheckBox("锁定比例")
        self.lock_ratio_cb.setChecked(True)
        
        # 连接信号
        self.width_input.textChanged.connect(self.on_width_changed)
        self.height_input.textChanged.connect(self.on_height_changed)
        
        size_layout.addWidget(self.width_input)
        size_layout.addWidget(QLabel("x"))
        size_layout.addWidget(self.height_input)
        size_layout.addWidget(self.lock_ratio_cb)
        size_layout.addStretch()
        settings_layout.addLayout(size_layout)

        # 格式与文件名
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("输出格式:"))
        self.format_group = QButtonGroup()
        self.gif_radio = QRadioButton("GIF")
        self.gif_radio.setChecked(True)
        self.webp_radio = QRadioButton("WebP")
        self.format_group.addButton(self.gif_radio)
        self.format_group.addButton(self.webp_radio)
        
        format_layout.addWidget(self.gif_radio)
        format_layout.addWidget(self.webp_radio)
        
        format_layout.addWidget(QLabel("  文件名(可选):"))
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("不带后缀名")
        format_layout.addWidget(self.filename_input)
        
        settings_layout.addLayout(format_layout)
        settings_group.setLayout(settings_layout)
        content_layout.addWidget(settings_group)

        # 4. 转换操作
        action_layout = QVBoxLayout()
        self.convert_btn = QPushButton("开始高质量转换")
        self.convert_btn.setObjectName("convertBtn")
        self.convert_btn.clicked.connect(self.start_conversion)
        self.convert_btn.setEnabled(False)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        action_layout.addWidget(self.convert_btn)
        action_layout.addWidget(self.progress_bar)
        action_layout.addWidget(self.status_label)
        content_layout.addLayout(action_layout)

        main_layout.addWidget(scroll)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择视频文件", "", 
                                                 "Video Files (*.mp4 *.avi *.mov *.webm *.mkv)")
        if file_name:
            self.load_video(file_name)

    def load_video(self, file_name):
        self.video_path = file_name
        self.media_player.setSource(QUrl.fromLocalFile(file_name))
        self.play_btn.setEnabled(True)
        self.seek_slider.setEnabled(True)
        self.mark_start_btn.setEnabled(True)
        self.mark_end_btn.setEnabled(True)
        self.prev_frame_btn.setEnabled(True)
        self.next_frame_btn.setEnabled(True)
        self.convert_btn.setEnabled(True)
        self.upload_btn.setText(f"已选择: {os.path.basename(file_name)}")
        
        # 获取视频分辨率
        w, h = get_video_resolution(file_name)
        if w > 0 and h > 0:
            self.original_width = w
            self.original_height = h
            self.aspect_ratio = w / h
            # 默认缩放到较小的尺寸，例如宽度800
            default_width = 800
            if w > default_width:
                self.width_input.setText(str(default_width))
                # 高度会自动计算
            else:
                self.width_input.setText(str(w))
        
        # 自动播放一下以获取元数据
        self.media_player.play()
        QTimer.singleShot(100, self.media_player.pause)

    def on_width_changed(self, text):
        if not self.lock_ratio_cb.isChecked() or not self.aspect_ratio:
            return
        if self.height_input.hasFocus(): # 避免循环更新
            return
        try:
            width = int(text)
            height = int(width / self.aspect_ratio)
            self.height_input.blockSignals(True)
            self.height_input.setText(str(height))
            self.height_input.blockSignals(False)
        except ValueError:
            pass

    def on_height_changed(self, text):
        if not self.lock_ratio_cb.isChecked() or not self.aspect_ratio:
            return
        if self.width_input.hasFocus(): # 避免循环更新
            return
        try:
            height = int(text)
            width = int(height * self.aspect_ratio)
            self.width_input.blockSignals(True)
            self.width_input.setText(str(width))
            self.width_input.blockSignals(False)
        except ValueError:
            pass

    def play_video(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def position_changed(self, position):
        self.seek_slider.setValue(position)
        self.update_time_label(position)

    def duration_changed(self, duration):
        self.duration = duration
        self.seek_slider.setRange(0, duration)
        self.end_time = min(duration, 30000) # 默认结束时间30秒或视频长度
        self.update_markers_display()

    def update_time_label(self, position):
        current = QTime(0, 0).addMSecs(position).toString("mm:ss")
        total = QTime(0, 0).addMSecs(self.duration).toString("mm:ss")
        self.time_label.setText(f"{current} / {total}")
        
        # 更新播放按钮图标
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
            self.play_btn.setText("暂停")
        else:
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.play_btn.setText("播放")

    def set_position(self, position):
        self.media_player.setPosition(position)

    def mark_time(self, type_):
        current = self.media_player.position()
        if type_ == 'start':
            self.start_time = current
            if self.start_time >= self.end_time:
                self.end_time = min(self.duration, self.start_time + 5000)
        else:
            self.end_time = current
            if self.end_time <= self.start_time:
                self.start_time = max(0, self.end_time - 5000)
        
        self.update_markers_display()

    def update_markers_display(self):
        self.start_marker_label.setText(f"开始: {self.start_time/1000:.2f}s")
        self.end_marker_label.setText(f"结束: {self.end_time/1000:.2f}s")
        duration = (self.end_time - self.start_time) / 1000
        self.duration_marker_label.setText(f"时长: {duration:.3f}s")

    def step_frame(self, direction):
        # 假设30fps，每帧约33ms
        current = self.media_player.position()
        new_pos = current + (direction * 33)
        self.media_player.setPosition(max(0, min(self.duration, new_pos)))

    def handle_errors(self):
        self.play_btn.setEnabled(False)
        err_msg = self.media_player.errorString()
        QMessageBox.critical(self, "错误", f"视频播放出错: {err_msg}\n请确保系统安装了相应的解码器。")

    def start_conversion(self):
        if not self.video_path:
            return
            
        duration = (self.end_time - self.start_time) / 1000
        if duration <= 0:
            QMessageBox.warning(self, "警告", "结束时间必须大于开始时间")
            return
            
        # 准备输出路径
        fmt = 'gif' if self.gif_radio.isChecked() else 'webp'
        custom_name = self.filename_input.text().strip()
        if not custom_name:
            custom_name = f"converted_{int(time.time())}"
        
        # 简单的文件名清理
        custom_name = "".join([c for c in custom_name if c.isalnum() or c in (' ', '_', '-')]).strip()
        output_filename = f"{custom_name}.{fmt}"
        
        # 保存对话框
        output_path, _ = QFileDialog.getSaveFileName(self, "保存文件", output_filename, 
                                                   f"{fmt.upper()} Files (*.{fmt})")
        
        if not output_path:
            return

        # 获取尺寸参数
        try:
            target_width = int(self.width_input.text())
            target_height = int(self.height_input.text())
        except ValueError:
            target_width = 0
            target_height = 0

        # 准备参数
        params = {
            'input_path': self.video_path,
            'output_path': output_path,
            'start_time': self.start_time / 1000,
            'duration': duration,
            'quality': self.quality_slider.value(),
            'fade_in': self.fade_in_slider.value(),
            'fade_out': self.fade_out_slider.value(),
            'format': fmt,
            'width': target_width,
            'height': target_height
        }

        # UI状态更新
        self.convert_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("正在初始化转换...")
        
        # 启动线程
        self.thread = ConversionThread(params)
        self.thread.progress_signal.connect(self.update_progress)
        self.thread.finished_signal.connect(self.conversion_finished)
        self.thread.start()

    def update_progress(self, val):
        self.progress_bar.setValue(val)
        if val < 100:
            self.status_label.setText(f"正在处理... {val}%")
        else:
            self.status_label.setText("处理完成，正在保存...")

    def conversion_finished(self, success, message, output_path):
        self.convert_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("")
        
        if success:
            QMessageBox.information(self, "成功", message)
            # 尝试打开文件夹
            try:
                if platform.system() == "Windows":
                    os.startfile(os.path.dirname(output_path))
                elif platform.system() == "Darwin":
                    subprocess.run(["open", os.path.dirname(output_path)])
                else:
                    subprocess.run(["xdg-open", os.path.dirname(output_path)])
            except:
                pass
        else:
            QMessageBox.critical(self, "失败", message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # 使用Fusion风格作为基础，配合QSS
    
    window = VideoConverterApp()
    window.show()
    
    sys.exit(app.exec())
