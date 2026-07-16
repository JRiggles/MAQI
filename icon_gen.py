from pathlib import Path

from PIL import Image, ImageDraw

ICON_SIZE = 19
ICON_PADDING = 3
RETINA_SCALE = 2
ANTIALIAS_SCALE = 8
OUTPUT_DIR = Path(__file__).parent / 'assets'
AQI_COLORS = [
    '#00e400', '#ffff00', '#ff7e00', '#ff0000', '#8f3f97', '#7e0023'
]

def create_circle_icon(
    fill_color: str,
    size: int = ICON_SIZE,
    padding: int = ICON_PADDING,
    antialias_scale: int = ANTIALIAS_SCALE,
) -> Image.Image:
    scaled_size = size * antialias_scale
    padding = max(0, min(padding, (size // 2) - 1))
    scaled_inset = padding * antialias_scale

    mask = Image.new('L', (scaled_size, scaled_size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse(
        (
            scaled_inset,
            scaled_inset,
            scaled_size - scaled_inset - 1,
            scaled_size - scaled_inset - 1,
        ),
        fill=255,
    )
    mask = mask.resize((size, size), resample=Image.Resampling.LANCZOS)

    icon = Image.new('RGBA', (size, size), fill_color)
    icon.putalpha(mask)
    return icon


def save_retina_pair(icon: Image.Image, stem: str) -> None:
    icon_1x = icon
    icon_2x = icon.resize(
        (ICON_SIZE * RETINA_SCALE, ICON_SIZE * RETINA_SCALE),
        resample=(Image.Resampling.LANCZOS),
    )
    icon_1x.save(OUTPUT_DIR / f'{stem}.png')
    icon_2x.save(OUTPUT_DIR / f'{stem}@2x.png')


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for i, color in enumerate(AQI_COLORS):
        icon = create_circle_icon(color)
        stem = f'aqi_{i + 1}'
        save_retina_pair(icon, stem)


if __name__ == '__main__':
    main()
