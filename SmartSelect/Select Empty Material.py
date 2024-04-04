from .__hh__ import *

if bpy.context.mode == 'OBJECT':
    bpy.ops.object.select_all(action='SELECT')
    selection = bpy.context.selected_objects
    bpy.ops.object.select_all(action='DESELECT')

    for ob in selection:
        for slot in ob.material_slots:
            if slot.material == None:
                ob.select_set(True)

    selection = bpy.context.selected_objects
    bpy.context.view_layer.objects.active = selection[0] if selection else None