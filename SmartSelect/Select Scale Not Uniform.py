from .__hh__ import *

if bpy.context.mode == 'OBJECT':
    bpy.ops.object.select_all(action='SELECT')
    selection = bpy.context.scene.objects
    for ob in selection:
        if ob.scale[0] == ob.scale[1] and ob.scale[1] == ob.scale[2]:
            ob.select_set(False)

    selection = bpy.context.scene.objects
    bpy.context.view_layer.objects.active = selection[0] if selection else None