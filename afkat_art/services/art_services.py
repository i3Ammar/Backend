from rest_framework import serializers

def validate_art_file(self , value):
    if value.size > 1024*1024*1024:
        raise serializers.ValidationError({ 'error':'Art Model file too large' })
    valid_extensions = ['gltf','glb',] # .obj ,.fbx  , .stl, others aren't supported until now we will do in the future
    ext = value.name.split('.')[-1].lower()
    if ext not in valid_extensions:
        raise serializers.ValidationError(f'Unsupported file extension.  Use: {', '.join(valid_extensions)}')

    return value
