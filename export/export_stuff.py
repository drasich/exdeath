import bpy
import struct

def start():
  print("will write to test.bin")
  file = open('test.bin', 'bw');
  for o in bpy.data.objects:
    export_object(file, o)
  file.close();

def export_object(file, object):
  print("object : ", object.name)
  if object.type == 'MESH':
    print("it's a mesh")
    mesh = create_mesh(object.data)
    write_mesh(file, mesh)
    mat = object.active_material
    write_material(file, mat)

  #file.write('This is a test!');

class Mesh:
  mesh = None
  vertices = []
  triangles = []
  normals = []
  uvs = []
  
  def __init__(self, mesh):
    self.mesh = mesh


def get_triangles(mesh_data, uvs, vv):
  triangles = []
  #uvs = []
  uvdata = mesh_data.uv_layers[0].data
  print("tess faces length : " + str(len(mesh_data.tessfaces)))
  i = 0
  uvc = 0
  for face in mesh_data.tessfaces:
    vertices = face.vertices
    triangles.append((vertices[0], vertices[1], vertices[2]))
    #print("vertice " + vertices[0] + " get this : " + vertices[0]
    print(str(i) + " append this " + str(vertices[0]) + str(vertices[1]) +str(vertices[2]))
    print(" with uv " + str(uvdata[uvc].uv) + str(uvdata[uvc+1].uv) +str(uvdata[uvc+2].uv))
    uvs[vertices[0]] = uvdata[uvc].uv
    uvs[vertices[1]] = uvdata[uvc+1].uv
    uvs[vertices[2]] = uvdata[uvc+2].uv
    i +=1
    uvc+=3
    # It's a quad we need one more triangle.
    if len(vertices) == 4:
      triangles.append((vertices[0], vertices[2], vertices[3]))
      #uvs.append(uvdata[vertices[3]].uv)
      uvs[vertices[3]] = uvdata[uvc].uv
      i +=1
      uvc+=1

  return triangles#, uvs
      
def get_vertices(mesh_data):
  vertices = []
  for v in mesh_data.vertices:
    vertices.append(v.co)
  return vertices

def get_normals(mesh_data):
  normals = []
  for v in mesh_data.vertices:
    normals.append(v.normal)
  return normals

def get_uvs(mesh_data):
  uvs = []
  #print("uv : " + str(mesh_data.uv_layers[0].data)) 
  #print("************ : " + str(dir(mesh_data)))
  uvs.append([1,0]) #d.uv)
  uvs.append([0,0]) #d.uv)
  uvs.append([1,1]) #d.uv) 2
  uvs.append([0,1]) #d.uv)
  uvs.append([0.5,0]) #d.uv)
  uvs.append([0.5,1]) #d.uv)
  uvs.append([1,0.5]) #d.uv) 6
  uvs.append([0,0.5]) #d.uv)
  uvs.append([0.5,0.5]) #d.uv) 8
  #uvs.append([0,1]) #d.uv)

  for d in mesh_data.uv_layers[0].data:
    print("yo : " + str(d.uv))
    #uvs.append(d.uv)
  return uvs


def create_mesh(mesh_data):
  mesh_data.update(calc_tessface=True)
  mesh = Mesh(mesh_data)
  mesh.vertices = get_vertices(mesh_data)
  for i in range(len(mesh.vertices)):
    mesh.uvs.append([0,0])
  print("vertices length : " + str(len(mesh.vertices)))
  mesh.triangles = get_triangles(mesh_data, mesh.uvs, mesh.vertices)
  print("triangles length : " + str(len(mesh.triangles)))
  #mesh.triangles = get_triangles(mesh_data)
  mesh.normals = get_normals(mesh_data)
  #mesh.uvs = get_uvs(mesh_data)

  return mesh

def write_mesh(file, mesh):
  print("mesh : " + str(mesh))
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
  print("texture : " + str(at))
  print("scale : " + str(mat.texture_slots[0].scale))
  print("filepath : " + bpy.data.textures[at.name].image.filepath)
  pass
