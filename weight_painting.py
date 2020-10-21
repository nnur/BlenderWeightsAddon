import bpy
import bmesh
import os
import random

bl_info = {
    "name": "Set Weight of Selected Vertices",
    "blender": (2,82,0),
    "category": "Object",
}

addon_keymaps = []

class SetWeightTool(bpy.types.WorkSpaceTool):
    bl_space_type='VIEW_3D'
    bl_context_mode='EDIT_MESH'

    # The prefix of the idname should be your add-on name.
    bl_idname = "object.set_weight"
    bl_label = "Set Weight"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = (
        "Adjust weights of vertices within the currently selected vertex group"
    )
    bl_icon = "ops.generic.select_circle"
    bl_widget = None
    # bl_keymap = (
    #     ("mesh.looptools_circle", {"type": 'LEFTMOUSE', "value": 'PRESS'},
    # {"properties": [("custom_radius", False), ("radius", 1)]}),
    #     )

class Object_set_weight(bpy.types.Operator):
    bl_idname = "object.set_weight"
    bl_label = "Set Weight of Selected Vertices"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Adjust weights of vertices within the currently selected vertex group"
    input_weight = 0
    # input_weight: bpy.props.FloatProperty(
    #     name="Weight", 
    #     description="Sets the weight of the selected vertices within the current vertex group",
    #     default=0.5, 
    #     soft_min=0.0, 
    #     soft_max=1.0
    # )
    
    def set_selected_weight(self, input_weight, context):
        if(bpy.context.mode == 'EDIT_MESH'):
            bpy.ops.object.mode_set(mode='OBJECT')
            mesh = context.object.data
            active_vertex_group = context.object.vertex_groups.active
            selected_vertices = [vertex.index for vertex in mesh.vertices if vertex.select]
            distance = self.mouse_x - self.prev_mouse_x
            if abs(distance) > 5:
                mode = "ADD" if distance > 0 else "SUBTRACT"
                active_vertex_group.add(selected_vertices, 0.05, mode)
                self.prev_mouse_x = self.mouse_x
            bpy.ops.object.mode_set(mode='EDIT')


    def execute(self, context):
        self.set_selected_weight(self.input_weight, context)
        return {"FINISHED"}
    
    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':  # Apply
            self.mouse_x = event.mouse_x
            self.execute(context)
        elif event.type == 'LEFTMOUSE':  # Confirm
            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:  # Cancel
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        self.mouse_x = event.mouse_x
        self.prev_mouse_x = event.mouse_x
        self.execute(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'


def register():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    bpy.utils.register_class(Object_set_weight)
    bpy.utils.register_tool(SetWeightTool, after={"builtin.scale_cage"}, separator=True, group=False)
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(Object_set_weight.bl_idname, type='W', value='PRESS', ctrl=True)
        addon_keymaps.append((km, kmi))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    bpy.utils.unregister_class(Object_set_weight)
    bpy.utils.unregister_class(SetWeightTool)


register()
# bpy.ops.object.set_weight('INVOKE_DEFAULT')