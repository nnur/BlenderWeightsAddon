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

def register():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    bpy.utils.register_class(Object_set_weight)
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(Object_set_weight.bl_idname, type='W', value='PRESS', shift=True, alt=True)
        addon_keymaps.append((km, kmi))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
        
        
    bpy.utils.unregister_class(Object_set_weight)


class Object_set_weight(bpy.types.Operator):
    bl_idname = "object.set_weight"
    bl_label = "Set Weight of Selected Vertices"
    bl_options = {"REGISTER", "UNDO"}
    input_weight: bpy.props.FloatProperty(
        name="Weight", 
        description="Sets the weight of the selected vertices within the current vertex group",
        default=random.random(), 
        soft_min=0.0, 
        soft_max=1.0
    )
    
    def set_selected_weight(self, input_weight, context):
        if(bpy.context.mode == 'EDIT_MESH'):
            bpy.ops.object.mode_set(mode='OBJECT')
            mesh = context.object.data
            active_vertex_group = context.object.vertex_groups.active
            selected_vertices = [vertex.index for vertex in mesh.vertices if vertex.select]

            
            active_vertex_group.add(selected_vertices, input_weight, "REPLACE")
            bpy.ops.object.mode_set(mode='EDIT')


    def execute(self, context):
        self.set_selected_weight(self.input_weight, context)
        return {"FINISHED"}
    
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH' and context.area.type == 'VIEW_3D'

#if __name__ == "main":
register()