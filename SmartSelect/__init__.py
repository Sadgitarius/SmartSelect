from .__hh__ import *
modeList = ['Mode: Type', 'Mode: Name', 'Mode: GeoNode']
global savedMode
savedMode = ['','','']
addon_dir = os.path.dirname(__file__)
bl_info = {
        "name": "SmartSelect",
        "author": "Boris Levin",
        "location": "View3D > Sidebar > Smart Select",
        "version": (1, 0),
        "blender": (3, 3, 1),
        "description": "Feng Shui Ensurer.\nScene management addon that utilizes many selection tools to save time and clean up the scene.\nWhenever fitting, offers useful functionalty based on selection.",
        "category": "Object"
        }


class ModifierPanel(bpy.types.Panel):
    bl_label = "Modifiers"
    bl_idname = "OBJECT_PT_modifier_name_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'       
    bl_category = "Smart Select"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Modifiers:")

        row = box.row(align=True)
        row.operator("modifiermode.toggle", text=context.scene.modifier_mode)

        row = box.row(align=True)
        row.operator("fromactive.button", text="From Active")
        row.operator("fromlist.button", text="From List")

        row = box.row(align=True)
        mode_index = modeList.index(context.scene.modifier_mode)
        row.prop(context.scene, "modifier_name", text=modeList[mode_index][6:])
        row.operator("refresh.button", text="", icon='FILE_REFRESH')

        row = box.row(align=True)
        row = box.row(align=True)
        row.prop(context.scene, "stack_order_toggle", text=' First in Stack Only', toggle=False)
        row = box.row(align=True)
        row.prop(context.scene, "curve_toggle", text=' Apply Curves', toggle=False)
        row = box.row(align=True)
        row.prop(context.scene, "mirror_split_toggle", text=' Mirror Split', toggle=False)
        row.enabled = False if mode_index == 2 else row.enabled
        row = box.row(align=True)
        row.prop(context.scene, "mirror_recenter_toggle", text=' Mirror Recenter', toggle=False)
        row.enabled = context.scene.mirror_split_toggle
        row.enabled = False if mode_index == 2 else row.enabled

        row = box.row(align=True)
        box.label(text="Methods:")
        row = box.row(align=True)
        row.operator("modifierselect.button", text="Select")
        row = box.row(align=True)
        row.operator("modifierapply.button", text="Apply Selection")
        row = box.row(align=True)
        row.operator("modifierremove.button", text="Remove Selection")

        row = box.row(align=True)
        row.operator("modifierstackoff.button", text="Collapse Stacks")
        row.operator("modifierstackon.button", text="Expand Stacks")

class UpdateMirrorRecenterToggle(bpy.types.Operator):
    bl_idname = "object.update_mirror_recenter_toggle"
    bl_label = "Update Mirror Recenter Toggle"

    def execute(self, context):
        if not context.scene.mirror_split_toggle:
            context.scene.mirror_recenter_toggle = False
            row.enabled = False
        return {'FINISHED'}

class MODIFIER_MODE(bpy.types.Operator):
    """TYPE: Modifier types.\nNAME: Modifier names.\nGEONODE: Geometry node tree names"""
    bl_idname = "modifiermode.toggle"
    bl_label = "Modifier Mode"
    
    def execute(self, context):
        global savedMode
        mode_index = modeList.index(context.scene.modifier_mode)
        savedMode[mode_index] = context.scene.modifier_name
        mode_index = (mode_index + 1) % len(modeList)
        context.scene.modifier_name = savedMode[mode_index]
        context.scene.modifier_mode = modeList[mode_index]
        return {'FINISHED'}

class FROM_ACTIVE(bpy.types.Operator):
    """Displays modifiers from active object based on the mode"""
    bl_label = "From Active"
    bl_idname = "fromactive.button"

    def execute(self, context):
        # Show a menu to select a modifier

        if context.active_object is not None:
            mode_index = modeList.index(context.scene.modifier_mode) 
            if mode_index == 0:
                self.menu_items = [modifier.type for modifier in bpy.context.active_object.modifiers]
            elif mode_index == 1:
                self.menu_items = [modifier.name for modifier in bpy.context.active_object.modifiers]
            elif mode_index == 2:
                self.menu_items = []
                for modifier in bpy.context.active_object.modifiers:
                    if modifier.type == "NODES":
                        self.menu_items.append(modifier.node_group.name)

            self.menu_items = list(set(self.menu_items))
            self.menu_items = sorted(self.menu_items)

            if self.menu_items:
                return context.window_manager.invoke_popup(self)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        for item in self.menu_items:
            layout.operator("set.modifier_name", text=item).modifier_type = item

