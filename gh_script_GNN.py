import clr
clr.AddReference("PolyFramework")
clr.AddReference("PolyFrameGH")
import PolyFramework as pf
from PolyFrameGH.Core import *
import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import numpy as np
import networkx as nx
a = PF.Faces
b = PF.Vertices
c = PF.Edges

#for i in a:
#    if not i.External:
#        c.append(i.FMesh)
#        print(i.Planarized)
#        print(i.Area)
internal_faces = []
areas = []
for i in a:
    if not i.External:
        internal_faces.append(i)
        areas.append(i.Area)
areas = np.array(areas)

areas = (areas-np.min(areas))/(np.max(areas)-np.min(areas))


internal_vertices = [] 
for i in b:
    if not i.External:
        internal_vertices.append(i)
t = []


rates = np.zeros((len(internal_faces)))
for i,j in enumerate(internal_faces):
    inf = False
    for k in j.Edges:
        if len(k.Faces)==1:
            t.append(j.FMesh)
            rates[i] = np.Infinity
            inf = True
            break
    if not inf:
        try:
            rates[i] = (1-areas[i])*coef1 + coef2*len(j.Edges) + coef3*performance[i]
        except:
            print(areas[i],j.Edges, performance[i])

indices = np.argsort(rates)[::-1]

sorted_faces = []
for i in indices:
    sorted_faces.append(internal_faces[i])

internal_edges = []

for i in PF.Edges:
    if not i.External and i.Id>=0:
        internal_edges.append(i)


indeterminancy = len(internal_edges)+reactions-3*len(internal_vertices)

chosenfaces = []
for i in sorted_faces:

    if indeterminancy + len(i.Edges) - 3 <= 0:
        chosenfaces.append(i)
        indeterminancy = indeterminancy + len(i.Edges) - 3
c = []
for t in chosenfaces:
    c.append(t.FMesh)
a = []
absent_edges = []
for i in internal_edges:
    check = True
    for j in chosenfaces:
        ids = [abs(t.Id) for t in j.Edges]
        if i.Id in ids:
            check = False
            break
    if check:
        absent_edges.append(i)

chosen = []
for i in absent_edges:
    ids = [abs(t.Id) for t in i.Faces]
    choices = []
    for h in ids:
        for index,x in enumerate(sorted_faces):
            if h == x.Id:
                choices.append(index)
                break

    

    chosen.append(min(choices))

extrafaces = []

chosen = list(set(chosen))

for i in chosen:
    chosenfaces.append(sorted_faces[i])
    extrafaces.append(sorted_faces[i].FMesh)




print(len(absent_edges))


import Rhino.Geometry as rg


def join_meshes(mesh_list1, mesh_list2):
    # Create an empty mesh to store the combined result
    combined_mesh = rg.Mesh()

    # Loop through the first list of meshes and append to the combined mesh
    for mesh in mesh_list1:
        combined_mesh.Append(mesh)

    # Loop through the second list of meshes and append to the combined mesh
    for mesh in mesh_list2:
        combined_mesh.Append(mesh)

    # Once all meshes are added, combine vertices and faces
    combined_mesh.Vertices.CombineIdentical(True, True)
    combined_mesh.FaceNormals.ComputeFaceNormals()
    combined_mesh.Normals.ComputeNormals()
    combined_mesh.Compact()

    return combined_mesh




def find_single_vertex_face_connections(mesh):
    # Create an empty list to store vertices where only 2 faces are connected
    single_vertex_connections = []
    indices = []
    # Iterate through all vertices in the mesh
    for v_index in range(mesh.Vertices.Count):
        # Get all faces connected to the vertex
        connected_faces = mesh.TopologyVertices.ConnectedFaces(v_index)
        
        # Only consider vertices that are connected to exactly 2 faces
        if len(connected_faces) == 2:
            face1_index = connected_faces[0]
            face2_index = connected_faces[1]

            # Get the vertices of both faces
            face1_vertices = set(mesh.Faces.GetFaceVertices(face1_index))
            face2_vertices = set(mesh.Faces.GetFaceVertices(face2_index))
            
            # Find the common vertices between the two faces
            common_vertices = face1_vertices.intersection(face2_vertices)

            # If only one common vertex, store the vertex
            if len(common_vertices) == 1:
                single_vertex_connections.append(mesh.Vertices[v_index])
                indices.append(v_index)
        elif len(connected_faces)>2:
            face_graph = nx.Graph()
            face_indices = list(connected_faces)
            shared_edges = set()
            for f1 in face_indices:
                face_graph.add_node(f1)
                for f2 in face_indices:
                    if f1 != f2:
                        # Check if faces f1 and f2 share an edge
                        setv1 = set([mesh.Faces[f1].A,mesh.Faces[f1].B,mesh.Faces[f1].C])
                        setv2 = set([mesh.Faces[f2].A,mesh.Faces[f2].B,mesh.Faces[f2].C])
                        if len(setv1.intersection(setv2))==2:
                            shared_edges.add((f1, f2))
                            face_graph.add_edge(f1, f2)
        # If there are fewer shared edges than pairs of faces, this is a problematic vertex
            connected_components = list(nx.connected_components(face_graph))
            
            if len(connected_components) > 1:
                indices.append(v_index)
                single_vertex_connections.append(mesh.Vertices[v_index])
    return single_vertex_connections, indices





combined_mesh = join_meshes(c, extrafaces)
g, h = find_single_vertex_face_connections(combined_mesh)

print(h)

pc = rg.PointCloud([i.Point for i in PF.Vertices if not i.External])
pcvertices = [i for i in PF.Vertices if not i.External]
closestpfvertices = [pc.ClosestPoint(i) for i in g]

chosenfaces_ids = [i.Id for i in chosenfaces]

newly_added = []
for i in closestpfvertices:
    f = pcvertices[i].Faces
    sorted_f = sorted(f,key=lambda t:t.Area)
    for j in sorted_f:
        if j.Id not in chosenfaces_ids and -j.Id not in chosenfaces_ids:
            newly_added.append(j)
            break

newly_added = list(set(newly_added))

if newly_added:
    chosenfaces+=newly_added

    combined_mesh = rg.Mesh()
    for i in chosenfaces:
        combined_mesh.Append(i.FMesh)

    combined_mesh.Vertices.CombineIdentical(True, True)
    combined_mesh.FaceNormals.ComputeFaceNormals()
    combined_mesh.Normals.ComputeNormals()
    combined_mesh.Compact()


g, h = find_single_vertex_face_connections(combined_mesh)

print(h)


closestpfvertices = [pc.ClosestPoint(i) for i in g]

print(closestpfvertices)

now = pcvertices[13].Faces

now_mesh = [i.Id for i in now]

