# -*- coding: utf-8 -*-
"""Square crop + resize for profile avatars."""
from __future__ import annotations

import io


def crop_avatar(
    image_bytes: bytes,
    zoom_factor: float = 1.0,
    offset_x_pct: float = 0.0,
    offset_y_pct: float = 0.0,
    output_size: int = 300,
) -> bytes:
    from PIL import Image

    img = Image.open(io.BytesIO(image_bytes))
    if img.mode in ("RGBA", "LA"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1])
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    width, height = img.size
    min_dim = min(width, height)
    zoom = max(0.5, min(float(zoom_factor or 1.0), 2.5))
    crop_size = int(min_dim / zoom)
    crop_size = min(crop_size, width, height)
    crop_size = max(crop_size, 10)

    center_x = width / 2
    center_y = height / 2
    max_offset_x = (width - crop_size) / 2
    max_offset_y = (height - crop_size) / 2
    ox = max(-0.5, min(float(offset_x_pct or 0.0), 0.5))
    oy = max(-0.5, min(float(offset_y_pct or 0.0), 0.5))
    center_x += ox * 2 * max_offset_x
    center_y += oy * 2 * max_offset_y

    left = max(0, int(center_x - crop_size / 2))
    top = max(0, int(center_y - crop_size / 2))
    right = min(width, left + crop_size)
    bottom = min(height, top + crop_size)
    box = min(right - left, bottom - top)
    right = left + box
    bottom = top + box

    cropped = img.crop((left, top, right, bottom)).resize(
        (output_size, output_size), Image.Resampling.LANCZOS
    )
    out = io.BytesIO()
    cropped.save(out, format="PNG")
    return out.getvalue()
