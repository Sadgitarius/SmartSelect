from .__hh__ import *

mirror_selection_toggle = bpy.context.scene.mirror_selection_toggle
mirror_source           = bpy.context.scene.mirror_source
mirror_target           = bpy.context.scene.mirror_target

if mirror_selection_toggle:
    selection = bpy.context.selected_objects
else:
    selection = bpy.context.scene.objects

if bpy.context.mode == 'OBJECT':
    if selection:
        for ob in selection:
            if ob.modifiers:
                for mod in ob.modifiers:
                    if mod.type == 'MIRROR':
                        try:
                            if mod.mirror_object.name == mirror_source:
                                mod.mirror_object = bpy.data.objects[mirror_target]
                        except:
                            pass