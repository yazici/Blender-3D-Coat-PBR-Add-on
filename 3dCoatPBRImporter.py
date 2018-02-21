#### 3D Coat PBR to Blender Principled BSDF V 0.7
#### Plugin to import 3D Coat's generated PBR material files to Blender's Principal BSDF shader
####
####            DO WHAT THE F**K YOU WANT TO PUBLIC LICENSE
####                    Version 2, December 2004
####
#### Copyright (C) 2004 Sam Hocevar
####  14 rue de Plaisance, 75014 Paris, France
#### Everyone is permitted to copy and distribute verbatim or modified
#### copies of this license document, and changing it is allowed as long
#### as the name is changed.
####
####            DO WHAT THE F**K YOU WANT TO PUBLIC LICENSE
####   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
####
####  0. You just DO WHAT THE F**K YOU WANT TO.
#########################################################################


bl_info = {
    'name': "3D Coat PBR material",
    'category': "Import",
    'author': 'Marcel Meisner (Haunted)',
    'version': (0, 7, 0),
    'blender': (2, 79, 0),
    'location': 'File > Import > 3D Coat PBR material',
    'description': "Import 3D Coat's generated PBR material files to Blender's Principal BSDF shader",
    'warning': '',
    'support': 'COMMUNITY',
}

import bpy
import os
from collections import namedtuple
from enum import Enum
import glob

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

Simple3DCoatKey = 'io_simple_3dcoat'

class ImportFilesCollection(bpy.types.PropertyGroup):
    name = StringProperty(
            name="File Path",
            description="Filepath used for importing the file",
            maxlen=1024,
            subtype='FILE_PATH',
            )
bpy.utils.register_class(ImportFilesCollection)

class Coat3DPanelAddOn(bpy.types.Panel):
    bl_label = "3D Coat PBR"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Ex'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        if hasattr(scene, 'simple3Dcoat'):
            simple3Dcoat = bpy.context.scene.simple3Dcoat

            # GUI
            row = layout.row()
            row.label(text="Update Material")
            row = layout.row()
            row.operator("pbr_import.simple_3d_coat", text="Import")
            row.operator("pbr_export.simple_3d_coat", text="Export")
            
            bpy.utils.register_class(Coat3DPanelAddOn)


class EMapType(Enum):
    diffuse     = 1
    metallic    = 2
    roughness   = 3
    normal      = 4
    
AvailableMaps = namedtuple('AvailableMaps', 'diffuse metallic roughness normal')

class ImportTex(bpy.types.Operator):
    bl_idname = "pbr_import.simple_3d_coat"
    bl_label = "Import PBR"
    bl_description = "Imports all PBR textures"

    def invoke(self, context, event):
        self.report({'ERROR'},'Not yet implemented')
        return {'CANCELLED'}
    
        # Addon Preferences
        user_preferences = context.user_preferences
        if Simple3DCoatKey in user_preferences.addons:
            addon_prefs = user_preferences.addons[Simple3DCoatKey].preferences
            print(addon_prefs.exchangedir)
        else:
            self.report({'ERROR'},'Please install Simple3DCoat AppLink.')

        return {'FINISHED'}
bpy.utils.register_class(ImportTex)

class ExportTex(bpy.types.Operator):
    bl_idname = "pbr_export.simple_3d_coat"
    bl_label = "Export PBR"
    bl_description = "Exports all PBR textures in the objects shader"

    def invoke(self, context, event):
        self.report({'ERROR'},'Not yet implemented')
        return {'CANCELLED'}
    
        user_preferences = context.user_preferences
        if Simple3DCoatKey in user_preferences.addons:
            addon_prefs = user_preferences.addons[Simple3DCoatKey].preferences
            print(addon_prefs.exchangedir)
        else:
            self.report({'ERROR'},'Please install Simple3DCoat AppLink.')

        return {'FINISHED'}
bpy.utils.register_class(ExportTex)

