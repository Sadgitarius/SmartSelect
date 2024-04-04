from .__hh__ import *

if bpy.context.mode == 'OBJECT':
    selection = bpy.context.selected_objects
    bpy.context.view_layer.objects.active = selection[0] if selection else None

    if selection:
        for ob in selection:
            for slot_index, slot in enumerate(ob.material_slots):
                if slot.material == None:
                    bpy.context.view_layer.objects.active = ob
                    bpy.context.object.active_material_index = slot_index
                    bpy.ops.object.material_slot_remove()