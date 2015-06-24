import bpy
import struct


def start():
  objects_to_write = []
  for o in bpy.data.objects:
    obj = export_object(o)

    for a in bpy.data.actions:
      action = export_action(o, a)
      if obj is not None and action is not None:
        print("adding action to object '" + obj.name +"'")
        obj.actions.append(action)

    if obj is not None:
      obj.position = o.location
      bv = o.rotation_quaternion
      obj.rotation = [bv.x, bv.y, bv.z, bv.w]
      obj.scale = o.scale
      objects_to_write.append(obj)
 
  print("Will write " + str(len(objects_to_write))+ " object(s) to file test.bin")
  file = open('test.bin', 'bw');
  file.write(struct.pack('H', len(objects_to_write)))
  for o in objects_to_write:
    print("object name write : " + o.name)
    o.write(file)
  file.close();

  write(objects_to_write)

def write(objects):
  for o in objects:
    filename = o.name
    if type(o) == Mesh:
      filename = o.name + ".mesh"
    elif type(o) == Armature:
      filename = o.name + ".arm"
    print("Will write object '" + o.name + "' to file: " + filename)
    file = open(filename, 'bw');
    o.write(file)
  file.close();


class Action:
  def __init__(self, name):
    self.name = name
    self.curves = []

  def getOrCreateCurve(self, bone_name, t):
    #TODO can optimize this?
    for c in self.curves:
      if c.bone == bone_name and c.datatype == t:
        return c

    c = Curve(bone_name, t)
    self.curves.append(c)
    return c

class Curve:
  def __init__(self, bone, t):
    self.bone = bone
    self.datatype = t
    self.frames = []

  def addFrame(self, frame, index, value):
    found = False
    if self.datatype == "quaternion":
      if index == 0:
        index = 3
      else:
        index = index -1;
    for f in self.frames:
      if f[0] == frame:
        f[1][index] = value
        found = True
        break
    if not found:
      if self.datatype == "quaternion":
        self.frames.append((frame, [0,0,0,0]))
      else:
        self.frames.append((frame, [0,0,0]))
      f = self.frames[-1]
      f[1][index] = value
      if index == 3:
        print("frame : " + str(f))



from bpy.types import PoseBone
def export_action(object, action):
  print("Action name : " + action.name)
  a = Action(action.name)
  a.frame_range = action.frame_range

  pr = object.path_resolve
  for fcu in action.fcurves:
    try:
      prop = pr(fcu.data_path, False)
    except:
      prop = None

    if prop is not None:
      #print("object " + object.name + " has action " + action.name + " with prop : " + str(prop))
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

        curve = a.getOrCreateCurve(prop.data.bone.name, t)
        for frame in fcu.keyframe_points:
          #curve.frames.append(frame.co)
          curve.addFrame(frame.co[0], fcu.array_index, frame.co[1])
          #print("couple : " + str(frame.co))

        #a.curves.append(curve)
        #j'ai besoin de :
        # bone name
        # savoir ce que c'est genre position rotation x, y z w
        #
  if len(a.curves) == 0: return None
  return a

class VertexGroup:
  def __init__(self, name):
    self.name = name
    self.weights = []


def export_object(object):
  print("object : ", object.name)
  if object.type == 'MESH':
    print("it's a mesh")
    mesh = create_mesh(object.data)
    mesh.groups = []
    for vg in object.vertex_groups:
      #g = (vg.index, vg.name)
      g = VertexGroup(vg.name)
      mesh.groups.insert(vg.index, g)
      print("vg index : " + str(vg.index))
      print("vg name : " + str(vg.name))
      try:
        print("vg weight of vertex 0 : " + str(vg.weight(0)))
      except:
        print("vertex 0 is not in this group")

    for i,w in enumerate(mesh.weights):
      for g in w:
        mesh.groups[g[0]].weights.append([i,g[1]])

      #print("i is : " + str(i))
      #print("index of group is : " + str(w))
      
    #print("group 1 : " + str(mesh.groups[1].weights))


    #TODO material
    mat = object.active_material
    if mat:
      write_material(mat)
    handle_modifiers(object)
    return mesh
  elif object.type == 'ARMATURE':
    print("it's an armature")
    armature = create_armature(object.data)
    return armature

  return None

class Armature:
  pass #bones = []

  def write(armature, file):
    #return
    write_type(file, "armature")
    write_string(file, armature.name)

    write_vec3(file, armature.position)
    write_vec4(file, armature.rotation)
    write_vec3(file, armature.scale)

    file.write(struct.pack('H', len(armature.bones)))
    for bone in armature.bones:
      write_bone(file, bone)

    file.write(struct.pack('H', len(armature.actions)))
    for action in armature.actions:
      #print("i have to write action : " + action.name)
      write_string(file, action.name)
      file.write(struct.pack('H', len(action.curves)))
      for curve in action.curves:
        write_string(file, curve.bone)
        write_string(file, curve.datatype)
        file.write(struct.pack('H', len(curve.frames)))
        for frame in curve.frames:
          #print("   frame : " + str(frame[0]) + " with value : " + str(frame[1]))
          file.write(struct.pack('f', frame[0]))
          for value in frame[1]:
            #print("       writing value : " + str(value))
            file.write(struct.pack('f', value))



class Bone:
  pass
