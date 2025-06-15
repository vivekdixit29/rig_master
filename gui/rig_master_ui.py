"""
rig_master_ui.py

This module defines the `RigMasterUi` class, a PySide6-based user interface for 
controlling rigging operations within Maya.

The interface includes:
    - Dropdown for selecting connection types
    - Radio buttons for specifying the creation mode (Mesh, Ctrl, Ctrl + Mesh)
    - Checkboxes for enabling additional features (Polygon, Surface, Combine)
    - A button to trigger the rig creation process

This UI is intended to be integrated into a Maya rigging pipeline and provides
a clean, interactive way to define how geometry or controls are created and connected.
"""

from PySide6 import QtWidgets

class RigMasterUi(QtWidgets.QMainWindow):
    """
    A custom PySide6 UI window for rigging-related operations in Maya.

    This UI allows users to:
        - Select a connection type via dropdown
        - Choose between different control creation modes (Mesh, Ctrl, Ctrl + Mesh)
        - Enable options such as Polygon, Surface, and Combine
        - Trigger an action using the 'Create' button

    Designed to be used as part of a larger rigging pipeline where these inputs 
    control how objects are attached or manipulated within Maya.
    """

    def setupUi(self):
        """
        Initializes and sets up the UI layout and widgets for the RigMaster tool.

        Widgets:
            - QComboBox: Connection Type selection
            - QRadioButtons: Create With (Mesh, Ctrl, Ctrl + Mesh)
            - QCheckBoxes: Polygon, Surface, Combine options
            - QPushButton: Create

        Layout is structured vertically with appropriate grouping and spacing.
        """
        self.resize(300, 218)

        # Central Widget
        self.centralwidget = QtWidgets.QWidget()
        self.verticalLayout = QtWidgets.QVBoxLayout()

        # Connection Type Row
        self.connection_layout = QtWidgets.QHBoxLayout()
        self.connection_label = QtWidgets.QLabel("Connection Type :")
        self.connection_combobox = QtWidgets.QComboBox()
        self.connection_layout.addWidget(self.connection_label)
        self.connection_layout.addWidget(self.connection_combobox)
        self.verticalLayout.addLayout(self.connection_layout)

        # Radio Button Group: Create With
        self.groupBox = QtWidgets.QGroupBox("Create With")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)

        self.mesh_btn = QtWidgets.QRadioButton("Mesh", self.groupBox)
        self.cruve_btn = QtWidgets.QRadioButton("Ctrl", self.groupBox)
        self.ctrl_mesh_btn = QtWidgets.QRadioButton("Ctrl + Mesh", self.groupBox)

        self.horizontalLayout.addWidget(self.mesh_btn)
        self.horizontalLayout.addWidget(self.cruve_btn)
        self.horizontalLayout.addWidget(self.ctrl_mesh_btn)
        self.verticalLayout.addWidget(self.groupBox)

        # Horizontal Line Separator
        self.seprator = QtWidgets.QFrame()
        self.seprator.setFrameShape(QtWidgets.QFrame.HLine)
        self.seprator.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLayout.addWidget(self.seprator)

        # Checkboxes: Options
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.poly_chkbox = QtWidgets.QCheckBox("Polygon")
        self.surface_chkbox = QtWidgets.QCheckBox("Surface")
        self.combine_chkbox = QtWidgets.QCheckBox("Combine")

        self.horizontalLayout_3.addWidget(self.poly_chkbox)
        self.horizontalLayout_3.addWidget(self.surface_chkbox)
        self.horizontalLayout_3.addWidget(self.combine_chkbox)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        # Create Button
        self.create_btn = QtWidgets.QPushButton("Create")
        self.verticalLayout.addWidget(self.create_btn)

        # Finalize Layout
        self.centralwidget.setLayout(self.verticalLayout)
        self.setCentralWidget(self.centralwidget)