class FROM_LIST(bpy.types.Operator):
    """Displays all modifiers in the scene based on the mode"""
    bl_label = "From List"
    bl_idname = "fromlist.button"

    def execute(self, context):
        # Show a menu to select a modifier
        mode_index = modeList.index(context.scene.modifier_mode) 
        self.menu_items = [el.name for el in bpy.data.node_groups] if mode_index == 2 else get_unique_modifiers(mode_index)
        self.menu_items = sorted(self.menu_items)
        return context.window_manager.invoke_popup(self)

    def draw(self, context):
        layout = self.layout
        for item in self.menu_items:
            layout.operator("set.modifier_name", text=item).modifier_type = item

class SET_MODIFIER_NAME(bpy.types.Operator):
    """String based on which the methods are going to be executed"""
    bl_label = "Set Modifier Name"
    bl_idname = "set.modifier_name"
    modifier_type: bpy.props.StringProperty()

    def invoke(self, context, event):
        context.scene.modifier_name = self.modifier_type
        bpy.context.area.tag_redraw()
        close_panel(event) 
        return {'FINISHED'}

class REFRESH_MODIFIER_NAME(bpy.types.Operator):
    """All Modes"""
    bl_label = "Refresh Modifier Strings."
    bl_idname = "refresh.button"

    def execute(self, context):
        context.scene.modifier_name = ""
        global savedMode
        savedMode = ['','','']
        return {'FINISHED'}

class MODIFIER_SELECT(bpy.types.Operator):
    """Selects objects based on the textfield string, mode and selected settings"""
    bl_label = "Modifier Select"
    bl_idname = "modifierselect.button"

    def execute(self, context):
        # Load and run script
        script_file = os.path.join(addon_dir, "Modifier Select.py")
        with open(script_file) as f:
            code = compile(f.read(), script_file, 'exec')
            exec(code, globals())
        return {'FINISHED'}

class MODIFIER_APPLY(bpy.types.Operator):
    """Applies modifiers of selected objects based on:\nTextfield string, mode and selected settings"""
    bl_label = "Modifier Apply"
    bl_idname = "modifierapply.button"

    def execute(self, context):
        # Load and run script
        script_file = os.path.join(addon_dir, "Modifier Apply.py")
        with open(script_file) as f:
            code = compile(f.read(), script_file, 'exec')
            exec(code, globals())
        return {'FINISHED'}

class MODIFIER_REMOVE(bpy.types.Operator):
    """Removes modifiers of selected objects based on:\nTextfield string, mode and selected settings"""
    bl_label = "Modifier Remove"
    bl_idname = "modifierremove.button"

    def execute(self, context):
        # Load and run script
        script_file = os.path.join(addon_dir, "Modifier Remove.py")
        with open(script_file) as f:
            code = compile(f.read(), script_file, 'exec')
            exec(code, globals())
        return {'FINISHED'}

class MODIFIER_STACK_ON(bpy.types.Operator):
    """Expands all modifers in the scene"""
    bl_label = "Modifier Stack On"
    bl_idname = "modifierstackon.button"

    def execute(self, context):
        # Load and run script
        script_file = os.path.join(addon_dir, "Modifier Stack On.py")
        with open(script_file) as f:
            code = compile(f.read(), script_file, 'exec')
            exec(code, globals())
        return {'FINISHED'}

class MODIFIER_STACK_OFF(bpy.types.Operator):
    """Collapses all modifers in the scene"""
    bl_label = "Modifier Stack Off"
    bl_idname = "modifierstackoff.button"

    def execute(self, context):
        # Load and run script
        script_file = os.path.join(addon_dir, "Modifier Stack Off.py")
        with open(script_file) as f:
            code = compile(f.read(), script_file, 'exec')
            exec(code, globals())
        return {'FINISHED'}


