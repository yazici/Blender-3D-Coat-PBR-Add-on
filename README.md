# Blender-3D-Coat-PBR-Add-on
This Add-On for Blender allows you to import 3D Coat PBR material into Blender. This Add-on supports Blender’s Cycles/Eevee renderer.

#### **How to install**

Download the .zip and unpack it.

In Blender:

- Open File menu
- User Preferences …
- Open the “Add-ons” tab
- Click on the “Install Add-on from File…” button at the bottom
- Choose the ‘3dCoatPBRImporter.py’ file
- Activate the newly added plugin (filter for ‘coat’ if you can’t find it)

#### **How to use**

Export your model from 3D Coat like so:

- ‘File’ => ‘Export Objects & Textures
- Check the following ONLY (and select the Blender Export Preset):
  - Export Color
  - Export Roughness
  - Export Metalness
  - Export Tangent Normal Map
  - ExportAO
  - ExportCurvature
- In Blender import the mesh you exported via File => import => .obj/.fbx
- Select the object you want to apply the new material to
- Go to File => Import => 3D Coat PBR material (.tga/.png./bmp)
- Choose your model in the file dialog browser. The textures/maps must be in the same directory
- If the material doesn’t show up, check the material tab and delete the standard material created by the mesh import (or delete the .mtl file that 3D Coat created before importing the object/mesh)

More infos can be found here: https://irrgeist.de/blender-3d-coat-pbr-import-add-on/
