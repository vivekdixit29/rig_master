"""
uv_pin_setup.py

This module provides the `UVPinSetup` class which integrates a user interface and 
backend logic for creating UV pin setups and skinCluster bindings within Autodesk Maya.

It allows users to:
    - Select vertices from the Maya scene
    - Apply UV pin constraints and joint setups
    - Optionally connect to existing UV pins or skinClusters
    - Manage rigging elements via an intuitive PySide2-based interface

The UI is built on top of `UVPinUi`, and relies on `MayaOperations` for all
Maya scene manipulations. Designed to support rigging workflows and automate
repetitive setup steps.
"""

from maya_dev.rig_master.gui.uvPin_ui import UVPinUi
from maya_dev.rig_master.src.maya_operations import MayaOperations
from PySide2 import QtCore


class UVPinSetup(UVPinUi):
    """
    UVPinSetup provides a UI-driven workflow for creating UV pin and skin cluster setups
    in Autodesk Maya. It allows users to select vertices, apply joints, UV pins, and optionally
    connect those to skinClusters, streamlining rigging tasks.

    Inherits:
        UVPinUi: Custom QWidget-based UI class containing layout and UI elements.

    Attributes:
        maya_ops (MayaOperations): Backend Maya operation interface for all scene interactions.
    """

    def __init__(self):
        """
        Initializes the UVPinSetup class, connects signals to slots, and configures the UI state.
        """
        super(UVPinSetup, self).__init__()
        self.setupUi(self)
        self.maya_ops = MayaOperations()
        self.setWindowTitle("UVpin Setup")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        self.uvpin_listbox.setVisible(False)
        self.skincluster_listbox.setVisible(False)

        self.connections()
        self.create_btn_enable()
        self.add_master_cluster()

    def connections(self):
        """
        Connects UI components to their corresponding slot methods.
        """
        self.uvpin_chkbox.stateChanged.connect(self.get_uvpin)
        self.skin_cluster_chkbox.stateChanged.connect(self.get_skin_cluster)
        self.create_btn.clicked.connect(self.create_uvpin_setup)
        self.add_btn.clicked.connect(self.get_selected_points)
        self.remove_btn.clicked.connect(self.clear_points_selection)

    def clear_points_selection(self):
        """
        Clears the current selection of vertices from the selected_vertex_listbox.
        """
        self.selected_vertex_listbox.clear()

    def create_uvpin_setup(self):
        """
        Gathers user-selected data and calls `create_bones` with appropriate parameters
        to generate joints, UV pins, and/or skinCluster bindings.
        """
        master_skin_cluster = self.master_cluster_listbox.selectedItems()[0].text()
        selection = [self.selected_vertex_listbox.item(i).text() for i in range(self.selected_vertex_listbox.count())]

        if self.uvpin_chkbox.isChecked() and self.skin_cluster_chkbox.isChecked():
            selected_uv_pin = self.uvpin_listbox.selectedItems()[0].text()
            selected_cluster = self.skincluster_listbox.selectedItems()[0].text()
            self.create_bones(master_skin_cluster, selection, uv_pin=selected_uv_pin, sel_cluster=selected_cluster)
        elif self.uvpin_chkbox.isChecked():
            selected_uv_pin = self.uvpin_listbox.selectedItems()[0].text()
            self.create_bones(master_skin_cluster, selection, uv_pin=selected_uv_pin)
        elif self.skin_cluster_chkbox.isChecked():
            selected_cluster = self.skincluster_listbox.selectedItems()[0].text()
            self.create_bones(master_skin_cluster, selection, sel_cluster=selected_cluster)
        else:
            self.create_bones(master_skin_cluster, selection)

    def get_selected_points(self):
        """
        Fetches selected components from the Maya scene and populates the vertex listbox.
        """
        selection = self.maya_ops.get_selected_component(flatten_flag=True)
        self.selected_vertex_listbox.addItems(selection)
        self.create_btn_enable()

    def create_btn_enable(self):
        """
        Enables the Create button if both vertex and master cluster selections are valid.
        """
        self.create_btn.setEnabled(False)
        if self.selected_vertex_listbox.count() and self.master_cluster_listbox.count():
            self.create_btn.setEnabled(True)

    def get_uvpin(self):
        """
        Toggles UV pin list visibility and populates it with available UV pin nodes.
        """
        if self.uvpin_chkbox.checkState():
            all_uv_pin = self.maya_ops.get_object_based_on_type("uvPin")
            self.uvpin_listbox.setVisible(True)
            self.uvpin_listbox.addItems(all_uv_pin)
        else:
            self.uvpin_listbox.clear()
            self.uvpin_listbox.setVisible(False)

    def get_skin_cluster(self):
        """
        Toggles skin cluster list visibility and populates it with available skinClusters.
        """
        if self.skin_cluster_chkbox.checkState():
            all_skin_cluster = self.maya_ops.get_object_based_on_type("skinCluster")
            self.skincluster_listbox.setVisible(True)
            self.skincluster_listbox.addItems(all_skin_cluster)
        else:
            self.skincluster_listbox.clear()
            self.skincluster_listbox.setVisible(False)

    def add_master_cluster(self):
        """
        Populates the master skinCluster list with all available skinClusters in the scene.
        """
        self.master_cluster_listbox.clear()
        cluster = self.maya_ops.get_object_based_on_type("skinCluster")
        self.master_cluster_listbox.addItems(cluster)

    def create_bones(self, master_cluster, selected_vertices, uv_pin=None, sel_cluster=None):
        """
        Main logic to create bones (joints), control groups, apply UV pin setups and bind to
        skinClusters based on the user's choices.

        Args:
            master_cluster (str): Name of the main skinCluster to connect to.
            selected_vertices (list): List of selected vertex components from the mesh.
            uv_pin (str, optional): Name of the UV pin node, if selected.
            sel_cluster (str, optional): Name of alternate skinCluster to use for binding.
        """
        self.maya_ops.open_undo_chunk()
        cluster_name = None

        if sel_cluster and sel_cluster != master_cluster:
            cluster_name = sel_cluster

        joint_list = []

        for sel in selected_vertices:
            self.maya_ops.clear_selection()
            shape_node = self.maya_ops.get_relatives(sel.split(".")[0], shape_flag=True)[0]
            pos = self.maya_ops.get_object_position(sel)
            bone_jt = self.maya_ops.create_bone(pos)
            joint_list.append(bone_jt)
            self.maya_ops.deselect_object(bone_jt)

            grp_name = self.maya_ops.create_ctrl_setup(bone_jt)
            loc_shape, uv_pin_node = self.maya_ops.create_uv_pin_setup(shape_node, sel, sel_uv_pin=uv_pin)

            self.maya_ops.parent_constrain(loc_shape, grp_name)

            if cluster_name:
                self.maya_ops.setup_skincluster(cluster_name, bone_jt=bone_jt)
            else:
                cluster_name = self.maya_ops.setup_skincluster(
                    joint_list=joint_list,
                    mesh_name=selected_vertices[0].split(".")[0]
                )

            self.maya_ops.create_connection_with_bones(master_cluster, cluster_name, uv_pin_node, grp_name, bone_jt)

        self.maya_ops.close_undo_chunk()
