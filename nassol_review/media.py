"""Locally render five square text cards and an optional vertical MP4.
No external images, paid services, or publishing. Requires Pillow; video requires FFmpeg.
"""
from pathlib import Path
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont

SIZE = 1080
FONT_CANDIDATES = [
    "C:/Windows/Fonts/malgun.ttf",
    "C:/Windows/Fonts/malgunbd.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

def font(size: int):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    raise RuntimeError("Korean-capable font not found. Install a Korean font.")

def wrap(draw, text: str, f, max_width: int):
    lines = []
    for paragraph in text.splitlines():
        line = ""
        for char in paragraph:
            if draw.textbbox((0, 0), line + char, font=f)[2] > max_width and line:
                lines.append(line)
                line = char
            else:
                line += char
        lines.append(line)
    return lines

def cards(data: dict, folder: Path) -> list[Path]:
    editorial = data.get("editorial", {})
    sources = data["sources"]
    claims = [str(s["claim"]) for s in sources]
    items = [
        ("방송 이후", str(data["person"])),
        ("공개된 이야기", claims[0]),
        ("확인된 내용", claims[1] if len(claims) > 1 else claims[0]),
        ("지니지구의 시선", str(editorial["take"])),
        ("마지막 생각", str(editorial["ending"])),
    ]
    out = folder / "cards"
    out.mkdir(exist_ok=True)
    result = []
    for i, (heading, body) in enumerate(items, 1):
        im = Image.new("RGB", (SIZE, SIZE), (18, 24, 38))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((65, 65, 1015, 1015), radius=38, outline=(93, 116, 154), width=3)
        d.text((115, 145), f"{i:02d} / 05", font=font(35), fill=(144, 185, 240))
        d.text((115, 245), heading, font=font(65), fill=(255, 255, 255))
        lines = wrap(d, body, font(48), 825)
        if len(lines) > 9:
            raise ValueError(f"Card {i} text too long; shorten the input before rendering")
        y = 400
        for line in lines:
            d.text((115, y), line, font=font(48), fill=(231, 236, 245))
            y += 72
        d.text((115, 935), "지니지구 | 검수용 · 출처 확인 필요", font=font(27), fill=(153, 163, 180))
        path = out / f"card_{i:02d}.png"
        im.save(path)
        result.append(path)
    return result

def video(card_paths: list[Path], folder: Path) -> Path | None:
    exe = shutil.which("ffmpeg")
    if not exe:
        return None
    concat = folder / "video_inputs.txt"
    # Paths generated locally, not supplied by the user.
    lines = []
    for p in card_paths:
        lines.extend([f"file '{p.as_posix()}'", "duration 3"])
    lines.append(f"file '{card_paths[-1].as_posix()}'")
    concat.write_text("\n".join(lines) + "\n", encoding="utf-8")
    dest = folder / "nassol_short.mp4"
    cmd = [exe, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
           "-i", str(concat), "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=0x121826,format=yuv420p",
           "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-movflags", "+faststart", str(dest)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=180)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError("FFmpeg could not render the video") from exc
    return dest
