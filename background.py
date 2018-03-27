import sys
import os

path = os.path.abspath(__file__)
path = os.path.dirname(path)
sys.path.insert(0, path)

import export

def main():
  argv = sys.argv
  obj_out = argv[0]

  directory = ""
  if "--" in argv:
    argv = argv[argv.index("--") + 1:] # get all args after "--"
    directory = argv[0]

  print(*argv, sep='\n')

  print("in the main")
  yep = export.backgroundExport(directory)
   
  #bpy.ops.export_stuff.obj(filepath=obj_out, axis_forward='-Z', axis_up='Y')


main()
