from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex, pyqtSignal, QItemSelectionModel
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableView, QStyledItemDelegate, QSpinBox, QLineEdit, QComboBox, QTextEdit 

from enum import StrEnum
import sys

MAX_READ_LEN = 100
 
# Modbus blocks types 
class ModbusBlock(StrEnum):
    COIL    = 'coil'
    H_REG   = 'hold. reg'
    I_DISC  = 'disc. in'
    I_REG   = 'in. reg'

# Modbus variable types
class VarType(StrEnum):
    BOOL    = 'bool'
    INT16   = 'int16'
    INT32   = 'int32'
    FLOAT_IEEE  = 'float IEEE'
    FLOAT_S7    = 'float S7'

# Data block reading
class ReadDataBlock():
    def __init__(self) -> None:
        self.coils           = {'address' : [], 'length' :0, 'return': []}
        self.discrete_inputs = {'address' : [], 'length' :0, 'return': []}
        self.hold_registers  = {'address' : [], 'length' :0, 'return': []}
        self.input_registers = {'address' : [], 'length' :0, 'return': []}

    def updateLength(self):
        if len(self.coils['address']) > 0: 
            self.coils['address'].sort()
            self.coils['length'] = self.coils['address'][-1] - self.coils['address'][0] + 1
        if len(self.discrete_inputs['address']) > 0: 
            self.discrete_inputs['address'].sort()
            self.discrete_inputs['length'] = self.discrete_inputs['address'][-1] - self.discrete_inputs['address'][0] + 1
        if len(self.hold_registers['address']) > 0: 
            self.hold_registers['address'].sort()
            self.hold_registers['length'] = self.hold_registers['address'][-1] - self.hold_registers['address'][0] + 1
        if len(self.input_registers['address']) > 0: 
            self.input_registers['address'].sort()
            self.input_registers['length'] = self.input_registers['address'][-1] - self.input_registers['address'][0] + 1

    def __str__(self) -> str:
        outCoil = f"Coils adresses are: {self.coils['address']}\n Coils length: {self.coils['length']}\n"
        outDisI = f"Discrete input adresses are: {self.discrete_inputs['address']}\n Discrete input length: {self.discrete_inputs['length']}\n"
        outHReg = f"Holding registers adresses are: {self.hold_registers['address']}\n Holding registers length: {self.hold_registers['length']}\n"
        outIReg = f"Input registers adresses are: {self.input_registers['address']}\n Input registers length: {self.input_registers['length']}\n"
        return outCoil + outDisI + outHReg + outIReg

class TableModel(QAbstractTableModel):

    def __init__(self, data = [[0, "Register 40001", "hold. reg", "int16", "ab", "", ""]],
                 headers = ["Data Address", "Alias", "Blocks", "Type", "Order", "Value", "Modify"]):
        super(TableModel, self).__init__()
        self._data = data
        self._headers = headers

    def data(self, index, role = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            return self._data[index.row()][index.column()]
        return None

    def rowCount(self, index=None):
        return len(self._data)

    def columnCount(self, index=None):
        return len(self._data[0])

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        # setData for table delegation change
        if index.isValid() and role == Qt.ItemDataRole.EditRole:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, {role})
            return True
        return False
    
    def flags(self, index):
        """
        Return the item flags for the given index.

        The flags are used by the View to determine the item's appearance and
        behavior. The base flags are those of a normal table item.

        If the column is not the Modify column (5), the item is also editable.
        """
        
        if index.column() !=  5:
            return super().flags(index) | Qt.ItemFlag.ItemIsEditable
        return super().flags(index)

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._headers[section]
            else:
                return f"Row {section + 1}"
    
    def insertRows(self, position, rows, parent=QModelIndex()):
        """
        Insert a row into the table data.

        :param position: The row number to insert at
        :param rows: The number of rows to insert
        :param parent: The parent item
        :return: True if successful
        """
        self.beginInsertRows(parent, position, position + rows - 1)
        for i in range(position, position + rows):
            self._data.insert(position, [""] * self.columnCount(parent))
            # self._data.insert(position, self.getDataArray(i, 1)[0])
        self.endInsertRows()
        return True 

    def removeRows(self, position, rows, parent=QModelIndex()):
        """
        Remove a row from the table data.

        :param position: The row number to remove at
        :param rows: The number of rows to remove
        :param parent: The parent item
        :return: True if successful
        """
        self.beginRemoveRows(parent, position, position + rows - 1)
        for _ in range(rows):
            del self._data[position]
        self.endRemoveRows()
        return True
    
    def getDataRows(self, row, count=1):
        """
        Get the data rows of the table model from a row index.

        :param row: The starting row index
        :param count: The number of rows to retrieve
        :return: A list of lists containing the data
        """
        dummy = []
        for i in range(row, min(self.rowCount(), row + count)):
            dummy.append(self._data[i])
        return dummy

    def setDataRows(self, rowIndex: int, value: list, parent=QModelIndex()):
        """
        Set the data row of the table model from a list of lists.

        :param rowIndex: The starting row index
        :param value: The list of lists to set the data from
        :param parent: The parent QModelIndex
        """
        for row in range(len(value)):
            if row >= self.rowCount(): break
            for col in range(len(value[row])):
                if col >= self.columnCount(): break
                index = self.index(rowIndex, col, parent)
                self.setData(index, value[row][col])

    def getReadData(self) -> ReadDataBlock:
        readDataBlock = ReadDataBlock()
        for row in range(self.rowCount()):
            actualRow = self.getDataRows(row)[0]
            match actualRow[2]:
                case ModbusBlock.COIL:
                    if not(actualRow[0] in readDataBlock.coils['address']): 
                        readDataBlock.coils['address'].append(actualRow[0])
                case ModbusBlock.I_DISC:
                    if not(actualRow[0] in readDataBlock.coils['address']): 
                        readDataBlock.discrete_inputs['address'].append(actualRow[0])
                case ModbusBlock.H_REG:
                    if not(actualRow[0] in readDataBlock.coils['address']): 
                        readDataBlock.hold_registers['address'].append(actualRow[0])
                case ModbusBlock.I_REG:
                    if not(actualRow[0] in readDataBlock.coils['address']): 
                        readDataBlock.input_registers['address'].append(actualRow[0])
        readDataBlock.updateLength()
        return readDataBlock
    
    def updateReadData(self, values: ReadDataBlock):
        for row in range(self.rowCount()):
            actualRow = self.getDataRows(row)[0]
            index = self.createIndex(row, 5)
            match actualRow[2]:
                case ModbusBlock.COIL:
                    relativeAddress = actualRow[0] - values.coils['address'][0]
                    self.setData(index, values.coils['return'][relativeAddress])
                case ModbusBlock.I_DISC:
                    relativeAddress = actualRow[0] - values.discrete_inputs['address'][0]
                    self.setData(index, values.discrete_inputs['return'][relativeAddress])
                case ModbusBlock.H_REG:
                    relativeAddress = actualRow[0] - values.hold_registers['address'][0]
                    self.setData(index, values.hold_registers['return'][relativeAddress])
                case ModbusBlock.I_REG:
                    relativeAddress = actualRow[0] - values.input_registers['address'][0]
                    self.setData(index, values.input_registers['return'][relativeAddress])
  
                        
                    
