import bpy
import os

posModifiers = ['ARMATURE','ARRAY','BEVEL','BOOLEAN','BUILD','CAST','CORRECTIVE_SMOOTH','CURVE','DATA_TRANSFER','DECIMATE','DISPLACE','EDGE_SPLIT','HOOK','LAPLACIANDEFORM','LAPLACIANSMOOTH','LATTICE','MASK','MESH_CACHE','MESH_DEFORM','MESH_SEQUENCE_CACHE','MESH_TO_MESH','MIRROR','MULTIRES','NOISE','NORMAL_EDIT','OBJECT_DATA','OFFSET','PARTICLE_INSTANCE','PARTICLE_SYSTEM','REMESH','SCREW','SHRINKWRAP','SIMPLE_DEFORM','SKIN','SMOOTH','SOFT_BODY','SOLIDIFY','SUBSURF','SURFACE','TEXT','TILT','TRIANGULATE','UV_PROJECT','UV_WARP','VERTEX_WEIGHT_EDIT','VERTEX_WEIGHT_MIX','VERTEX_WEIGHT_PROXIMITY','WARP','WAVE','WEIGHTED_NORMAL','WIREFRAME']

def close_panel(event):
    x, y = event.mouse_x, event.mouse_y
    bpy.context.window.cursor_warp(10, 10)
    move_back = lambda: bpy.context.window.cursor_warp(x, y)
    bpy.app.timers.register(move_back, first_interval=0.001)

def get_unique_modifiers(mode):
    modifier_types = set()
    print('----------')
    print(mode)
    print('----------')
    for obj in bpy.context.scene.objects:
        if obj.modifiers:
            for mod in obj.modifiers:
                if mode == 0:
                    modifier_types.add(mod.type)
                elif mode == 1:
                    modifier_types.add(mod.name)

    return list(modifier_types)

def curve_to_mesh_with_mod(ob):
    new_obj = ob.copy()
    new_obj.data = ob.data.copy()
    bpy.context.scene.collection.objects.link(new_obj)
    for modifier in ob.modifiers:
        modifier.show_viewport = False
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True) 
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.convert(target='MESH')
    new_obj.select_set(True)
    bpy.context.view_layer.objects.active = new_obj
    bpy.ops.object.make_links_data(type='MODIFIERS')
    ob.select_set(False) 
    bpy.ops.object.delete(use_global=False)
    ob.select_set(True) 
    bpy.context.view_layer.objects.active = ob

    return ob

def mirror_split(ob, recenter):
    # Separate by loose parts from Mirrored list
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.ops.mesh.separate(type='LOOSE')

    if recenter:
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

    return ob
