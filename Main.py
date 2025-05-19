"""
This module defines the `rigMaster` class, which is a GUI tool built with PySide6
for simplifying rigging operations in Autodesk Maya. It provides a user interface
to connect geometry to follicles or surfaces using Maya's muscle and follicle systems.

Classes:
    rigMaster: A PySide6-based GUI that allows users to choose between follicle and surface attach operations
               and execute them based on user selection.
"""

from PySide6 import QtWidgets

from maya_dev.rig_master.gui.rig_master_ui import RigMasterUi
from maya_dev.rig_master.src.maya_operations import MayaOperations


class rigMaster(RigMasterUi, QtWidgets.QMainWindow):
    """
    Main GUI window for the Rig Master tool.

    Inherits from:
        RigMasterUi (Custom UI layout)
        QtWidgets.QMainWindow (PySide6 Main Window)

    Attributes:
        maya_ops (MayaOperations): Provides Maya-specific functionality.

    Methods:
        update_ui(): Sets window properties and populates dropdowns.
        connections(): Connects GUI widgets to their respective callback methods.
        critical_popup(): Displays an error message popup.
        connection_changed(): Handles the behavior when dropdown selection changes.
        create_btn_clicked(): Performs the selected rigging operation based on UI input.
    """

    def __init__(self):
        """
        Initializes the rigMaster UI and Maya operations handler.
        """
        super().__init__()
        self.setup_ui()
        self.maya_ops = MayaOperations()
        self.update_ui()

    def update_ui(self):
        """
        Configures the main window UI, sets size, title,
        populates connection types, and establishes widget connections.
        """
        self.setWindowTitle("Rig Master")
        self.setFixedSize(300, 150)
        connection_type = ["Follicle", "Surface Attach"]
        self.connection_combobox.addItems(connection_type)
        self.connections()

    def connections(self):
        """
        Connects UI signals to corresponding slot methods.
        """
        self.connection_combobox.currentTextChanged.connect(self.connection_changed)
        self.create_btn.clicked.connect(self.create_btn_clicked)

    def critical_popup(self):
        """
        Displays a critical error popup if invalid input is detected.
        """
        QtWidgets.QMessageBox.critical(
            self,
            "Error",
            "Please Select proper options",
            QtWidgets.QMessageBox.StandardButton.Ok
        )

    def connection_changed(self):
        """
        Updates UI widget states based on the current connection type selected in the dropdown.
        """
        print(self.connection_combobox.currentText())
        if self.connection_combobox.currentText() == "Follicle":
            self.mesh_radiobtn.setEnabled(True)
            self.ctrl_radiobtn.setEnabled(True)
        else:
            self.mesh_radiobtn.setEnabled(True)
            self.ctrl_radiobtn.setEnabled(False)

    def create_btn_clicked(self):
        """
        Executes the appropriate Maya operation based on the user's selection in the UI.
        """
        if self.connection_combobox.currentText() == "Follicle":
            if self.mesh_radiobtn.isChecked():
                self.maya_ops.follicle_with_poly()
            elif self.ctrl_radiobtn.isChecked():
                self.follicle_with_ctrl_mesh()
            else:
                self.critical_popup()
        elif self.connection_combobox.currentText() == "Surface Attach":
            if self.mesh_radiobtn.isChecked():
                self.surface_attach_with_poly()
            else:
                self.critical_popup()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    win = rigMaster()
    win.show()
    app.exec()
else:
    win = rigMaster()
    win.show()
