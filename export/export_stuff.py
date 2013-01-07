import bpy
import struct

def start():
  print("will write to test.bin")
  file = open('test.bin', 'bw');
  for o in bpy.data.objects:
    export_object(file, o)
    for a in bpy.data.actions:
      export_action(file, o, a)
  file.close();

def export_action(file, object, action):
  #to get a frame/value couple
  #action.fcurves[1].keyframe_points[0].co
  pr = object.path_resolve
  for fcu in action.fcurves:
    try:
      prop = pr(fcu.data_path, False)
    except:
      prop = None

    if prop is not None:
      print("object " + object.name + " has action " + action.name + " with prop : " + str(prop))
      print("and prop data is : " + str(prop.data))
      print("and prop data name is : " + str(prop.data.name))
    #else:
    #  print("object " + object.name + " has not action " + action.name)
  pass

def export_object(file, object):
  print("object : ", object.name)
  if object.type == 'MESH':
    #TODO get vertex groups with object.vertex_groups
    print("it's a mesh")
    mesh = create_mesh(object.data)
    write_mesh(file, mesh)
    #TODO material
    mat = object.active_material
    if mat:
      write_material(file, mat)
    handle_modifiers(object)
  elif object.type == 'ARMATURE':
    print("it's an armature")
    armature = create_armature(object.data)
    write_armature(file, armature)

  #file.write('This is a test!');

class Armature:
  pass #bones = []

class Bone:
  pass
#  matrix
# children
# name

def create_armature(data):
  armature = Armature()
  armature.bones = []
  armature.name = data.name
  #TODO position and rotation of armature
  for b in data.bones:
    bone = create_bone(b)
    armature.bones.append(bone)
  return armature


def create_bone(bone):
  bo = Bone()
  #bo.test
  bo.name = bone.name
  bo.matrix = bone.matrix_local
  bo.position = bone.matrix_local.to_translation()
  bo.rotation = bone.matrix_local.to_quaternion()
  #print("bone " + bone.name)
  #print("matrix " + str(bone.matrix))
  #print("matrix relative to armature " + str(bone.matrix_local))
  #print("matrix relative to armature to translation " + str(bone.matrix_local.to_translation()))
  #print("matrix head " + str(bone.head))
  #head = position
  # I don't think we need tail? maybe later?
  bo.children = []
  for b in bone.children:
    child = create_bone(b)
    bo.children.append(child)

  return bo

class Mesh:
  vertices = []
  triangles = []
  normals = []
  uvs = [] #TODO multiple uvs

  #TODO texture name
  textures = []
  
  def __init__(self, mesh):
    self.mesh = mesh


def get_triangles_uvs(mesh_data, vv):
  triangles = []
  uvs = []
  uvdata = []

  if len(mesh_data.uv_layers) > 0:
    uvdata = mesh_data.uv_layers[0].data
    uvs = [0,0]* len(vv)

  i = 0
  uvc = 0

  for face in mesh_data.tessfaces:
    vertices = face.vertices
    triangles.append((vertices[0], vertices[1], vertices[2]))
    #print(str(i) + " append this " + str(vertices[0]) + str(vertices[1]) +str(vertices[2]))
    if uvdata:
      print(" with uv " + str(uvdata[uvc].uv) + str(uvdata[uvc+1].uv) +str(uvdata[uvc+2].uv))
      uvs[vertices[0]] = uvdata[uvc].uv
      uvs[vertices[1]] = uvdata[uvc+1].uv
      uvs[vertices[2]] = uvdata[uvc+2].uv
    i +=1
    uvc+=3

    # It's a quad we need one more triangle.
    if len(vertices) == 4:
      triangles.append((vertices[0], vertices[2], vertices[3]))
      #print(str(i) + " append this4  " + str(vertices[0]) + str(vertices[2]) +str(vertices[3]))
      if uvdata:
        uvs[vertices[3]] = uvdata[uvc].uv
      i +=1
      uvc+=1

  return triangles, uvs
      
def get_vertices(mesh_data):
  vertices = []
  for v in mesh_data.vertices:
    vertices.append(v.co)
    #TODO weight and groups
    #for g in v.groups:

      #print(" vert group  " + str(g.group))
      #print(" vert weight  " + str(g.weight))

  return vertices

def get_normals(mesh_data):
  normals = []
  for v in mesh_data.vertices:
    normals.append(v.normal)
    #print("normal  " + str(v.normal))
  return normals

def create_mesh(mesh_data):
  #TODO position and rotation of mesh or object
  mesh_data.update(calc_tessface=True)
  mesh = Mesh(mesh_data)
  mesh.name = mesh_data.name
  mesh.vertices = get_vertices(mesh_data)
  mesh.triangles, mesh.uvs = get_triangles_uvs(mesh_data, mesh.vertices)
  mesh.normals = get_normals(mesh_data)

  return mesh

def write_type(file, str):
  write_string(file, str)

def write_string(file, str):
  s = str.encode('latin1')
  file.write(struct.pack("H%ds" % len(s), len(s), s))

def write_mesh(file, mesh):
  #print("mesh : " + str(mesh))
  write_type(file, "mesh")
  write_string(file, mesh.name)

  file.write(struct.pack('H', len(mesh.vertices)))
  for v in mesh.vertices:
    file.write(struct.pack('fff', v[0], v[1], v[2]))

  file.write(struct.pack('H', len(mesh.triangles)))
  for t in mesh.triangles:
    file.write(struct.pack('HHH', t[0], t[1], t[2]))

  file.write(struct.pack('H', len(mesh.vertices)))
  for n in mesh.normals:
    file.write(struct.pack('fff', n[0], n[1], n[2])) 

  file.write(struct.pack('H', len(mesh.uvs)))
  for uv in mesh.uvs:
    file.write(struct.pack('ff', uv[0], uv[1])) 
  
def write_material(file, mat):
  #file.write(struct.pack('H', len(mesh.vertices)))
  at =  mat.active_texture
  #print("texture : " + str(at))
  #print("scale : " + str(mat.texture_slots[0].scale))
  if bpy.data.textures[at.name].type == 'IMAGE':
    print("texture filepath : " + bpy.data.textures[at.name].image.filepath)
    
def handle_modifiers(o):
  for m in o.modifiers:
    if m.type == 'ARMATURE':
      print("there is an armature")
      armature = m.object
      print("armature name is " + armature.name)


def write_armature(file, armature):
  #return
  write_type(file, "armature")
  write_string(file, armature.name)
  file.write(struct.pack('H', len(armature.bones)))
  for bone in armature.bones:
    write_bone(file, bone)


def write_bone(file, bone):
  write_string(file, bone.name)
  v = bone.position
  file.write(struct.pack('fff', v[0], v[1], v[2]))
  v = bone.rotation
  file.write(struct.pack('ffff', v[0], v[1], v[2], v[3]))
  file.write(struct.pack('H', len(bone.children)))
  for c in bone.children:
    write_bone(file, c)



