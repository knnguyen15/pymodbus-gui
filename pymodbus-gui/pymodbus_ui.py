from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QRect

import sys
from time import sleep
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusIOException

from var_table import VarTable, ReadDataBlock, WriteDataBlock
from main_window import Ui_MainWindow

class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(ReadDataBlock)
    
    
    def __init__(self, parent: QObject | None = None, 
                 address: str = 'localhost', port: int = 502, 
                 sampleRate: float = 0.5,
                 readDataBlock: ReadDataBlock = ReadDataBlock()) -> None:
        super().__init__(parent)
        self.client = ModbusTcpClient(address, port=port)
        self.readDataBlock = readDataBlock
        self.sampleRate = sampleRate

    def run(self):
        try:
            """Long-running task."""
            self.client.connect()
            while True:
                
                if self.readDataBlock.coils['length'] > 0:
                    result = self.client.read_coils(address=self.readDataBlock.coils['address'][0], count=self.readDataBlock.coils['length'])
                    self.readDataBlock.coils['return'] = result.bits
                if self.readDataBlock.discrete_inputs['length'] > 0:
                    result = self.client.read_discrete_inputs(address=self.readDataBlock.discrete_inputs['address'][0], count=self.readDataBlock.discrete_inputs['length'])
                    self.readDataBlock.discrete_inputs['return'] = result.bits
                if self.readDataBlock.hold_registers['length'] > 0:
                    result = self.client.read_holding_registers(address=self.readDataBlock.hold_registers['address'][0], count=self.readDataBlock.hold_registers['length'])
                    self.readDataBlock.hold_registers['return'] = result.registers
                if self.readDataBlock.input_registers['length'] > 0:
                    result = self.client.read_input_registers(address=self.readDataBlock.input_registers['address'][0], count=self.readDataBlock.input_registers['length'])
                    self.readDataBlock.input_registers['return'] = result.registers
                self.progress.emit(self.readDataBlock)
                
                sleep(self.sampleRate)  

        except ConnectionException:
            ...
        except ModbusIOException:
            ...
        except AttributeError:
            ...
        finally:
            ...
        
        self.client.close()
        self.client.close()
    
    def write(self, writeDB: WriteDataBlock):
        for coil in writeDB.coils:
            self.client.write_coil(address = coil, value = writeDB.coils[coil])
        for register in writeDB.hold_registers:
            self.client.write_register(address = register, value = writeDB.hold_registers[register])
        

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

        self.connectBtn.clicked.connect(self.runLongTask)
        self.writeBtn.clicked.connect(self.test)

        self.ipaddInput.setText('127.0.0.1')
        self.portInput.setText('5020')
        self.rateInput.setText('0.5')
    
    def test(self):
        print(str(self.dataTable.model().getWriteData()))
        self.worker.write(self.dataTable.model().getWriteData())
        #print(str(self.dataTable.model().getReadData()))

    def runLongTask(self):
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        try:
            address = self.ipaddInput.toPlainText()
            port = int(self.portInput.toPlainText())
            sampleRate = float(self.rateInput.toPlainText())
        except ValueError:
            print("Input Error")
            return
        else:
            self.worker = Worker(address = address, 
                                port = port, 
                                sampleRate = sampleRate,
                                readDataBlock = self.dataTable.model().getReadData())
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.dataTable.model().updateReadData)
        # Step 6: Start the thread
        self.thread.start()
     
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    #window.runLongTask()
    #window.update_cell(0, 1, "Updated Value")


    # Example of adding a new row
    #window.add_row(["New Row, Col1", "New Row, Col2", "New Row, Col3", "New Row, Col4", "New Row, Col5"])

    sys.exit(app.exec())
