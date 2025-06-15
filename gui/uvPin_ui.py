"""
This module defines the UVPinUi class, a PySide6 QWidget that serves as a UI panel 
for setting up UV pinning in Autodesk Maya. It allows the user to configure clusters, 
UV pins, and skin clusters, and select specific vertices for processing.

Classes:
    UVPinUi: A QWidget that provides options for creating or selecting existing UV pins,
             skin clusters, and master clusters, along with a list for vertex selection and UI controls.
"""

from PySide6 import QtWidgets, QtCore


class UVPinUi(QtWidgets.QWidget):
    """
    UVPinUi is a PySide6-based QWidget for managing UV Pin-related options in a Maya rigging tool.
    
    UI Features:
        - List existing master clusters
        - Toggle and list existing UV pins
        - Toggle and list existing skin clusters
        - List of selected vertices with add/remove controls
        - Button to trigger the creation of UV pinning
    
    Methods:
        setupUi(): Initializes the layout and widgets.
    """

    def setupUi(self):
        """
        Initializes and sets up the UI layout for UV Pinning.
        """
        self.resize(412, 507)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self)

        # Master Cluster section
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.master_cluster_lbl = QtWidgets.QLabel("Master Cluster")
        self.horizontalLayout.addWidget(self.master_cluster_lbl)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.master_cluster_listbox = QtWidgets.QListWidget()
        self.master_cluster_listbox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.verticalLayout.addWidget(self.master_cluster_listbox)
        self.verticalLayout_5.addLayout(self.verticalLayout)

        # UV Pin and Skin Cluster section
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()

        # UV Pin Panel
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.uvpin_chkbox = QtWidgets.QCheckBox("Use Existing UV pin")
        self.verticalLayout_2.addWidget(self.uvpin_chkbox)
        self.uvpin_listbox = QtWidgets.QListWidget()
        self.verticalLayout_2.addWidget(self.uvpin_listbox)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)

        # Skin Cluster Panel
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.skin_cluster_chkbox = QtWidgets.QCheckBox("Use Existing Skin Cluster")
        self.verticalLayout_4.addWidget(self.skin_cluster_chkbox)
        self.skincluster_listbox = QtWidgets.QListWidget()
        self.verticalLayout_4.addWidget(self.skincluster_listbox)
        self.horizontalLayout_3.addLayout(self.verticalLayout_4)

        self.verticalLayout_5.addLayout(self.horizontalLayout_3)

        # Vertex selection section
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.label_2 = QtWidgets.QLabel("Points to create")
        self.horizontalLayout_2.addWidget(self.label_2)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.remove_btn = QtWidgets.QPushButton("-")
        self.horizontalLayout_2.addWidget(self.remove_btn)
        self.add_btn = QtWidgets.QPushButton("+")
        self.horizontalLayout_2.addWidget(self.add_btn)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.selected_vertex_listbox = QtWidgets.QListWidget()
        self.verticalLayout_3.addWidget(self.selected_vertex_listbox)
        self.verticalLayout_5.addLayout(self.verticalLayout_3)

        # Create Button
        self.create_btn = QtWidgets.QPushButton("Create")
        self.verticalLayout_5.addWidget(self.create_btn)
