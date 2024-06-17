from ursina import *
from ursina.shaders import basic_lighting_shader

class Cylinder(Pipe):
    def __init__(self, resolution=8, radius=.5, start=0, height=1, direction=(0,1,0), mode='triangle', **kwargs):
        super().__init__(
            base_shape=Circle(resolution=resolution, radius=.5),
            origin=(0,0),
            path=((0,start,0), Vec3(direction) * (height+start)),
            thicknesses=((radius*2, radius*2),),
            mode=mode,
            **kwargs
            )

def spin():
    global offset
    global anim
    if anim == False:
        anim = True
        cube.animate('rotation_y', cube.rotation_y+(360/num), duration=delay, curve=curve.in_out_expo, auto_destroy = True)
 
        # Animate cubes
        for i in range(len(cubes)):
            cubes[i].animate_x(cubes[i].position.x+offset, duration=delay, curve=curve.in_out_expo)
            for j in range(len(cubes)):
                ccube[i][j].animate_x(ccube[i][j].position.x+offset+j, duration=delay, curve=curve.in_out_expo)

        print('clicked', anim)
        #create a delay
        offset += offset 
        invoke(go, -1 , delay=delay)

def go(i):
    global anim
    if anim == True:
        if i != -1:
            cubes[i].animate_x(offset, duration=delay, curve=curve.in_out_expo)
            for x in range(len(ccube[i])):
                ccube[i][x].animate_x(0, duration=delay, curve=curve.in_out_expo)
        else:
            for i in range(len(cubes)):
                cubes[i].animate_x(0, duration=delay, curve=curve.in_out_expo)
                for x in range(len(ccube[i])):
                        ccube[i][x].animate_x(0, duration=delay, curve=curve.in_out_expo)
    anim = False

def single_click(i):
    global anim
    anim = True
    print('clicked',i)
    cubes[i].animate_x(cubes[i].position.x+1, duration=delay, curve=curve.in_out_expo)
    for j in range(len(cubes)):
        ccube[i][j].animate_x(ccube[i][j].position.x+offset+j, duration=delay, curve=curve.in_out_expo)
    #create a delay
    invoke(go, i,  delay=delay)

def update():
    #get mouse input MOUSE
    if held_keys['left mouse'] or held_keys['right mouse']:
        cube.rotation_y += (held_keys['left mouse'] - held_keys['right mouse']) * time.dt * 100
        
    #get mouse position x and y MOUSE
    if mouse.hovered_entity == cube:
        cube.color = color.red
    else:
        cube.color = color.white
    
    if mouse.x >0.99:
        mouse.x = 0.99
    if mouse.x <-0.99:
        mouse.x = -0.99
    if mouse.y >0.99:
        mouse.y = 0.99
    if mouse.y <-0.99:
        mouse.y = -0.99

    # i need to calculate the mouse position in the cube
    # so we need to get window size and calculate the position
    # of the mouse in the window, so mouse pointer hover the cube
    
    # get ursina window size 
    window_x = app.getSize()[0]
    window_y = app.getSize()[1]

    app.show_camera_frustum = True



    if mouse.x > 0 and mouse.x < 1 or mouse.x < 0 and mouse.x > -1:
        cube.x= mouse.x * 30
    if mouse.y > 0 and mouse.x < 1 or  mouse.y < 0 and mouse.y > -1:
        cube.z = mouse.y * 30

    print(window_x, window_y, mouse.x, mouse.y , cube.x, cube.z, app.getAspectRatio())
    
    
    # test all cubes
    for c in cubes:
        if cube.intersects(c).hit:
            c.color = color.lime
        else:
            c.color = color.hsv(30,1,1)

app = Ursina( forced_aspect_ratio = True, window_title='Ursina 3D', window_size=(800, 600))

cubes = []
anim = False


num = 6  
delay = 2# num/10  
offset = ((num/num)*1)
cube = Entity(model='cube', color=hsv(10,1,1), scale=1, collider='box', shader=basic_lighting_shader)

# Create cylinder
cylinder = Cylinder(resolution=6, radius=2, height=5)


# Create cubes
for i in range(num):
    c = Entity(model='cube', color=hsv(30,1,1), scale=1, collider='box', shader=basic_lighting_shader)
    tmp = Entity()
    tmp.parent = cube
    tmp.rotation_y = (360/num)*i
    c.parent = tmp
    c.position = (offset, 0, 0)
    cubes.append(c)
    c.on_click = Func(single_click, i)

# Initialize ccube after cubes is populated
ccube = [[None for _ in range(len(cubes))] for _ in range(len(cubes))]
for i in range(num):
    last = cubes[i]
    for j in range(num):
        c = Entity(model='cube', color=hsv(30,1,1), scale=.75, collider='box', shader=basic_lighting_shader)
        ccube[i][j] = c
        ccube[i][j].parent = last
        last = ccube[i][j]

ed = EditorCamera(rotation_speed = 200, panning_speed=200)



cube.on_click = spin

pivot = Entity()
DirectionalLight(parent=pivot, y=2, z=3,rotation=(45,45,0),shadows=True)

# hide mouse cursor SplashScreen??
#app.mouse.visible = False

app.run()