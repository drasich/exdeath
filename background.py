import sys
import os

path = os.path.abspath(__file__)
path = os.path.dirname(path)
sys.path.insert(0, path)

import export

def main():
  argv = sys.argv
  #argv = argv[argv.index("--") + 1:] # get all args after "--"
 
  obj_out = argv[0]
  print("in the main")
  yep = export.backgroundExport()
   
  #bpy.ops.export_stuff.obj(filepath=obj_out, axis_forward='-Z', axis_up='Y')


main()
