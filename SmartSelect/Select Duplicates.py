from .__hh__ import *

if bpy.context.mode == 'OBJECT':
    margin = bpy.context.scene.duplicates_slider
    duplicates = []

    # Assemble unqiue data about meshes and find duplicates
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH') 
    selection = bpy.context.selected_objects

    if selection:
        data_table = []
        for i, el in enumerate(selection):
            arrayToAppend = []
            arrayToAppend.append(len(el.data.vertices))
            arrayToAppend.append(len(el.data.edges))
            arrayToAppend.append(len(el.data.polygons))
            arrayToAppend.append(round(el.matrix_world.to_translation()[0], margin))
            arrayToAppend.append(round(el.matrix_world.to_translation()[1], margin))
            arrayToAppend.append(round(el.matrix_world.to_translation()[2], margin))
            arrayToAppend.append(round(el.rotation_euler[0], margin))
            arrayToAppend.append(round(el.rotation_euler[1], margin))
            arrayToAppend.append(round(el.rotation_euler[2], margin))
            arrayToAppend.append(round(el.scale[0], margin))
            arrayToAppend.append(round(el.scale[1], margin))
            arrayToAppend.append(round(el.scale[2], margin))
            data_table.append(arrayToAppend)

        seen = set()
        for i, el in enumerate(data_table):
            t = tuple(el)
            if t not in seen:
                seen.add(t)
            else:
                duplicates.append(selection[i])
            
            
    # Assemble unqiue data about curves and find duplicates     
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='CURVE') 
    selection = bpy.context.selected_objects

    if selection:
        data_table = []
        for i, el in enumerate(selection):
            arrayToAppend = []
            arrayToAppend.append(el.data.bevel_depth)
            arrayToAppend.append(el.data.offset)
            arrayToAppend.append(el.data.bevel_resolution)
            arrayToAppend.append(el.data.resolution_u)
            arrayToAppend.append(el.data.resolution_v)
            arrayToAppend.append(el.data.bevel_depth)
            arrayToAppend.append(el.data.extrude)
            arrayToAppend.append(round(el.matrix_world.to_translation()[0], margin))
            arrayToAppend.append(round(el.matrix_world.to_translation()[1], margin))
            arrayToAppend.append(round(el.matrix_world.to_translation()[2], margin))
            arrayToAppend.append(round(el.rotation_euler[0], margin))
            arrayToAppend.append(round(el.rotation_euler[1], margin))
            arrayToAppend.append(round(el.rotation_euler[2], margin))
            arrayToAppend.append(round(el.scale[0], margin))
            arrayToAppend.append(round(el.scale[1], margin))
            arrayToAppend.append(round(el.scale[2], margin))
            data_table.append(arrayToAppend)

        seen = set()
        for i, el in enumerate(data_table):
            t = tuple(el)
            if t not in seen:
                seen.add(t)
            else:
                duplicates.append(selection[i])


    # Select elements in Duplicates
    bpy.ops.object.select_all(action='DESELECT')
    [el.select_set(True) for el in duplicates]
    selection = bpy.context.selected_objects
    bpy.context.view_layer.objects.active = selection[0] if selection else None
