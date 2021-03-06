import bpy 
import os
import pathlib
import math




#Deselect all
bpy.ops.object.select_all(action='DESELECT')


def delete_all_cameras_and_empty_objects():


    # Delete all the Camera Objetcs
    bpy.ops.object.select_all(action='DESELECT')
    
    for o in bpy.context.scene.objects:
        if o.type == 'CAMERA':
            o.select_set(True)
        else:
            o.select_set(False)
    
    bpy.ops.object.delete()
    
    
    # Delete the Empty objects
    bpy.ops.object.select_all(action='DESELECT')
    
    for o in bpy.context.scene.objects:
        if o.type == 'EMPTY':
            o.select_set(True)
        else:
            o.select_set(False)
            
  
    bpy.ops.object.delete()
    
    
    # Save and re-open the file to clean up the data blocks
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)


# Create a empty cube as a target.
def create_target_and_camera():
    
    
    # Creating the Camera    
    camera_data = bpy.data.cameras.new(name='Camera')
    camera_object = bpy.data.objects.new('Camera', camera_data)
    bpy.context.scene.collection.objects.link(camera_object)
        
    
    # Creating empty box with the name Target
    o = bpy.data.objects.new( "empty", None )
    bpy.context.scene.collection.objects.link( o )

    o.empty_display_size = 2
    o.empty_display_type = 'CUBE'

    o.name = "Target"
       
       
    # Adding the "Track to" constraint to the camera.
    constraint = bpy.data.objects["Camera"].constraints.new(type='TRACK_TO')
    constraint.target = bpy.data.objects["Target"]
    
    # Deselecting all if anything was selected
    bpy.ops.object.select_all(action='DESELECT')
       
    

  
def create_folders():
    
    # Thi function creates 3 folders that are required for the 360 renders.
    pwd = bpy.data.filepath
    parent = os.path.join(pwd, os.pardir)
    file_root_path = os.path.abspath(parent)
    
    pathlib.Path(file_root_path + '/360/WIREFRAME').mkdir(parents=True, exist_ok=True) 
    pathlib.Path(file_root_path + '/360/MATERIAL').mkdir(parents=True, exist_ok=True)
    pathlib.Path(file_root_path + '/360/RENDERED').mkdir(parents=True, exist_ok=True)
    
    
            
def move_target_body(object_name):
    
    # Target
    target = bpy.data.objects['Target']
    
    # Moving the target to the middle of "object_name" provide 
    target.location[2] = math.ceil(bpy.data.objects[object_name].location[2]) / 2 + 1
    


def create_settings():
    bpy.data.scenes["Scene"].render.use_simplify = False
    bpy.data.scenes["Scene"].render.film_transparent = True
    bpy.data.scenes["Scene"].render.use_overwrite = False
    bpy.data.scenes["Scene"].render.use_placeholder = True
    bpy.data.scenes["Scene"].render.image_settings.color_mode = "RGBA"

    

def render(shading_type):
    
    sce = bpy.context.scene.name
    file_number = 0 
    
    # Initialize Path
    bpy.data.scenes[sce].render.filepath = "//"+"360"+"/"+shading_type + "/" + "360"+"_" + str(file_number) 

    # Getting the current file path: 
    file_root_path = os.path.abspath(os.path.join(bpy.data.filepath, os.pardir))
    nPath = file_root_path + "/" + "360" + "/" + shading_type

    
    # lst of all images in current renderd path
    lst=os.listdir(nPath)


    # Inscrease file_number based on last rendered file.
    for i in lst:
        if int(i[4:-4]) <= file_number:
            file_number += 1
        
            
            
    # Changes the path based if new_number ( I think this can be shorter ) 
    bpy.data.scenes[sce].render.filepath = "//"+"360"+"/"+shading_type + "/" + "360"+"_" + str(file_number) 

    # Getting info about the screen to toggle the xray??????
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        
        
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            
            # Going into camera view and changing shading type
            # area.spaces[0].region_3d.view_perspective = 'CAMERA'
            area.spaces[0].shading.type = str(shading_type)
            
            # Toogle xray off.
            if area.spaces[0].shading.show_xray_wireframe:
                # This is depriciated, need a new way maybe later
                # Context.temp_override(..), calling "view3d.toggle_xray"

                override = {'window': window, 'screen': screen, 'area': area}
                bpy.ops.view3d.toggle_xray(override)
                

        # Disable / Enable "Show_Overlays"
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.overlay.show_overlays = False
                
               
        
    # Render image through viewport  
    if shading_type != "RENDERED":
        bpy.ops.render.opengl(write_still=True)
    else:
        bpy.ops.render.render(write_still=True)  
    

    

# This is the second function you should call with the type of shading you want for yout 360
# Shading Type, Shading type name, 
def preview_360(preview_type):
    
    # List of camera angels # xyz
    camera_locations = [
        [0,-42,9.5],
        [29.9,-29.9,9.5],
        [29.9,29.9,9.5],
        [0,42,9.5],
        [-29.9,29.9,9.5],
    ]
    
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D': 
            # Going into camera view
            area.spaces[0].region_3d.view_perspective = 'CAMERA'
            #context.space_data.region_3d.view_perspective = 'CAMERA'
            break
        
    bpy.ops.view3d.camera_to_view.poll()
    #bpy.ops.view3d.camera_to_view()
    #bpy.ops.view3d.view_camera()
    
    camera_obj = bpy.data.objects["Camera"]

    # Choose camera type 'PANO', 'PERSP' and 'ORTHO' 
    bpy.data.cameras['Camera'].type = 'PERSP'
    
    # Reset he camera location
    for i in range(3):
        camera_obj.location[i] = 0
        camera_obj.rotation_euler[i] = 0

    # Loop trough list of poses and then viewport render
    for i in camera_locations:
        # change position
        for j in range(3):
            camera_obj.location[j] = i[j]
        
        # render ( # Shading Type, Shading type name, Path ? )
        render(preview_type)
        
        # Reset he camera location
        for i in range(3):
            camera_obj.location[i] = 0
            camera_obj.rotation_euler[i] = 0
            
            
def go_into_camera_view():

    scene = bpy.context.scene
    scene.camera = bpy.data.objects['Camera']

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
            break

def setup(object_name):
    # Delete all cameras
    delete_all_cameras_and_empty_objects()
        
    # This function creates a camera that tracks the target
    create_target_and_camera()
        
    # This function creates all the folders required for a 360 render.
    create_folders()
        
    # Object name that we want to place our target in the middle of
    move_target_body(object_name)
            
    # Great function name, does what it says.
    create_settings()
    
    # Go into camera view.
    go_into_camera_view()
    
######################################################################################################################################################################################################################################################################################
######################################################################################################################################################################################################################################################################################


# 1.
# We call the setup function with the name of the 3D Object that is the highest on the z axis. In this case its the "hair"
#setup("hair")

# 2.
# We either run the function below to go into camera view or just press 0 on numpad
# go_into_camera_view()

# 3.
# Once the above function runs, we comment it out and uncommenent functions below.
#preview_360("MATERIAL")
#preview_360("WIREFRAME")
#preview_360("RENDERED")