class GeneralPanel(bpy.types.Panel):
    bl_label = "General"
    bl_idname = "OBJECT_PT_General_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'       
    bl_category = "Smart Select"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        # SELECT NEXT
        box = layout.box()
        row = box.row(align=True)
        row.label(text="Select Next:")
        row.operator("selectnext.button", text="Select")

        # IDENTICAL OBJECTS
        box = layout.box()
        box.label(text="Identical Objects:")
        row = box.row(align=True)
        row.operator("selectbyobjectdata.button", text="Select")
        row = box.row(align=True)
        row.label(text="Sensitive to: ")
        row = box.row(align=True)
        row.prop(context.scene, "scale_toggle", text=' Scale', toggle=False)
        row.prop(context.scene, "dimensions_toggle", text=' Dimensions', toggle=False)
        row = box.row(align=True)
        row.prop(context.scene, "rotation_toggle", text=' Rotation', toggle=False)
        row.prop(context.scene, "location_toggle", text=' Location', toggle=False)
        row = box.row(align=True)
        transform_slider = context.scene.transform_slider
        row.label(text="Decimal Rounding: ")
        row.prop(context.scene, "transform_slider", text="", emboss=True)
        row.enabled = context.scene.location_toggle
        row = box.row(align=True)

        # SCALE
        box = layout.box()
        box.label(text="Scale:")
        row = box.row(align=True)
        row.label(text="Not Uniform:")
        row.operator("selectscalenotuniform.button", text="Select")
        row = box.row(align=True)
        row.label(text="Not One-One-One:")
        row.operator("selectscalenotone.button", text="Select")

        # MIRROR REWIRE
        box = layout.box()
        box.label(text="Mirror Rewire:")
        row = box.row(align=True)
        row.operator("mirrorrewire.button", text="Rewire")
        row = box.row(align=True)
        row.operator("mirror_source_fromactive.button", text="From Active")
        row.operator("mirror_source_fromlist.button", text="From List")
        row = box.row(align=True)
        row.prop(context.scene, "mirror_source", text="Source")
        row = box.row(align=True)
        row.operator("mirror_target_fromactive.button", text="From Active")
        row.operator("mirror_target_fromlist.button", text="From List")
        row = box.row(align=True)
        row.operator("active_name.button", text="Active Name")
        row = box.row(align=True)
        row.prop(context.scene, "mirror_target", text="Target")
        row = box.row(align=True)
        row.prop(context.scene, "mirror_selection_toggle", text=' Selection Only', toggle=False)
        row.operator("mirror_refresh.button", text="", icon='FILE_REFRESH')

class REFRESH_MIRROR_NAME(bpy.types.Operator):
    """Source and Target"""
    bl_label = "Refresh Fields."
    bl_idname = "mirror_refresh.button"

    def execute(self, context):
        context.scene.mirror_source = ""
        context.scene.mirror_target = ""
        return {'FINISHED'}

class SELECT_NEXT(bpy.types.Operator):
    """Selects the next object in selection"""
    bl_label = "Select Next"
    bl_idname = "selectnext.button"

    def execute(self, context):
        # Load and run script
        script_file = os.path.join(addon_dir, "Select Next.py")
        with open(script_file) as f:
            code = compile(f.read(), script_file, 'exec')
            exec(code, globals())
        return {'FINISHED'}

class SELECT_BY_OBJECT_DATA(bpy.types.Operator):
    """Selects objects with same number of vertices/edges/faces"""
    bl_label = "Select by Object Data"
    bl_idname = "selectbyobjectdata.button"

    def execute(self, context):
        # Load and run script
        script_file = os.path.join(addon_dir, "Select by Object Data.py")
        with open(script_file) as f:
            code = compile(f.read(), script_file, 'exec')
            exec(code, globals())
        return {'FINISHED'}

class SELECT_SCALE_NOT_UNIFORM(bpy.types.Operator):
    """Select objects with not uniform scale.\n(1,1,1) - Uniform.\n(5,5,5) - Uniform.\n(1,1,5) - Not Uniform"""
    bl_label = "Select Scale Not Uniform"
    bl_idname = "selectscalenotuniform.button"

    def execute(self, context):
        # Load and run script
        script_file = os.path.join(addon_dir, "Select Scale Not Uniform.py")
        with open(script_file) as f:
            code = compile(f.read(), script_file, 'exec')
            exec(code, globals())
        return {'FINISHED'}

class SELECT_SCALE_NOT_ONE(bpy.types.Operator):
    """Select objects that have a scale value not equal to (1,1,1)"""
    bl_label = "Select Scale Not One"
    bl_idname = "selectscalenotone.button"

    def execute(self, context):
        # Load and run script
        script_file = os.path.join(addon_dir, "Select Scale Not One.py")
        with open(script_file) as f:
            code = compile(f.read(), script_file, 'exec')
            exec(code, globals())
        return {'FINISHED'}

class MIRROR_REWIRE(bpy.types.Operator):
    """Rewires all mirror objects in the scene.\nSOURCE becomes TARGET"""
    bl_label = "Mirror Rewire"
    bl_idname = "mirrorrewire.button"

    def execute(self, context):
        # Load and run script
        script_file = os.path.join(addon_dir, "Mirror Rewire.py")
        with open(script_file) as f:
            code = compile(f.read(), script_file, 'exec')
            exec(code, globals())
        return {'FINISHED'}

class MIRROR_SOURCE_FROM_ACTIVE(bpy.types.Operator):
    """Displays mirror objects from active object"""
    bl_label = "Mirror Source From Active"
    bl_idname = "mirror_source_fromactive.button"

    def execute(self, context):
        # Show a menu to select a modifier
        self.menu_items = []
        if context.active_object is not None:
            modifiers = bpy.context.active_object.modifiers
            if modifiers:
                for mod in bpy.context.active_object.modifiers:
                    if mod.type == "MIRROR":
                        if mod.mirror_object:
                            self.menu_items.append(mod.mirror_object.name)

                self.menu_items = list(set(self.menu_items))
                self.menu_items = sorted(self.menu_items)

            if self.menu_items:
                return context.window_manager.invoke_popup(self)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        for item in self.menu_items:
            layout.operator("set.mirror_source", text=item).source_name = item

