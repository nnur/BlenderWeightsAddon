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
            distance = ((self.mouse_x - self.prev_mouse_x) ** 2 + (self.mouse_y - self.prev_mouse_y) ** 2) ** 0.5
            direction = self.mouse_x - self.prev_mouse_x + self.mouse_y - self.prev_mouse_y
            if abs(distance) > 10:
                mode = "ADD" if direction > 0 else "SUBTRACT"
                self.active_vertex_group.add(list(self.selected_vertices.keys()), 0.05, mode)
                self.prev_mouse_x = self.mouse_x
                self.prev_mouse_y = self.mouse_y
            bpy.ops.object.mode_set(mode='EDIT')

    def execute(self, context):
        self.set_selected_weight(self.input_weight, context)
        return {"FINISHED"}
    
    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':  # Apply
            self.mouse_x = event.mouse_x
            self.mouse_y = event.mouse_y
            self.execute(context)
        elif event.type == 'LEFTMOUSE':  # Confirm
            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:  # Cancel
            for index, weight in self.og_vertices:
                self.active_vertex_group.add([index], weight, "REPLACE")
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        self.prev_mouse_x = event.mouse_x
        self.prev_mouse_y = event.mouse_y

        mesh = context.object.data
        self.active_vertex_group = context.object.vertex_groups.active
        self.selected_vertices = {}
        self.og_vertices = {}
        for vertex in mesh.vertices:
            if vertex.select:
                for group in vertex.groups:
                    if group.group == self.active_vertex_group.index:
                        self.selected_vertices[vertex.index] = group.weight
                        self.og_vertices[vertex.index] = group.weight
                        break

        self.execute(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

class SetWeightTool(bpy.types.WorkSpaceTool):
    bl_space_type='VIEW_3D'
    bl_context_mode='EDIT_MESH'

    # The prefix of the idname should be your add-on name.
    bl_idname = "object.set_weight"
    bl_label = "Adjust Weight"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = (
        "Adjust weights of vertices within the currently selected vertex group"
    )
    bl_icon = "ops.paint.weight_gradient"
    bl_widget = "VIEW3D_GGT_tool_generic_handle_normal"
    bl_keymap = (
        (Object_set_weight.bl_idname, {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": []}),
    )
    def draw_settings(context, layout, tool):
        props = tool.operator_properties("object.set_weight")
        # layout.prop(props, "mode")

def register():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    bpy.utils.register_class(Object_set_weight)
    bpy.utils.register_tool(SetWeightTool, after={"builtin.rip_region"}, separator=True, group=True)

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    bpy.utils.unregister_class(Object_set_weight)
    bpy.utils.unregister_class(SetWeightTool)


register()
# bpy.ops.object.set_weight('INVOKE_DEFAULT')