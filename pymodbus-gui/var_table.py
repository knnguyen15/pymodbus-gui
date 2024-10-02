from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex, pyqtSignal, QItemSelectionModel
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableView, QStyledItemDelegate, QSpinBox, QLineEdit, QComboBox, QTextEdit 

from enum import StrEnum
from utils import BytesConversion as conv
import sys

MAX_READ_LEN = 100
 
# Modbus blocks types 
class ModbusBlock(StrEnum):
    COIL    = 'coil'
    H_REG   = 'hold. reg'
    I_DISC  = 'disc. in'
    I_REG   = 'in. reg'

# Modbus variable types
class DispVarType(StrEnum):
    BOOL    = 'bool'
    UINT16  = 'uint16'
    INT16   = 'int16'
    UINT32  = 'uint32'
    INT32   = 'int32'
    FLOAT   = 'float32'
    UINT64  = 'uint64'
    INT64   = 'int64'
    DOUBLE  = 'float64'
    def __len__(self) -> int:
        """Return the size in bytes of a variable of this type."""
        if self == DispVarType.BOOL: return 1
        if self == DispVarType.UINT16: return 2
        if self == DispVarType.INT16: return 2
        if self == DispVarType.UINT32: return 4
        if self == DispVarType.INT32: return 4
        if self == DispVarType.FLOAT: return 4
        if self == DispVarType.UINT64: return 8
        if self == DispVarType.INT64: return 8
        if self == DispVarType.DOUBLE: return 8
    def typeLength(type: str) -> int:
        """Return the size in bytes of a variable of this type."""
        if type == DispVarType.BOOL: return 1
        if type == DispVarType.UINT16: return 2
        if type == DispVarType.INT16: return 2
        if type == DispVarType.UINT32: return 4
        if type == DispVarType.INT32: return 4
        if type == DispVarType.FLOAT: return 4
        if type == DispVarType.UINT64: return 8
        if type == DispVarType.INT64: return 8
        if type == DispVarType.DOUBLE: return 8

# Data block reading
class ReadDataBlock():
    def __init__(self) -> None:
        self.coils           = {'address' : [], 'length' :0, 'return': []}
        self.discrete_inputs = {'address' : [], 'length' :0, 'return': []}
        self.hold_registers  = {'address' : [], 'length' :0, 'return': []}
        self.input_registers = {'address' : [], 'length' :0, 'return': []}

    def updateLength(self, maxLen: dict = {'coil':1, 'disc_in':1, 'hold_reg':1, 'in_reg':1}) -> None:
        if len(self.coils['address']) > 0: 
            self.coils['address'].sort()
            self.coils['length'] = self.coils['address'][-1] - self.coils['address'][0] + maxLen['coil']
        if len(self.discrete_inputs['address']) > 0: 
            self.discrete_inputs['address'].sort()
            self.discrete_inputs['length'] = self.discrete_inputs['address'][-1] - self.discrete_inputs['address'][0] + maxLen['disc_in']
        if len(self.hold_registers['address']) > 0: 
            self.hold_registers['address'].sort()
            self.hold_registers['length'] = self.hold_registers['address'][-1] - self.hold_registers['address'][0] + maxLen['hold_reg']
        if len(self.input_registers['address']) > 0: 
            self.input_registers['address'].sort()
            self.input_registers['length'] = self.input_registers['address'][-1] - self.input_registers['address'][0] + maxLen['in_reg']

    def __str__(self) -> str:
        outCoil = f"Coils adresses are: {self.coils['address']}\n Coils length: {self.coils['length']}\n"
        outDisI = f"Discrete input adresses are: {self.discrete_inputs['address']}\n Discrete input length: {self.discrete_inputs['length']}\n"
        outHReg = f"Holding registers adresses are: {self.hold_registers['address']}\n Holding registers length: {self.hold_registers['length']}\n"
        outIReg = f"Input registers adresses are: {self.input_registers['address']}\n Input registers length: {self.input_registers['length']}\n"
        return outCoil + outDisI + outHReg + outIReg

