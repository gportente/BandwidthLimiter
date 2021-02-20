import threading
import time
import pydivert

from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit, QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy, QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit, QVBoxLayout, QWidget)

def seconds_to_bytes(numSeconds, maxSendRateBytesPerSecond):
   return numSeconds*maxSendRateBytesPerSecond

def bytes_to_seconds(numBytes, maxSendRateBytesPerSecond):
    return float(numBytes)/maxSendRateBytesPerSecond

def thread_function(kilobytes):
    maxSendRateBytesPerSecond = kilobytes * 1000
    bytesAheadOfSchedule = 0
    prevTime = None

    print("Proceed to limit bandwidth at %d KB/s" % kilobytes)

    with pydivert.WinDivert("inbound") as handle:
        for packet in handle:

            global w
            if not w.toggle_status:
                print("Thread has been killed")
                return

            # Grabbiamo il time attuale
            now = time.time()

            if prevTime != None:
                bytesAheadOfSchedule -= seconds_to_bytes(now-prevTime, maxSendRateBytesPerSecond)

            prevTime = now
            numBytesSent = len(packet.raw)

            try:
                handle.send(packet)
            except:
                pass

            if (numBytesSent > 0):
                bytesAheadOfSchedule += numBytesSent

                if (bytesAheadOfSchedule > 0):
                    time.sleep(bytes_to_seconds(bytesAheadOfSchedule, maxSendRateBytesPerSecond))

class CoreWindow(QDialog):
    def __init__(self, parent=None):
        super(CoreWindow, self).__init__(parent)

        self.toggle_status = False

        self.create_settings_box()

        self.toggle_button = QPushButton("Toggle")
        self.toggle_button.setDefault(False)
        self.toggle_button.clicked.connect(self.handle_toggle_button)

        main_layout = QGridLayout()
        main_layout.addWidget(self.settings_box, 1, 0)
        main_layout.addWidget(self.toggle_button)

        self.setLayout(main_layout)
        self.setFixedHeight(300)
        self.setFixedWidth(250)

        self.setWindowTitle("Bandwidth Limiter")
        self.change_style('Fusion')

    def handle_toggle_button(self):    
        if self.toggle_status:
            self.toggle_status = False
            self.style_label.setText("Disabled")
            self.style_label.setStyleSheet("color: red;")


        else:
            self.toggle_status = True
            self.style_label.setText("Enabled")
            self.style_label.setStyleSheet("color: green;")

            kilobytes_limit = 1000

            if self.radioButton1.isChecked():
                kilobytes_limit = 2250
            elif self.radioButton2.isChecked():
                kilobytes_limit = 5250
            elif self.radioButton3.isChecked():
                kilobytes_limit = 10250

            self.current_thread = threading.Thread(target=thread_function, args=([kilobytes_limit]))
            self.current_thread.start()

    def change_style(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))

    def create_settings_box(self):
        self.settings_box = QGroupBox("Settings")

        self.style_label = QLabel("Disabled")
        self.style_label.setStyleSheet("color: red;") 

        self.radioButton1 = QRadioButton("2 MB/s")
        self.radioButton2 = QRadioButton("5 MB/s")
        self.radioButton3 = QRadioButton("10 MB/s")
        self.radioButton1.setChecked(True)

        layout = QVBoxLayout()
        layout.addWidget(self.style_label)
        layout.addWidget(self.radioButton1)
        layout.addWidget(self.radioButton2)
        layout.addWidget(self.radioButton3)
        layout.addStretch(1)
        
        self.settings_box.setLayout(layout)    


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    w = CoreWindow()
    w.show()
    w.toggle_status = False
    sys.exit(app.exec_())

