import bpy
import bmesh
import random


#Caches pivot information for sub-meshes (selected), based on a premade compund mesh's bounding box (active)

bl_info ={
    "name" : "Bake pivots selected to active",
    "blender" : (2,80,0),
    "category" : "Object"
}


NORMALIZE_POSITIONS = True
DEBUG = True



class PivotBaker(bpy.types.Operator):
    """Sub mesh pivot baker"""
    bl_idname = "object.bake_sub_pivots"
    bl_label = "Bake sub mesh pivots in vertex colors"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    def remap_range_01(self, value):
        return value * 0.5 + 0.5 if NORMALIZE_POSITIONS else value
    
    def calculate_cacheable_pivot(self, active_object, selected_object):
        bounding_box = active_object.dimensions if NORMALIZE_POSITIONS else (1,1,1)
        x = self.remap_range_01((selected_object.location.x - active_object.location.x) / bounding_box[0])
        y = self.remap_range_01((selected_object.location.y - active_object.location.y) / bounding_box[1])
        z = self.remap_range_01((selected_object.location.z - active_object.location.z) / bounding_box[2])
        
        if DEBUG:
            print(f"Bounding Box: {bounding_box} \n ObjectSpace Pivot: {selected_object.location.x - active_object.location.x} , {selected_object.location.y - active_object.location.y}, {selected_object.location.z - active_object.location.z} \t Result: {(x,y,z)}")  
        return (x,y,z)

    def execute(self, context):
        scene = context.scene
        
        CACHE_LAYER = "PIVOT_CACHE"

        selection = context.selected_objects #submeshes
        active = context.active_object #compund mesh

        if NORMALIZE_POSITIONS:
            if active.dimensions[0] <= 0 or active.dimensions[1] <= 0 or active.dimensions[2] <= 0:
                print('active object\'s bounding box is not correctly setup. Aborting')
                return {'FINISHED'}



        for obj in selection:
            if active == obj: 
                continue
            color = self.calculate_cacheable_pivot(active, obj)
            
            bm = bmesh.new()
            if CACHE_LAYER in obj.data.vertex_colors:
                obj.data.vertex_colors.remove(obj.data.vertex_colors[CACHE_LAYER])
            bm.from_mesh(obj.data)
            
            color_layer = bm.loops.layers.color.new(CACHE_LAYER)
            
            for face in bm.faces:
                for loop in face.loops:
                    loop[color_layer] = (color[0], color[1], color[2], random.uniform(0.0,1.0))
                    if DEBUG:
                        print(loop[color_layer])

            print(color_layer == None)
                    
                    
            bm.to_mesh(obj.data)
        
        print('Finished')
        return {'FINISHED'}
    
def menu_func(self, context):
    self.layout.operator(PivotBaker.bl_idname)
    
def register():
    bpy.utils.register_class(PivotBaker)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    print("Registered")
    
def unregister():
    bpy.utils.unregister_class(PivotBaker)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()
