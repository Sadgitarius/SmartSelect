from .__hh__ import *
import datetime
a = datetime.datetime.now()
clear = lambda: os.system('cls')
clear()

merge_collection_toggle         = bpy.context.scene.merge_collection_toggle
export_mirror_split_toggle      = bpy.context.scene.export_mirror_split_toggle
export_mirror_recenter_toggle   = bpy.context.scene.export_mirror_recenter_toggle

disable_last_subd_toggle        = bpy.context.scene.disable_last_subd_toggle
disable_all_subd_toggle         = bpy.context.scene.disable_all_subd_toggle
multires_toggle                 = bpy.context.scene.multires_toggle


def unhide_collections_EYE(collections):
    for col in collections:
        col.hide_viewport = False
        unhide_collections_EYE(col.children)

def unhide_collections_MONITOR():
    for col_name in collection_names:
        col = bpy.data.collections.get(col_name)
        col.hide_viewport = False 

def unhide_collections_SELECTION():
    for col_name in collection_names:
        col = bpy.data.collections.get(col_name)
        col.hide_select = False 

def delete_empty_collections():
    for col_name in collection_names:
        col = bpy.data.collections.get(col_name)
        if not col.objects:
            bpy.data.collections.remove(col)

def create_hierarchy(parent, collections, parent_col):

    Subd_list_col = []
    Other_list_col = []
    for ob in parent_col.objects:
        if ob in Subd_list:
            Subd_list_col.append(ob)
        else:
            Other_list_col.append(ob)

    if Subd_list_col:
        empty_subd = bpy.data.objects.new('abc_subd_'+parent_col.name, None)
        empty_subd.empty_display_type = 'PLAIN_AXES'
        empty_subd.empty_display_size = 1
        empty_subd.matrix_world.translation = (0,0,0)
        empty_subd.parent = parent
        bpy.context.collection.objects.link(empty_subd)
        empties.append(empty_subd)

        bpy.ops.object.select_all(action='DESELECT')
        empty_subd.select_set(True)
        bpy.context.view_layer.objects.active = empty_subd
        [ob.select_set(True) for ob in Subd_list_col]
        [empty.select_set(False) for empty in empties]
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

    if Other_list_col:
        empty_other = bpy.data.objects.new('abc_other_'+parent_col.name, None)
        empty_other.empty_display_type = 'PLAIN_AXES'
        empty_other.empty_display_size = 1
        empty_other.matrix_world.translation = (0,0,0)
        empty_other.parent = parent
        bpy.context.collection.objects.link(empty_other)
        empties.append(empty_other)

        bpy.ops.object.select_all(action='DESELECT')
        empty_other.select_set(True)
        bpy.context.view_layer.objects.active = empty_other
        [ob.select_set(True) for ob in Other_list_col]
        [empty.select_set(False) for empty in empties]
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

    for col in collections:
        empty = bpy.data.objects.new(col.name, None)
        empty.empty_display_type = 'PLAIN_AXES'
        empty.empty_display_size = 1
        empty.matrix_world.translation = (0,0,0)
        empty.parent = parent
        bpy.context.collection.objects.link(empty)
        empties.append(empty)
        create_hierarchy(empty, col.children, col)

def get_children(ob):
    children = []
    for child in ob.children:
        children.append(child)
        children.extend(get_children(child))
    return children

def get_all_collections_names(collections):
    global collection_names
    for collection in collections:
        collection_names.append(collection.name)
        get_all_collections_names(collection.children)

def delete_all_collections():
    for col_name in collection_names:
        col = bpy.data.collections.get(col_name)
        if col:
            for ob in col.objects:
                bpy.context.scene.collection.objects.link(ob)
            bpy.data.collections.remove(col)