class MIRROR_SOURCE_FROM_LIST(bpy.types.Operator):
    """Displays mirror objects from the entire scene"""
    bl_label = "Mirror Source From List"
    bl_idname = "mirror_source_fromlist.button"

    def execute(self, context):
        # Show a menu to select a modifier
        self.menu_items = []
        objects = bpy.context.scene.objects
        if objects:
            for ob in objects:
                modifiers = ob.modifiers
                if modifiers:
                    for mod in ob.modifiers:
                        if mod.type == "MIRROR":
                            if mod.mirror_object:
                                self.menu_items.append(mod.mirror_object.name)

            self.menu_items = list(set(self.menu_items))
            self.menu_items = sorted(self.menu_items)

            if self.menu_items:
                return context.window_manager.invoke_popup(self)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        for item in self.menu_items:
            layout.operator("set.mirror_source", text=item).source_name = item

class MIRROR_TARGET_FROM_ACTIVE(bpy.types.Operator):
    """Displays mirror objects from active object"""
    bl_label = "Mirror Target From Active"
    bl_idname = "mirror_target_fromactive.button"

    def execute(self, context):
        # Show a menu to select a modifier
        self.menu_items = []
        if context.active_object is not None:
            self.menu_items = []
            for mod in bpy.context.active_object.modifiers:
                if mod.type == "MIRROR":
                    if mod.mirror_object:
                        self.menu_items.append(mod.mirror_object.name)

            self.menu_items = list(set(self.menu_items))
            self.menu_items = sorted(self.menu_items)

            if self.menu_items:
                return context.window_manager.invoke_popup(self)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        for item in self.menu_items:
            layout.operator("set.mirror_target", text=item).target_name = item

class MIRROR_TARGET_FROM_LIST(bpy.types.Operator):
    """Displays mirror objects from the entire scene"""
    bl_label = "Mirror Target From List"
    bl_idname = "mirror_target_fromlist.button"

    def execute(self, context):
        # Show a menu to select a modifier
        self.menu_items = []
        objects = bpy.context.scene.objects
        if objects:
            for ob in objects:
                modifiers = ob.modifiers
                if modifiers:
                    for mod in ob.modifiers:
                        if mod.type == "MIRROR":
                            if mod.mirror_object:
                                self.menu_items.append(mod.mirror_object.name)

            self.menu_items = list(set(self.menu_items))
            self.menu_items = sorted(self.menu_items)

            if self.menu_items:
                return context.window_manager.invoke_popup(self)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        for item in self.menu_items:
            layout.operator("set.mirror_target", text=item).target_name = item

class ACTIVE_NAME(bpy.types.Operator):
    """Pastes active objects' name into the target field"""
    bl_label = "Active Name"
    bl_idname = "active_name.button"

    def execute(self, context):
        if context.active_object is not None:
            context.scene.mirror_target = context.active_object.name
            return {'FINISHED'}

class SET_SOURCE_NAME(bpy.types.Operator):
    """Name of the source mirror object, those mirror objects will be swapped for the target mirror object"""
    bl_label = "Set Source Name"
    bl_idname = "set.mirror_source"
    source_name: bpy.props.StringProperty()

    def invoke(self, context, event):
        context.scene.mirror_source = self.source_name
        bpy.context.area.tag_redraw()
        close_panel(event) 
        return {'FINISHED'}

class SET_TARGET_NAME(bpy.types.Operator):
    """Name of the target mirror object, this name will be used to replace source mirror objects"""
    bl_label = "Set Target Name"
    bl_idname = "set.mirror_target"
    target_name: bpy.props.StringProperty()

    def invoke(self, context, event):
        context.scene.mirror_target = self.target_name
        bpy.context.area.tag_redraw()
        close_panel(event) 
        return {'FINISHED'}


class CleanUpPanel(bpy.types.Panel):
    bl_label = "Clean Up"
    bl_idname = "OBJECT_PT_clean_up_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'       
    bl_category = "Smart Select"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        # DUPLICATES
        box = layout.box()
        box.label(text="Duplicates:")
        row = box.row(align=True)
        row.operator("selectduplicates.button", text="Select")
        row = box.row(align=True)
        row.label(text="Decimal Rounding:")
        duplicates_slider = context.scene.duplicates_slider
        row.prop(context.scene, "duplicates_slider", text="", emboss=True)

        # EMPTY MATERIAL SLOTS
        box = layout.box()
        box.label(text="Empty Material Slots:")
        row = box.row(align=True)
        row.operator("selectemptymaterial.button", text="Select")
        row = box.row(align=True)
        row.operator("removeemptymaterial.button", text="Remove Selection")

        # EMPTY MESHES AND MAYA NORMALS
        box = layout.box()
        row = box.row(align=True)
        row.label(text="Empty Meshes:")
        row.operator("selectemptymeshes.button", text="Select")
        row = box.row(align=True)
        row.label(text="Maya Normals:")
        row.operator("cleanmayanormals.button", text="Clean")

