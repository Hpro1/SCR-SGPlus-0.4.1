"""
Window that sticks to the top of the screen
"""

import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import ctypes
import pyautogui
from pyautogui import *
import time
import math
import autoit
import keyboard
import win32api
import win32gui
import winsound
import PIL
import PIL.ImageGrab
import colorama
import os
import json
import webbrowser
from modules import *
import traceback
import tempfile

keyboardThread = None
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('sgplus.04')
starttime = time.time()
version = "v0.4"
color_vals = {
    (0, 201, 0),  # Lit Green
    (204, 153, 0),  # Lit Yellow
    (213, 0, 0),  # Lit Red
    (0, 94, 0),  # Unlit Green
    (96, 60, 0),  # Unlit Yellow
    (99, 0, 0),  # Unlit Red
}


def color_approx_eq(color1, color2):
    """
    Checks if two colors are approximately equal
    :param color1:
    :param color2:
    :return:
    """
    return abs(color1[0] - color2[0]) <= 7 and abs(color1[1] - color2[1]) <= 7 and abs(color1[2] - color2[2]) <= 7


def screen_grab(x, y, width, height):
    """
    Grabs a screenshot of the screen
    :param x:
    :param y:
    :param width:
    :param height:
    :return:
    """
    image = PIL.ImageGrab.grab(bbox=[x, y, x + width, y + height])
    return image


def click_signal(sig):
    """
    Clicks a signal
    :param sig:
    :return:
    """
    if win32gui.GetWindowText(win32gui.GetForegroundWindow()) != "Roblox":
        return

    autoit.mouse_click("left")

    while True:
        more_center = pyautogui.locateCenterOnScreen('more.png', confidence=0.2)
        if more_center:
            break

    keyboard.press_and_release(sig)
    time.sleep(backspace_wait)
    keyboard.press_and_release("backspace")


def click_camera_button():
    """
    Clicks the camera button
    :return:
    """
    if win32gui.GetWindowText(win32gui.GetForegroundWindow()) != "Roblox":
        return
    
    if pyautogui.locateCenterOnScreen('rotate.png', confidence=0.9):
        keyboard.press_and_release("backspace")
        hwnd = win32gui.FindWindow(None, 'Roblox')
        x0, y0, x1, y1 = win32gui.GetWindowRect(hwnd)
        w = x1 - x0
        h = y1 - y0
        autoit.mouse_move(math.ceil(w/2), math.ceil(h/2), 2)
        keyboard.press_and_release("backspace")
        keyboard.press_and_release("backspace")
        return
    
    autoit.mouse_click("left")

    more_center = None
    start_time = time.time()
    while not more_center and time.time() - start_time < 0.4:
        more_center = pyautogui.locateCenterOnScreen('more.png', confidence=0.7)

        if not more_center:
            plat_center = pyautogui.locateCenterOnScreen('plat.png', confidence=0.5)

            if plat_center:
                x, y = plat_center
                autoit.mouse_click("left", x, y, 1, 2)
                return

    if not more_center:
        return

    x, y = more_center
    autoit.mouse_click("left", x, y, 1, 2)

    camera_center = None
    start_time = time.time()
    while not camera_center and time.time() - start_time < 1:
        camera_center = pyautogui.locateCenterOnScreen('camera.png', grayscale=True, confidence=0.8)

    if not camera_center:
        return

    x, y = camera_center
    autoit.mouse_click("left", x, y, 1, 2)


def able_to_run():
    if win32gui.GetWindowText(win32gui.GetForegroundWindow()) != "Roblox":
        logfile = open("log.txt", "a")
        if debug: logfile.write("Not in Roblox\n")
        logfile.close()
        return False
    else:
        return True


