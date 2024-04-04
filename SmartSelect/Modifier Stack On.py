from .__hh__ import *

for obj in bpy.context.scene.objects:
    if obj.modifiers:
        for mod in obj.modifiers:
            if not mod.show_expanded:
                mod.show_expanded = True
