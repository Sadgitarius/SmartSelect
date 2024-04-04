from .__hh__ import *

if bpy.context.mode == 'OBJECT':
    # User Inputs
    modifier_name      = bpy.context.scene.modifier_name
    stack_order_toggle = bpy.context.scene.stack_order_toggle
    curve_toggle       = bpy.context.scene.curve_toggle
    modifier_mode      = bpy.context.scene.modifier_mode
    mode_index         = ['Mode: Type', 'Mode: Name', 'Mode: GeoNode'].index(modifier_mode) 

    # Filter out Curves if Necessary
    selection = bpy.context.selected_objects
    if selection:
        if not curve_toggle:
            for ob in selection:
                if ob.type == 'CURVE':
                    ob.select_set(False)
        selection = bpy.context.selected_objects
        bpy.context.view_layer.objects.active = selection[0] if selection else None

        # Logic
        for ob in selection:
            bpy.context.view_layer.objects.active = ob

            if stack_order_toggle:
                if ob.modifiers:
                    if mode_index == 0:
                        if ob.modifiers[0].type == modifier_name:
                            bpy.ops.object.modifier_remove(modifier=ob.modifiers[0].name)
                    elif mode_index == 1:
                        if ob.modifiers[0].name == modifier_name:
                            bpy.ops.object.modifier_remove(modifier=ob.modifiers[0].name)
                    elif mode_index == 2:
                        if ob.modifiers[0].type == "NODES":
                            if ob.modifiers[0].node_group.name == modifier_name:
                                bpy.ops.object.modifier_remove(modifier=ob.modifiers[0].name)

            else:
                if ob.modifiers:
                    for mod in ob.modifiers:
                        if mode_index == 0:
                            if mod.type == modifier_name:
                                bpy.ops.object.modifier_remove(modifier=mod.name)
                        elif mode_index == 1:
                            if mod.name == modifier_name:
                                bpy.ops.object.modifier_remove(modifier=mod.name)
                        elif mode_index == 2:
                            if mod.type == "NODES":
                                if mod.node_group.name == modifier_name:
                                    bpy.ops.object.modifier_remove(modifier=mod.name)
