bl_info = {
    "name":         "export stuff",
    "author":       "chris",
    "blender":      (2,6,2),
    "version":      (0,0,1),
    "location":     "File > Import-Export",
    "description":  "script that export stuff",
    "category":     "Import-Export"
}
        
import bpy
from bpy_extras.io_utils import ExportHelper
from . import export_stuff

if "bpy" in locals():
  from imp import reload
  if "export_stuff" in locals():
    reload(export_stuff)

class ExportStuff(bpy.types.Operator, ExportHelper):
    bl_idname       = "export_stuff.stf";
    bl_label        = "export stuff";
    bl_options      = {'PRESET'};
    
    filename_ext    = ".stf";
    
    def execute(self, context):
        export_stuff.start()
        return {'FINISHED'};

def menu_func(self, context):
    self.layout.operator(ExportStuff.bl_idname, text="Stuff(.stf)");

def register():
    bpy.utils.register_module(__name__);
    bpy.types.INFO_MT_file_export.append(menu_func);
    
def unregister():
    bpy.utils.unregister_module(__name__);
    bpy.types.INFO_MT_file_export.remove(menu_func);

if __name__ == "__main__":
    register()

def backgroundExport(directory):
  export_stuff.start(directory)
