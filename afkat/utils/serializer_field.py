# utils/serializer_fields.py
from rest_framework import serializers
from .image_compression import compress_image


class CompressedImageField(serializers.ImageField):
    """
    A Django REST Framework Field that automatically compresses images.
    """

    def __init__(self, *args, **kwargs):
        self.max_size = kwargs.pop('max_size', 1200)
        self.quality = kwargs.pop('quality', 80)
        self.format = kwargs.pop('format', None)
        self.maintain_format = kwargs.pop('maintain_format', True)
        self.max_file_size_kb = kwargs.pop('max_file_size_kb', None)
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        file = super().to_internal_value(data)
        return compress_image(
            file,
            max_size = self.max_size,
            quality = self.quality,
            format = self.format,
            maintain_format = self.maintain_format,
            max_file_size_kb = self.max_file_size_kb
        )