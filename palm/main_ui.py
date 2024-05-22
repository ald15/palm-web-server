import threading
import sys
from PyQt6 import QtWidgets
import PyQt6
import PyQt6.QtCore
import os
import ui_main
import ui_about_us
import server

running = True

'''
Требуется внесение комментариев
'''

class AboutDialog(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = ui_about_us.Ui_Form()
        self.ui.setupUi(self)
        self.ui.btnExit.clicked.connect(self.close)

class ExampleApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = ui_main.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.about_us.triggered.connect(self.show_about_dialog)
        self.ui.lineIP.textChanged.connect(self.updateIP)
        self.ui.linePort.textChanged.connect(self.updatePort)

        self.ui.btnStart.clicked.connect(self.start_server)
        self.ui.btnRestart.clicked.connect(self.restart_server)
        self.ui.btnStop.clicked.connect(self.stop_server)
        self.ui.btnLogClear.clicked.connect(self.clearLog)
        self.ui.btnExit.clicked.connect(QtWidgets.QApplication.quit)

        self.serverIP = "localhost"
        self.serverPort = 80
        self.serverIsStart = False
        self.last_modified = 0
        self.ui.lineIP.setText(self.serverIP)
        self.ui.linePort.setText(str(self.serverPort))

        self.timer = PyQt6.QtCore.QTimer(self)
        self.timer.timeout.connect(self.getLog)
        self.timer.start(1000)

    def show_about_dialog(self):
        self.dialog = AboutDialog()
        self.dialog.show()

    def updateIP(self):
        self.serverIP = self.ui.lineIP.text()
    def updatePort(self):
        try:
            self.serverPort = int(self.ui.linePort.text())
        except:
            self.ui.linePort.clear()

    def updateStatus(self, type):
        if type == 0:
            self.ui.labelStatus.setText("Остановлен")
            self.ui.labelServerStatus.setText("Остановлен")
            self.ui.labelStatus.setStyleSheet("color:red;")
        elif type == 1:
            self.ui.labelStatus.setText("Запущен...")
            self.ui.labelServerStatus.setText("Запущен...")
            self.ui.labelStatus.setStyleSheet("color:green;")
        elif type == 2:
            self.ui.labelStatus.setText("Перезапускается...")
            self.ui.labelServerStatus.setText("Перезапускается...")
            self.ui.labelStatus.setStyleSheet("color:yellow;")

    def updateInfo(self):
        self.ui.labelServerIP.setText(self.serverIP)
        self.ui.labelServerPort.setText(str(self.serverPort))
        self.ui.labelRoutesAmount.setText("2")
        self.ui.labelRoutesActiveAmount.setText("2")

    def serverStart(self, address, port):
        global running
        print(f"Starting server on {address}:{port}")
        self.new_server = server.palmServer(address, port )
        self.new_server.start()

    def start_server(self):
        server.running = True
        self.serverIsStart = True
        self.server_thread = threading.Thread(target=self.serverStart, args=(self.serverIP, self.serverPort), daemon=True)
        self.server_thread.start()
        self.updateStatus(1)
        self.updateInfo()
        
    def stop_server(self):
        server.running = False
        self.updateStatus(0)
        self.new_server.stop()
        self.server_thread.join()

    def restart_server(self):
        if self.serverIsStart:

            self.updateStatus(2)
            self.new_server.log("restart")
            self.stop_server()
            self.start_server()
            self.new_server.log("restarted")
    
    def getLog(self):
        if self.serverIsStart:
            modified = os.path.getmtime(self.new_server.logFile)
            if modified != self.last_modified:
                self.last_modified = modified
                with open(self.new_server.logFile, "r+", encoding="utf8") as f:
                    l = "\n".join(f.readlines())
                self.ui.textLog.setPlainText(l)
                scrollbar = self.ui.textLog.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())

    def clearLog(self):
        if self.serverIsStart:
            os.remove(self.new_server.logFile)
            with open(self.new_server.logFile, "w+"): pass

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ExampleApp()
    window.show()
    sys.exit(app.exec()) 
    
if __name__ == '__main__':
    main()