def CreatePBRMaterial(obj, availableMaps, useOldBlender):
    matName = obj.name + '_3d_coat_pbr'

    print("Creating material '" + matName + "'.")
    
    mat = bpy.data.materials.new(matName)
    mat.use_nodes = True  
    obj.data.materials.append(mat)
    
    material_output = mat.node_tree.nodes.get("Material Output")
    if useOldBlender:
        pbrNode = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        mat.node_tree.links.new(pbrNode.outputs[0], material_output.inputs[0])
        mat.node_tree.nodes.remove(mat.node_tree.nodes.get('Diffuse BSDF'))
    else:
        pbrNode = mat.node_tree.nodes.get("Principled BSDF")
    
    material_output.location = 200,0
    
    if(availableMaps.diffuse != None):
        AddTexture(mat, pbrNode, EMapType.diffuse, availableMaps.diffuse)
    if(availableMaps.metallic != None):
        AddTexture(mat, pbrNode, EMapType.metallic, availableMaps.metallic)
    if(availableMaps.roughness != None):
        AddTexture(mat, pbrNode, EMapType.roughness, availableMaps.roughness)
    if(availableMaps.normal != None):
        AddTexture(mat, pbrNode, EMapType.normal, availableMaps.normal)

          
def AddTexture(material, pbrNode, type, mapPath):
    material_output = material.node_tree.nodes.get('Material Output')
    tree = material.node_tree
    
    if type == EMapType.diffuse:
        print('Adding diffuse map.')
        
        node = CreateNewTextureNode(material, -300, 200, mapPath)
        node.label = 'Albedo/Diffuse'
        
        tree.links.new(node.outputs[0], pbrNode.inputs[0])
    elif type == EMapType.metallic:
        print('Adding metallic map.')
        
        node = CreateNewTextureNode(material, -800, -100, mapPath)
        rgbNode = CreateNewRGBCurveNode(material, -600, -100)
        bwNode = CreateNewRGBToBWNode(material, -300, -100)
        
        node.color_space = "NONE"
        node.label = 'Metallic'
        
        tree.links.new(node.outputs[0], rgbNode.inputs[1])
        tree.links.new(rgbNode.outputs[0], bwNode.inputs[0])
        tree.links.new(bwNode.outputs[0], pbrNode.inputs[4])
        
    elif type == EMapType.roughness:
        print('Adding roughness map.')
        
        node = CreateNewTextureNode(material, -800, -400, mapPath)
        rgbNode = CreateNewRGBCurveNode(material, -600, -400)
        bwNode = CreateNewRGBToBWNode(material, -300, -400)
        
        node.color_space = "NONE"
        node.label = 'Roughness'
        
        tree.links.new(node.outputs[0], rgbNode.inputs[1])
        tree.links.new(rgbNode.outputs[0], bwNode.inputs[0])
        tree.links.new(bwNode.outputs[0], pbrNode.inputs[7])
    elif type == EMapType.normal:
        print('Adding normal map.')
        
        nm_node = CreateNewNormalMapNode(material, -300, -700, mapPath)
        node = CreateNewTextureNode(material, -500, -700, mapPath)
        
        node.color_space = "NONE"
        node.label = 'Normal'
        
        tree.links.new(node.outputs[0], nm_node.inputs[1])
        tree.links.new(nm_node.outputs[0], pbrNode.inputs["Normal"])

      
def CreateNewTextureNode(material, x, y, imgPath):
        node = material.node_tree.nodes.new('ShaderNodeTexImage')
        node.image = bpy.data.images.load(imgPath)
        node.location= x, y
        return node


def CreateNewNormalMapNode(material, x, y, imgPath):
        node = material.node_tree.nodes.new('ShaderNodeNormalMap')
        node.location= x, y
        return node
    
    
def CreateNewRGBToBWNode(material, x, y):
        node = material.node_tree.nodes.new('ShaderNodeRGBToBW')
        node.location= x, y
        return node
    
    
def CreateNewRGBCurveNode(material, x, y):
        node = material.node_tree.nodes.new('ShaderNodeRGBCurve')
        node.location= x, y
        return node

