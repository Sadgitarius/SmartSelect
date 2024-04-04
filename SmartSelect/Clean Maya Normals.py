from .__hh__ import *


if bpy.context.mode == 'OBJECT':
    selection = bpy.context.selected_objects
    bpy.context.view_layer.objects.active = selection[0] if selection else None

    for ob in selection:
        if ob.type == "MESH":
            bpy.context.view_layer.objects.active = ob
            bpy.ops.mesh.customdata_custom_splitnormals_clear()