from PySide2 import QtCore, QtWidgets
import math
import sys

from MayaDev.tools.rig_master.ui.rig_master_ui import Ui_MainWindow
from MayaDev.tools.rig_master.src.maya_operations import MayaOperations
from MayaDev.tools.rig_master.uvpin import UVPinSetup


class RigMaster(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(RigMaster, self).__init__()
        print("Start")
        self.setWindowTitle("Rig Master")
        self.setupUi(self)
        self.maya_ops = MayaOperations()
        self.update_ui()
        self.connections()

    def update_ui(self):
        self.setWindowTitle("Rig Master")
        self.setMaximumSize(240, 120)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        connection_type_list = ["Surface Attach", "Follicle", "UV Pin"]
        self.connection_combobox.addItems(connection_type_list)
        self.update_attach_options()
        self.create_btn.setEnabled(False)

    def connections(self):
        self.connection_combobox.currentTextChanged.connect(self.update_attach_options)
        self.create_btn.clicked.connect(self.create_rig)
        self.poly_chkbox.clicked.connect(self.uncheck_surface)
        self.surface_chkbox.clicked.connect(self.uncheck_mesh)
        self.mesh_btn.clicked.connect(self.update_attach_widget)
        self.cruve_btn.clicked.connect(self.update_attach_widget)
        self.ctrl_mesh_btn.clicked.connect(self.update_attach_widget)

    def create_rig(self):
        self.maya_ops.open_undo_chunk()
        if self.connection_combobox.currentText() == "Follicle":
            self.follicle_system()
        if self.connection_combobox.currentText() == "Surface Attach":
            self.surface_attach_system()
        self.maya_ops.close_undo_chunk()

    def update_attach_options(self):
        self.combine_chkbox.setVisible(True)
        self.surface_chkbox.setVisible(True)
        self.combine_chkbox.setEnabled(True)
        self.surface_chkbox.setEnabled(True)
        self.poly_chkbox.setEnabled(True)
        self.mesh_btn.setEnabled(True)
        self.cruve_btn.setEnabled(True)
        self.ctrl_mesh_btn.setEnabled(True)
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
        if self.poly_chkbox.isChecked():
            self.combine_chkbox.setVisible(True)
        else:
            self.combine_chkbox.setVisible(False)

    def uncheck_mesh(self):
        self.poly_chkbox.setCheckState(QtCore.Qt.Unchecked)
        self.combine_chkbox.setCheckState(QtCore.Qt.Unchecked)
        self.update_combine_widget()

    def uncheck_surface(self):
        self.surface_chkbox.setCheckState(QtCore.Qt.Unchecked)
        self.combine_chkbox.setCheckState(QtCore.Qt.Unchecked)
        self.update_combine_widget()

    def surface_attach_system(self):
        if self.cruve_btn.isChecked():
            self.surface_attach_with_ctrl()
        if self.mesh_btn.isChecked():
            self.maya_ops.surface_attach_with_poly()
        if self.ctrl_mesh_btn.isChecked():
            self.surface_with_ctrl_mesh()

    def surface_attach_with_ctrl(self):
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
                    if self.checkBox.isChecked():
                        self.maya_ops.parent_constrain(surface_attach, grp, mo_flag=True)
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
                if self.checkBox.isChecked():
                    self.maya_ops.parent_constrain(surface_attach, grp, mo_flag=True)


    def surface_with_ctrl_mesh(self):
        face_list = []
        selected_objects = self.maya_ops.get_selected_objects()
        face_count = self.maya_ops.get_face_count(selected_objects[-1])
        for comp in range(len(selected_objects) - 1):
            ctrl_pos = self.maya_ops.get_world_position(selected_objects[comp])
            min_dist = float("inf")
            closest_face = None

            for i in range(face_count):
                verts = self.maya_ops.get_vertex_from_face(f"{selected_objects[-1]}.f[{i}]")[0].split()
                vert_indices = [int(v) for v in verts[2:]]
                positions = []
                for idx in vert_indices:
                    vtx_pos = self.maya_ops.get_world_position(f"{selected_objects[-1]}.vtx[{idx}]")
                    positions.append(vtx_pos)
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
            if self.checkBox.isChecked():
                self.maya_ops.parent_constrain(surface_attach, grp, mo_flag=True)


    def follicle_system(self):
        if self.mesh_btn.isChecked():
            self.maya_ops.follicle_with_poly()
        if self.cruve_btn.isChecked():
            self.follicle_with_cruve()
        if self.ctrl_mesh_btn.isChecked():
            self.maya_ops.follicle_with_ctrl_mesh()


    def follicle_with_cruve(self):
        selected_grp = self.maya_ops.get_selected_objects()
        nurbs_obj = []
        follicle_obj = []
        count = 0
        for selected in selected_grp:
            count = count + 1
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
                print("follicle_shape", follicle_shape)
                follicle_node = self.maya_ops.get_relatives(follicle_shape, ap_flag=True)[0]
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
                self.maya_ops.create_connections("{}.outRotate".format(follicle_shape),
                                                 "{}.rotate".format(follicle_node))
                self.maya_ops.create_connections("{}.outTranslate".format(follicle_shape),
                                                 "{}.translate".format(follicle_node))

                self.maya_ops.select_objects(selected)
                self.maya_ops.create_grp()
                self.maya_ops.rename_selected_object(f"{selected}_offset_grp")
                grp = self.maya_ops.get_selected_objects()
                print("Yes")
                if self.checkBox.isChecked():
                    self.maya_ops.parent_constrain(follicle_node, grp, mo_flag=True)
                print("No")

        if self.combine_chkbox.isChecked():
            coombined_obj = self.maya_ops.combine_poly(nurbs_obj)[0]
            self.maya_ops.automatic_uv(coombined_obj)
            self.maya_ops.delete_history()
            for n in range(0, len(nurbs_obj)):
                self.maya_ops.select_objects("{0}.f[{1}]".format(coombined_obj, n))
                component = self.maya_ops.get_selected_objects()[0]
                uv_shell = self.maya_ops.component_to_UV(component)
                uv_coords = self.maya_ops.get_uv_coordinates(uv_shell)
                num_uvs = len(uv_coords) // 2
                avg_u = sum(uv_coords[i] for i in range(0, len(uv_coords), 2)) / num_uvs
                avg_v = sum(uv_coords[i + 1] for i in range(0, len(uv_coords), 2)) / num_uvs
                follicle_shape = self.maya_ops.create_follicle_node()
                follicle_node = self.maya_ops.get_relatives(follicle_shape)[0]
                follicle_obj.append(follicle_node)
                self.maya_ops.set_attribute("{}.parameterU".format(follicle_shape), avg_u)
                self.maya_ops.set_attribute("{}.parameterV".format(follicle_shape), avg_v)

                self.maya_ops.create_connections(f"{coombined_obj}.worldMatrix", f"{follicle_shape}.inputWorldMatrix")
                self.maya_ops.create_connections(f"{coombined_obj}.outMesh", f"{follicle_shape}.inputMesh")

                self.maya_ops.create_connections("{}.outRotate".format(follicle_shape),
                                                 "{}.rotate".format(follicle_node))
                self.maya_ops.create_connections("{}.outTranslate".format(follicle_shape),
                                                 "{}.translate".format(follicle_node))
                self.maya_ops.select_objects(selected_grp[n])
                self.maya_ops.create_grp()
                self.maya_ops.rename_selected_object(f"{selected_grp[n]}_offset_grp")
                grp = self.maya_ops.get_selected_objects()
                if self.checkBox.isChecked():
                    self.maya_ops.parent_constrain(follicle_node, grp, mo_flag=True)
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

