from .__hh__ import *

if bpy.context.mode == 'OBJECT':
    # User Inputs
    modifier_name          = bpy.context.scene.modifier_name
    stack_order_toggle     = bpy.context.scene.stack_order_toggle
    curve_toggle           = bpy.context.scene.curve_toggle
    mirror_split_toggle    = bpy.context.scene.mirror_split_toggle
    mirror_recenter_toggle = bpy.context.scene.mirror_recenter_toggle
    modifier_mode          = bpy.context.scene.modifier_mode
    mode_index             = ['Mode: Type', 'Mode: Name', 'Mode: GeoNode'].index(modifier_mode) 

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
                            if ob.type == 'CURVE':
                                curve_to_mesh_with_mod(ob)
                            try:
                                bpy.ops.object.modifier_apply(modifier=ob.modifiers[0].name)
                                if modifier_name == "MIRROR" and mirror_split_toggle and ob.modifiers[0].type == "MIRROR":
                                    mirror_split(ob, mirror_recenter_toggle)
                            except:
                                pass
                    elif mode_index == 1:
                        if ob.modifiers[0].name == modifier_name:
                            if ob.type == 'CURVE':
                                curve_to_mesh_with_mod(ob)
                            try:
                                bpy.ops.object.modifier_apply(modifier=ob.modifiers[0].name)
                                if modifier_name == "MIRROR" and mirror_split_toggle and ob.modifiers[0].type == "MIRROR":
                                    mirror_split(ob, mirror_recenter_toggle)
                            except:
                                pass
                    elif mode_index == 2:
                        if ob.modifiers[0].type == "NODES":
                            if ob.modifiers[0].node_group.name == modifier_name:
                                try:
                                    bpy.ops.object.modifier_apply(modifier=ob.modifiers[0].name)
                                except:
                                    pass
                            
            else:
                if ob.modifiers:
                    if ob.type == 'CURVE':
                        curve_to_mesh_with_mod(ob)

                    for mod in ob.modifiers:
                        if mode_index == 0:
                            if mod.type == modifier_name:
                                try:
                                    bpy.ops.object.modifier_apply(modifier=mod.name)
                                    if modifier_name == "MIRROR" and mirror_split_toggle and mod.type == "MIRROR":
                                        mirror_split(ob, mirror_recenter_toggle)
                                except:
                                    pass
                        elif mode_index == 1:
                            if mod.name == modifier_name:
                                try:
                                    bpy.ops.object.modifier_apply(modifier=mod.name)
                                    if modifier_name == "MIRROR" and mirror_split_toggle and mod.type == "MIRROR":
                                        mirror_split(ob, mirror_recenter_toggle)
                                except:
                                    pass
                        elif mode_index == 2:
                            if mod.type == "NODES":
                                if mod.node_group.name == modifier_name:
                                    try:
                                        bpy.ops.object.modifier_apply(modifier=mod.name)
                                    except:
                                        pass

        # Get Initial Selection
        bpy.ops.object.select_all(action='DESELECT')
        for ob in selection:
            ob.select_set(True)
        bpy.context.view_layer.objects.active = selection[0] if selection else None
