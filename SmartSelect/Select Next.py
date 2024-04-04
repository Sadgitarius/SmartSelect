from .__hh__ import *

if bpy.context.mode == 'OBJECT':
    selection = bpy.context.selected_objects
    active_object = bpy.context.active_object
    if active_object not in selection:
        bpy.context.view_layer.objects.active = selection[0] if selection else None
        
    if len(selection) > 1:
        active_object = bpy.context.active_object
        index = selection.index(active_object)
        index = (index + 1) % len(selection)
        bpy.context.view_layer.objects.active = selection[index]