# Data block writing
class WriteDataBlock():
    def __init__(self) -> None:
        self.coils = {}
        self.hold_registers  = {}
    
    def __str__(self) -> str:
        coilStr = '--------- Coils write address and value: \n'
        for coil in self.coils: coilStr = coilStr + f"Coils adresses: {coil} -- Value {self.coils[coil]}\n"
        regStr = '-------- Register write address and value: \n'
        for reg in self.hold_registers: regStr = regStr + f"Register adresses: {reg} -- Value {self.hold_registers[reg]}\n"
        return coilStr + regStr

# Model
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
    
    def insertRows(self, row, rows, parent=QModelIndex()):
        """
        Insert a row into the table data.

        :param position: The row number to insert at
        :param rows: The number of rows to insert
        :param parent: The parent item
        :return: True if successful
        """
        self.beginInsertRows(parent, row, row + rows - 1)
        for i in range(row, row + rows):
            self._data.insert(row, [""] * self.columnCount(parent))
            # self._data.insert(position, self.getDataArray(i, 1)[0])
        self.endInsertRows()
        return True 

    def removeRows(self, row, count, parent=QModelIndex()):
        """
        Remove a row from the table data.

        :param position: The row number to remove at
        :param rows: The number of rows to remove
        :param parent: The parent item
        :return: True if successful
        """
        self.beginRemoveRows(parent, row, row + count - 1)
        for _ in range(count):
            del self._data[row]
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
        # max address for each register type
        co_max = 0
        di_max = 0
        hr_max = 0
        ir_max = 0
        # datalength corresponding to max address
        co_last = 1
        di_last = 1
        hr_last = 1
        ir_last = 1

        for row in range(self.rowCount()):
            actualRow = self.getDataRows(row)[0]
            match actualRow[2]:
                case ModbusBlock.COIL:
                    if not(actualRow[0] in readDataBlock.coils['address']): 
                        readDataBlock.coils['address'].append(actualRow[0])
                        co_max = max(co_max, actualRow[0])
                        if co_max == actualRow[0]: co_last = DispVarType.typeLength(actualRow[3])
                case ModbusBlock.I_DISC:
                    if not(actualRow[0] in readDataBlock.discrete_inputs['address']): 
                        readDataBlock.discrete_inputs['address'].append(actualRow[0])
                        di_max = max(di_max, actualRow[0])
                        if di_max == actualRow[0]: di_last = DispVarType.typeLength(actualRow[3])
                case ModbusBlock.H_REG:
                    if not(actualRow[0] in readDataBlock.hold_registers['address']): 
                        readDataBlock.hold_registers['address'].append(actualRow[0])
                        hr_max = max(hr_max, actualRow[0])
                        if hr_max == actualRow[0]: hr_last = DispVarType.typeLength(actualRow[3])
                case ModbusBlock.I_REG:
                    if not(actualRow[0] in readDataBlock.input_registers['address']): 
                        readDataBlock.input_registers['address'].append(actualRow[0])
                        ir_max = max(ir_max, actualRow[0])
                        if ir_max == actualRow[0]: ir_last = DispVarType.typeLength(actualRow[3])
        readDataBlock.updateLength({'coil':co_last, 'disc_in':di_last, 'hold_reg':hr_last, 'in_reg':ir_last})
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
                    # ======= Check Byte Swapping
                    match actualRow[4]:
                        # 16-bit data length
                        case 'ab': setData = values.hold_registers['return'][relativeAddress]
                        case 'ba': setData = conv.swapBytes([values.hold_registers['return'][relativeAddress]])[0]
                        # 32-bit data length
                        case 'abcd': bufferUInt16 = values.hold_registers['return'][relativeAddress:relativeAddress+2]
                        case 'badc': bufferUInt16 = conv.swapBytes(values.hold_registers['return'][relativeAddress:relativeAddress+2])
                        case 'cdab': bufferUInt16 = conv.swapWords(values.hold_registers['return'][relativeAddress:relativeAddress+2])
                        case 'dcba': bufferUInt16 = conv.swapBytes(conv.swapWords(values.hold_registers['return'][relativeAddress:relativeAddress+2]))
                        # 64-bit data length - 1 swap
                        case 'no-swap'      : bufferUInt16 = values.hold_registers['return'][relativeAddress:relativeAddress+4]
                        case 'byte swap'    : bufferUInt16 = conv.swapBytes(values.hold_registers['return'][relativeAddress:relativeAddress+4])
                        case 'word swap'    : bufferUInt16 = conv.swapWords(values.hold_registers['return'][relativeAddress:relativeAddress+4])
                        case 'dword swap'   : bufferUInt16 = conv.swapDwords(values.hold_registers['return'][relativeAddress:relativeAddress+4])
                        # 64-bit data length - 2 swap
                        case 'd-w swap'     : 
                            bufferUInt16 = conv.swapDwords(values.hold_registers['return'][relativeAddress:relativeAddress+4])
                            bufferUInt16 = conv.swapWords(bufferUInt16)
                        case 'd-b swap'     : 
                            bufferUInt16 = conv.swapDwords(values.hold_registers['return'][relativeAddress:relativeAddress+4])
                            bufferUInt16 = conv.swapBytes(bufferUInt16)
                        case 'w-b swap'     :  
                            bufferUInt16 = conv.swapWords(values.hold_registers['return'][relativeAddress:relativeAddress+4])
                            bufferUInt16 = conv.swapBytes(bufferUInt16) 
                        # 64-bit data length - 3 swap
                        case 'd-w-b swap'     :  
                            bufferUInt16 = conv.swapDwords(values.hold_registers['return'][relativeAddress:relativeAddress+4])
                            bufferUInt16 = conv.swapWords(bufferUInt16)
                            bufferUInt16 = conv.swapBytes(bufferUInt16) 
                            
                    # ======= Check Data Format
                    match actualRow[3]:
                        # 16-bit data length
                        case DispVarType.INT16:     setData = conv.toInt16(setData)
                        case DispVarType.UINT16:    setData = setData
                        # 32-bit data length
                        case DispVarType.INT32:     setData = conv.toInt32(bufferUInt16)
                        case DispVarType.UINT32:    setData = conv.toUInt32(bufferUInt16)
                        case DispVarType.FLOAT:     setData = conv.toFloat32(bufferUInt16)
                        # 64-bit data length
                        case DispVarType.INT64:     setData = conv.toInt64(bufferUInt16)
                        case DispVarType.UINT64:    setData = conv.toUInt64(bufferUInt16)
                        case DispVarType.DOUBLE:    setData = conv.toDouble(bufferUInt16)

                    self.setData(index, setData)

                case ModbusBlock.I_REG:
                    relativeAddress = actualRow[0] - values.input_registers['address'][0]
                    # ======= Check Byte Swapping
                    match actualRow[4]:
                        # 16-bit data length
                        case 'ab': setData = values.input_registers['return'][relativeAddress]
                        case 'ba': setData = conv.swapBytes([values.input_registers['return'][relativeAddress]])[0]
                        # 32-bit data length
                        case 'abcd': bufferUInt16 = values.input_registers['return'][relativeAddress:relativeAddress+2]
                        case 'badc': bufferUInt16 = conv.swapBytes(values.input_registers['return'][relativeAddress:relativeAddress+2])
                        case 'cdab': bufferUInt16 = conv.swapWords(values.input_registers['return'][relativeAddress:relativeAddress+2])
                        case 'dcba': bufferUInt16 = conv.swapBytes(conv.swapWords(values.input_registers['return'][relativeAddress:relativeAddress+2]))
                        # 64-bit data length - 1 swap
                        case 'no-swap'      : bufferUInt16 = values.input_registers['return'][relativeAddress:relativeAddress+4]
                        case 'byte swap'    : bufferUInt16 = conv.swapBytes(values.input_registers['return'][relativeAddress:relativeAddress+4])
                        case 'word swap'    : bufferUInt16 = conv.swapWords(values.input_registers['return'][relativeAddress:relativeAddress+4])
                        case 'dword swap'   : bufferUInt16 = conv.swapDwords(values.input_registers['return'][relativeAddress:relativeAddress+4])
                        # 64-bit data length - 2 swap
                        case 'd-w swap'     : 
                            bufferUInt16 = conv.swapDwords(values.input_registers['return'][relativeAddress:relativeAddress+4])
                            bufferUInt16 = conv.swapWords(bufferUInt16)
                        case 'd-b swap'     : 
                            bufferUInt16 = conv.swapDwords(values.input_registers['return'][relativeAddress:relativeAddress+4])
                            bufferUInt16 = conv.swapBytes(bufferUInt16)
                        case 'w-b swap'     :  
                            bufferUInt16 = conv.swapWords(values.input_registers['return'][relativeAddress:relativeAddress+4])
                            bufferUInt16 = conv.swapBytes(bufferUInt16) 
                        # 64-bit data length - 3 swap
                        case 'd-w-b swap'     :  
                            bufferUInt16 = conv.swapDwords(values.input_registers['return'][relativeAddress:relativeAddress+4])
                            bufferUInt16 = conv.swapWords(bufferUInt16)
                            bufferUInt16 = conv.swapBytes(bufferUInt16) 
                    # ======= Check Data Format
                    match actualRow[3]:
                        # 16-bit data length
                        case DispVarType.INT16:     setData = conv.toInt16(setData)
                        case DispVarType.UINT16:    setData = setData
                        # 32-bit data length
                        case DispVarType.INT32:     setData = conv.toInt32(bufferUInt16)
                        case DispVarType.UINT32:    setData = conv.toUInt32(bufferUInt16)
                        case DispVarType.FLOAT:   setData = conv.toFloat32(bufferUInt16)
                        # 64-bit data length
                        case DispVarType.INT64:     setData = conv.toInt64(bufferUInt16)
                        case DispVarType.UINT64:    setData = conv.toUInt64(bufferUInt16)
                        case DispVarType.DOUBLE:   setData = conv.toDouble(bufferUInt16)

                    self.setData(index, setData)

    def getWriteData(self) -> WriteDataBlock:
        writeDataBlock = WriteDataBlock()
        
        for row in range(self.rowCount()):
            actualRow = self.getDataRows(row)[0]
            match actualRow[3]:
                case DispVarType.BOOL:
                    if str(actualRow[6]).lower() in ['true', '1']:
                        writeDataBlock.coils.update({actualRow[0]: True})
                    elif str(actualRow[6]).lower() in ['false', '0']:
                        writeDataBlock.coils.update({actualRow[0]: False})
                    else:
                        continue
                case DispVarType.INT16:
                    try:
                        value = conv.fromInt16(int(actualRow[6]))[0]
                        writeDataBlock.hold_registers.update({actualRow[0]: value})
                    except ValueError:
                        continue
                case DispVarType.UINT16:
                    try:
                        value = int(actualRow[6])
                        writeDataBlock.hold_registers.update({actualRow[0]: value})
                    except ValueError:
                        continue
                case DispVarType.INT32:
                    try:
                        value = conv.fromInt32(int(actualRow[6]))
                        writeDataBlock.hold_registers.update({actualRow[0]: value [0]})
                        writeDataBlock.hold_registers.update({actualRow[0] + 1: value [1]})
                    except ValueError:
                        continue
                case DispVarType.UINT32:
                    try:
                        value = conv.fromUInt32(int(actualRow[6]))
                        writeDataBlock.hold_registers.update({actualRow[0]: value [0]})
                        writeDataBlock.hold_registers.update({actualRow[0] + 1: value [1]})
                    except ValueError:
                        continue
                case DispVarType.FLOAT:
                    try:
                        value = conv.fromFloat32(float(actualRow[6]))
                        writeDataBlock.hold_registers.update({actualRow[0]: value [0]})
                        writeDataBlock.hold_registers.update({actualRow[0] + 1: value [1]})
                    except ValueError:
                        continue
        
        return writeDataBlock



