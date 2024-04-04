from .__hh__ import *

if bpy.context.mode == 'OBJECT':
    margin = 3
    bpy.ops.object.select_all(action='SELECT')
    selection = bpy.context.selected_objects 
        

    for el in selection:
        if round(el.scale[0], margin) == round(el.scale[1], margin) and round(el.scale[1], margin) == round(el.scale[2], margin):
            el.select_set(False)