class SELECT_DUPLICATES(bpy.types.Operator):
    """Selects potential duplicates in the scene.\nDecimal rounding determines rounding of Loc, Rot and Sca"""
    bl_label = "Select Duplicates"
    bl_idname = "selectduplicates.button"

    def execute(self, context):
        # Load and run script
        script_file = os.path.join(addon_dir, "Select Duplicates.py")
        with open(script_file) as f:
            code = compile(f.read(), script_file, 'exec')
            exec(code, globals())
        return {'FINISHED'}

class SELECT_EMPTY_MATERIAL(bpy.types.Operator):
    """Selects objects that have empty material slots.\n That occurs when a material is deleted in the Blender File window"""
    bl_label = "Select Empty Material"
    bl_idname = "selectemptymaterial.button"

    def execute(self, context):
        # Load and run script
        script_file = os.path.join(addon_dir, "Select Empty Material.py")
        with open(script_file) as f:
            code = compile(f.read(), script_file, 'exec')
            exec(code, globals())
        return {'FINISHED'}

class REMOVE_EMPTY_MATERIAL(bpy.types.Operator):
    """Removes empty material slots from selection.\n That occurs when a material is deleted in the Blender File window"""
    bl_label = "Remove Empty Material"
    bl_idname = "removeemptymaterial.button"

    def execute(self, context):
        # Load and run script
        script_file = os.path.join(addon_dir, "Remove Empty Material.py")
        with open(script_file) as f:
            code = compile(f.read(), script_file, 'exec')
            exec(code, globals())
        return {'FINISHED'}

class SELECT_EMPTY_MESHES(bpy.types.Operator):
    """Selects MESHES that have no vertices"""
    bl_label = "Select by Empty Meshes"
    bl_idname = "selectemptymeshes.button"

    def execute(self, context):
        # Load and run script
        script_file = os.path.join(addon_dir, "Select Empty Meshes.py")
        with open(script_file) as f:
            code = compile(f.read(), script_file, 'exec')
            exec(code, globals())
        return {'FINISHED'}

class CLEAN_MAYA_NORMALS(bpy.types.Operator):
    """Resets Normals of objects modelled in Maya.\nNot doing that will cause artifacting and incompatibility with some softwares such as Substance Painter"""
    bl_label = "Clean Maya Normals"
    bl_idname = "cleanmayanormals.button"

    def execute(self, context):
        # Load and run script
        script_file = os.path.join(addon_dir, "Clean Maya Normals.py")
        with open(script_file) as f:
            code = compile(f.read(), script_file, 'exec')
            exec(code, globals())
        return {'FINISHED'}


class OrganiseMayaPanel(bpy.types.Panel):
    bl_label = "Maya Export"
    bl_idname = "OBJECT_PT_organise_for_maya"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'       
    bl_category = "Smart Select"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        # ORGANISE FOR MAYA
        box = layout.box()
        box.label(text="Organise for Maya:")
        row = box.row(align=True)
        row.operator("saveas.button", text="[SAVE COPY BEFORE]", emboss=False)
        row = box.row(align=True)
        row.operator("organise_for_maya.custom_confirm_dialog")
        row = box.row(align=True)
        row.operator("console_toggle.button", text="Console Toggle")

        box = layout.box()
        row = box.row(align=True)
        row.prop(context.scene, "disable_last_subd_toggle", text=' Disable Last SubD', toggle=False)
        row = box.row(align=True)
        row.prop(context.scene, "disable_all_subd_toggle", text=' Disable All SubD', toggle=False)
        row = box.row(align=True)
        row.prop(context.scene, "apply_all_subd_toggle", text=' Apply All SubD', toggle=False)

        box = layout.box()
        row = box.row(align=True)
        row.prop(context.scene, "export_mirror_split_toggle", text=' Mirror Split', toggle=False)
        row = box.row(align=True)
        row.prop(context.scene, "export_mirror_recenter_toggle", text=' Mirror Recenter', toggle=False)
        row.enabled = context.scene.export_mirror_split_toggle

        box = layout.box()
        row = box.row(align=True)
        row.prop(context.scene, "multires_toggle", text=' Disable Multires', toggle=False)
        row = box.row(align=True)
        row.prop(context.scene, "merge_collection_toggle", text=' Merge Collections', toggle=False)

