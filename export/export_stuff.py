import bpy
import struct

objects_to_write = []

def start():
  for o in bpy.data.objects:
    export_object(o)
    for a in bpy.data.actions:
      export_action(o, a)

  print("will write to test.bin")
  file = open('test.bin', 'bw');
  file.write(struct.pack('H', len(objects_to_write)))
  for o in objects_to_write:
    o.write(file)
  file.close();

class Action:
  def __init__(self, name):
    self.name = name
    self.curves = []

  def addCurve(self, c):
    self.curves.append(c)
    pass

class Curve:
  def __init__(self, bone, t):
    self.name = bone
    self.type = t
    self.frames = []

  def addFrame(self, frame, value):
    self.frames.append((frame, value))
    pass


from bpy.types import PoseBone
def export_action(object, action):
  a = Action(action.name)
  a.frame_range = action.frame_range
  #print("action name " + action.name)
  #print("action frame range " + str(action.frame_range))
  #to get a frame/value couple
  #action.fcurves[1].keyframe_points[0].co

  actions = []
  pr = object.path_resolve
  for fcu in action.fcurves:
    try:
      #print("curve data path : " + fcu.data_path)
      #print("Object rotation mode : " + object.rotation_mode)
      prop = pr(fcu.data_path, False)
    except:
      prop = None

    if prop is not None:
      print("object " + object.name + " has action " + action.name + " with prop : " + str(prop))
      #print("dir prop : " + str(dir(prop.data)))
      #print("and prop data is : " + str(prop.data))
      #print("and prop data name is : " + str(prop.data.name))
      #print("and prop type is : " + str(type(prop)))


      if isinstance(prop.data, PoseBone):
        #print("bone associated : " + str(prop.data.bone))
        #print("bone associated name : " + str(prop.data.bone.name))
        #print("bone rotmode : " + str(prop.data.rotation_mode))
        #print("bone group : " + str(prop.data.bone_group))
        #print("posebone basename  : " + str(prop.data.basename))

        t = ""

        if fcu.data_path.endswith("scale"):
          t = "scale"
        elif fcu.data_path.endswith("rotation_quaternion"):
          t ="quaternion"
        elif fcu.data_path.endswith("rotation_euler"):
          print("it's euler angles but how do we know the angles order?")
          t = "euler"
        elif fcu.data_path.endswith("location"):
          t="position"

        curve = Curve(prop.data.bone.name, t)
        for frame in fcu.keyframe_points:
          curve.frames.append(frame.co)
          print("couple : " + str(frame.co))

        #j'ai besoin de :
        # bone name
        # savoir ce que c'est genre position rotation x, y z w
        #
    #else:
    #  print("object " + object.name + " has not action " + action.name)
  pass

def export_object(object):
  print("object : ", object.name)
  if object.type == 'MESH':
    print("it's a mesh")
    mesh = create_mesh(object.data)
    objects_to_write.append(mesh)
    mesh.groups = []
    #TODO get vertex groups with object.vertex_groups
    for vg in object.vertex_groups:
      g = (vg.index, vg.name)
      mesh.groups.append(g)
      print("vg index : " + str(vg.index))
      print("vg name : " + str(vg.name))
      try:
        print("vg weight of vertex 0 : " + str(vg.weight(0)))
      except:
        print("vertex 0 is not in this group")

    #TODO material
    mat = object.active_material
    if mat:
      write_material(mat)
    handle_modifiers(object)
  elif object.type == 'ARMATURE':
    print("it's an armature")
    armature = create_armature(object.data)
    objects_to_write.append(armature)

class Armature:
  pass #bones = []

  def write(armature, file):
    #return
    write_type(file, "armature")
    write_string(file, armature.name)
    file.write(struct.pack('H', len(armature.bones)))
    for bone in armature.bones:
      write_bone(file, bone)


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

  def write(mesh, file):
    #print("mesh : " + str(mesh))
    write_type(file, "mesh")
    write_string(file, mesh.name)
  
    file.write(struct.pack('H', len(mesh.vertices)))
    for v in mesh.vertices:
      file.write(struct.pack('fff', v[0], v[1], v[2]))
  
    file.write(struct.pack('H', len(mesh.triangles)))
    for t in mesh.triangles:
      file.write(struct.pack('HHH', t[0], t[1], t[2]))
  
    file.write(struct.pack('H', len(mesh.normals)))
    for n in mesh.normals:
      file.write(struct.pack('fff', n[0], n[1], n[2])) 
  
    file.write(struct.pack('H', len(mesh.uvs)))
    for uv in mesh.uvs:
      file.write(struct.pack('ff', uv[0], uv[1])) 

    # TODO write vertex groups
    # number of groups
    file.write(struct.pack('H', len(mesh.groups)))
    for g in mesh.groups:
      # name
      # index
      write_string(file, g[1])
      file.write(struct.pack('H', g[0]))

    #TODO write vertex weights
    # number of vertex
    file.write(struct.pack('H', len(mesh.weights)))
    for w in mesh.weights:
      # index
      # weight
      file.write(struct.pack('H', w[0]))
      file.write(struct.pack('f', w[1]))
      #print("write weight : " + str(w[0]) + " with weight : " +str(w[1]))
  

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
  return vertices

def get_weights(mesh_data):
  weights = []
  for v in mesh_data.vertices:
    #TODO weight and groups
    for g in v.groups:
      w = (g.group, g.weight)
      weights.append(w)
      #print(" vert group  " + str(g.group))
      #print(" vert weight  " + str(g.weight))
  return weights


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
  #TODO we parse vertices 2 times
  mesh.vertices = get_vertices(mesh_data)
  mesh.weights = get_weights(mesh_data)
  mesh.triangles, mesh.uvs = get_triangles_uvs(mesh_data, mesh.vertices)
  mesh.normals = get_normals(mesh_data)

  return mesh

def write_type(file, str):
  write_string(file, str)

def write_string(file, str):
  s = str.encode('latin1')
  file.write(struct.pack("H%ds" % len(s), len(s), s))
 
def write_material(mat):
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

def write_bone(file, bone):
  write_string(file, bone.name)
  v = bone.position
  file.write(struct.pack('fff', v[0], v[1], v[2]))
  v = bone.rotation
  file.write(struct.pack('ffff', v[0], v[1], v[2], v[3]))
  file.write(struct.pack('H', len(bone.children)))
  for c in bone.children:
    write_bone(file, c)



