import bpy
import os
clear = lambda: os.system('cls')
clear()


switchFrom = ['abc Center.001', 'abc Center.002', 'abc Center.003', 'abc Center.004', 'abc Center.005']
switchTo = 'abc Center'

bpy.ops.object.select_all(action='SELECT')
selection = bpy.context.selected_objects


for el in selection:
    for mod in el.modifiers:
        if mod.type == 'MIRROR':
            try:
                if mod.mirror_object.name in switchFrom:
                    mod.mirror_object = bpy.data.objects[switchTo]
            except:
                pass
                
                