class CONSOLE_TOGGLE(bpy.types.Operator):
    """Toggle Console to see step by step progress.\nTo verify that the script isn't frozen"""
    bl_label = "Console Toggle"
    bl_idname = "console_toggle.button"

    def execute(self, context):
        bpy.ops.wm.console_toggle()
        return {'FINISHED'}

class UpdateAntiDisableLastToggle(bpy.types.Operator):
    bl_idname = "object.updateantidisablelasttoggle"
    bl_label = "Update Anti Disable Last Toggle"

    def execute(self, context):
        if context.scene.disable_last_subd_toggle:
            context.scene.disable_all_subd_toggle = False
            context.scene.apply_all_subd_toggle = False


        return {'FINISHED'}

class UpdateAntiDisableAllToggle(bpy.types.Operator):
    bl_idname = "object.updateantidisablealltoggle"
    bl_label = "Update Anti Disable All Toggle"

    def execute(self, context):
        if context.scene.disable_all_subd_toggle:
            context.scene.disable_last_subd_toggle = False
            context.scene.apply_all_subd_toggle = False

        return {'FINISHED'}

class UpdateAntiApplyAllToggle(bpy.types.Operator):
    bl_idname = "object.updateantiapplyalltoggle"
    bl_label = "Update Anti Apply All Toggle"

    def execute(self, context):
        if context.scene.apply_all_subd_toggle:
            context.scene.disable_all_subd_toggle = False
            context.scene.disable_last_subd_toggle = False


        return {'FINISHED'}

class UpdateExportRecenterToggle(bpy.types.Operator):
    bl_idname = "object.update_export_recenter_toggle"
    bl_label = "Update Export Recenter Toggle"

    def execute(self, context):
        if not context.scene.mirror_split_toggle:
            context.scene.export_mirror_recenter_toggle = False
        return {'FINISHED'}

class SAVE_AS(bpy.types.Operator):
    """Save As"""
    bl_label = "Save As"
    bl_idname = "saveas.button"

    def execute(self, context):
        return {'FINISHED'}

