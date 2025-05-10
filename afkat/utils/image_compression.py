# utils/image_compression.py
from PIL import Image
import io
import sys
from django.core.files.uploadedfile import InMemoryUploadedFile
import magic


def compress_image(image_file, max_size = 1200, quality = 80, format = None,
                   maintain_format = True, max_file_size_kb = None):
    """
    Compresses an image while maintaining aspect ratio.

    Args:
        image_file: Django uploaded file object
        max_size: Maximum dimension (width or height) in pixels
        quality: JPEG/WebP compression quality (1-100)
        format: Output format ('JPEG', 'PNG', 'WebP', etc.) or None to auto-detect
        maintain_format: If True, try to keep original format unless size constraints require JPEG
        max_file_size_kb: Target maximum file size in KB (approximate)

    Returns:
        Compressed InMemoryUploadedFile object
    """
    if not image_file:
        return image_file

    img = Image.open(image_file)

    original_format = img.format if maintain_format else None
    img_format = format or original_format or 'JPEG'

    if img_format.upper() == 'JPG':
        img_format = 'JPEG'

    if img_format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if 'transparency' in img.info:
            background.paste(img, mask = img.split()[3] if img.mode == 'RGBA' else None)
        else:
            background.paste(img)
        img = background

    width, height = img.size
    if width > max_size or height > max_size:
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))
        img = img.resize((new_width, new_height), Image.LANCZOS)

    output = io.BytesIO()

    if img_format == 'JPEG':
        mime_type = 'image/jpeg'
        file_ext = 'jpg'
        img.save(output, format = img_format, quality = quality, optimize = True)
    elif img_format == 'PNG':
        mime_type = 'image/png'
        file_ext = 'png'
        img.save(output, format = img_format, optimize = True)
    elif img_format == 'WEBP':
        mime_type = 'image/webp'
        file_ext = 'webp'
        img.save(output, format = img_format, quality = quality)
    else:
        mime_type = 'image/jpeg'
        file_ext = 'jpg'
        img.save(output, format = 'JPEG', quality = quality, optimize = True)

    if max_file_size_kb and img_format in ['JPEG', 'WEBP']:
        current_size = sys.getsizeof(output) / 1024
        current_quality = quality

        while current_size > max_file_size_kb and current_quality > 20:
            output = io.BytesIO()
            current_quality -= 5
            img.save(output, format = img_format, quality = current_quality, optimize = True)
            current_size = sys.getsizeof(output) / 1024

    output.seek(0)

    if '.' in image_file.name:
        original_name = '.'.join(image_file.name.split('.')[:-1])
    else:
        original_name = image_file.name

    new_filename = f"{original_name}.{file_ext}"

    return InMemoryUploadedFile(
        output,
        'ImageField',
        new_filename,
        mime_type,
        sys.getsizeof(output),
        None
    )