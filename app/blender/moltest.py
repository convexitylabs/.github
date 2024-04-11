# Hello! This is a script that will render a .pdb file in Blender using the MolecularNodes addon.
# You need to be using a python version between 3.10 and 3.11 for this script to work (i used a virtual enviroment for this)
# You'll also need to have Blender installed and the molecularnodes addon installed.
# Notably this script will only work for molecular nodes v.4.0.12
# You'll need to use pip install molecularnodes==4.0.12
# and pip install bpy
# it's messy because I'm not sure exactly what I can change without breaking it but I've added comments throughout to explain what I'm doing.


import sys
import os
import bpy
import numpy as np
import molecularnodes as mn
import random
from PIL import Image
import math
mn.register()

#This is a more powerful rendering engine, it takes about 30 seconds and I've commented
#it out for now just for testing purposes.
#bpy.context.scene.render.engine = 'CYCLES'

#import the .pdb file. Future directions is to allow other types of files.
pdb_file_path = '/Users/lily/Downloads/Condition28Design1.pdb'
# standard test path: '/Users/lily/Downloads/Condition28Design1.pdb'

#Change the background colour of the outputted image
bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.05, 0.05, 1.0)

#Clear the scene of any objects (always necessary for new bleder world)
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.object.select_by_type(type="MESH")
bpy.ops.object.delete()

#Import the .pdb file in cartoon style
bpy.context.scene.MN_import_local_path = pdb_file_path
bpy.context.scene.MN_import_local_name = "NewMolecule"
bpy.context.scene.MN_import_style = 'cartoon'
bpy.ops.mn.import_protein_local()

#Import the .pdb file in surface style
bpy.context.scene.MN_import_local_name = "NewMoleculeSurface"
bpy.context.scene.MN_import_style = 'surface'
bpy.ops.mn.import_protein_local()

# get parameters to randomly set the .pdb's color 
obj_name = "NewMolecule"
modifier_name = "MolecularNodes"
node_tree_name = "MN_NewMolecule"
# Get the object with the modifier
obj = bpy.data.objects[obj_name]
# Get the Geometry Nodes modifier
nodes_modifier = obj.modifiers.get(modifier_name)
# Function to set seed values for color attribute random nodes
def set_seed_for_color_attribute_random_nodes(node_tree, seed_value):
    for node in node_tree.nodes:
        # Check if the node is an 'MN_color_attribute_random' node
        if 'MN_color_attribute_random' in node.name:
            if 'Seed' in node.inputs:
                node.inputs['Seed'].default_value = seed_value
                print(f"Updated Seed value for {node.name} to {seed_value}")
# Check if the modifier and its type are correct
if nodes_modifier and nodes_modifier.type == 'NODES':
    print(f"Modifier found: {nodes_modifier.name}")
    node_tree = nodes_modifier.node_group

    seed_value = random.randint(1, 20)  # Generate a random seed value within the range
    # random colours are picked from a list of colours that can be found in material.py in the molecular nodes files. https://github.com/BradyAJohnston/MolecularNodes/releases/ a future direction could be modifying these colours or adding to them

    # Update seed values for MN_color_attribute_random nodes
    set_seed_for_color_attribute_random_nodes(node_tree, seed_value)

    print("All relevant nodes have been updated.")
else:
    print("Modifier not found or is not a Geometry Nodes modifier.")

#this gets the location of the molecule (will be used for camera location setting)
molecule = bpy.data.objects["NewMolecule"]
vertices = [molecule.matrix_world @ v.co for v in molecule.data.vertices]
center = np.mean(vertices, axis=0)
min_corner = np.min(vertices, axis=0)
max_corner = np.max(vertices, axis=0)
size = max_corner - min_corner
distance = max(size) * 1.5

# Here we duplicate and modify the material of that is used for NewMolecule and NewMoleculeSurface
# This new transparent, glossy and metalic material will be applied to NewMoleculeSurface

# Get the original material by its name
original_material = bpy.data.materials.get("MN Default")
# Check if the original material exists
if original_material:
    # Duplicate the material
    duplicated_material = original_material.copy()
    
    # Rename the duplicated material
    duplicated_material.name = "MN Default Copy"
    
    # Ensure the duplicated material uses nodes
    duplicated_material.use_nodes = True
    nodes = duplicated_material.node_tree.nodes
    
    # Find the Principled BSDF node
    principled_bsdf = next((node for node in nodes if node.type == 'BSDF_PRINCIPLED'), None)
    
    # If the Principled BSDF node is found, set its Metallic, roughness and Alpha(transparency) values
    if principled_bsdf:
        principled_bsdf.inputs['Metallic'].default_value = 0.7  
        principled_bsdf.inputs['Alpha'].default_value = 0.04    
        principled_bsdf.inputs['Roughness'].default_value = 0.3    
        # Set the blend mode to 'Alpha blend'
        duplicated_material.blend_method = 'BLEND'
         # Adjust shadow mode for transparency
        duplicated_material.shadow_method = 'HASHED'  # Or 'NONE' for no shadows from transparent areas
        print(f"Material '{duplicated_material.name}' updated ")
    else:
        print("Principled BSDF node not found in the duplicated material.")