class ORGANISE_FOR_MAYA(bpy.types.Operator):
    """MIGHT RUN A LONG TIME IF SCENE IS BIG.\nMIGHT SEEM FROZEN, BUT ITS NOT\nVIEW STEPS IN CONSOLE\n\nReorganises the entire scene to be exportable to Maya.\nObjects will be organasied to ToBeSubdivided and Other.\nParent links will be replaced by collection parenting.\nHidden elements will be deleted.\nScript Accounts for:\nMESH/CURVE/LATTICE/EMPTY/Instances/Modifiers"""
    bl_idname = "organise_for_maya.custom_confirm_dialog"
    bl_label = "Organise"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        script_file = os.path.join(addon_dir, "Organise for Maya.py")
        with open(script_file) as f:
            code = compile(f.read(), script_file, 'exec')
            exec(code, globals())
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
def register():
    bpy.utils.register_class(ModifierPanel)
    bpy.utils.register_class(UpdateMirrorRecenterToggle)
    bpy.utils.register_class(MODIFIER_MODE)
    bpy.utils.register_class(FROM_ACTIVE)
    bpy.utils.register_class(FROM_LIST)
    bpy.utils.register_class(SET_MODIFIER_NAME)
    bpy.utils.register_class(REFRESH_MODIFIER_NAME)
    bpy.utils.register_class(MODIFIER_SELECT)
    bpy.utils.register_class(MODIFIER_APPLY)
    bpy.utils.register_class(MODIFIER_REMOVE)
    bpy.utils.register_class(MODIFIER_STACK_ON)
    bpy.utils.register_class(MODIFIER_STACK_OFF)
    bpy.types.Scene.modifier_mode = bpy.props.EnumProperty(name="Modifier Mode", items=[("Mode: Type", "", "", 0),("Mode: Name", "", "", 1),("Mode: GeoNode", "", "", 2),], default="Mode: Type")
    bpy.types.Scene.modifier_name = bpy.props.StringProperty(name="Modifier String", default="")
    bpy.types.Scene.stack_order_toggle = bpy.props.BoolProperty(name="stack_order_toggle", description="Filter out if modifier NOT first in order.\nNon-destructive flow")
    bpy.types.Scene.curve_toggle = bpy.props.BoolProperty(name="curve_toggle", description="Filter out curves")
    bpy.types.Scene.mirror_split_toggle = bpy.props.BoolProperty(name="Mirror Split", description="Separate by LOOSE PARTS if applying mirrors", update=UpdateMirrorRecenterToggle.execute)
    bpy.types.Scene.mirror_recenter_toggle = bpy.props.BoolProperty(name="Mirror Recenter", description="If Separating by LOOSE PARTS, recenter origins to GEOMERY")

    bpy.utils.register_class(GeneralPanel)
    bpy.utils.register_class(REFRESH_MIRROR_NAME)
    bpy.utils.register_class(SELECT_NEXT)
    bpy.utils.register_class(SELECT_BY_OBJECT_DATA)
    bpy.utils.register_class(SELECT_SCALE_NOT_UNIFORM)
    bpy.utils.register_class(SELECT_SCALE_NOT_ONE)
    bpy.utils.register_class(MIRROR_REWIRE)
    bpy.utils.register_class(MIRROR_SOURCE_FROM_ACTIVE)
    bpy.utils.register_class(MIRROR_SOURCE_FROM_LIST)
    bpy.utils.register_class(MIRROR_TARGET_FROM_ACTIVE)
    bpy.utils.register_class(MIRROR_TARGET_FROM_LIST)
    bpy.utils.register_class(ACTIVE_NAME)
    bpy.utils.register_class(SET_SOURCE_NAME)
    bpy.utils.register_class(SET_TARGET_NAME)
    bpy.types.Scene.mirror_source = bpy.props.StringProperty(name="Source Name", default="")
    bpy.types.Scene.mirror_target = bpy.props.StringProperty(name="Target Name", default="")
    bpy.types.Scene.location_toggle = bpy.props.BoolProperty(name="location_toggle", description="If ENABLED will take into account Location")
    bpy.types.Scene.dimensions_toggle = bpy.props.BoolProperty(name="dimensions_toggle", description="If ENABLED will take into account Dimensions")
    bpy.types.Scene.rotation_toggle = bpy.props.BoolProperty(name="rotation_toggle", description="If ENABLED will take into account Rotation")
    bpy.types.Scene.scale_toggle = bpy.props.BoolProperty(name="scale_toggle", description="If ENABLED will take into account Scale")
    bpy.types.Scene.transform_slider = bpy.props.IntProperty(name="-5 -> 100000\n-4 -> 10000\n-3 -> 1000\n-2 -> 100\n-1 -> 10\n 0 -> 0\n 1 -> 0.0\n 2 -> 0.00\n 3 -> 0.000\n 4 -> 0.0000\n 5 -> 0.00000", default=-5, min=-5, max=5)
    bpy.types.Scene.mirror_selection_toggle = bpy.props.BoolProperty(name="mirror_selection_toggle", description="If ENABLED will only rewire selected objects")

    bpy.utils.register_class(CleanUpPanel)
    bpy.utils.register_class(CLEAN_MAYA_NORMALS)
    bpy.utils.register_class(SELECT_DUPLICATES)
    bpy.utils.register_class(SELECT_EMPTY_MESHES)
    bpy.utils.register_class(SELECT_EMPTY_MATERIAL)
    bpy.utils.register_class(REMOVE_EMPTY_MATERIAL)
    bpy.types.Scene.duplicates_slider = bpy.props.IntProperty(name="-5 -> 100000\n-4 -> 10000\n-3 -> 1000\n-2 -> 100\n-1 -> 10\n 0 -> 0\n 1 -> 0.0\n 2 -> 0.00\n 3 -> 0.000\n 4 -> 0.0000\n 5 -> 0.00000", default=5, min=-5, max=5)

    bpy.utils.register_class(OrganiseMayaPanel)
    bpy.utils.register_class(CONSOLE_TOGGLE)
    bpy.utils.register_class(UpdateAntiDisableLastToggle)
    bpy.utils.register_class(UpdateAntiDisableAllToggle)
    bpy.utils.register_class(UpdateAntiApplyAllToggle)
    bpy.utils.register_class(UpdateExportRecenterToggle)
    bpy.utils.register_class(SAVE_AS)
    bpy.utils.register_class(ORGANISE_FOR_MAYA)
    bpy.types.Scene.disable_last_subd_toggle = bpy.props.BoolProperty(name="disable_last_subd_toggle", description="Will apply all subdivisions except the last", update=UpdateAntiDisableLastToggle.execute, default=True)
    bpy.types.Scene.disable_all_subd_toggle = bpy.props.BoolProperty(name="disable_all_subd_toggle", description="Will Disable all subdivisions", update=UpdateAntiDisableAllToggle.execute)
    bpy.types.Scene.apply_all_subd_toggle = bpy.props.BoolProperty(name="apply_all_subd_toggle", description="Will apply all subdivisions", update=UpdateAntiApplyAllToggle.execute)
    bpy.types.Scene.export_mirror_split_toggle = bpy.props.BoolProperty(name="export_mirror_split_toggle", description="Separate by LOOSE PARTS when applying mirrors.\nConsiderablly slows the script down", update=UpdateExportRecenterToggle.execute)
    bpy.types.Scene.export_mirror_recenter_toggle = bpy.props.BoolProperty(name="export_mirror_recenter_toggle", description="If Separating by LOOSE PARTS, recenter origins to GEOMERY.\nConsiderablly slows the script down")
    bpy.types.Scene.merge_collection_toggle = bpy.props.BoolProperty(name="merge_collection_toggle", description="If ENABLED Will merge all collections into one.\nIf DISABLED, will respect existing collections", default=True)
    bpy.types.Scene.multires_toggle = bpy.props.BoolProperty(name="multires_toggle", description="If ENABLED will disable multiresolution modifiers, instead of applying", default=True)

