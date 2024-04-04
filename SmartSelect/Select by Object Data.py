from .__hh__ import *

dimensions_toggle   = bpy.context.scene.dimensions_toggle
scale_toggle        = bpy.context.scene.scale_toggle
rotation_toggle     = bpy.context.scene.rotation_toggle
location_toggle     = bpy.context.scene.location_toggle
margin              = bpy.context.scene.transform_slider

if bpy.context.mode == 'OBJECT':
    ob = bpy.context.view_layer.objects.active
    if ob:
        duplicates = []
        duplicates.append(ob)
        if ob.type == 'MESH':
            active_data = []
            active_data.append(len(ob.data.vertices))
            active_data.append(len(ob.data.edges))
            active_data.append(len(ob.data.polygons))
            if dimensions_toggle:
                active_data.append(ob.dimensions[0])
                active_data.append(ob.dimensions[1])
                active_data.append(ob.dimensions[2])
            if rotation_toggle:
                active_data.append(ob.rotation_euler[0])
                active_data.append(ob.rotation_euler[1])
                active_data.append(ob.rotation_euler[2])
            if scale_toggle:
                active_data.append(ob.scale[0])
                active_data.append(ob.scale[1])
                active_data.append(ob.scale[2])
            if location_toggle:
                active_data.append(round(ob.matrix_world.to_translation()[0], margin))
                active_data.append(round(ob.matrix_world.to_translation()[1], margin))
                active_data.append(round(ob.matrix_world.to_translation()[2], margin))

            bpy.ops.object.select_by_type(type='MESH') 
            ob.select_set(False)
            selection = bpy.context.selected_objects
            
            for ob in selection:
                temp_data = []
                temp_data.append(len(ob.data.vertices))
                temp_data.append(len(ob.data.edges))
                temp_data.append(len(ob.data.polygons))
                if dimensions_toggle:
                    temp_data.append(ob.dimensions[0])
                    temp_data.append(ob.dimensions[1])
                    temp_data.append(ob.dimensions[2])
                if rotation_toggle:
                    temp_data.append(ob.rotation_euler[0])
                    temp_data.append(ob.rotation_euler[1])
                    temp_data.append(ob.rotation_euler[2])
                if scale_toggle:
                    temp_data.append(ob.scale[0])
                    temp_data.append(ob.scale[1])
                    temp_data.append(ob.scale[2])
                if location_toggle:
                    temp_data.append(round(ob.matrix_world.to_translation()[0], margin))
                    temp_data.append(round(ob.matrix_world.to_translation()[1], margin))
                    temp_data.append(round(ob.matrix_world.to_translation()[2], margin))
                if active_data == temp_data:
                    duplicates.append(ob)

        if ob.type == 'CURVE':
            active_data = []
            active_data.append(ob.data.bevel_depth)
            active_data.append(ob.data.offset)
            active_data.append(ob.data.bevel_resolution)
            active_data.append(ob.data.resolution_u)
            active_data.append(ob.data.resolution_v)
            active_data.append(ob.data.bevel_depth)
            active_data.append(ob.data.extrude)
            if dimensions_toggle:
                active_data.append(ob.dimensions[0])
                active_data.append(ob.dimensions[1])
                active_data.append(ob.dimensions[2])
            if rotation_toggle:
                active_data.append(ob.rotation_euler[0])
                active_data.append(ob.rotation_euler[1])
                active_data.append(ob.rotation_euler[2])
            if scale_toggle:
                active_data.append(ob.scale[0])
                active_data.append(ob.scale[1])
                active_data.append(ob.scale[2])
            if location_toggle:
                active_data.append(round(ob.matrix_world.to_translation()[0], margin))
                active_data.append(round(ob.matrix_world.to_translation()[1], margin))
                active_data.append(round(ob.matrix_world.to_translation()[2], margin))
            bpy.ops.object.select_by_type(type='CURVE') 
            ob.select_set(False)
            selection = bpy.context.selected_objects
            for ob in selection:
                temp_data = []
                temp_data.append(ob.data.bevel_depth)
                temp_data.append(ob.data.offset)
                temp_data.append(ob.data.bevel_resolution)
                temp_data.append(ob.data.resolution_u)
                temp_data.append(ob.data.resolution_v)
                temp_data.append(ob.data.bevel_depth)
                temp_data.append(ob.data.extrude)
                if dimensions_toggle:
                    temp_data.append(ob.dimensions[0])
                    temp_data.append(ob.dimensions[1])
                    temp_data.append(ob.dimensions[2])
                if rotation_toggle:
                    temp_data.append(ob.rotation_euler[0])
                    temp_data.append(ob.rotation_euler[1])
                    temp_data.append(ob.rotation_euler[2])
                if scale_toggle:
                    temp_data.append(ob.scale[0])
                    temp_data.append(ob.scale[1])
                    temp_data.append(ob.scale[2])
                if location_toggle:
                    temp_data.append(round(ob.matrix_world.to_translation()[0], margin))
                    temp_data.append(round(ob.matrix_world.to_translation()[1], margin))
                    temp_data.append(round(ob.matrix_world.to_translation()[2], margin))
                if active_data == temp_data:
                    duplicates.append(ob)

        # Select elements in Duplicates
        bpy.ops.object.select_all(action='DESELECT')
        [ob.select_set(True) for ob in duplicates]
        selection = bpy.context.selected_objects
        bpy.context.view_layer.objects.active = duplicates[0] if selection else None
