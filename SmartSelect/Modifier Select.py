from .__hh__ import *

if bpy.context.mode == 'OBJECT':
    # User Inputs
    modifier_name      = bpy.context.scene.modifier_name
    stack_order_toggle = bpy.context.scene.stack_order_toggle
    curve_toggle       = bpy.context.scene.curve_toggle
    modifier_mode      = bpy.context.scene.modifier_mode
    mode_index         = ['Mode: Type', 'Mode: Name', 'Mode: GeoNode'].index(modifier_mode) 

    # Logic
    bpy.ops.object.select_all(action='DESELECT')
    mlist = []
    for ob in bpy.data.objects:
        if stack_order_toggle:
            if ob.modifiers:
                if mode_index == 0:
                    if modifier_name == ob.modifiers[0].type and ob.name in bpy.context.scene.objects:
                        mlist.append(ob)
                elif mode_index == 1:
                    if modifier_name == ob.modifiers[0].name and ob.name in bpy.context.scene.objects:
                        mlist.append(ob)
                elif mode_index == 2:
                    if ob.modifiers[0].type == "NODES":
                        if modifier_name == ob.modifiers[0].node_group.name:
                            mlist.append(ob)
        else:
            if ob.modifiers:
                for mod in ob.modifiers:
                    if mode_index == 0:
                        if modifier_name == mod.type and ob.name in bpy.context.scene.objects:
                            mlist.append(ob)
                    elif mode_index == 1:
                        if modifier_name == mod.name and ob.name in bpy.context.scene.objects:
                            mlist.append(ob)
                    elif mode_index == 2:
                        if mod.type == "NODES":
                            if modifier_name == mod.node_group.name:
                                mlist.append(ob)

    # Update Selection and Filter Out Curves If Needed
    for ob in mlist:
        ob.select_set(True)
        if not curve_toggle:
            if ob.type == 'CURVE':
                ob.select_set(False)


    selection = bpy.context.selected_objects
    bpy.context.view_layer.objects.active = selection[0] if selection else None