#  matrix
# children
# name

def create_armature(data):
  armature = Armature()
  armature.bones = []
  armature.actions = []
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
  lrs = bone.matrix_local.decompose()
  bo.position = lrs[0]
  bq = lrs[1]
  bo.rotation = [bq.x, bq.y, bq.z, bq.w]
  #print("bone rotation " + str(bo.rotation))
  print("bone " + bone.name)
  #print("matrix " + str(bone.matrix))
  #print("matrix relative to armature " + str(bone.matrix_local))
  #print("matrix relative to armature to translation " + str(bone.matrix_local.to_translation()))
  print("bone position " + str(bo.position))
  print("bone head " + str(bone.head))
  print("bone head local " + str(bone.head_local))
  print("bone tail " + str(bone.tail))
  #print("matrix " + str(bone.matrix))
  #print("matrix local " + str(bone.matrix_local))
  #head = position
  bo.head = bone.head;
  bo.tail = bone.tail;
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

    #write_vec3(file, mesh.position)
    #write_vec4(file, mesh.rotation)
  
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
    #print("uvs : " + str(mesh.uvs))
    for uv in mesh.uvs:
      #print("uv to write " + str(uv))
      #print("uv0 to write " + str(uv) + ", " + str(uv[0]))
      #print("uv1 to write " + str(uv) + ", " + str(uv[1]))
      file.write(struct.pack('ff', uv[0], uv[1])) 

    # number of groups
    file.write(struct.pack('H', len(mesh.groups)))
    for g in mesh.groups:
      # name
      # index
      write_string(file, g.name)
      print("mesh group : " + g.name)
      file.write(struct.pack('H', len(g.weights)))
      for w in g.weights:
        file.write(struct.pack('H', w[0]))
        file.write(struct.pack('f', w[1]))
        #print("mesh weight : " + str(w))
      pass

    # number of vertex
    file.write(struct.pack('H', len(mesh.weights)))
    for warray in mesh.weights:
      # index
      # weight
      file.write(struct.pack('H', len(warray)))
      for w in warray:
        file.write(struct.pack('H', w[0]))
        file.write(struct.pack('f', w[1]))
        #print("write weight : " + str(w[0]) + " with weight : " +str(w[1]))
    #  pass
  
def vertex_index_get_or_create(face_uv, uvs, vertices, vertex_indices, face_vert_index):
  olduv = uvs[vertex_indices[face_vert_index]]
  newuv = face_uv[face_vert_index]
  if olduv != 0 :
    if olduv[0] != newuv[0] or olduv[1] != newuv[1]:
      newvert = vertices[vertex_indices[face_vert_index]]
      vertices.append(newvert)
      uvs.append(newuv)
      index = len(vertices) -1
    else:
      uvs[vertex_indices[face_vert_index]] = newuv
      index = vertex_indices[face_vert_index]
  else:
    uvs[vertex_indices[face_vert_index]] = newuv
    index = vertex_indices[face_vert_index]
  return index

def get_triangles_uvs(mesh_data, vv):
  triangles = []
  uvs = []
  uvdata = []

  curlen = len(vv)

  if len(mesh_data.uv_layers) > 0:
    uvs = [0]* len(vv)

  for i, face in enumerate(mesh_data.tessfaces):
    vertices = face.vertices
    ind0 = vertices[0]
    ind1 = vertices[1]
    ind2 = vertices[2]
    do_uv = bool(mesh_data.tessface_uv_textures)
    uvdata = None
    if do_uv:
      uvdata = mesh_data.tessface_uv_textures.active.data[i]
      f_uv = uvdata.uv;
      ind0 = vertex_index_get_or_create(f_uv, uvs, vv, vertices, 0)
      ind1 = vertex_index_get_or_create(f_uv, uvs, vv, vertices, 1)
      ind2 = vertex_index_get_or_create(f_uv, uvs, vv, vertices, 2)

    triangles.append((ind0, ind1, ind2))

      # It's a quad we need one more triangle.
    if len(vertices) == 4:
      ind3 = vertices[3]
      if do_uv:
        f_uv = uvdata.uv;
        ind3 = vertex_index_get_or_create(f_uv, uvs, vv, vertices, 3)

      triangles.append((ind0, ind2, ind3))

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
    vw = []
    for g in v.groups:
      w = (g.group, g.weight)
      vw.append(w)
      #print(" vert group  " + str(g.group))
      #print(" vert weight  " + str(g.weight))
    weights.append(vw)
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

def write_vec3(file, v):
  file.write(struct.pack('fff', v[0], v[1], v[2]))

def write_vec4(file, v):
  file.write(struct.pack('ffff', v[0], v[1], v[2], v[3]))
 
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
      #print("armature name is " + armature.name)

def write_bone(file, bone):
  write_string(file, bone.name)
  v = bone.position
  file.write(struct.pack('fff', v[0], v[1], v[2]))
  v = bone.head
  file.write(struct.pack('fff', v[0], v[1], v[2]))
  v = bone.tail
  file.write(struct.pack('fff', v[0], v[1], v[2]))
  v = bone.rotation
  file.write(struct.pack('ffff', v[0], v[1], v[2], v[3]))
  file.write(struct.pack('H', len(bone.children)))
  for c in bone.children:
    write_bone(file, c)