class TableDelegate(QStyledItemDelegate):

    blockChanged = pyqtSignal(QModelIndex, str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        if index.column() == 0: # Address
            editor = QSpinBox(parent)
            editor.setFrame(False)
            editor.setMinimum(0)
            editor.setMaximum(399999)
        if index.column() == 1: # Alias
            editor = QLineEdit(parent)
        if index.column() == 2: # Blocks
            editor = QComboBox(parent)
            editor.addItems([item.value for item in ModbusBlock.__members__.values()])
        if index.column() == 3: # Type
            model = index.model()
            selectedBlock = str(model.data(model.index(index.row(), 2), Qt.ItemDataRole.DisplayRole))
            editor = QComboBox(parent)
            if selectedBlock in [ModbusBlock.COIL, ModbusBlock.I_DISC]:
                editor.addItems([VarType.BOOL])
            else:
                editor.addItems([VarType.INT16, VarType.INT32, VarType.FLOAT_IEEE, VarType.FLOAT_S7])
        if index.column() == 4: # Order
            model = index.model()
            selectedBlock = str(model.data(model.index(index.row(), 3), Qt.ItemDataRole.DisplayRole))
            editor = QComboBox(parent)
            if selectedBlock == VarType.BOOL:
                editor.addItems([''])
            elif selectedBlock == VarType.INT16:
                editor.addItems(['ab', 'ba'])
            else:
                editor.addItems(['abcd', 'dcba', 'badc', 'cdba'])    
        if index.column() >= 5: # Value & Modify
            editor = QTextEdit(parent)
         
        if index.column() in [2, 3]: 
            editor.currentIndexChanged.connect(lambda: self.updateChanged(index, editor.currentText()))
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        if index.column() == 0:
            editor.setValue(value)
        if index.column() == 1:
            editor.setText(value)
        if index.column() >= 2 and index.column() <= 4 and value:
            i = editor.findText(value)
            if i == -1: i = 0
            editor.setCurrentIndex(i)

    def setModelData(self, editor, model, index):
        if index.column() == 0:
            editor.interpretText()
            value = editor.value()
        if index.column() == 1:
            value = editor.displayText()
        if index.column() >= 2 and index.column() <= 4:
            value = editor.currentText()
        model.setData(index, value, Qt.ItemDataRole.EditRole)
        if index.column() in [2, 3, 4]:
            editor.currentIndexChanged.connect(lambda: self.updateChanged(index))

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def updateChanged(self, index, data):
        self.blockChanged.emit(index, data)

class VarTable(QTableView):

    def __init__(self, model: TableModel = TableModel(), delegate: TableDelegate = TableDelegate(), parent=None):
        super().__init__(parent)
        self.setModel(model)
        self.setItemDelegate(delegate)
        self.setColumnWidth(0, 100)
        self.setColumnWidth(1, 150)
        delegate.blockChanged.connect(self.checkSelection)

    def addRow(self, rows = 1):
        # Add one row to selected index or last row if nothing is selected
        selected = self.selectionModel().currentIndex()
        if selected.row() < 1: row = self.model().rowCount()
        else: row = selected.row() + 1
        oldRow = self.model().getDataRows(row - 1, 1)
        self.model().insertRows(row, 1, self.rootIndex())
        
        # Move selected cursor to added row and set data to new row 
        self.selectionModel().setCurrentIndex(selected, QItemSelectionModel.SelectionFlag.Clear)
        self.selectionModel().setCurrentIndex(selected.sibling(selected.row() + 1, selected.column()), QItemSelectionModel.SelectionFlag.Select)
        match oldRow[0][2]: # check old row block type
            case ModbusBlock.COIL:
                newRow = [[oldRow[0][0] + 1, "Register " + str(oldRow[0][0] + 2), 
                           oldRow[0][2],  oldRow[0][3], oldRow[0][4], '', '']]
                self.model().setDataRows(row, newRow)
            case ModbusBlock.I_DISC:
                newRow = [[oldRow[0][0] + 1, "Register " + str(oldRow[0][0] + 10002), 
                           oldRow[0][2],  oldRow[0][3], oldRow[0][4], '', '']]
                self.model().setDataRows(row, newRow)
            case ModbusBlock.H_REG:
                if oldRow[0][3] == VarType.INT16: offset = 1
                else: offset = 2
                newRow = [[oldRow[0][0] + offset, "Register " + str(oldRow[0][0] + 40001 + offset), 
                           oldRow[0][2],  oldRow[0][3], oldRow[0][4], '', '']]
                self.model().setDataRows(row, newRow)
            case ModbusBlock.I_REG:
                if oldRow[0][3] == VarType.INT16: offset = 1
                else: offset = 2
                newRow = [[oldRow[0][0] + offset, "Register " + str(oldRow[0][0] + 30001 + offset), 
                           oldRow[0][2],  oldRow[0][3], oldRow[0][4], '', '']]
                self.model().setDataRows(row, newRow)
    
    def removeRow(self, rows = 1):
        if self.model().rowCount() < 2: return
        selected = self.selectionModel().currentIndex()
        if selected.row() < 0: row = self.model().rowCount() - 1
        else: row = selected.row() 
        self.model().removeRows(row, 1, self.rootIndex())

    def checkSelection(self, index: QModelIndex, selection):
        block_index = index.sibling(index.row(), 2)
        type_index  = index.sibling(index.row(), 3)
        order_index = index.sibling(index.row(), 4)

        print(f'--------Row {index.row()} changed --- {selection}')
        print(self.model().data(block_index))
        print(self.model().data(type_index))
        print(self.model().data(order_index))
        
        # if user change block 
        if index.column() == 2: 
            if  selection in [ModbusBlock.COIL, ModbusBlock.I_DISC]:
                if self.model().data(type_index) != VarType.BOOL: 
                    self.model().setData(type_index, VarType.BOOL.value)
                    self.model().setData(order_index, '')
            else:
                if not (self.model().data(type_index) in [VarType.INT16, VarType.INT32, VarType.FLOAT_S7, VarType.FLOAT_IEEE]):
                    self.model().setData(type_index, VarType.INT16.value)
                if not (self.model().data(order_index) in ['ab', 'ba', 'abcd', 'dcba', 'badc', 'cdba']):          
                    self.model().setData(order_index, 'ab')
        
        # if user change type
        if index.column() == 3: 
            if  selection == VarType.BOOL: 
                if self.model().data(order_index) != '':                          
                    self.model().setData(order_index, '')
                if not (self.model().data(block_index) in [ModbusBlock.COIL, ModbusBlock.I_DISC]):  
                    self.model().setData(block_index, ModbusBlock.COIL.value)
            elif  selection == VarType.INT16: 
                if not (self.model().data(order_index) in ['ab', 'ba']):          
                    self.model().setData(order_index, 'ab')
                if not (self.model().data(block_index) in [ModbusBlock.H_REG, ModbusBlock.I_REG]):
                    self.model().setData(block_index, ModbusBlock.H_REG.value)
            else:
                if not (self.model().data(order_index) in ['abcd', 'dcba', 'badc', 'cdba']):          
                    self.model().setData(order_index, 'abcd')
                if not (self.model().data(block_index) in [ModbusBlock.H_REG, ModbusBlock.I_REG]):
                    self.model().setData(block_index, ModbusBlock.H_REG.value)

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Var Table")
        self.setGeometry(100, 100, 800, 400)

        self.table_view = VarTable()

        self.setCentralWidget(self.table_view)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()

    sys.exit(app.exec())