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

class ObjectAdjustWeight(bpy.types.Operator):
    bl_idname = "object.adjust_weight"
    bl_label = "Adjust Weight of Selected Vertices"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Adjust weights of vertices within the currently selected vertex group"
    
    def adjust_selected_weight(self, context):
        if(bpy.context.mode == 'EDIT_MESH'):
            bpy.ops.object.mode_set(mode='OBJECT')
            distance = ((self.mouse_x - self.prev_mouse_x) ** 2 + (self.mouse_y - self.prev_mouse_y) ** 2) ** 0.5
            direction = self.mouse_x - self.prev_mouse_x + self.mouse_y - self.prev_mouse_y
            if abs(distance) > 5:
                mode = "ADD" if direction > 0 else "SUBTRACT"
                self.active_vertex_group.add(list(self.selected_vertices.keys()), 0.05, mode)
            self.prev_mouse_x = self.mouse_x
            self.prev_mouse_y = self.mouse_y
            bpy.ops.object.mode_set(mode='EDIT')

    def execute(self, context):
        self.make_selected_vertices(context)
        self.adjust_selected_weight(context)
        return {"FINISHED"}
    
    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':  # Apply
            self.mouse_x = event.mouse_x
            self.mouse_y = event.mouse_y
            self.execute(context)
        elif event.type == 'LEFTMOUSE':  # Confirm
            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:  # Cancel
            bpy.ops.object.mode_set(mode='OBJECT')
            for index, weight in self.og_vertices.items():
                self.active_vertex_group.add([index], weight, "REPLACE")
            bpy.ops.object.mode_set(mode='EDIT')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        self.prev_mouse_x = event.mouse_x
        self.prev_mouse_y = event.mouse_y
        self.og_vertices = {}
        self.execute(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def make_selected_vertices(self, context):
        mesh = context.object.data
        self.active_vertex_group = context.object.vertex_groups.active
        self.selected_vertices = {}
        not_in_group = True
        for vertex in mesh.vertices:
            if vertex.select:
                for group in vertex.groups:
                    if group.group == self.active_vertex_group.index:
                        self.selected_vertices[vertex.index] = group.weight
                        if vertex.index not in self.og_vertices:
                            self.og_vertices[vertex.index] = group.weight
                        not_in_group = False
                        break
                if not_in_group:
                    self.selected_vertices[vertex.index] = 0
                    if vertex.index not in self.og_vertices:
                        self.og_vertices[vertex.index] = 0
                not_in_group = True
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'


class AdjustWeightTool(bpy.types.WorkSpaceTool):
    bl_space_type='VIEW_3D'
    bl_context_mode='EDIT_MESH'

    bl_idname = ObjectAdjustWeight.bl_idname
    bl_label = "Adjust Weight"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = (
        "Adjust weights of vertices within the currently selected vertex group"
    )
    bl_icon = "ops.paint.weight_gradient"
    bl_widget = "VIEW3D_GGT_tool_generic_handle_normal"
    bl_keymap = (
        (ObjectAdjustWeight.bl_idname, {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": []}),
    )
    def draw_settings(context, layout, tool):
        props = tool.operator_properties(ObjectAdjustWeight.bl_idname)


# class DB():
#     is_changed = False

#     @classmethod

def changed(self, context):
    self.is_changed = True

class ObjectSetWeight(bpy.types.Operator):

    bl_idname = "ob.set_weight"
    bl_label = "Set Weight of Selected Vertices"
    bl_options = {"REGISTER", "UNDO"}
    is_changed = bpy.props.BoolProperty(options={'HIDDEN'})
    input_weight = bpy.props.FloatProperty(
            name="Weight",
            soft_min=0.0,
            soft_max=1.0,
            update=changed
        )
    
    def execute(self, context):
        if(bpy.context.mode == 'EDIT_MESH') and self.is_changed:
            bpy.ops.object.mode_set(mode='OBJECT')
            mesh = context.object.data
            active_vertex_group = context.object.vertex_groups.active
            selected_vertices = [v.index for v in mesh.vertices if v.select]
            active_vertex_group.add(selected_vertices, self.input_weight, "REPLACE")
            self.last_weight = self.input_weight
            self.is_changed = False
            bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}

    # def invoke(self, context, event):
    #     return self.execute(context)
        # wm = context.window_manager
        # return wm.invoke_props_popup(self, event)

    # @classmethod
    # def changed(cls, context):
    #     cls.is_changed = True


class SetWeightTool(bpy.types.WorkSpaceTool):
    bl_space_type='VIEW_3D'
    bl_context_mode='EDIT_MESH'

    bl_idname = ObjectSetWeight.bl_idname
    bl_label = "Set Weight"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = (
        "Set weights of vertices within the currently selected vertex group"
    )
    bl_icon = "ops.paint.weight_sample"
    bl_keymap = (
        (ObjectSetWeight.bl_idname, {"type": 'W', "value": 'PRESS'},
         {"properties": []}),
    )
    def draw_settings(context, layout, tool):
        props = tool.operator_properties(ObjectSetWeight.bl_idname)




def register():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    bpy.utils.register_class(ObjectAdjustWeight)
    bpy.utils.register_class(ObjectSetWeight)
    bpy.utils.register_tool(AdjustWeightTool, after={"builtin.measure"}, separator=True, group=True)
    bpy.utils.register_tool(SetWeightTool, after={AdjustWeightTool.bl_idname})

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    bpy.utils.unregister_class(ObjectAdjustWeight)
    bpy.utils.unregister_class(ObjectSetWeight)
    bpy.utils.unregister_class(AdjustWeightTool)
    bpy.utils.unregister_class(SetWeightTool)


register()