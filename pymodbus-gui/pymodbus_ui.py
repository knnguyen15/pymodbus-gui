from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QRect

import sys
from time import sleep
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

from var_table import VarTable
from main_window import Ui_MainWindow

class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(list)
    client = ModbusTcpClient('192.168.138.146', port=5020)

    def run(self):
        try:
            """Long-running task."""
            for i in range(1800):
                sleep(1)
                result = self.client.read_holding_registers(address=0, count=10)
                self.progress.emit(result.registers)
            self.client.close()
            self.finished.emit()
        except: ConnectionException

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyModbus GUI")
        self.setGeometry(100, 100, 800, 400)
        self.setupUi(self)

        self.dataTable = VarTable(parent=self.centralwidget)
        self.dataTable.setGeometry(QRect(20, 50, 850, 550))
        self.dataTable.setObjectName("dataTable")

        self.addBtn.clicked.connect(self.dataTable.addRow)
        self.removeBtn.clicked.connect(self.dataTable.removeRow)

        self.connectBtn.clicked.connect(self.test)
    
    def test(self):
        print(str(self.dataTable.model().getReadData()))

    def updateValues(self, values):
        index = self.dataTable.model().createIndex(0, 5)
        self.dataTable.model().setData(index, values[0])

    def runLongTask(self):
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.updateValues)
        # Step 6: Start the thread
        self.thread.start()
     
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.runLongTask()
    #window.update_cell(0, 1, "Updated Value")


    # Example of adding a new row
    #window.add_row(["New Row, Col1", "New Row, Col2", "New Row, Col3", "New Row, Col4", "New Row, Col5"])

    sys.exit(app.exec())