else:
    print("Material 'MN Default' not found.")

obj_name = "NewMoleculeSurface"
modifier_name = "MolecularNodes"
node_tree_name = "MN_NewMolecule.001"

# Ok now we actually apply that new material to NewMoleculeSurface. 
# Get the object with the modifier
obj = bpy.data.objects[obj_name]

# Get the Geometry Nodes modifier
nodes_modifier = obj.modifiers.get(modifier_name)

# Function to set seed values for color attribute random nodes
def set_seed_for_color_attribute_random_nodes(node_tree, seed_value):
    for node in node_tree.nodes:
        # Check if the node is an 'MN_color_attribute_random' node
        if 'MN_color_attribute_random' in node.name:
            if 'Seed' in node.inputs:
                node.inputs['Seed'].default_value = seed_value
                print(f"Updated Seed value for {node.name} to {seed_value}")

# Check if the modifier and its type are correct
if nodes_modifier and nodes_modifier.type == 'NODES':
    print(f"Modifier found: {nodes_modifier.name}")
    node_tree = nodes_modifier.node_group

    # Update seed values for MN_color_attribute_random nodes
    set_seed_for_color_attribute_random_nodes(node_tree, seed_value)

    print("All relevant nodes have been updated.")
else:
    print("Modifier not found or is not a Geometry Nodes modifier.")

# Names of the node tree and the node
node_tree_name = "MN_NewMoleculeSurface"
node_name = "MN_style_surface"
new_material_name = "MN Default Copy"

# Get the material
new_material = bpy.data.materials.get(new_material_name)

if new_material:
    # Get the node tree
    node_tree = bpy.data.node_groups.get(node_tree_name)

    if node_tree:
        # Find the specific node
        style_surface_node = node_tree.nodes.get(node_name)

        if style_surface_node:
            # Find the input socket for the material. Adjust 'Material' if the actual name differs.
            material_input = style_surface_node.inputs.get('Material')
            
            if material_input:
                # Assign the material object directly to the socket's default_value
                material_input.default_value = new_material
                print(f"Material updated to '{new_material_name}' in node '{node_name}'.")
            else:
                print(f"Material input not found in node '{node_name}'.")
        else:
            print(f"Node '{node_name}' not found in node tree '{node_tree_name}'.")
    else:
        print(f"Node tree '{node_tree_name}' not found.")
else:
    print(f"Material '{new_material_name}' not found.")


#Changing the light style and its energy (brightness)
# Access the light object by its name
light = bpy.data.objects['Light']

# Check if the object is indeed a light source
if light.type == 'LIGHT':
    # Increase the light's energy (brightness)
    light.data.energy = 1500  
    light.data.type = 'AREA'
    print(f"The light type has been changed to: {light.data.type}")
else:
    print("The specified object is not a light source.")

#Set the camera location and rotation
camera = bpy.data.objects["Camera"]
camera.location = center + np.array([0, -distance, distance])
camera.rotation_euler = np.array([np.arctan(1), 0, 0])
camera.data.dof.use_dof = True
camera.data.dof.focus_distance = distance
camera.data.dof.aperture_fstop = 11
camera.data.clip_end = distance * 2
camera.data.lens = 65


# Ignore this please, I'm adding a plane to make it have a shadow but it's not working well.
# # Create a new plane
# bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0))

# # Reference the newly created plane
# plane = bpy.context.active_object

# # Scale the plane by 10 in the X and Y axes
# plane.scale = (10, 10, 1)

# # Get the location of the NewMolecule object
# new_molecule_location = bpy.data.objects["NewMolecule"].location

# # Set the location of the plane to be 1 meter below the NewMolecule on the Z axis
# plane.location = (new_molecule_location.x, new_molecule_location.y, new_molecule_location.z - 1)

# # Create a new material with a black color
# black_material = bpy.data.materials.new(name="BlackMaterial")
# black_material.diffuse_color = (0, 0, 0.041, 1)  # RGB and Alpha

# # Assign the material to the plane
# if plane.data.materials:
#     # If the plane already has a material, replace it
#     plane.data.materials[0] = black_material
# else:
#     # If the plane has no materials, append the new material
#     plane.data.materials.append(black_material)

#Render the image
path = "test.png"
bpy.context.scene.render.resolution_x = 1000 #These two lines set the resolution of the image, but they can be adjusted to change the output width and height too.
bpy.context.scene.render.resolution_y = 1000
bpy.context.scene.render.image_settings.file_format = "PNG" 
bpy.context.scene.render.filepath = path
bpy.ops.render.render(write_still=True)
bpy.data.images["Render Result"].save_render(filepath=bpy.context.scene.render.filepath)

# New code to rotate the image. This is not necessary for the script but I've left it in because I'm trying to figure out why the proteins sometimes look sideways. 
img = Image.open(path)
img_rotated = img.rotate(90, expand=True)  # Rotate and expand to fit the new orientation
img_rotated.save(path)  # Overwrite the original image or save as a new file