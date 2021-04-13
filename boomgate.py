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

class Form(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.data = json.load(f)
        self.gate_setter("gate_one")
        
        self.ui.comboBox.currentIndexChanged.connect(self.on_gate_changed)
        self.ui.button_enter.clicked.connect(self.address_enter)

    
    def on_gate_changed(self, i):
        if i == 0:
            self.gate = "gate_one"
        else:
            self.gate = "gate_two"
        self.gate_setter(self.gate)
        return self.gate
    
    def gate_setter(self, gate):
        self.ui.line_camera.setText(self.data[gate]["camera_address"])
        self.ui.line_gate.setText(self.data[gate]["gate_address"])
        self.ui.line_port.setText(self.data[gate]["port_address"])

    def address_enter(self):
        print("[START] Boomgate is Starting...")
        mainWindow.camera_address_enter(self.ui.line_camera.text())
        mainWindow.gate_address_enter(self.ui.line_gate.text())
        mainWindow.port_address_enter(self.ui.line_port.text())
        self.hide()

    def closeEvent(self, event):
        mainWindow.close()

class MainWindow(QMainWindow):
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

        self.gate_selected_handler = self.GateSelectedHandler()
        self.gate_selected_handler.selected_gate.connect(self.on_gate_selected)
        self.gate_stream_address = ''

        self.port_selected_handler = self.PortSelectedHandler()
        self.port_selected_handler.selected_port.connect(self.on_port_selected)
        self.port_stream_address = ''

        
        self.Form = Form()
        self.Form.show()

        self.trans = QTranslator(self)
        self.retranslateUi()
        self.ind_language_selected()

    def closeEvent(self, event):
        self.Form.close()

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUi()
        super(MainWindow, self).changeEvent(event)

    def addMenu(self):
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
        print("ENGLISH")
        QtWidgets.QApplication.instance().removeTranslator(self.trans)
    
    @pyqtSlot()
    def ind_language_selected(self):
        print("BAHASA INDONESIA")
        data = "languages/eng-ind"
        self.trans.load(data)
        QtWidgets.QApplication.instance().installTranslator(self.trans)
    
    @pyqtSlot()
    def camera_address_enter(self, camera_stream_address):
        try:
            self.camera_stream_address = camera_stream_address
            self.camera_stream = CameraStream(self.container_camera, self.screen_width //
                                3, self.screen_height//3, camera_stream_address)
        except:
            print("CAMERA FAILED")
    
    @pyqtSlot()
    def gate_address_enter(self, gate_stream_address):
        self.gate_stream_address = gate_stream_address
        self.gate_selected_handler.selected_gate.emit(True)
        try:
            if self.gate_stream_address == '':
                self.msg[1].setText(QtWidgets.QApplication.translate("MainWindow", "No gate selected"))
                self.msg[1].setIcon(QMessageBox.Warning)
            else:
                self.msg[1].setText(QtWidgets.QApplication.translate("MainWindow", "Gate have been selected"))
                self.msg[1].setIcon(QMessageBox.Information)
                self.msg[1].setDetailedText(self.gate_stream_address)
        except:
            print("GATE FAILED")
    
    @pyqtSlot()
    def port_address_enter(self, port_stream_address):
        self.port_stream_address = port_stream_address
        self.port_selected_handler.selected_port.emit(True)
        try:
            if self.port_stream_address == '':
                self.msg[2].setText(QtWidgets.QApplication.translate("MainWindow", "No port selected"))
                self.msg[2].setIcon(QMessageBox.Warning)
            else:
                self.msg[2].setText(QtWidgets.QApplication.translate("MainWindow", "Port have been selected"))
                self.msg[2].setIcon(QMessageBox.Information)
                self.msg[2].setDetailedText(self.port_stream_address)
                if not self.WebhookWorker.isRunning():
                    print("[START] Webhhok is Starting...")
                    self.WebhookWorker.start()
        except:
            print("PORT FAILED")

    def message_container(self):
        self.msg = {}
        for i in range(3):
            self.msg[i] = QtWidgets.QMessageBox()
            self.msg[i].setWindowTitle("Qlue Boomgate")
            self.msg[i].setIcon(QMessageBox.Warning)

    def show_date(self):
        currentDate = QDate.currentDate()
        currentTime = QTime.currentTime()
        displayTime = currentTime.toString('hh:mm:ss')
        displayDate = currentDate.toString('dd MM yyyy')
        self.ui.label_date.setText(displayDate + " | " + displayTime)

    def welcome_setter(self):
        if status["welcome"] == True:
            self.pixmap_setter(qlue)
            self.ui.label_top.setStyleSheet("font: bold 22px \"Open Sans\";\n"
                                            "color: #ffffff;")
            self.ui.label_top.setText(QtWidgets.QApplication.translate("MainWindow", "Welcome to\nQlue Performa Indonesia"))
            self.ui.label_bot.setText(QtWidgets.QApplication.translate("MainWindow", ""))

    def detection_setter(self):
        if status["valid"] == False:
            self.detection_invalid_setter()
        else:
            pool = QThreadPool().globalInstance()
            runnable = self.PathRun()
            runnable.signals.path_update.connect(self.detection_valid_setter)
            pool.start(runnable)

    def detection_invalid_setter(self):
        self.pixmap_setter(invalid)
        self.label_top.setStyleSheet("font: bold 22px \"Open Sans\";\n"
                                           "color: #e8382b;")
        self.label_top.setText(QtWidgets.QApplication.translate("MainWindow", "Identification Failed"))
        self.label_bot.setText(QtWidgets.QApplication.translate("MainWindow", "Please Try Again"))
        QTimer.singleShot(3000, self.back_welcome_setter)
        
    def detection_valid_setter(self, p):
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
                self.signals.path_update.emit(qlue)
                print("invalid image")    

    @pyqtSlot()
    def back_welcome_setter(self):
        status["valid"] = False
        status["welcome"] = True

    def pixmap_setter(self, path):
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(path)
        label = self.ui.label_image
        label.setMinimumSize(1, 1)
        # label.setMaximumSize(380, 380)
        pixmap = pixmap.scaled(label.width(), label.height(),
                               QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        label.setPixmap(pixmap)

    class APIHandler(QObject):
        setter = pyqtSignal()

    class Webhook:
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
            status['welcome'] = request.json.get(
                'welcome', status['welcome'])
            return jsonify({'status': status})

    class WebhookWorker(QThread):
        def run(self):
            self.port = mainWindow.port_stream_address
            app.run(debug=True, use_reloader=False, port=self.port)

    class GetRequest(QObject):
        timeout_status = pyqtSignal(bool)
        def start(self):
            self.url = mainWindow.gate_stream_address
            self.payload = {}
            self.headers = {}
            self.timeout = False
            try:
                response = requests.request(
                    "GET", self.url, headers=self.headers, data=self.payload, timeout=0.1)
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

    @QtCore.pyqtSlot(bool)
    def on_status_timeout(self, timeout):
        if timeout:
            self.msg[0].show()
        else:
            self.msg[0].hide()

    class GateSelectedHandler(QObject):
        selected_gate = pyqtSignal(bool)

    class PortSelectedHandler(QObject):
        selected_port = pyqtSignal(bool)
    
    @pyqtSlot(bool)
    def on_gate_selected(self, selected):
        if selected:
            self.msg[1].show()
        else:
            self.msg[1].hide()        
    
    @pyqtSlot(bool)
    def on_port_selected(self, selected):
        if selected:
            self.msg[2].show()
        else:
            self.msg[2].hide()        

if __name__ == "__main__":
    application = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(application.exec_())