def unregister():
    bpy.utils.unregister_class(ModifierPanel)
    bpy.utils.unregister_class(UpdateMirrorRecenterToggle)
    bpy.utils.unregister_class(MODIFIER_MODE)
    bpy.utils.unregister_class(FROM_ACTIVE)
    bpy.utils.unregister_class(FROM_LIST)
    bpy.utils.unregister_class(SET_MODIFIER_NAME)
    bpy.utils.unregister_class(REFRESH_MODIFIER_NAME)
    bpy.utils.unregister_class(MODIFIER_SELECT)
    bpy.utils.unregister_class(MODIFIER_APPLY)
    bpy.utils.unregister_class(MODIFIER_REMOVE)
    bpy.utils.unregister_class(MODIFIER_STACK_ON)
    bpy.utils.unregister_class(MODIFIER_STACK_OFF)
    del bpy.types.Scene.modifier_mode
    del bpy.types.Scene.modifier_name
    del bpy.types.Scene.stack_order_toggle
    del bpy.types.Scene.curve_toggle
    del bpy.types.Scene.mirror_split_toggle
    del bpy.types.Scene.mirror_recenter_toggle

    bpy.utils.unregister_class(GeneralPanel)
    bpy.utils.unregister_class(REFRESH_MIRROR_NAME)
    bpy.utils.unregister_class(SELECT_NEXT)
    bpy.utils.unregister_class(SELECT_BY_OBJECT_DATA)
    bpy.utils.unregister_class(SELECT_SCALE_NOT_UNIFORM)
    bpy.utils.unregister_class(SELECT_SCALE_NOT_ONE)
    bpy.utils.unregister_class(MIRROR_REWIRE)
    bpy.utils.unregister_class(MIRROR_SOURCE_FROM_ACTIVE)
    bpy.utils.unregister_class(MIRROR_SOURCE_FROM_LIST)
    bpy.utils.unregister_class(MIRROR_TARGET_FROM_ACTIVE)
    bpy.utils.unregister_class(MIRROR_TARGET_FROM_LIST)
    bpy.utils.unregister_class(ACTIVE_NAME)
    bpy.utils.unregister_class(SET_SOURCE_NAME)
    bpy.utils.unregister_class(SET_TARGET_NAME)
    del bpy.types.Scene.mirror_source
    del bpy.types.Scene.mirror_target
    del bpy.types.Scene.location_toggle
    del bpy.types.Scene.dimensions_toggle
    del bpy.types.Scene.rotation_toggle
    del bpy.types.Scene.scale_toggle
    del bpy.types.Scene.transform_slider
    del bpy.types.Scene.mirror_selection_toggle

    bpy.utils.unregister_class(CleanUpPanel)
    bpy.utils.unregister_class(CLEAN_MAYA_NORMALS)
    bpy.utils.unregister_class(SELECT_DUPLICATES)
    bpy.utils.unregister_class(SELECT_EMPTY_MATERIAL)
    bpy.utils.unregister_class(REMOVE_EMPTY_MATERIAL)
    bpy.utils.unregister_class(SELECT_EMPTY_MESHES)
    del bpy.types.Scene.duplicates_slider

    bpy.utils.unregister_class(OrganiseMayaPanel)
    bpy.utils.unregister_class(CONSOLE_TOGGLE)
    bpy.utils.unregister_class(UpdateAntiDisableLastToggle)
    bpy.utils.unregister_class(UpdateAntiDisableAllToggle)
    bpy.utils.unregister_class(UpdateAntiApplyAllToggle)
    bpy.utils.unregister_class(UpdateExportRecenterToggle)
    bpy.utils.unregister_class(SAVE_AS)
    bpy.utils.unregister_class(ORGANISE_FOR_MAYA)
    del bpy.types.Scene.disable_last_subd_toggle
    del bpy.types.Scene.disable_all_subd_toggle
    del bpy.types.Scene.apply_all_subd_toggle
    del bpy.types.Scene.export_mirror_split_toggle
    del bpy.types.Scene.export_mirror_recenter_toggle
    del bpy.types.Scene.merge_collection_toggle
    del bpy.types.Scene.multires_toggle

if __name__ == "__main__":
    register()