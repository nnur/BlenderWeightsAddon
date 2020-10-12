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

class VIEW3D_PT_set_weights(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_set_weights"
    bl_label = "Adjust Weights"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
 
    def draw(self, context):
        self.layout.operator("object.set_weight", icon='COLORSET_02_VEC', text="Adjust Weights Relatively")

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

def menu_draw(self, context):
    self.layout.operator(Object_set_weight.bl_idname)

def register():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    bpy.utils.register_class(Object_set_weight)
    # bpy.utils.register_class(VIEW3D_PT_set_weights)
    bpy.types.WM_MT_toolsystem.append(menu_draw)
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(Object_set_weight.bl_idname, type='W', value='PRESS', ctrl=True)
        addon_keymaps.append((km, kmi))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    bpy.utils.unregister_class(Object_set_weight)
    bpy.types.WM_MT_toolsystem_submenu.remove(menu_draw)

    # bpy.utils.unregister_class(VIEW3D_PT_set_weights)

register()
bpy.ops.object.set_weight('INVOKE_DEFAULT')