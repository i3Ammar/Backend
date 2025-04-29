# afkat_game/services/game_service.py

from afkat_game.models import GameRating
from rest_framework import serializers

def get_user_rating(game, user):
    if user.is_authenticated:
        try:
            rating = GameRating.objects.get(game=game, user=user)
            return rating.rating
        except GameRating.DoesNotExist:
            return None
    return None

def validate_cover_image(self , value):
    if value.size > 5*1024*1024:
        raise serializers.ValidationError({ 'error':'Image too large' })

    valid_extensions = ['jpg', 'jpeg', 'webp', 'png']
    ext = value.name.split('.')[-1].lower()
    if ext not in valid_extensions:
        raise serializers.ValidationError({ 'error':f'Unsupported file extension. Use: {", ".join(valid_extensions)}' })

def validate_game_file(self , value):
    if value.size > 1024*1024*1024:
        raise serializers.ValidationError({ 'error':'Game file too large' })
    valid_extensions = ['zip', 'rar','7z']
    ext = value.name.split('.')[-1].lower()
    if ext not in valid_extensions:
        raise serializers.ValidationError({ 'error':f'Unsupported file extension.  Use: {', '.join(valid_extensions)}' })

    return value



def process_webgl_upload(archive_file, game_id):
    import os
    import zipfile
    from django.conf import settings
    from django.core.files.storage import default_storage

    # Create a directory for this game's WebGL build
    webgl_dir = f"games/{game_id}/"

    file_name = archive_file.name.lower()

    if file_name.endswith('.zip'):
        # Process ZIP file
        with zipfile.ZipFile(archive_file) as z:
            for file_info in z.infolist():
                extracted_path = webgl_dir + file_info.filename
                if not file_info.is_dir():
                    with z.open(file_info) as source, default_storage.open(extracted_path, 'wb') as target:
                        target.write(source.read())

            # Return the full URL instead of just the path
            return default_storage.url(webgl_dir + "index.html")

    elif file_name.endswith('.7z'):
        # Process 7z file
        try:
            import py7zr
        except ImportError:
            raise ImportError("The 'py7zr' module is required to process 7z files. Install it with 'pip install py7zr'")

        # Create a temporary file to store the 7z content
        import tempfile
        import shutil

        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the uploaded file to a temporary location
            temp_archive_path = os.path.join(temp_dir, "temp_archive.7z")
            with open(temp_archive_path, 'wb') as f:
                f.write(archive_file.read())

            # Extract the archive
            with py7zr.SevenZipFile(temp_archive_path, 'r') as archive:
                archive.extractall(path=temp_dir)

            # Copy extracted files to storage
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file == "temp_archive.7z":
                        continue

                    rel_path = os.path.relpath(os.path.join(root, file), temp_dir)
                    extracted_path = webgl_dir + rel_path

                    with open(os.path.join(root, file), 'rb') as source, default_storage.open(extracted_path, 'wb') as target:
                        target.write(source.read())

            # Return the full URL instead of just the path
            return default_storage.url(webgl_dir + "index.html")

    else:
        raise ValueError("Unsupported archive format. Only ZIP, and 7Z files are supported.")


    # elif file_name.endswith('.rar'):   #rar cor the  futur
    #     # Process RAR file
    #     try:
    #         import rarfile
    #         # You can specify the path to unrar if it's not in PATH
    #         # rarfile.UNRAR_TOOL = r"C:\path\to\unrar.exe"  # Uncomment and set path if needed
    #     except ImportError:
    #         raise ImportError("The 'rarfile' module is required to process RAR files. Install it with 'pip install rarfile'")
    #
    #     # Note: rarfile requires the unrar tool to be installed on your system
    #     with rarfile.RarFile(archive_file) as r:
    #         for file_info in r.infolist():
    #             extracted_path = webgl_dir + file_info.filename
    #             if not file_info.is_dir():
    #                 with r.open(file_info) as source, default_storage.open(extracted_path, 'wb') as target:
    #                     target.write(source.read())