def ExecuteImport(self, availableMaps):
        blenderVersion = None
        useOldBlender = True
        
        print(bpy.app.version[0])
        if (2, 80, 3) >= bpy.app.version:
            blenderVersion = bpy.context.scene.render.engine
        else:
            blenderVersion = bpy.context.workspace.view_render.engine
            useOldBlender = False
        
        if (blenderVersion != 'CYCLES') and (blenderVersion != 'BLENDER_EEVEE'):
            self.report({'ERROR'},'Add-on works with Cycles and Eevee Renderer only (for now).')
            return {'CANCELLED'}

        #Check for selected objects
        layerIndex = 0  #Chosen layer
        
        if useOldBlender:
            objects = bpy.context.scene.objects
            selectedObjects = [ob for ob in objects if ob.layers[layerIndex] 
            and ob.select 
            and ob.type == 'MESH']
        else:
            objects = bpy.context.scene_collection.objects
            selectedObjects = [ob for ob in objects if ob.select_get()
            and ob.type == 'MESH']
            
        if len(selectedObjects) > 0:
            #Create material
            for obj in selectedObjects:
                CreatePBRMaterial(obj, availableMaps, useOldBlender)
        else:
            msg = 'No object selected to import the PBR material to.'
            self.report({'ERROR'},msg)
            print(msg)
            return {'CANCELLED'}
            
        return {'FINISHED'}
    
class Import3DCoatPBR(Operator, ImportHelper):
    """Generate a Principled BSDF material for each selected object from 3D Coat's exported PBR files."""
    bl_idname = "node.pbr_3dcoat"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import 3DCoat PBR maps"

    # ImportHelper mixin class uses this
    filename_ext    = ".obj"
    
    filter_glob = StringProperty(
            default="*.obj;*.fbx",
            options={'HIDDEN'},
            )
            
    files = bpy.props.CollectionProperty(type=ImportFilesCollection)
    print(bpy.app.version)
    def execute(self, context):
            
        for i, f in enumerate(self.files, 1):
            suffix_color    = 'color'
            suffix_metal    = 'metalness'
            suffix_rough    = 'rough'
            suffix_nmap     = 'nmap'
    
            # Setup base filename and base path
            filename = os.path.splitext(f.name)[0]
            fdir = os.path.dirname(self.properties.filepath)
            filepath = os.path.join(fdir,filename)
            
            extension = '.tga'
            pathCheckName = filepath + '_*_' + suffix_color
            
            if len(glob.glob(pathCheckName + '.tga')) > 0:
                extension = '.tga'
            elif len(glob.glob(pathCheckName + '.png')) > 0:
                extension = '.png'
            elif len(glob.glob(pathCheckName + '.bmp')) > 0:
                extension = '.bmp'
                
            # Flags for textures
            hasDiffuse      = False
            hasMetallic     = False
            hasRoughness    = False
            hasNormalmap    = False
            
            # Search for these files on disc
            diffuse     = glob.glob(filepath + '_*_' + suffix_color + extension)
            metallic    = glob.glob(filepath + '_*_' + suffix_metal + extension)
            roughness   = glob.glob(filepath + '_*_' + suffix_rough + extension)
            normalmap   = glob.glob(filepath + '_*_' + suffix_nmap + extension)
            
            diffuse = diffuse[0] if len(diffuse) > 0 else ''
            metallic = metallic[0] if len(metallic) > 0 else ''
            roughness = roughness[0] if len(roughness) > 0 else ''
            normalmap = normalmap[0] if len(normalmap) > 0 else ''
            
            # Check if files are existing
            print("Searching PBR maps...")
            availableMaps = AvailableMaps(
                diffuse if os.path.isfile(diffuse) else None, 
                metallic if os.path.isfile(metallic) else None, 
                roughness if os.path.isfile(roughness) else None, 
                normalmap if os.path.isfile(normalmap) else None,
                )
            
            #Output
            print("Diffuse map: \t" + ("found=" + availableMaps.diffuse  if availableMaps.diffuse != None else "not found!"))
            print("Metallic map: \t" + ("found=" + availableMaps.metallic  if availableMaps.metallic != None  else "not found!"))
            print("Roughness map: \t" + ("found=" + availableMaps.roughness if availableMaps.roughness != None else "not found!"))
            print("Normal map: \t" + ("found=" + availableMaps.normal if availableMaps.normal != None  else "not found!"))

            ExecuteImport(self, availableMaps)
            
        return {'FINISHED'}


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(Import3DCoatPBR.bl_idname, text="3D Coat PBR material (.tga/.png./bmp)")


def register():
    bpy.utils.register_class(Import3DCoatPBR)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(Import3DCoatPBR)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
    
    bpy.ops.node.pbr_3dcoat('INVOKE_DEFAULT')