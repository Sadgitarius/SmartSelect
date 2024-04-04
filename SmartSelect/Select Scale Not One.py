from .__hh__ import *

if bpy.context.mode == 'OBJECT':
    bpy.ops.object.select_all(action='DESELECT')
    for ob in bpy.context.scene.objects:
        if any(s != 1 for s in ob.scale):
            ob.select_set(True)