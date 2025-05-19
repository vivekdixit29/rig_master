"""
This module defines the `RigMasterUi` class which creates the user interface layout
for the Rig Master tool using PySide6. The layout includes UI components for selecting
connection types and performing mesh or control-based operations in Autodesk Maya.
"""

from PySide6 import QtWidgets

class RigMasterUi(QtWidgets.QMainWindow):
    """
    Defines the UI layout for the Rig Master tool.

    This class sets up the main window layout, including:
        - A dropdown to choose the type of connection (e.g., Follicle, Surface Attach).
        - Radio buttons to choose connection with Mesh or Control.
        - A push button to trigger the creation logic.

    Attributes:
        connection_combobox (QComboBox): Dropdown for selecting connection type.
        mesh_radiobtn (QRadioButton): Radio button to select Mesh connection.
        ctrl_radiobtn (QRadioButton): Radio button to select Control connection.
        create_btn (QPushButton): Button to initiate the operation.
    """

    def setup_ui(self):
        """
        Initializes and arranges the UI widgets inside the main window.

        Widgets created:
            - QLabel: "Connection Type"
            - QComboBox: Dropdown for selecting operation
            - QGroupBox: Contains mesh/control radio buttons
            - QRadioButton: "Mesh"
            - QRadioButton: "Ctrl"
            - QPushButton: "Create"
            - QFrame: Horizontal separator

        The layout is assigned to the central widget of the QMainWindow.
        """
        central_widget = QtWidgets.QWidget()
        final_layout = QtWidgets.QVBoxLayout(central_widget)

        self.connection_type_label = QtWidgets.QLabel("Connection Type")
        self.connection_combobox = QtWidgets.QComboBox()
        self.connection_type_layout = QtWidgets.QHBoxLayout()
        self.connection_type_layout.addWidget(self.connection_type_label)
        self.connection_type_layout.addWidget(self.connection_combobox)

        self.connect_grpbox = QtWidgets.QGroupBox()
        self.connect_grpbox.setTitle("Connect With")
        self.mesh_radiobtn = QtWidgets.QRadioButton("Mesh")
        self.ctrl_radiobtn = QtWidgets.QRadioButton("Ctrl")
        self.connect_layout = QtWidgets.QHBoxLayout()
        self.connect_layout.addWidget(self.mesh_radiobtn)
        self.connect_layout.addWidget(self.ctrl_radiobtn)
        self.connect_grpbox.setLayout(self.connect_layout)

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.create_btn = QtWidgets.QPushButton("Create")

        final_layout.addLayout(self.connection_type_layout)
        final_layout.addWidget(self.connect_grpbox)
        final_layout.addWidget(separator)
        final_layout.addWidget(self.create_btn)

        self.setCentralWidget(central_widget)
