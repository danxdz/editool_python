import open3d as o3d

print("Testing mesh in Open3D...")
armadillo_mesh = o3d.data.ArmadilloMesh()
mesh = o3d.io.read_triangle_mesh(armadillo_mesh.path)

knot_mesh = o3d.data.KnotMesh()
mesh = o3d.io.read_triangle_mesh(knot_mesh.path)
print(mesh)
print('Vertices:')

print("Computing normal and rendering it.")
mesh.compute_vertex_normals()
o3d.visualization.draw_geometries([mesh])