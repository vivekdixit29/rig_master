"""
This module provides a class `MayaOperations` that encapsulates common Maya commands
for simplifying scene manipulation tasks using Maya's `cmds` and `mel` modules.
It includes methods for handling selections, creating and manipulating geometry,
connecting nodes, creating follicles, and other utility operations used in a rigging or TD pipeline.

Usage:
    ops = MayaOperations()
    ops.create_poly_plane()
    ops.surface_attach_with_poly()
    ops.follicle_with_ctrl_mesh()
"""

from maya import cmds, mel


class MayaOperations:
    """Encapsulates common Maya operations using cmds and MEL."""

    def open_undo_chunk(self):
        """Opens an undo chunk to group multiple operations into a single undo step."""
        cmds.undoInfo(openChunk=True)

    def close_undo_chunk(self):
        """Closes the undo chunk previously opened."""
        cmds.undoInfo(closeChunk=True)

    def surface_attach_with_poly(self):
        """
        Attaches selected polygon components to a surface using cMuscleSurfAttachSetup.
        Also sets appropriate attributes based on the type of component.
        """
        selected_component = cmds.ls(selection=True, flatten=True)
        if selected_component:
            for component in selected_component:
                cmds.select(component)
                mel.eval("cMuscleSurfAttachSetup")
                surface_attach = cmds.ls(selection=True)[0]
                cmds.setAttr("{}.size".format(surface_attach), .1)
                if component.split(".")[1].startswith("e["):
                    cmds.setAttr("{}.vLoc".format(surface_attach), 0)
                    cmds.setAttr("{}.uLoc".format(surface_attach), 0)

    def get_selected_objects(self):
        """Returns the currently selected objects in the scene."""
        selected_grp = cmds.ls(selection=True)
        return selected_grp

    def create_poly_plane(self):
        """Creates a small polygon plane and returns it."""
        planes = cmds.polyPlane(n="plane_msh", width=0.05, height=0.05, axis=[0, 1, 0],
                                subdivisionsX=1,
                                subdivisionsY=1)
        return planes

    def parent_constrain(self, parent, child, mo=False):
        """
        Applies a parent constraint between the parent and child.

        Args:
            parent (str): Name of the parent object.
            child (str): Name of the child object.
            mo (bool): Maintain offset flag.

        Returns:
            list: The created constraint node(s).
        """
        local_constrain = cmds.parentConstraint(parent, child, mo=mo)
        return local_constrain

    def select_objects(self, objects):
        """Selects the given list of objects."""
        cmds.select(objects)

    def delete_selected(self):
        """Deletes currently selected objects."""
        mel.eval("doDelete")

    def create_surface_attach(self):
        """Creates a surface attachment using cMuscleSurfAttachSetup."""
        mel.eval("cMuscleSurfAttachSetup")

    def set_attribute(self, attribute, value):
        """
        Sets the value of a given attribute.

        Args:
            attribute (str): Full attribute path.
            value: Value to set.
        """
        cmds.setAttr(attribute, value)

    def create_grp(self):
        """Creates a new group from the selected objects."""
        mel.eval("doGroup 0 1 1")

    def rename_selected_object(self, name):
        """Renames the selected object to the given name."""
        cmds.rename(name)

    def combine_poly(self, combine_objects):
        """
        Combines the given polygon objects into a single mesh.

        Args:
            combine_objects (list): List of objects to combine.

        Returns:
            list: The newly created combined mesh.
        """
        combined_obj = cmds.polyUnite(combine_objects, ch=True, mergeUVSets=True, centerPivot=True,
                                      name="combine_msh")
        return combined_obj

    def delete_history(self):
        """Deletes construction history on selected objects."""
        cmds.delete(ch=True)

    def get_face_count(self, object):
        """
        Returns the number of faces on the given object.

        Args:
            object (str): Name of the mesh object.
        """
        face_count = cmds.polyEvaluate(object, face=True)
        return face_count

    def get_world_position(self, object):
        """Returns the world position of the given object."""
        return cmds.xform(object, q=True, ws=True, t=True)

    def get_vertex_from_face(self, face_name):
        """Returns the vertices belonging to the specified face."""
        return cmds.polyInfo(face_name, faceToVertex=True)

    def follicle_with_poly(self):
        """
        Creates follicles based on selected polygon components and groups them under 'follicle_grp'.
        """
        follicle_obj = []
        selected_component = cmds.ls(selection=True, flatten=True)
        if selected_component:
            obj_name = selected_component[0].split(".")[0]
            shape_node = cmds.listRelatives(obj_name, shapes=True)
            shape_type = cmds.objectType(shape_node[0])
            for component in selected_component:
                if not shape_type == "nurbsSurface":
                    uv_shell = cmds.polyListComponentConversion(component, toUV=True)
                    uv_coords = cmds.polyEditUV(uv_shell, query=True)
                    num_uvs = len(uv_coords) // 2
                    avg_u = sum(uv_coords[i] for i in range(0, len(uv_coords), 2)) / num_uvs
                    avg_v = sum(uv_coords[i + 1] for i in range(0, len(uv_coords), 2)) / num_uvs
                follicle_shape = cmds.createNode("follicle", n="follicle")
                if not shape_type == "nurbsSurface":
                    self.set_attribute("{}.parameterU".format(follicle_shape), avg_u)
                    self.set_attribute("{}.parameterV".format(follicle_shape), avg_v)
                else:
                    self.set_attribute("{}.parameterU".format(follicle_shape), .5)
                    self.set_attribute("{}.parameterV".format(follicle_shape), .5)
                follicle_node = cmds.listRelatives(follicle_shape, ap=True)[0]
                follicle_obj.append(follicle_node)
                cmds.makeIdentity(follicle_node, apply=True, translate=True, rotate=True, scale=True)
                cmds.connectAttr(f"{obj_name}.worldMatrix", f"{follicle_shape}.inputWorldMatrix", force=True)
                try:
                    cmds.connectAttr(f"{obj_name}.outMesh", f"{follicle_shape}.inputMesh", force=True)
                except:
                    cmds.connectAttr(f"{obj_name}.local", f"{follicle_shape}.inputSurface", force=True)

                cmds.connectAttr("{}.outRotate".format(follicle_shape), "{}.rotate".format(follicle_node), force=True)
                cmds.connectAttr("{}.outTranslate".format(follicle_shape), "{}.translate".format(follicle_node), force=True)

            self.select_objects(follicle_obj)
            self.create_grp()
            self.rename_selected_object("follicle_grp")
        else:
            print("Please select a proper object")

    def create_nurb_plane(self):
        """Creates a NURBS plane."""
        nurbs_plane = cmds.nurbsPlane(ax=[0, 1, 0])
        return nurbs_plane

    def get_dag_objects(self, object):
        """Returns DAG hierarchy of the given object."""
        return cmds.ls(object, dag=True)

    def create_follicle_node(self):
        """Creates a follicle shape node."""
        follicle_shape = cmds.createNode("follicle", n="follicle")
        return follicle_shape

    def get_relatives(self, object):
        """Returns the list of all parent nodes for a given object."""
        list_relatives = cmds.listRelatives(object, ap=True)
        return list_relatives

    def freeze_transform(self, object):
        """Freezes transformations (translate, rotate, scale) of the given object."""
        cmds.makeIdentity(object, apply=True, translate=True, rotate=True, scale=True)

    def create_connections(self, source, destination):
        """Connects an attribute from source to destination."""
        cmds.connectAttr(source, destination, force=True)

    def automatic_uv(self, object):
        """Applies automatic UV mapping to the given object."""
        cmds.polyAutoProjection(object)

    def component_to_UV(self, component):
        """Converts a polygon component to its corresponding UV shell."""
        uv_shell = cmds.polyListComponentConversion(component, toUV=True)
        return uv_shell

    def get_uv_coordinates(self, uv_shell):
        """Returns UV coordinates for the given UV shell."""
        values = cmds.polyEditUV(uv_shell, query=True)
        return values

    def follicle_with_ctrl_mesh(self):
        """
        Attaches selected objects to a mesh or surface using follicles.
        The last selected object is assumed to be the driver mesh/surface.
        Creates offset groups for the attached objects.
        """
        cpm = None
        selected_objects = self.get_selected_objects()
        shape_node = cmds.listRelatives(selected_objects[-1], shapes=True)
        shape_type = cmds.objectType(shape_node[0])
        if shape_type == "nurbsSurface" or shape_type == "mesh":
            for obj in range(len(selected_objects) - 1):
                follicle_shape = cmds.createNode("follicle", n="follicle")
                follicle_node = self.get_relatives(follicle_shape)[0]
                localconstrain = self.parent_constrain(selected_objects[obj], follicle_node)
                self.select_objects(localconstrain)
                self.delete_selected()

                cmds.makeIdentity(follicle_node, apply=True, translate=True, rotate=True, scale=True)

                ctrl_pos = cmds.xform(selected_objects[obj], q=True, ws=True, t=True)
                cmds.connectAttr(f"{shape_node[0]}.worldMatrix", f"{follicle_shape}.inputWorldMatrix", force=True)
                if shape_type == "nurbsSurface":
                    cmds.connectAttr(f"{selected_objects[-1]}.local", f"{follicle_shape}.inputSurface", force=True)
                    cpm = cmds.createNode("closestPointOnSurface", n="closestPointOnSurface")
                    cmds.connectAttr(f"{selected_objects[-1]}.worldSpace", f"{cpm}.inputSurface", force=True)
                    cmds.setAttr(f"{cpm}.inPosition", *ctrl_pos)

                if shape_type == "mesh":
                    cmds.connectAttr(f"{shape_node[0]}.worldMesh", f"{follicle_shape}.inputMesh", force=True)
                    cpm = cmds.createNode("closestPointOnMesh", n="closetPointOnMesh")
                    cmds.connectAttr(f"{selected_objects[-1]}.outMesh", f"{cpm}.inMesh", force=True)
                    cmds.connectAttr(f"{selected_objects[-1]}.worldMatrix", f"{cpm}.inputMatrix", force=True)
                    cmds.setAttr(f"{cpm}.inPosition", *ctrl_pos)

                if cpm:
                    u = cmds.getAttr(f"{cpm}.result.u")
                    v = cmds.getAttr(f"{cpm}.result.v")
                    self.set_attribute("{}.parameterU".format(follicle_shape), u)
                    self.set_attribute("{}.parameterV".format(follicle_shape), v)
                    self.select_objects(cpm)
                    self.delete_selected()

                cmds.connectAttr("{}.outRotate".format(follicle_shape), "{}.rotate".format(follicle_node),
                                force=True)
                cmds.connectAttr("{}.outTranslate".format(follicle_shape), "{}.translate".format(follicle_node),
                              force=True)
                self.select_objects(selected_objects[obj])
                self.create_grp()
                self.rename_selected_object(f"{selected_objects[obj]}_offset_grp")
                grp = self.get_selected_objects()
                self.parent_constrain(follicle_node, grp, mo=True)


    @staticmethod
    def get_object_based_on_type(type_flag):
        """
        Returns a list of objects in the scene based on the given type.

        Args:
            type_flag (str): The type of object to search for (e.g., "mesh", "nurbsCurve", "joint").

        Returns:
            list: A list of object names matching the given type.
        """
        return cmds.ls(type=type_flag)
    
    def create_uv_pin_setup(self, shape_node, sel, sel_uv_pin=None):
        """
        Creates a UV pin setup in Maya by associating a locator with UV coordinates on a mesh.

        Args:
            shape_node (str): The name of the shape node (mesh) to attach the UV pin.
            sel (list): A list of selected vertices to convert into UV space.
            sel_uv_pin (str, optional): An existing UV pin node to use. If None, a new one is created.

        Returns:
            tuple:
                - str: The name of the locator created and positioned using UV pin.
                - str: The UV pin node used or created.
        """
        uv = cmds.polyListComponentConversion(sel, fromVertex=True, toUV=True)
        uv = cmds.filterExpand(uv, selectionMask=35)
        u_coords, v_coords = cmds.polyEditUV(uv[0], query=True)
        if sel_uv_pin:
            uvpin = sel_uv_pin
        else:
            uvpin = cmds.createNode("uvPin", name="uv_Test")
        loc_shape = cmds.spaceLocator(name="uvPin_loc")[0]

        indices = cmds.getAttr(f"{uvpin}.outputMatrix", multiIndices=True)
        if indices:
            cmds.setAttr(f"{uvpin}.coordinate[{len(indices)}].coordinateU", u_coords)
            cmds.setAttr(f"{uvpin}.coordinate[{len(indices)}].coordinateV", v_coords)
            cmds.connectAttr(f"{uvpin}.outputMatrix[{len(indices)}]", f"{loc_shape}.offsetParentMatrix", force=True)
        else:
            cmds.setAttr(f"{uvpin}.coordinate[0].coordinateU", u_coords)
            cmds.setAttr(f"{uvpin}.coordinate[0].coordinateV", v_coords)
            cmds.connectAttr(f"{uvpin}.outputMatrix[0]", f"{loc_shape}.offsetParentMatrix", force=True)

        if not cmds.isConnected(f"{shape_node}.worldMesh[0]", f"{uvpin}.deformedGeometry"):
            cmds.connectAttr(f"{shape_node}.worldMesh[0]", f"{uvpin}.deformedGeometry", force=True)

        cmds.setAttr(f"{loc_shape}.translate", 0, 0, 0, type="double3")
        cmds.setAttr(f"{loc_shape}.rotate", 0, 0, 0, type="double3")

        return loc_shape, uvpin

    def create_connection_with_bones(self, master_cluster, current_cluster, uv_pin, ctrl_grp, bone):
        """
        Connects UV pin geometry to a cluster's output geometry and links a control group 
        to influence a skinCluster using the given bone.

        Args:
            master_cluster (str): The cluster whose output geometry connects to the UV pin.
            current_cluster (str): The cluster influenced by the skinCluster.
            uv_pin (str): The UV pin node to be connected.
            ctrl_grp (str): The control group whose inverse matrix will bind the skin.
            bone (str): The bone joint that should influence the current cluster.
        """
        cmds.connectAttr(f"{master_cluster}.outputGeometry[0]", f"{uv_pin}.deformedGeometry", force=True)
        influences = cmds.skinCluster(current_cluster, query=True, influence=True)
        if bone in influences:
            index = influences.index(bone)
            cmds.connectAttr(f"{ctrl_grp}.inverseMatrix", f"{current_cluster}.bindPreMatrix[{index}]", force=True)

    def create_ctrl_setup(self, joint_name):
        """
        Creates a control curve, groups it twice, aligns it to a joint, and constrains 
        the joint to follow the control.

        Args:
            joint_name (str): The name of the joint to be controlled.

        Returns:
            str: The name of the top-level group containing the control curve.
        """
        curv_cmd = "curve -d 1 -p 1 1 -1 -p 1 -1 -1 -p -1 -1 -1 -p -1 1 -1 -p 1 1 -1 -p 1 1 1 -p -1 1 1 -p -1 1 -1 -p -1 -1 -1 -p -1 -1 1 -p -1 1 1 -p -1 -1 1 -p 1 -1 1 -p 1 1 1 -p 1 -1 1 -p 1 -1 -1 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15"
        mel.eval(curv_cmd)
        crv_name = self.get_selected_component()[0]
        self.set_attribute(f"{crv_name}.scaleX", 0.1)
        self.set_attribute(f"{crv_name}.scaleY", 0.1)
        self.set_attribute(f"{crv_name}.scaleZ", 0.1)
        cmds.select(crv_name)
        self.freeze_trnasfrom()

        mel.eval("doGroup 0 1 1")
        mel.eval("doGroup 0 1 1")
        grp_name = self.get_selected_component()
        coonstraint_name = self.parent_constrain(joint_name, grp_name)
        cmds.delete(coonstraint_name)
        self.parent_constrain(crv_name, joint_name)
        return grp_name[0]

    def freeze_trnasfrom(self):
        """
        Freezes the transformations (translate, rotate, scale) on the currently selected object in Maya.
        """
        cmds.makeIdentity(apply=True)