if bpy.context.mode == 'OBJECT':

    global collection_names
    collection_names = [] 
    get_all_collections_names(bpy.context.scene.collection.children)
    unhide_collections_SELECTION()
    for ob in bpy.context.scene.objects:
        ob.hide_select = False

    consoleStr = '------------------------------------------------------\n'
    bpy.ops.object.select_all(action='SELECT')
    selection = bpy.context.selected_objects
    if selection:

        # BLOCK
        clear()
        consoleStr += 'Making Single User Object and Data\n'
        print(consoleStr)
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False, obdata_animation=False)
        bpy.ops.object.select_all(action='DESELECT')


        # BLOCK
        clear()
        consoleStr += 'Making Instances Real and saving instance base meshes for deletion\n'
        print(consoleStr)
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.duplicates_make_real()
        bpy.ops.object.select_all(action='INVERT')
        base_meshes_instances = bpy.context.selected_objects


        # BLOCK
        clear()
        consoleStr += 'Clearing all parent ties\n'
        print(consoleStr)
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        bpy.ops.object.select_all(action='DESELECT')


        # BLOCK
        clear()
        consoleStr += 'Hiding Unexpected Types (Not: MESH, CURVE, LATTICE, EMPTY)\n'
        print(consoleStr)
        bpy.ops.object.select_all(action='SELECT')
        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        for ob in selection:
            if ob.type != 'MESH' and ob.type != 'CURVE' and ob.type != 'LATTICE' and ob.type != 'EMPTY':
                bpy.context.view_layer.objects.active = ob
                bpy.context.active_object.hide_viewport = True # MONITOR
                bpy.context.active_object.hide_set(True) # EYE


        # BLOCK
        clear()
        consoleStr += 'Handling Subdivision and MultiResolution. Creating SubD list.\n'
        print(consoleStr)
        global Subd_list
        Subd_list = []
        bpy.ops.object.select_all(action='SELECT')
        selection = bpy.context.selected_objects
        for ob in selection:
            if ob.modifiers:
                mod_types = [mod.type for mod in ob.modifiers]
                if multires_toggle:
                    if 'MULTIRES' in mod_types:
                        for mod in ob.modifiers:
                            if mod.type == 'MULTIRES':
                                mod.show_viewport = False 

                if 'SUBSURF' in mod_types:
                    if disable_all_subd_toggle:
                        for mod in ob.modifiers:
                            if mod.type == 'SUBSURF':
                                mod.show_viewport = False 
                                Subd_list.append(ob)

                    elif disable_last_subd_toggle:
                        count = mod_types.count('SUBSURF')
                        if count > 1:
                            highest_index = len(mod_types) - 1 - mod_types[::-1].index('SUBSURF')
                            ob.modifiers[highest_index].show_viewport = False 
                            Subd_list.append(ob)
                        else:
                            for mod in ob.modifiers:
                                if mod.type == 'SUBSURF':
                                    mod.show_viewport = False 
                                    Subd_list.append(ob)
        Subd_list = list(set(Subd_list))
        

        # BLOCK
        clear()
        consoleStr += 'Converting To Mesh / Applying modifiers\n'
        print(consoleStr)
        if export_mirror_split_toggle:
            Mirror_list         = []
            Mirror_Subd_list    = []
            bpy.ops.object.select_all(action='SELECT')
            selection = bpy.context.selected_objects
            bpy.context.view_layer.objects.active = selection[0] 
            for ob in selection:
                if ob.modifiers:
                    mod_types = [mod.type for mod in ob.modifiers]
                    if 'MIRROR' in mod_types:
                        if 'SUBSURF' in mod_types:
                            Mirror_Subd_list.append(ob)
                        else:
                            Mirror_list.append(ob)

            bpy.ops.object.convert(target='MESH')
            bpy.ops.object.select_all(action='DESELECT')

            if Mirror_list:
                [ob.select_set(True) for ob in Mirror_list]
                bpy.context.view_layer.objects.active = Mirror_list[0]
                bpy.ops.mesh.separate(type='LOOSE')
                if export_mirror_recenter_toggle:
                    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
                bpy.ops.object.select_all(action='DESELECT')

            if Mirror_Subd_list:
                [ob.select_set(True) for ob in Mirror_Subd_list]
                bpy.context.view_layer.objects.active = Mirror_Subd_list[0]
                bpy.ops.mesh.separate(type='LOOSE')
                if export_mirror_recenter_toggle:
                    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
                [ob.select_set(False) for ob in Mirror_Subd_list]
                Subd_list.extend(bpy.context.selected_objects)
                bpy.ops.object.select_all(action='DESELECT')
                    
        else:
            bpy.ops.object.select_by_type(type='EMPTY') 
            bpy.ops.object.select_all(action='INVERT')
            selection = bpy.context.selected_objects
            bpy.context.view_layer.objects.active = selection[0] if selection else None
            bpy.ops.object.convert(target='MESH')
            bpy.ops.object.select_all(action='DESELECT')

        bpy.ops.object.select_by_type(type='MESH') 
        bpy.ops.object.select_all(action='INVERT')
        bpy.ops.object.delete()


        # BLOCK
        clear()
        consoleStr += 'Deleting instance base meshes\n'
        print(consoleStr)
        [ob.select_set(True) for ob in base_meshes_instances]
        bpy.ops.object.delete()


        # BLOCK
        clear()
        consoleStr += 'Deleting objects with no faces, Lattices and Empties.\n'
        print(consoleStr)
        bpy.ops.object.select_by_type(type='MESH')
        selection = bpy.context.selected_objects
        for ob in selection:
            if len(ob.data.polygons) != 0: 
                ob.select_set(False)

        selection = bpy.context.selected_objects
        bpy.ops.object.select_by_type(type='LATTICE')
        selection.extend(bpy.context.selected_objects)
        bpy.ops.object.select_by_type(type='EMPTY')
        selection.extend(bpy.context.selected_objects)
        [ob.select_set(True) for ob in selection]

        bpy.context.view_layer.objects.active = selection[0] if selection else None
        bpy.ops.object.delete()


        # BLOCK
        clear()
        consoleStr += 'Saving objects that are going to be kept\n'
        print(consoleStr)
        bpy.ops.object.select_all(action='SELECT')
        selection = bpy.context.selected_objects


        # BLOCK
        clear()
        consoleStr += 'Unhiding all collections\n'
        print(consoleStr)
        unhide_collections_EYE(bpy.context.view_layer.layer_collection.children)
        unhide_collections_MONITOR()


        # BLOCK
        clear()
        consoleStr += 'Unhiding all objects\n'
        print(consoleStr)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.hide_view_clear() # EYE
        for ob in bpy.data.objects:
            ob.hide_viewport = False # MONITOR


        # BLOCK
        clear()
        consoleStr += 'Deleting all objects except saved ones, deleting empty collections\n'
        print(consoleStr)
        bpy.ops.object.select_all(action='SELECT')
        for ob in selection:
            ob.select_set(False)
        bpy.ops.object.delete()


        # BLOCK
        clear()
        consoleStr += 'Reorganising hierarchy using empties\n'
        print(consoleStr)
        if merge_collection_toggle: 
            clear()
            consoleStr += 'Running\n'
            print(consoleStr)
            delete_all_collections()

            clear()
            consoleStr += 'Parenting subdivision objects\n'
            print(consoleStr)
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            SubSurfEmpty = bpy.context.active_object
            SubSurfEmpty.name = "Subdivision"
            for ob in Subd_list:
                try:
                    ob.select_set(True)
                except:
                    pass
            # [ob.select_set(True) for ob in Subd_list if hasattr(ob, 'select_set')]
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
            bpy.ops.object.select_all(action='DESELECT')

            clear()
            consoleStr += 'Parenting other objects\n'
            print(consoleStr)
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            OtherEmpty = bpy.context.active_object
            OtherEmpty.name = "Other"
            bpy.ops.object.select_all(action='SELECT')
            for ob in Subd_list:
                try:
                    ob.select_set(False)
                except:
                    pass
            # [ob.select_set(False) for ob in Subd_list if hasattr(ob, 'select_set')]
            SubSurfEmpty.select_set(False)
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
            bpy.ops.object.select_all(action='DESELECT')

        else:
            clear()
            consoleStr += 'Running\n'
            print(consoleStr)
            root_ob = bpy.data.objects.new(bpy.context.scene.collection.name, None)
            root_ob.empty_display_type = 'PLAIN_AXES'
            root_ob.empty_display_size = 1
            root_ob.matrix_world.translation = (0,0,0)
            bpy.context.collection.objects.link(root_ob) #change

            global empties
            empties =[root_ob]
            create_hierarchy(root_ob, bpy.context.scene.collection.children, bpy.context.scene.collection)

            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.move_to_collection(collection_index=0)
            bpy.ops.object.select_all(action='DESELECT')
            delete_all_collections()


        # Block
        clear()
        consoleStr += 'Renaming objects to fit Maya\n'
        for ob in bpy.context.scene.objects:
            new_name = ob.name.replace('.', '_')
            ob.name = new_name
            new_name = ob.name.replace(' ', '_')
            ob.name = new_name

        clear()
        consoleStr += '\n'
        consoleStr += 'Script ran for:'
        print(consoleStr)
        b = datetime.datetime.now()
        delta = b - a
        print(str(delta.total_seconds()) + ' s')
        print('------------------------------------------------------\n\n\n')
