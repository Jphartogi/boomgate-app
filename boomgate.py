from image.image_loader import *

from flask import Flask, jsonify, abort, make_response, request
from flask_restful import Api, Resource, abort
import urllib.request

import time
import sys
import requests
import json

from scripts.form import Ui_Form
from scripts.boomgate_gui import *
from scripts.camera_stream import CameraStream

app = Flask(__name__)
api = Api(app)

status = {
    'name': 'unknown',
    'image': '',
    'valid': False,
    'welcome': True
}

f = open('scripts/data.json')
data = json.load(f)

class Form(QMainWindow):
    """Form Class for camera, gate, and port address selection"""
    def __init__(self):
        super().__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.gate_setter("gate_one")
        
        self.ui.comboBox.currentIndexChanged.connect(self.on_gate_changed)
        self.ui.button_enter.clicked.connect(self.address_enter)

    def on_gate_changed(self, i):
        """Gate change/selector handler to set the default value"""
        if i == 0:
            self.gate = "gate_one"
        else:
            self.gate = "gate_two"
        self.gate_setter(self.gate)
        return self.gate
    
    def gate_setter(self, gate):
        """Set the default value for each address from scripts/data.json files"""
        self.ui.line_camera.setText(data[gate]["camera_address"])
        self.ui.line_gate.setText(data[gate]["gate_address"])
        self.ui.line_port.setText(data[gate]["port_address"])

    def address_enter(self):
        """Address entered/selected handler to run the application"""
        print("[START] Boomgate is Starting...")
        mainWindow.camera_address_enter(self.ui.line_camera.text())
        mainWindow.gate_address_enter(self.ui.line_gate.text())
        mainWindow.port_address_enter(self.ui.line_port.text())
        mainWindow.enter_selected_handler.selected_enter.emit(True)
        self.hide()

    def closeEvent(self, event):
        mainWindow.close()

