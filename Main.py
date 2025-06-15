"""
rig_master.py

This module defines the `RigMaster` class, a PySide6-based GUI for rigging tools in Autodesk Maya.
It allows users to attach geometry to surfaces using follicles or muscle-based surface attach techniques.
This tool is designed to simplify repetitive rigging tasks for technical artists.

Usage Modes:
- Follicle-based attachment (polygonal/nurbs surfaces)
- Surface attach via Maya muscle system
- UV Pin-based attachment (opens separate UI)

Classes:
    RigMaster (QtWidgets.QMainWindow): The main UI window class for the Rig Master tool.
"""

from PySide6 import QtCore, QtWidgets
import math
import sys

from maya_dev.rig_master.gui.rig_master_ui import RigMasterUi
from maya_dev.rig_master.src.uvpin import UVPinSetup
from maya_dev.rig_master.src.maya_operations import MayaOperations


class RigMaster(QtWidgets.QMainWindow, RigMasterUi):
    """
    Main window class for the Rig Master tool. Allows the user to choose between different geometry
    attachment options like Follicle, Surface Attach, and UV Pin.

    Inherits:
        QtWidgets.QMainWindow: Provides the main window behavior.
        RigMasterUi: The UI layout generated via Qt Designer.

    Methods:
        update_ui(): Initializes and updates default UI settings.
        connections(): Connects UI signals to their respective slots.
        create_rig(): Executes the selected rigging operation.
        update_attach_options(): Updates UI based on selected rigging mode.
        update_attach_widget(): Manages enable/disable state of options based on widget selection.
        update_combine_widget(): Shows/hides combine checkbox depending on poly state.
        uncheck_mesh(): Helper method to uncheck poly-related options.
        uncheck_surface(): Helper method to uncheck surface-related options.
        surface_attach_system(): Executes muscle-based surface attach logic.
        surface_attach_with_ctrl(): Surface attach logic when using controls on curves or meshes.
        surface_with_ctrl_mesh(): Surface attach logic with closest polygon face logic.
        follicle_system(): Executes follicle-based attachment logic.
        follicle_with_cruve(): Follicle attachment using poly/nurbs plane per control or combined surface.
    """
    
    def __init__(self):
        """
        Initialize the Rig Master UI and set up internal tools and UI behavior.
        """
        super(RigMaster, self).__init__()
        print("Start")
        self.setWindowTitle("Rig Master")
        self.setupUi()
        self.maya_ops = MayaOperations()
        self.update_ui()
        self.connections()

    def update_ui(self):
        """
        Sets default window title, sizing, and combo box options.
        """
        self.setWindowTitle("Rig Master")
        self.setMaximumSize(240, 120)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        connection_type_list = ["Surface Attach", "Follicle", "UV Pin"]
        self.connection_combobox.addItems(connection_type_list)
        self.update_attach_options()
        self.create_btn.setEnabled(False)

    def connections(self):
        """
        Connects user interactions (buttons, checkboxes, combo box changes) to appropriate slots.
        """
        self.connection_combobox.currentTextChanged.connect(self.update_attach_options)
        self.create_btn.clicked.connect(self.create_rig)
        self.poly_chkbox.clicked.connect(self.uncheck_surface)
        self.surface_chkbox.clicked.connect(self.uncheck_mesh)
        self.mesh_btn.clicked.connect(self.update_attach_widget)
        self.cruve_btn.clicked.connect(self.update_attach_widget)
        self.ctrl_mesh_btn.clicked.connect(self.update_attach_widget)

    def create_rig(self):
        """
        Initiates the selected rigging operation and wraps it inside an undo chunk.
        """
        self.maya_ops.open_undo_chunk()
        if self.connection_combobox.currentText() == "Follicle":
            self.follicle_system()
        if self.connection_combobox.currentText() == "Surface Attach":
            self.surface_attach_system()
        self.maya_ops.close_undo_chunk()

    def update_attach_options(self):
        """
        Updates checkboxes and combo box behavior based on selected rigging type.
        Launches the UV Pin UI if selected.
        """
        if self.connection_combobox.currentText() == "Follicle":
            self.surface_chkbox.setVisible(True)
            self.combine_chkbox.setVisible(False)
        if self.connection_combobox.currentText() == "Surface Attach":
            self.surface_chkbox.setVisible(False)
            self.combine_chkbox.setVisible(True)
        if self.connection_combobox.currentText() == "UV Pin":
            self.combine_chkbox.setVisible(False)
            self.surface_chkbox.setVisible(False)
            self.combine_chkbox.setEnabled(False)
            self.surface_chkbox.setEnabled(False)
            self.poly_chkbox.setEnabled(False)
            self.mesh_btn.setEnabled(False)
            self.cruve_btn.setEnabled(False)
            self.ctrl_mesh_btn.setEnabled(False)
            self.uvpin_window = UVPinSetup()
            self.uvpin_window.show()
            self.uvpin_window.raise_()
            self.uvpin_window.activateWindow()

        self.poly_chkbox.setVisible(True)
        self.combine_chkbox.setCheckState(QtCore.Qt.Unchecked)
        self.surface_chkbox.setCheckState(QtCore.Qt.Unchecked)
        self.poly_chkbox.setCheckState(QtCore.Qt.Unchecked)

    def update_attach_widget(self):
        """
        Enables/disables checkboxes based on which mesh/curve/control mesh button is active.
        """
        if self.mesh_btn.isChecked() or self.ctrl_mesh_btn.isChecked():
            self.combine_chkbox.setEnabled(False)
            self.surface_chkbox.setEnabled(False)
            self.poly_chkbox.setEnabled(False)
        elif self.cruve_btn.isChecked():
            self.combine_chkbox.setEnabled(True)
            self.surface_chkbox.setEnabled(True)
            self.poly_chkbox.setEnabled(True)
        if self.mesh_btn.isChecked() or self.cruve_btn.isChecked() or self.ctrl_mesh_btn.isChecked():
            self.create_btn.setEnabled(True)
        else:
            self.create_btn.setEnabled(False)

        self.combine_chkbox.setCheckState(QtCore.Qt.Unchecked)
        self.surface_chkbox.setCheckState(QtCore.Qt.Unchecked)
        self.poly_chkbox.setCheckState(QtCore.Qt.Unchecked)

    def update_combine_widget(self):
        """
        Updates visibility of combine checkbox based on poly checkbox.
        """
        self.combine_chkbox.setVisible(self.poly_chkbox.isChecked())

    def uncheck_mesh(self):
        """
        Clears poly-related checkboxes when surface checkbox is clicked.
        """
        self.poly_chkbox.setCheckState(QtCore.Qt.Unchecked)
        self.combine_chkbox.setCheckState(QtCore.Qt.Unchecked)
        self.update_combine_widget()

    def uncheck_surface(self):
        """
        Clears surface-related checkboxes when poly checkbox is clicked.
        """
        self.surface_chkbox.setCheckState(QtCore.Qt.Unchecked)
        self.combine_chkbox.setCheckState(QtCore.Qt.Unchecked)
        self.update_combine_widget()

    def surface_attach_system(self):
        """
        Triggers the surface attach operation based on selected geometry.
        """
        if self.cruve_btn.isChecked():
            self.surface_attach_with_ctrl()
        if self.mesh_btn.isChecked():
            self.maya_ops.surface_attach_with_poly()
        if self.ctrl_mesh_btn.isChecked():
            self.surface_with_ctrl_mesh()

    def surface_attach_with_ctrl(self):
        """
        Surface attach using created poly planes per object. Supports combining surfaces.
        """
        selected_grp = self.maya_ops.get_selected_objects()
        combine_plane = []
        for selected in selected_grp:
            if self.poly_chkbox.isChecked():
                planes = self.maya_ops.create_poly_plane()
                local_constrain = self.maya_ops.parent_constrain(selected, planes)
                self.maya_ops.select_objects(local_constrain)
                self.maya_ops.delete_selected()
                if not self.combine_chkbox.isChecked():
                    self.maya_ops.select_objects("{0}.f[0]".format(planes[0]))
                    self.maya_ops.create_surface_attach()
                    surface_attach = self.maya_ops.get_selected_objects()[0]
                    self.maya_ops.set_attribute("{}.size".format(surface_attach), .5)
                    self.maya_ops.select_objects(selected)
                    self.maya_ops.create_grp()
                    self.maya_ops.rename_selected_object(f"{selected}_offset_grp")
                    grp = self.maya_ops.get_selected_objects()
                    self.maya_ops.parent_constrain(surface_attach, grp, mo=True)
                combine_plane.append(planes[0])
        if self.combine_chkbox.isChecked():
            combined_obj = self.maya_ops.combine_poly(combine_plane)[0]
            self.maya_ops.delete_history()
            for n in range(0, len(selected_grp)):
                self.maya_ops.select_objects("{0}.f[{1}]".format(combined_obj, n))
                self.maya_ops.create_surface_attach()
                surface_attach = self.maya_ops.get_selected_objects()[0]
                self.maya_ops.set_attribute("{}.size".format(surface_attach), .5)
                self.maya_ops.select_objects(selected_grp[n])
                self.maya_ops.create_grp()
                self.maya_ops.rename_selected_object(f"{selected_grp[n]}_offset_grp")
                grp = self.maya_ops.get_selected_objects()
                self.maya_ops.parent_constrain(surface_attach, grp, mo=True)

    def surface_with_ctrl_mesh(self):
        """
        Attaches control to the closest face of a mesh using surface attach.
        """
        selected_objects = self.maya_ops.get_selected_objects()
        face_count = self.maya_ops.get_face_count(selected_objects[-1])
        for comp in range(len(selected_objects) - 1):
            ctrl_pos = self.maya_ops.get_world_position(selected_objects[comp])
            min_dist = float("inf")
            closest_face = None
            for i in range(face_count):
                verts = self.maya_ops.get_vertex_from_face(f"{selected_objects[-1]}.f[{i}]")[0].split()
                vert_indices = [int(v) for v in verts[2:]]
                positions = [self.maya_ops.get_world_position(f"{selected_objects[-1]}.vtx[{idx}]")
                             for idx in vert_indices]
                avg_pos = [sum(coords) / len(coords) for coords in zip(*positions)]
                dist = math.dist(ctrl_pos, avg_pos)
                if dist < min_dist:
                    min_dist = dist
                    closest_face = i
            self.maya_ops.select_objects(f"{selected_objects[-1]}.f[{closest_face}]")
            self.maya_ops.create_surface_attach()
            surface_attach = self.maya_ops.get_selected_objects()[0]
            self.maya_ops.set_attribute("{}.size".format(surface_attach), .5)
            self.maya_ops.select_objects(selected_objects[comp])
            self.maya_ops.create_grp()
            self.maya_ops.rename_selected_object(f"{selected_objects[comp]}_offset_grp")
            grp = self.maya_ops.get_selected_objects()
            self.maya_ops.parent_constrain(surface_attach, grp, mo=True)

    def follicle_system(self):
        """
        Executes follicle attachment based on selected object and checkbox state.
        """
        if self.mesh_btn.isChecked():
            self.maya_ops.follicle_with_poly()
        if self.cruve_btn.isChecked():
            self.follicle_with_cruve()
        if self.ctrl_mesh_btn.isChecked():
            self.maya_ops.follicle_with_ctrl_mesh()

    def follicle_with_cruve(self):
        """
        Follicle setup using either individual or combined poly/nurbs planes for selected controls.
        """
        selected_grp = self.maya_ops.get_selected_objects()
        nurbs_obj = []
        follicle_obj = []
        for selected in selected_grp:
            nurbs_plane = None
            if self.surface_chkbox.isChecked():
                nurbs_plane = self.maya_ops.create_nurb_plane()
            if self.poly_chkbox.isChecked():
                nurbs_plane = self.maya_ops.create_poly_plane()
            if nurbs_plane:
                nurbs_obj.append(nurbs_plane[0])
                self.maya_ops.set_attribute("{}.width".format(nurbs_plane[1]), 0.1)
                self.maya_ops.delete_history()
                nurbs_shape = self.maya_ops.get_dag_objects(nurbs_plane)[0]
                localconstrain = self.maya_ops.parent_constrain(selected, nurbs_plane[0])
                self.maya_ops.select_objects(localconstrain)
                self.maya_ops.delete_selected()

            if not self.combine_chkbox.isChecked():
                follicle_shape = self.maya_ops.create_follicle_node()
                self.maya_ops.set_attribute("{}.parameterU".format(follicle_shape), 0.5)
                self.maya_ops.set_attribute("{}.parameterV".format(follicle_shape), 0.5)
                follicle_node = self.maya_ops.get_relatives(follicle_shape)[0]
                follicle_obj.append(follicle_node)
                localconstrain = self.maya_ops.parent_constrain(selected, follicle_node)
                self.maya_ops.select_objects(localconstrain)
                self.maya_ops.delete_selected()
                self.maya_ops.freeze_transform(follicle_node)
                self.maya_ops.create_connections(f"{nurbs_shape}.worldMatrix", f"{follicle_shape}.inputWorldMatrix")
                if self.surface_chkbox.isChecked():
                    self.maya_ops.create_connections(f"{nurbs_shape}.local", f"{follicle_shape}.inputSurface")
                if self.poly_chkbox.isChecked():
                    self.maya_ops.create_connections(f"{nurbs_shape}.outMesh", f"{follicle_shape}.inputMesh")
                self.maya_ops.create_connections(f"{follicle_shape}.outRotate", f"{follicle_node}.rotate")
                self.maya_ops.create_connections(f"{follicle_shape}.outTranslate", f"{follicle_node}.translate")
                self.maya_ops.select_objects(selected)
                self.maya_ops.create_grp()
                self.maya_ops.rename_selected_object(f"{selected}_offset_grp")
                grp = self.maya_ops.get_selected_objects()
                self.maya_ops.parent_constrain(follicle_node, grp, mo=True)

        if self.combine_chkbox.isChecked():
            combined_obj = self.maya_ops.combine_poly(nurbs_obj)[0]
            self.maya_ops.automatic_uv(combined_obj)
            self.maya_ops.delete_history()
            for n in range(len(nurbs_obj)):
                self.maya_ops.select_objects(f"{combined_obj}.f[{n}]")
                component = self.maya_ops.get_selected_objects()[0]
                uv_shell = self.maya_ops.component_to_UV(component)
                uv_coords = self.maya_ops.get_uv_coordinates(uv_shell)
                num_uvs = len(uv_coords) // 2
                avg_u = sum(uv_coords[i] for i in range(0, len(uv_coords), 2)) / num_uvs
                avg_v = sum(uv_coords[i + 1] for i in range(0, len(uv_coords), 2)) / num_uvs
                follicle_shape = self.maya_ops.create_follicle_node()
                follicle_node = self.maya_ops.get_relatives(follicle_shape)[0]
                follicle_obj.append(follicle_node)
                self.maya_ops.set_attribute(f"{follicle_shape}.parameterU", avg_u)
                self.maya_ops.set_attribute(f"{follicle_shape}.parameterV", avg_v)
                self.maya_ops.create_connections(f"{combined_obj}.worldMatrix", f"{follicle_shape}.inputWorldMatrix")
                self.maya_ops.create_connections(f"{combined_obj}.outMesh", f"{follicle_shape}.inputMesh")
                self.maya_ops.create_connections(f"{follicle_shape}.outRotate", f"{follicle_node}.rotate")
                self.maya_ops.create_connections(f"{follicle_shape}.outTranslate", f"{follicle_node}.translate")
                self.maya_ops.select_objects(selected_grp[n])
                self.maya_ops.create_grp()
                self.maya_ops.rename_selected_object(f"{selected_grp[n]}_offset_grp")
                grp = self.maya_ops.get_selected_objects()
                self.maya_ops.parent_constrain(follicle_node, grp, mo=True)
                self.maya_ops.freeze_transform(follicle_node)

        else:
            self.maya_ops.select_objects(nurbs_obj)
            self.maya_ops.create_grp()
            self.maya_ops.rename_selected_object("object_grp")
        self.maya_ops.select_objects(follicle_obj)
        self.maya_ops.create_grp()
        self.maya_ops.rename_selected_object("follicle_grp")



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    obj = RigMaster()
    obj.show()
    sys.exit(app.exec_())
else:
    rigmaster = RigMaster()
    rigmaster.show()
