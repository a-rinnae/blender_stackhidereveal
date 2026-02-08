import bpy

bl_info = {
    "name": "Stack Hide/Reveal",
    "version": (1, 0),
    "blender": (4, 4, 0),
    "description": """(OBJECT MODE ONLY) 
    Hide objects as usual with H. Pressing Alt-H will reveal only the most recently hidden objects, stepping 
    back through what was hidden. If there is no previous hide history available, for example, after a Blender restart, 
    Alt-H will default back to revealing all hidden objects."""
}

_hide_stack = []

class stack_hide(bpy.types.Operator):
    bl_idname = "object.stack_hide"
    bl_label = "Stack Hide"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        to_hide = [obj for obj in context.selected_objects if not obj.hide_get()]
        
        if not to_hide:
            return {'CANCELLED'}

        _hide_stack.append(to_hide)

        for obj in to_hide:
            obj.hide_set(True)
            obj.select_set(False)
            
        self.report({'INFO'}, f"Hid {len(to_hide)} objects")
        return {'FINISHED'}
    

class stack_reveal(bpy.types.Operator):
    bl_idname = "object.stack_reveal"
    bl_label = "Stack Reveal"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        if not _hide_stack:
            self.report({'INFO'}, "Revealing all hidden objects")
            bpy.ops.object.hide_view_clear()
            return {'FINISHED'}
        
        num_objects_to_reveal = len(_hide_stack[-1])
        deleted_count = 0
        objects_to_reveal = _hide_stack.pop()
        
        for obj in objects_to_reveal:
            try:
                obj.hide_set(False)
                obj.select_set(True)
            except ReferenceError:
                deleted_count += 1
                continue
            
        if deleted_count > 0:
            self.report({'WARNING'}, "Attempted to reveal an object that was either revealed by undo (Ctrl-Z) or deleted, skipping...")
        else:
            self.report({'INFO'}, f"Revealed {num_objects_to_reveal} objects")
        return {'FINISHED'}

addon_keymaps = []

def register():
    bpy.utils.register_class(stack_hide)
    bpy.utils.register_class(stack_reveal)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')

        kmi_hide = km.keymap_items.new("object.stack_hide", 'H', 'PRESS')
        addon_keymaps.append((km, kmi_hide))
        
        kmi_unhide = km.keymap_items.new("object.stack_reveal", 'H', 'PRESS', alt=True)
        addon_keymaps.append((km, kmi_unhide))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(stack_hide)
    bpy.utils.unregister_class(stack_reveal)

if __name__ == "__main__":
    register()