class MainWindow(QMainWindow):
    """Main Window Class"""
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.label_bot = self.ui.label_bot
        self.label_top = self.ui.label_top

        self.file_menu = self.ui.menuSettings
        self.addMenu()
       
        self.message_container()

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.start()

        self.timer.timeout.connect(self.show_date)
        self.timer.timeout.connect(self.welcome_setter)

        self.screen_width = QApplication.desktop().screenGeometry().width()
        self.screen_height = QApplication.desktop().screenGeometry().height()

        self.container_camera = self.ui.container_camera_top
        self.WebhookWorker = self.WebhookWorker()

        self.handler = self.APIHandler()
        self.handler.setter.connect(self.detection_setter)

        self.request_timeout = self.GetRequest()
        self.request_timeout.timeout_status.connect(
            self.on_status_timeout)
        
        self.enter_selected_handler = self.EnterSelectedHandler()
        self.enter_selected_handler.selected_enter.connect(self.on_enter_selected)

        self.gate_stream_address = ''
        self.port_stream_address = ''
        
        self.Form = Form()
        self.Form.show()

        self.trans = QTranslator(self)
        self.retranslateUi()
        self.ind_language_selected()

    def closeEvent(self, event):
        self.Form.close()

    def changeEvent(self, event):
        """Change event handler, for language change"""
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUi()
        super(MainWindow, self).changeEvent(event)

    def addMenu(self):
        """Function to modified the Menu Bar"""
        self.dictionaries = {
            "function": [self.eng_language_selected, self.ind_language_selected],
            "lang": ["English", "Bahasa Indonesia"]
        }
        self.menu_language = QMenu(self)
        self.file_menu.addMenu(self.menu_language)

        for i, text in enumerate(self.dictionaries["lang"]):
            self.lang_action = QAction(text, self)
            self.lang_action.triggered.connect(self.dictionaries["function"][i])
            self.menu_language.addAction(self.lang_action)

    def retranslateUi(self):
        """Function to set text with translatable method"""
        self.Form.ui.label_camera.setText(QtCore.QCoreApplication.translate("Form", "Choose Camera Address:"))
        self.Form.ui.label_gate.setText(QtCore.QCoreApplication.translate("Form", "Choose Gate Address:"))
        self.Form.ui.label_port.setText(QtCore.QCoreApplication.translate("Form", "Choose Port Address:"))
        self.Form.ui.button_enter.setText(QtCore.QCoreApplication.translate("Form", "Enter"))
        self.Form.ui.comboBox.setItemText(0, QtCore.QCoreApplication.translate("Form", "Gate 1"))
        self.Form.ui.comboBox.setItemText(1, QtCore.QCoreApplication.translate("Form", "Gate 2"))
        self.ui.menuSettings.setTitle(QtCore.QCoreApplication.translate("MainWindow", "Settings"))
        self.menu_language.setTitle(QtCore.QCoreApplication.translate("MainWindow", "Language"))
    
    @pyqtSlot()
    def eng_language_selected(self):
        """English language selected handler"""
        print("ENGLISH")
        QtWidgets.QApplication.instance().removeTranslator(self.trans)
    
    @pyqtSlot()
    def ind_language_selected(self):
        """Bahasa language selected handler"""
        print("BAHASA INDONESIA")
        data = "languages/eng-ind"
        self.trans.load(data)
        QtWidgets.QApplication.instance().installTranslator(self.trans)
    
    @pyqtSlot()
    def camera_address_enter(self, camera_stream_address):
        """Camera address entered/selected handler"""
        try:
            self.camera_stream_address = camera_stream_address
            self.camera_stream = CameraStream(self.container_camera, self.screen_width //
                                3, self.screen_height//3, camera_stream_address)
        except:
            print("CAMERA FAILED")
    
    @pyqtSlot()
    def gate_address_enter(self, gate_stream_address):
        """Gate address entered/selected handler"""
        self.gate_stream_address = gate_stream_address
    
    @pyqtSlot()
    def port_address_enter(self, port_stream_address):
        """Port address entered/selected handler"""
        self.port_stream_address = port_stream_address
        try:
            if self.port_stream_address == '':
                pass
            else:
                if not self.WebhookWorker.isRunning():
                    print("[START] Webhhok is Starting...")
                    self.WebhookWorker.start()
        except:
            print("PORT FAILED")

    def message_container(self):
        """Pop-up message default setter"""
        self.msg = {}
        for i in range(2):
            self.msg[i] = QtWidgets.QMessageBox()
            self.msg[i].setWindowTitle("Qlue Boomgate")
            self.msg[i].setIcon(QMessageBox.Warning)

    def show_date(self):
        """Show current date and time"""
        currentDate = QDate.currentDate()
        currentTime = QTime.currentTime()
        displayTime = currentTime.toString('hh:mm:ss')
        displayDate = currentDate.toString('dd MM yyyy')
        self.ui.label_date.setText(displayDate + " | " + displayTime)

    def welcome_setter(self):
        """Set display to Welcome State"""
        if status["welcome"] == True:
            self.pixmap_setter(qlue)
            self.ui.label_top.setStyleSheet("font: bold 22px \"Open Sans\";\n"
                                            "color: #ffffff;")
            self.ui.label_top.setText(QtWidgets.QApplication.translate("MainWindow", "Welcome to\n{}").format(data["company_name"]))
            self.ui.label_bot.setText(QtWidgets.QApplication.translate("MainWindow", ""))

    def detection_setter(self):
        """Set display based on detection result (valid/invalid)"""
        if status["valid"] == False:
            self.detection_invalid_setter()
        else:
            pool = QThreadPool().globalInstance()
            runnable = self.PathRun()
            runnable.signals.path_update.connect(self.detection_valid_setter)
            pool.start(runnable)

    def detection_invalid_setter(self):
        """Invalid detection display"""
        self.pixmap_setter(invalid)
        self.label_top.setStyleSheet("font: bold 22px \"Open Sans\";\n"
                                           "color: #e8382b;")
        self.label_top.setText(QtWidgets.QApplication.translate("MainWindow", "Identification Failed"))
        self.label_bot.setText(QtWidgets.QApplication.translate("MainWindow", "Please Try Again"))
        QTimer.singleShot(3000, self.back_welcome_setter)
        
    def detection_valid_setter(self, p):
        """Valid detection display"""
        self.pixmap_setter(p)
        self.label_top.setStyleSheet("font: bold 22px \"Open Sans\";\n"
                                           "color: #00bd99;")
        self.label_top.setText(QtWidgets.QApplication.translate("MainWindow", "Identification Success"))
        self.label_bot.setText(QtWidgets.QApplication.translate("MainWindow", "Welcome, {}").format(status['name']))
        self.request_timeout.start()
        QTimer.singleShot(3000, self.back_welcome_setter)

    class PathUpdate(QObject):
        path_update = pyqtSignal(bytes)

    class PathRun(QRunnable):
        """Runnable Class to read/translate image from url using urllib"""
        def __init__(self):
            super().__init__()
            self.signals = mainWindow.PathUpdate()

        @pyqtSlot()
        def run(self):
            url = status['image']
            try:
                path = urllib.request.urlopen(url).read()
                self.signals.path_update.emit(path)
            except ValueError as ve:
                self.signals.path_update.emit(logo)
                print("invalid image")    

    @pyqtSlot()
    def back_welcome_setter(self):
        """Set display back to Welcome State"""
        status["valid"] = False
        status["welcome"] = True

    def pixmap_setter(self, path):
        """Set image to responsive pixmap display"""
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(path)
        label = self.ui.label_image
        label.setMinimumSize(1, 1)
        pixmap = pixmap.scaled(label.width(), label.height(),
                               QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        label.setPixmap(pixmap)

    class APIHandler(QObject):
        setter = pyqtSignal()

    class Webhook:
        """Webhook Class for API listener"""
        @app.route("/api", methods=['POST'])
        def post():
            if status["welcome"] == True:
                mainWindow.handler.setter.emit()
            else:
                pass
            if len(status) == 0:
                abort(404)
            if not request.json:
                abort(400)
            if 'name' in request.json and type(request.json['name']) is not str:
                abort(400)
            if 'image' in request.json and type(request.json['image']) is not str:
                abort(400)
            if 'valid' in request.json and type(request.json['valid']) is not bool:
                abort(400)
            if 'welcome' in request.json and type(request.json['welcome']) is not bool:
                abort(400)
            status['name'] = request.json.get(
                'name', status['name'])
            status['image'] = request.json.get(
                'image', status['image'])
            status['valid'] = request.json.get(
                'valid', status['valid'])
            status['welcome'] = False
            return jsonify({'status': status})

    class WebhookWorker(QThread):
        """Webhook Worker Class to run on another thread"""
        def run(self):
            self.port = mainWindow.port_stream_address
            app.run(debug=True, use_reloader=False, port=self.port)

    class GetRequest(QObject):
        """Get request for Gate Address using requests"""
        timeout_status = pyqtSignal(bool)
        def start(self):
            self.url = mainWindow.gate_stream_address
            self.payload = {}
            self.headers = {}
            self.timeout = False
            try:
                response = requests.request(
                    "GET", self.url, headers=self.headers, data=self.payload, timeout=1)
                response.raise_for_status()
            except requests.exceptions.HTTPError as errh:
                self.timeout = True
                txt = "Http Error: " + str(errh)
                mainWindow.msg[0].setText(QtWidgets.QApplication.translate("MainWindow", "Can't connect to the Gate"))
                mainWindow.msg[0].setDetailedText(txt)
                print(txt)
            except requests.exceptions.ConnectionError as errc:
                self.timeout = True
                txt = "Error Connecting: " + str(errc)
                mainWindow.msg[0].setText(QtWidgets.QApplication.translate("MainWindow", "Can't connect to the Gate"))
                mainWindow.msg[0].setDetailedText(txt)
                print(txt)
            except requests.exceptions.Timeout as errt:
                self.timeout = True
                txt = "Timeout Error: " + str(errt)
                mainWindow.msg[0].setText(QtWidgets.QApplication.translate("MainWindow", "Can't connect to the Gate"))
                mainWindow.msg[0].setDetailedText(txt)
                print(txt)
            except requests.exceptions.RequestException as err:
                self.timeout = True
                txt = "Oops: Something Else, " + str(err)
                mainWindow.msg[0].setText(QtWidgets.QApplication.translate("MainWindow", "Can't connect to the Gate"))
                mainWindow.msg[0].setDetailedText(txt)
                print(txt)
            else:
                self.timeout = False
                print("Connected Successfully")

            self.timeout_status.emit(self.timeout)

    @pyqtSlot(bool)
    def on_status_timeout(self, timeout):
        """Pop-up message modifier on GetRequest timeout"""
        if timeout:
            self.msg[0].show()
        else:
            self.msg[0].hide()

    class EnterSelectedHandler(QObject):
        selected_enter = pyqtSignal(bool)
    
    @pyqtSlot(bool)
    def on_enter_selected(self, selected):
        """Pop-up message modifier on address entered/selected"""
        self.msg[1].setText(QtWidgets.QApplication.translate("MainWindow", "Configuration has ben selected"))
        self.msg[1].setDetailedText(QtWidgets.QApplication.translate("MainWindow", "Camera: {}\nGate: {}\nPort: {}").format(
            self.camera_stream_address, self.gate_stream_address, self.port_stream_address))
        self.msg[1].setIcon(QMessageBox.Information)
        if selected:
            self.msg[1].show()
        else:
            self.msg[1].hide()

if __name__ == "__main__":
    application = QApplication(sys.argv)
    application.setWindowIcon(QtGui.QIcon("ui/icon/black-icon.ico"))
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(application.exec_())
