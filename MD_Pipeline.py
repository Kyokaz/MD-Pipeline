bl_info = {
    "name": "MD Pipeline",
    "blender": (2, 80, 0),
    "category": "Object",
    "description": "A custom pipeline for setting up, viewing, and exporting collision objects as Alembic files.",
    "author": "Kyokaz",
    "version": (1, 0, 0),
}

import bpy
from bpy.props import BoolProperty

class MDPipelinePanel(bpy.types.Panel):
    bl_label = "MD Pipeline"
    bl_idname = "OBJECT_PT_md_pipeline"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MD Pipeline'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="1. Setup")
        row = layout.row()
        row.operator("md_pipeline.set_collision", icon='MOD_PHYSICS')
        row = layout.row()
        row.operator("md_pipeline.auto_detect", icon='VIEWZOOM')

        layout.separator()

        layout.label(text="2. Tools")
        row = layout.row()
        row.alert = scene.md_pipeline_view_collision_toggle
        row.operator("md_pipeline.view_collision", icon='VIEW_PERSPECTIVE')
        row = layout.row()
        row.operator("md_pipeline.clean_up", icon='TRASH')

        layout.separator()

        layout.label(text="3. Export")
        row = layout.row()
        row.operator("md_pipeline.export_alembic", icon='EXPORT')

class MDPipelineAutoDetect(bpy.types.Operator):
    bl_idname = "md_pipeline.auto_detect"
    bl_label = "Auto Detect"
    
    def execute(self, context):
        collision_objects = [obj for obj in bpy.data.objects if obj.name.endswith("-COL")]
        
        if not collision_objects:
            self.report({'WARNING'}, "No objects with the -COL suffix found.")
            return {'CANCELLED'}
        
        if "Collision Objects" not in bpy.data.collections:
            collision_collection = bpy.data.collections.new("Collision Objects")
            bpy.context.scene.collection.children.link(collision_collection)
        else:
            collision_collection = bpy.data.collections["Collision Objects"]
        
        for obj in collision_objects:
            obj.hide_render = True
            if obj.name not in collision_collection.objects:
                for collection in obj.users_collection:
                    collection.objects.unlink(obj)
                collision_collection.objects.link(obj)

        return {'FINISHED'}

class MDPipelineViewCollision(bpy.types.Operator):
    bl_idname = "md_pipeline.view_collision"
    bl_label = "View Collision Object"
    toggle: BoolProperty(default=False)

    def execute(self, context):
        scene = context.scene
        collision_collection = bpy.data.collections.get("Collision Objects")
        if not collision_collection:
            self.report({'WARNING'}, "Collision Objects collection not found.")
            return {'CANCELLED'}

        self.toggle = not scene.md_pipeline_view_collision_toggle
        scene.md_pipeline_view_collision_toggle = self.toggle
        for layer_collection in bpy.context.view_layer.layer_collection.children:
            if layer_collection.collection.name == "Collision Objects":
                layer_collection.exclude = not self.toggle
            else:
                layer_collection.exclude = self.toggle
        
        return {'FINISHED'}

class MDPipelineExportAlembic(bpy.types.Operator):
    bl_idname = "md_pipeline.export_alembic"
    bl_label = "Export ALEMBIC"
    
    def execute(self, context):
        collision_collection = bpy.data.collections.get("Collision Objects")
        if not collision_collection:
            self.report({'WARNING'}, "Collision Objects collection not found.")
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        for obj in collision_collection.objects:
            obj.select_set(True)

        bpy.ops.wm.alembic_export('INVOKE_DEFAULT', selected=True, evaluation_mode='VIEWPORT')

        return {'FINISHED'}

class MDPipelineSetCollision(bpy.types.Operator):
    bl_idname = "md_pipeline.set_collision"
    bl_label = "Set Collision"
    
    def execute(self, context):
        collision_objects = []
        for obj in bpy.context.selected_objects:
            if not obj.name.endswith("-COL"):
                obj.name = obj.name + "-COL"
            collision_objects.append(obj)

        if "Collision Objects" not in bpy.data.collections:
            collision_collection = bpy.data.collections.new("Collision Objects")
            bpy.context.scene.collection.children.link(collision_collection)
        else:
            collision_collection = bpy.data.collections["Collision Objects"]

        for obj in collision_objects:
            obj.hide_render = True
            if obj.name not in collision_collection.objects:
                for collection in obj.users_collection:
                    collection.objects.unlink(obj)
                collision_collection.objects.link(obj)

        return {'FINISHED'}

class MDPipelineCleanUp(bpy.types.Operator):
    bl_idname = "md_pipeline.clean_up"
    bl_label = "Clean Up"
    
    def execute(self, context):
        collision_objects = [obj for obj in bpy.data.objects if obj.name.endswith("-COL")]
        
        if not collision_objects:
            self.report({'WARNING'}, "No objects with the -COL suffix found.")
            return {'CANCELLED'}
        
        bpy.ops.object.select_all(action='DESELECT')
        for obj in collision_objects:
            obj.select_set(True)
        
        bpy.ops.object.delete()
        
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)

class MDPipelineHideCollision(bpy.types.Operator):
    bl_idname = "md_pipeline.hide_collision"
    bl_label = "Hide Collision"
    
    def execute(self, context):
        collision_collection = bpy.data.collections.get("Collision Objects")
        if not collision_collection:
            self.report({'WARNING'}, "Collision Objects collection not found.")
            return {'CANCELLED'}

        for layer_collection in bpy.context.view_layer.layer_collection.children:
            if layer_collection.collection.name == "Collision Objects":
                layer_collection.exclude = True
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MDPipelinePanel)
    bpy.utils.register_class(MDPipelineAutoDetect)
    bpy.utils.register_class(MDPipelineViewCollision)
    bpy.utils.register_class(MDPipelineExportAlembic)
    bpy.utils.register_class(MDPipelineSetCollision)
    bpy.utils.register_class(MDPipelineCleanUp)
    bpy.utils.register_class(MDPipelineHideCollision)
    bpy.types.Scene.md_pipeline_view_collision_toggle = BoolProperty(
        name="View Collision Toggle",
        description="Toggle the visibility of collision objects",
        default=False
    )

def unregister():
    bpy.utils.unregister_class(MDPipelinePanel)
    bpy.utils.unregister_class(MDPipelineAutoDetect)
    bpy.utils.unregister_class(MDPipelineViewCollision)
    bpy.utils.unregister_class(MDPipelineExportAlembic)
    bpy.utils.unregister_class(MDPipelineSetCollision)
    bpy.utils.unregister_class(MDPipelineCleanUp)
    bpy.utils.unregister_class(MDPipelineHideCollision)
    del bpy.types.Scene.md_pipeline_view_collision_toggle

if __name__ == "__main__":
    register()