def checkUpdate():
    """
    Checks for updates
    :return:
    """
    return 1


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    '''
    finished = Signal()  # QtCore.Signal
    error = Signal(tuple)
    result = Signal(object)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()  # QtCore.Slot
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class Overlay(QMainWindow):
    """
    Top most window
    """

    def __init__(self):
        # Parent constructor
        QMainWindow.__init__(self)
        # Set window flags
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # Translucent background
        self.setAttribute(Qt.WA_TranslucentBackground)
        # Properties
        with open("config.json", "r") as f:
            self.config = json.load(f)
            f.close()
        self.setStyleSheet("""
        QMainWindow {
            background-color: rgba(255, 255, 255, 0);
        }
        QLabel{
            border: 1px solid rgba(239, 239, 239, 0.15);
            border-radius: 5px;
        }
        QPushButton {
        border: 1px solid rgb(239, 239, 239);
        border-radius: 5px;
            }
        QPushButton:hover {
            border: 2px solid rgb(239, 239, 239);
            }
        QPushButton:pressed {
            border: 2px solid rgb(204, 105, 161);
            }
        """)
        self.animation: QPropertyAnimation | None = None
        self.button: QPushButton | None = None
        self.button2: QPushButton | None = None
        self.button3: QPushButton | None = None
        self.disabled = not self.config["enabledOnStart"]
        self.label: QLabel | None = QLabel(self)
        self.separator: QLabel | None = QLabel(self)
        self.layout: QVBoxLayout | None = QVBoxLayout()
        self.threadpool = QThreadPool()
        self.originalGeometry = None
        self.originalLabelGeometry = None
        self.newX = None
        self.newY = None
        self.rt = None
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        screensize: tuple = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        # Window modifiers
        self.move(0, 0)
        self.resize(screensize[0] * 0.1, screensize[1] * 0.035)
        self.setWindowOpacity(0.6)
        self.setWindowTitle("SG+")
        self.setWindowIcon(QIcon("icon.ico"))
        self.originalGeometry = self.geometry()
        # Label modifiers
        if self.disabled:
            self.label.setText("SG+: Disabled")
            self.label.setStyleSheet("background-color: red; color: white; font-size: 20px; font: 14pt \"Raleway Bold\";")
        else:
            self.label.setText("SG+: Enabled")
            self.label.setStyleSheet("background-color: green; color: white; font-size: 20px; font: 14pt \"Raleway Bold\";")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.resize(self.width(), self.height())
        self.separator.setText("----------")
        self.separator.setStyleSheet("background-color: grey; color: grey;")
        self.separator.resize(self.width(), int(self.height() * 0.2))
        # Layout modifiers
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.separator)
        # Move separator to under the label
        self.separator.move(0, self.height())
        self.setLayout(self.layout)

        keyboard.add_hotkey(self.config["toggle_key"], self.toggle_disable)  # F1

        if not self.disabled:
            self.add_hotkeys()

    def add_hotkeys(self):
        keyboard.add_hotkey(2, click_signal, args=["1"])  # 1
        keyboard.add_hotkey(3, click_signal, args=["2"])  # 2
        keyboard.add_hotkey(4, click_signal, args=["3"])  # 3
        keyboard.add_hotkey(46, click_camera_button)  # C
        winsound.Beep(500, 100)

    def remove_hotkeys(self):
        keyboard.remove_hotkey(2)
        keyboard.remove_hotkey(3)
        keyboard.remove_hotkey(4)
        keyboard.remove_hotkey(46)
        winsound.Beep(400, 100)

    def toggle_disable(self):
        if self.disabled:
            self.disabled = False
            worker = Worker(self.add_hotkeys)
            self.threadpool.start(worker)
            self.label.setText("SG+: Enabled")
            self.label.setStyleSheet("background-color: green; color: white; font-size: 20px; font: 14pt \"Raleway Bold\";")
            if self.button is not None:
                self.button.setText("Disable")
                self.button.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255, 175, 189, 255), stop:1 rgba(255, 195, 160, 255)); color: red; font-size: 20px;")
        else:
            # Remove all hotkeys
            worker = Worker(self.remove_hotkeys)
            self.threadpool.start(worker)
            self.disabled = True
            self.label.setText("SG+: Disabled")
            self.label.setStyleSheet(
                "background-color: red; color: white; font-size: 20px; font: 14pt \"Raleway Bold\";")
            if self.button is not None:
                self.button.setText("Enable")
                self.button.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255, 175, 189, 255), stop:1 rgba(255, 195, 160, 255)); color: green; font-size: 20px;")

    def enterEvent(self, event):
        """
        When hovering over the window
        :param event:
        :return:
        """

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(self.config["animation_duration"])
        self.animation.setStartValue(self.originalGeometry)
        self.animation.setEndValue(QRect(self.x(), self.y(), self.width(), 155))
        self.animation.start()

        self.setWindowOpacity(0.9)

        # Add buttons under the label
        if self.disabled:
            self.button = QPushButton("Enable", self)
            self.button.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255, 175, 189, 255), stop:1 rgba(255, 195, 160, 255)); color: green; font-size: 20px;")
        else:
            self.button = QPushButton("Disable", self)
            self.button.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255, 175, 189, 255), stop:1 rgba(255, 195, 160, 255)); color: red; font-size: 20px;")
        self.button.clicked.connect(self.toggle_disable)
        # Move button to under the separator
        self.button.move(0, self.height() + self.separator.height())
        self.button.resize(self.width(), self.height())

        # Add to layout
        self.layout.addWidget(self.button)
        # Display button
        self.button.show()

        # Add Properties button under self.button
        self.button2 = QPushButton("Properties", self)
        self.button2.clicked.connect(self.propertiesOpen)
        # Move button to under the Enable button
        self.button2.move(0, self.height() + self.separator.height() + self.button.height())
        self.button2.resize(self.width(), self.height())
        self.button2.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255, 175, 189, 255), stop:1 rgba(255, 195, 160, 255));; color: white; font-size: 20px;")
        # Add to layout
        self.layout.addWidget(self.button2)
        # Display button
        self.button2.show()

        # Add Exit button under self.button2
        self.button3 = QPushButton("Exit", self)
        self.button3.clicked.connect(self.close)
        # Move button to under the Properties button
        self.button3.move(0, self.height() + self.separator.height() + self.button.height() + self.button2.height())
        self.button3.resize(self.width(), self.height())
        self.button3.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255, 175, 189, 255), stop:1 rgba(255, 195, 160, 255)); color: white; font-size: 20px;")
        # Add to layout
        self.layout.addWidget(self.button3)
        # Display button
        self.button3.show()

    def leaveEvent(self, event):
        """
        When leaving the window
        :param event:
        :return:
        """
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(self.config["animation_duration"])
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(QRect(self.x(), self.y(), self.width(), 36))
        self.animation.start()

        self.setWindowOpacity(0.6)

    # Make overlay window draggable
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()
        self.newX = self.x()
        self.newY = self.y()
        self.originalGeometry = QRect(self.newX, self.newY, self.width(), self.height())

    def propertiesOpen(self):
        self.properties = Properties()
        self.properties.show()
        self.close()


class Update(QMainWindow):
    """
    Update window
    """

    def __init__(self):
        QMainWindow.__init__(self)
        self.window = None
        self.dragPos = None
        self.ui = Ui_UpdateWindow()
        self.ui.setupUi(self)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.ui.dropShadowFrame.setGraphicsEffect(self.shadow)
        self.ui.skipButton.clicked.connect(self.skip)
        self.ui.updateButton.clicked.connect(self.update)

    def update(self):
        """
        Update button
        """
        webbrowser.get().open("https://github.com/ElectricityMachine/SCR-SGPlus/releases")
        self.close()

    def skip(self):
        """
        Skip button
        :return:
        """
        self.window = Overlay()
        self.window.show()
        self.close()

    def mousePressEvent(self, event):
        """
        Mouse press event
        :param event:
        """
        self.dragPos = event.globalPos().toPoint()

class Properties(QMainWindow):
    """
    Update window
    """

    def __init__(self):
        QMainWindow.__init__(self)
        self.timer = None
        self.window = None
        self.dragPos = None
        self.key = None
        self.threadpool = QThreadPool()
        self.ui = Ui_PropertiesWindow()
        self.ui.setupUi(self)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.ui.dropShadowFrame.setGraphicsEffect(self.shadow)
        self.ui.skipButton.clicked.connect(self.skip)
        self.ui.updateButton.clicked.connect(self.update)
        self.ui.changeHotkey.clicked.connect(self.changeHotkey)

        with open("config.json", "r") as f:
            self.config = json.load(f)
            f.close()
        self.key = self.config["toggle_key"]
        self.ui.animationDuration.setPlainText(str(self.config["animation_duration"]) + "ms")
        # Convert key code to key name
        keycode = self.config["toggle_key"]
        if keycode == 59:
            keyname = "F1"
        else:
            keyname = keycode.upper()
        self.ui.toggleHotkey.setPlainText(keyname)
        self.ui.enabledOnStart.setChecked(self.config["enabledOnStart"])
        self.ui.debugMode.setChecked(self.config["debug"])
        self.ui.actionDelay.setPlainText(str(self.config["key_wait"]) + "ms")

        self.ui.actionDelay.setReadOnly(False)
        self.ui.animationDuration.setReadOnly(False)

    def changeHotkey(self):
        def waitForKeyPress():
            # Record keypress until the first key is pressed
            self.key = keyboard.read_key()
            print(self.key)
        self.ui.label_2.setText('<html><head/><body><p align="center">Press any key to assign this hotkey.</p></body></html>')
        # Wait for key press, in multithread
        self.worker = Worker(waitForKeyPress)
        self.worker.signals.result.connect(self.keyPress)
        self.threadpool.start(self.worker)

    def keyPress(self):
        self.ui.label_2.setText('<html><head/><body><p align="center">Click a box to change it\'s setting.</p></body></html>')
        self.ui.toggleHotkey.setPlainText(self.key.upper())


    def update(self):
        # Get values for all the fields
        animationDuration = self.ui.animationDuration.toPlainText().replace("ms", "")
        actionDelay = self.ui.actionDelay.toPlainText().replace("ms", "")
        try:
            animationDuration = int(animationDuration)
            actionDelay = int(actionDelay)
        except ValueError:
            animationDuration = 100
            actionDelay = 0
        toggleHotkey = self.ui.toggleHotkey.toPlainText()
        enabledOnStart = self.ui.enabledOnStart.isChecked()
        debugMode = self.ui.debugMode.isChecked()
        actionDelay = self.ui.actionDelay.toPlainText().replace("ms", "")
        configArray = {"key_wait": int(actionDelay), "backspace_wait": 0, "dialog_wait": 0.085, "debug": debugMode, "check_for_update": self.config["check_for_update"], "animation_duration": animationDuration, "enabledOnStart": enabledOnStart, "toggle_key": self.key}
        # Convert to JSON object and write to file
        jsonArray = json.dumps(configArray)
        with open("config.json", "w") as f:
            f.write(jsonArray)
            f.close()
        self.ui.updateButton.setText("Saved!")
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(lambda: self.ui.updateButton.setText("Apply"))
        self.timer.start(100)


    def skip(self):
        self.mainWindow = Overlay()
        self.mainWindow.show()
        self.close()

    def mousePressEvent(self, event):
        """
        Mouse press event
        :param event:
        """
        self.dragPos = event.globalPos().toPoint()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icon.ico'))
    pixmap = QPixmap('splash.png')
    splash = QSplashScreen(pixmap)
    splash.show()
    app.processEvents()
    if not os.path.exists(os.getcwd() + "/config.json"):
        with open(os.getcwd() + "/config.json", "w") as f:
            # Create dict for JSON
            config = {"key_wait": 0, "backspace_wait": 0, "dialog_wait": 0.085, "debug": False, "check_for_update": True, "animation_duration": 100, "enabledOnStart": False, "toggle_key": "f1"}
            # Write dict to JSON
            json.dump(config, f)
            f.close()
    else:
        with open(os.getcwd() + "/config.json", "r") as f:
            config = json.load(f)
            f.close()
    if config["debug"]:
        logfile = open("log.txt", "w")
        logfile.close()
    dialog_wait = config["dialog_wait"]
    key_wait = config["key_wait"]
    backspace_wait = config["backspace_wait"]
    debug = config["debug"]

    if "NUITKA_ONEFILE_PARENT" in os.environ:
        splash_filename = os.path.join(
            tempfile.gettempdir(),
            "onefile_%d_splash_feedback.tmp" % int(os.environ["NUITKA_ONEFILE_PARENT"]),
        )

        if os.path.exists(splash_filename):
            os.unlink(splash_filename)

    if config["check_for_update"]:
        update = checkUpdate()
        if update == 1:
            window = Update()
            window.show()
            splash.finish(window)
            sys.exit(app.exec())
        else:
            window = Overlay()
            window.show()
            splash.finish(window)
            sys.exit(app.exec())
    else:
        window = Overlay()
        window.show()
        splash.finish(window)
        sys.exit(app.exec())
