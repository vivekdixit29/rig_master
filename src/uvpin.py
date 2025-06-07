from MayaDev.tools.rig_master.ui.uvPin_ui import Ui_UVPinUi
from MayaDev.tools.rig_master.src.maya_operations import MayaOperations
from PySide2 import QtWidgets, QtCore


class UVPinSetup(QtWidgets.QMainWindow, Ui_UVPinUi):
    def __init__(self):
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
        """Connects UI components to their corresponding slot methods."""
        self.uvpin_chkbox.stateChanged.connect(self.get_uvpin)
        self.skin_cluster_chkbox.stateChanged.connect(self.get_skin_cluster)
        self.create_btn.clicked.connect(self.create_uvpin_setup)
        self.add_btn.clicked.connect(self.get_selected_points)
        self.remove_btn.clicked.connect(self.clear_points_selection)

    def clear_points_selection(self):
        """Clears the current selection of vertices in the listbox."""
        self.selected_vertex_listbox.clear()

    def create_uvpin_setup(self):
        """Gathers user selections and creates the UV pin and/or skin cluster setup
        by calling the `create_bones` method with the appropriate parameters."""
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
        """Retrieves selected vertex components from Maya and adds them to the listbox."""
        selection = self.maya_ops.get_selected_component(flatten_flag=True)
        self.selected_vertex_listbox.addItems(selection)
        self.create_btn_enable()

    def create_btn_enable(self):
        """Enables or disables the 'Create' button based on valid selections."""
        self.create_btn.setEnabled(False)
        if self.selected_vertex_listbox.count() and self.master_cluster_listbox.count():
            self.create_btn.setEnabled(True)

    def get_uvpin(self):
        """Toggles visibility and populates the UV pin list based on checkbox state."""
        if self.uvpin_chkbox.checkState():
            all_uv_pin = self.maya_ops.get_object_based_on_type("uvPin")
            self.uvpin_listbox.setVisible(True)
            self.uvpin_listbox.addItems(all_uv_pin)
        else:
            self.uvpin_listbox.clear()
            self.uvpin_listbox.setVisible(False)

    def get_skin_cluster(self):
        """Toggles visibility and populates the skin cluster list based on checkbox state."""
        if self.skin_cluster_chkbox.checkState():
            all_skin_cluster = self.maya_ops.get_object_based_on_type("skinCluster")
            self.skincluster_listbox.setVisible(True)
            self.skincluster_listbox.addItems(all_skin_cluster)
        else:
            self.skincluster_listbox.clear()
            self.skincluster_listbox.setVisible(False)

    def add_master_cluster(self):
        """Retrieves and lists all skinClusters in the scene for use as master clusters."""
        self.master_cluster_listbox.clear()
        cluster = self.maya_ops.get_object_based_on_type("skinCluster")
        self.master_cluster_listbox.addItems(cluster)

    def create_bones(self, master_cluster, selected_vertices, uv_pin=None, sel_cluster=None):
        """
        Creates joints, control groups, UV pins, and skin cluster bindings based on user selections.
        :param str master_cluster: The name of the primary skinCluster for connection setup.
        :param list selected_vertices: List of vertex component strings.
        :param str uv_pin: The name of the UV pin node to connect. Defaults to None.
        :param str sel_cluster: An alternate skinCluster name for binding. Defaults to None.
        """
        self.maya_ops.open_undo_chunk()
        cluster_name = None
        if not sel_cluster == master_cluster:
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
            loc_shape, uv_pin = self.maya_ops.create_uv_pin_setup(shape_node, sel, sel_uv_pin=uv_pin)

            self.maya_ops.parent_constrain(loc_shape, grp_name)
            if cluster_name:
                self.maya_ops.setup_skincluster(cluster_name, bone_jt=bone_jt)
            else:
                cluster_name = self.maya_ops.setup_skincluster(
                    joint_list=joint_list,
                    mesh_name=selected_vertices[0].split(".")[0]
                )
            self.maya_ops.create_connection_with_bones(master_cluster, cluster_name, uv_pin, grp_name, bone_jt)
        self.maya_ops.close_undo_chunk()