# Controller            
class TableDelegate(QStyledItemDelegate):

    blockChanged = pyqtSignal(QModelIndex, str)

    def __init__(self, parent=None):
        """
        Initialize a new TableDelegate.

        :param parent: The parent object of this delegate
        """
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        """
        Create an editor widget, based on the item data.

        :param parent: The parent object of this delegate
        :param option: The style options for the editor
        :param index: The QModelIndex of the item to be edited
        :return: The editor widget
        """
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
                editor.addItems([DispVarType.BOOL])
            else:
                editor.addItems([i for i in DispVarType.__members__.values() if i != DispVarType.BOOL])
        if index.column() == 4: # Order
            model = index.model()
            selectedBlock = str(model.data(model.index(index.row(), 3), Qt.ItemDataRole.DisplayRole))
            editor = QComboBox(parent)
            if selectedBlock == DispVarType.BOOL:
                editor.addItems([''])
            elif selectedBlock in [DispVarType.INT16, DispVarType.UINT16]:
                editor.addItems(['ab', 'ba'])
            elif selectedBlock in [DispVarType.INT32, DispVarType.UINT32, DispVarType.FLOAT]:
                editor.addItems(['abcd', 'dcba', 'badc', 'cdab'])    
            else:
                editor.addItems(['no-swap', 'dword swap', 'word swap', 'byte swap', 'd-w swap', 'd-b swap', 'w-b swap', 'd-w-b swap'])
        if index.column() >= 5: # Value & Modify
            editor = QLineEdit(parent)
         
        if index.column() in [2, 3]: 
            editor.currentIndexChanged.connect(lambda: self.updateChanged(index, editor.currentText()))
        return editor

    def setEditorData(self, editor, index):
        """
        Set the editor's data based on the data of the item being edited.

        :param editor: The editor widget
        :param index: The QModelIndex of the item to be edited
        :return: None
        """
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
        """
        Set the model's data based on the data of the item being edited.

        :param editor: The editor widget
        :param model: The model being edited
        :param index: The QModelIndex of the item to be edited
        :return: None
        """
        if index.column() == 0:
            editor.interpretText()
            value = editor.value()
        if index.column() in [1, 6]:
            value = editor.displayText()
        if index.column() in [2, 3, 4]:
            value = editor.currentText() 
        model.setData(index, value, Qt.ItemDataRole.EditRole)
        if index.column() in [2, 3, 4]:
            editor.currentIndexChanged.connect(lambda: self.updateChanged(index))

    def updateEditorGeometry(self, editor, option, index):
        """
        Set the geometry of the given editor based on the option and index.

        This is a reimplementation of QStyledItemDelegate.updateEditorGeometry.

        :param editor: The editor widget
        :param option: The style options
        :param index: The QModelIndex of the item to be edited
        :return: None
        """
        editor.setGeometry(option.rect)

    def updateChanged(self, index, data):
        """
        Emits the blockChanged signal when the value of the given index
        has changed.

        :param index: The QModelIndex of the item that has changed
        :param data: The new value
        :return: None
        """
        self.blockChanged.emit(index, data)

