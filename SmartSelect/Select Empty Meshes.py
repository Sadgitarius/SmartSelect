from .__hh__ import *

if bpy.context.mode == 'OBJECT':
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH') 
    selection = bpy.context.selected_objects
    bpy.context.view_layer.objects.active = selection[0] if selection else None

    for ob in selection:
        if len(ob.data.vertices) != 0 and len(ob.data.edges) != 0 and len(ob.data.polygons) != 0: 
            ob.select_set(False)

    selection = bpy.context.selected_objects
    bpy.context.view_layer.objects.active = selection[0] if selection else None

