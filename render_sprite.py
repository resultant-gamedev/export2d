bl_info = {"name": "Render Spritesheet", "category": "Render"}

import bpy
import os
import addon_utils


class RenderSpritesheetOperator(bpy.types.Operator):
    bl_idname = "render.render_sprite"
    bl_label = "Render Spritesheet"
    
    def _cleanup(self,path):
        files = [ f for f in os.listdir(path) if f.endswith(".png") ]
        for f in files:
            if f[0:4] == '_tmp':
                os.remove(path+"/"+f)
        return
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        
        #print("Running 2D sprite exporter...")
        #self._cleanup()
        
        c = 0
        
        rot_obj = bpy.data.objects.get(context.scene.rotation_object)
        if not rot_obj: rot_obj = bpy.context.active_object
        old_rot = rot_obj.rotation_euler
        
        sprite_path = os.path.expanduser(context.scene.sprite_path)
        sprite_name = context.scene.sprite_name
        sprite_colors = context.scene.sprite_colors
        
        tools_path = context.scene.sprite_tools_path
        
        num_frames = context.scene.number_frames
        num_directions = context.scene.number_directions
        res_x = context.scene.sprite_x
        res_y = context.scene.sprite_y
        
        bpy.context.scene.render.resolution_x = res_x
        bpy.context.scene.render.resolution_y = res_y
        bpy.context.scene.render.resolution_percentage = 100.0
        
        for i in range(0,num_directions):
            for f in range(0,num_frames):
                bpy.context.scene.frame_current = f
                bpy.context.scene.render.filepath = sprite_path+"/_tmp-000-%03d.png" % (c)
                bpy.ops.render.render(write_still=True)
                c += 1
            rot_obj.rotation_euler[2] += -3.1415*2 / num_directions
        
        rot_obj.rotation_euler = old_rot
        
        try: os.mkdir(sprite_path)
        except: pass
        os.chdir(sprite_path)
        
        #cmd = '"'+tools_path+'/montage" _tmp-000*.png -background transparent -geometry +0+0 -resize '+str(res_x)+'x'+str(res_y)+' -tile '+str(num_frames)+'x'+str(num_directions)+' '+sprite_name+'.png'
        cmd = 'montage _tmp-000*.png -background transparent -geometry +0+0 -resize '+str(res_x)+'x'+str(res_y)+' -tile '+str(num_frames)+'x'+str(num_directions)+' '+sprite_name+'.png'
        print(cmd)
        r = os.system(cmd)
        
        if sprite_colors != 0:
            os.system('"'+tools_path+'/pngnqi" -vf -e -indexed.png -g 2.2 -s 1 -Q n -n '+str(sprite_colors)+' '+sprite_name+'.png')
            
            os.system('"'+tools_path+'/pngout" /y /ktEXt '+sprite_name+'-indexed.png '+sprite_name+'-indexed.png')
            
            os.remove(sprite_name+'.png')
            os.rename(sprite_name+'-indexed.png', sprite_name+'.png')

        #os.startfile(sprite_path)
        
        self._cleanup(sprite_path)
        return {'FINISHED'}


class RenderSpritePanel(bpy.types.Panel):
    bl_label = "Render Spritesheet"
    bl_idname = "RENDER_SPRITESHEET"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    
    def draw(self, context):
        row = self.layout.row()
        #col = row.column()
        row.prop(bpy.context.scene, "rotation_object")

        row = self.layout.row()
        row.prop(bpy.context.scene, "number_directions")
        row.prop(bpy.context.scene, "number_frames")

        row = self.layout.row()
        row.prop(bpy.context.scene, "sprite_path")

        row = self.layout.row()
        row.prop(bpy.context.scene, "sprite_name")
        
        row = self.layout.row()
        row.prop(bpy.context.scene, "sprite_x")
        row.prop(bpy.context.scene, "sprite_y")
        row.prop(bpy.context.scene, "sprite_colors")
        
        row = self.layout.row()
        row.prop(bpy.context.scene, "sprite_tools_path")
        
        row = self.layout.row()
        row.operator("render.render_sprite")


def register():
    bpy.types.Scene.rotation_object = bpy.props.StringProperty(name="Rot. Object", default="None")
    bpy.types.Scene.number_directions = bpy.props.IntProperty(name="Num. Directions", default=8)
    bpy.types.Scene.number_frames = bpy.props.IntProperty(name="Num. Frames", default=8)
    bpy.types.Scene.sprite_x = bpy.props.IntProperty(name="Width", default=128)
    bpy.types.Scene.sprite_y = bpy.props.IntProperty(name="Height", default=128)
    bpy.types.Scene.sprite_path = bpy.props.StringProperty(name="Sprite Path:", default="~")
    bpy.types.Scene.sprite_name = bpy.props.StringProperty(name="Sprite Name:", default="sprite")
    bpy.types.Scene.sprite_tools_path = bpy.props.StringProperty(name="Tools Path:", default=addon_utils.paths()[1] + "/")
    bpy.types.Scene.sprite_colors = bpy.props.IntProperty(name="Colors", default=0)
    bpy.utils.register_class(RenderSpritesheetOperator)
    bpy.utils.register_class(RenderSpritePanel)


def unregister():
    bpy.utils.unregister_class(RenderSpritePanel)
    bpy.utils.unregister_class(RenderSpritesheetOperator)
    
if __name__ == "__main__":
    register()