# View
class VarTable(QTableView):

    def __init__(self, model: TableModel = TableModel(), delegate: TableDelegate = TableDelegate(), parent=None):
        """
        Initialize the VarTable widget.

        :param model: The TableModel instance to use.
        :type model: TableModel
        :param delegate: The TableDelegate instance to use.
        :type delegate: TableDelegate
        :param parent: The parent widget.
        :type parent: QWidget
        """
        super().__init__(parent)
        self.setModel(model)
        self.setItemDelegate(delegate)
        self.setColumnWidth(0, 100)
        self.setColumnWidth(1, 150)
        delegate.blockChanged.connect(self.checkSelection)

    def addRow(self, rows = 1):
        """
        Add one row to selected index or last row if nothing is selected
        Move selected cursor to added row and set data to new row 
        """
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
                offset = int(DispVarType.typeLength(oldRow[0][3]) / 2)
                newRow = [[oldRow[0][0] + offset, "Register " + str(oldRow[0][0] + 40001 + offset), 
                           oldRow[0][2],  oldRow[0][3], oldRow[0][4], '', '']]
                self.model().setDataRows(row, newRow)
            case ModbusBlock.I_REG:
                offset = int(DispVarType.typeLength(oldRow[0][3]) / 2)
                newRow = [[oldRow[0][0] + offset, "Register " + str(oldRow[0][0] + 30001 + offset), 
                           oldRow[0][2],  oldRow[0][3], oldRow[0][4], '', '']]
                self.model().setDataRows(row, newRow)
    
    def removeRow(self, rows = 1):
        """
        Remove one row from selected index or last row if nothing is selected
        Do not do anything if there is only one row left
        """
        if self.model().rowCount() < 2: return
        selected = self.selectionModel().currentIndex()
        if selected.row() < 0: row = self.model().rowCount() - 1
        else: row = selected.row() 
        self.model().removeRows(row, 1, self.rootIndex())

    def checkSelection(self, index: QModelIndex, selection):
        """
        Check if the selected cell has changed and update the related cells in the same row
        according to the logic of the table.

        :param index: The QModelIndex of the changed cell
        :param selection: The selected data
        :return: None
        """
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
                if self.model().data(type_index) != DispVarType.BOOL: 
                    self.model().setData(type_index, DispVarType.BOOL.value)
                    self.model().setData(order_index, '')
            else:
                if not (DispVarType.typeLength(self.model().data(type_index)) == 2):
                    self.model().setData(type_index, DispVarType.INT16.value)
                if not (self.model().data(order_index) in ['ab', 'ba', 'abcd', 'dcba', 'badc', 'cdab',
                                                           'no-swap', 'dword swap', 'word swap', 'byte swap', 'd-w swap', 'd-b swap', 'w-b swap', 'd-b swap']):          
                    self.model().setData(order_index, 'ab')
        
        # if user change type
        if index.column() == 3: 
            if  selection == DispVarType.BOOL: 
                if self.model().data(order_index) != '':                          
                    self.model().setData(order_index, '')
                if not (self.model().data(block_index) in [ModbusBlock.COIL, ModbusBlock.I_DISC]):  
                    self.model().setData(block_index, ModbusBlock.COIL.value)
            elif  selection in [DispVarType.INT16, DispVarType.UINT16]: 
                if not (self.model().data(order_index) in ['ab', 'ba']):          
                    self.model().setData(order_index, 'ab')
                if not (self.model().data(block_index) in [ModbusBlock.H_REG, ModbusBlock.I_REG]):
                    self.model().setData(block_index, ModbusBlock.H_REG.value)
            elif  selection in [DispVarType.INT32, DispVarType.UINT32, DispVarType.FLOAT]: 
                if not (self.model().data(order_index) in ['abcd', 'dcba', 'badc', 'cdab']):          
                    self.model().setData(order_index, 'abcd')
                if not (self.model().data(block_index) in [ModbusBlock.H_REG, ModbusBlock.I_REG]):
                    self.model().setData(block_index, ModbusBlock.H_REG.value)
            else:
                if not (self.model().data(order_index) in ['no-swap', 'dword swap', 'word swap', 'byte swap', 'd-w swap', 'd-b swap', 'w-b swap', 'd-b swap']):          
                    self.model().setData(order_index, 'no-swap')
                if not (self.model().data(block_index) in [ModbusBlock.H_REG, ModbusBlock.I_REG]):
                    self.model().setData(block_index, ModbusBlock.H_REG.value)

# Test Windows
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