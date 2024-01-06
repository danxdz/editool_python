import wxgl

# Define a directional light source with specific properties
light = wxgl.SunLight(direction=(0.5, -0.5, -1.0), diffuse=0.7, specular=0.98, shiny=100, pellucid=0.9)

# Create an application for the 3D scene with a light gray background and a field of view angle of 40 degrees
app = wxgl.App(bg='#f0f0f0', fovy=40)

# Add five spheres to the scene with specific positions, sizes, colors, and the previously defined light source
app.sphere((-2, 0, 0), 0.35, color='#d8d8d8', light=light)
app.sphere((0, 0, 0), 0.35, color='#d8d8d8', light=light)
app.sphere((2, 0, 0), 0.35, color='#d8d8d8', light=light)
app.sphere((-1, -1, 0), 0.35, color='#d8d8d8', light=light)
app.sphere((1, -1, 0), 0.35, color='#d8d8d8', light=light)

# Display the 3D scene
app.show()
