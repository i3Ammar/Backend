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
    if value:
        if value.size > 5*1024*1024:
            raise serializers.ValidationError({ 'error':'Image too large' })

        valid_extensions = ['jpg', 'jpeg', 'webp', 'png']
        ext = value.name.split('.')[-1].lower()
        if ext not in valid_extensions:
            raise serializers.ValidationError({ 'error':f'Unsupported file extension. Use: {", ".join(valid_extensions)}' })
    else :
        raise serializers.ValidationError({'error':'thumbnail is required' })

def validate_game_file(self , value):
    if value.size > 1024*1024*1024:
        raise serializers.ValidationError({ 'error':'Game file too large' })
    valid_extensions = ['zip','7z']
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
            # Consider logging this error as well
            raise ImportError("The 'py7zr' module is required to process 7z files. Install it with 'pip install py7zr'")

        import tempfile
        import os
        import shutil
        from django.core.files.storage import default_storage

        # Ensure the file pointer is at the beginning before reading
        archive_file.seek(0)

        # Create a temporary directory to work in
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a temporary file path within the temp directory
            temp_archive_path = os.path.join(temp_dir, "temp_archive.7z")

            # Save the uploaded file's content to the temporary file
            try:
                with open(temp_archive_path, 'wb') as f:
                    # Read from the uploaded file and write to the temporary file
                    shutil.copyfileobj(archive_file, f)
            except Exception as e:
                # Handle potential errors during file saving
                raise RuntimeError(f"Failed to save uploaded file to temporary storage: {e}")

            # Now, extract the archive using the path to the temporary file
            try:
                with py7zr.SevenZipFile(temp_archive_path, 'r') as archive:
                    archive.extractall(path=temp_dir)
            except py7zr.Bad7zFile:
                # Handle invalid 7z file error
                raise py7zr.Bad7zFile("The uploaded file is not a valid 7z archive or is corrupted.")
            except Exception as e:
                # Catch other potential exceptions during extraction
                raise RuntimeError(f"Failed to extract 7z archive: {e}")


            # Copy extracted files to storage
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    # Skip the temporary archive file itself if it's listed (it shouldn't be typically)
                    if os.path.join(root, file) == temp_archive_path:
                        continue

                    rel_path = os.path.relpath(os.path.join(root, file), temp_dir)
                    extracted_path = os.path.join(webgl_dir, rel_path).replace("\\", "/") # Ensure forward slashes

                    # Ensure the target directory exists in storage (optional, depends on storage backend)
                    target_dir = os.path.dirname(extracted_path)
                    if target_dir and not default_storage.exists(target_dir):
                        # Logic to create directories in storage if needed
                        # This might involve recursive calls or specific storage methods
                        # For basic FileSystemStorage, default_storage.open often handles it
                        pass

                    with open(os.path.join(root, file), 'rb') as source, default_storage.open(extracted_path, 'wb') as target:
                        shutil.copyfileobj(source, target) # Use shutil.copyfileobj for efficiency

            # Return the full URL instead of just the path
            index_html_path = os.path.join(webgl_dir, "index.html").replace("\\", "/") # Ensure forward slashes
            return default_storage.url(index_html_path)
            # return default_storage.url(webgl_dir + "index.html")

    else:
        raise ValueError("Unsupported archive format. Only ZIP, and 7Z files are supported.")


    # elif file_name.endswith('.rar'):   #rar cor the  future
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
