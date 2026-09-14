import io
import os

import qrcode

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# FONT HELPER
# ============================================================

def get_font(size, bold=False):
    """
    Find a usable font on Windows or Linux/PythonAnywhere.
    """

    if bold:
        font_candidates = [
            r"C:\Windows\Fonts\segoeuib.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        font_candidates = [
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

    for font_path in font_candidates:
        if os.path.exists(font_path):
            return ImageFont.truetype(
                font_path,
                size
            )

    return ImageFont.load_default()


# ============================================================
# CENTER TEXT
# ============================================================

def draw_centered_text(
    draw,
    text,
    y,
    font,
    fill,
    canvas_width
):
    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    text_width = bbox[2] - bbox[0]

    x = (
        canvas_width - text_width
    ) // 2

    draw.text(
        (x, y),
        text,
        font=font,
        fill=fill
    )


# ============================================================
# CREATE TABLE QR POSTER
# ============================================================

def create_table_qr_poster(
    table_number,
    menu_url,
    title="Group of BBN Coastal Pearl Samudrathali",
    message='Digital Menu - "Scan QR and check our menu"',
):
    """
    Creates a high-resolution printable PNG poster.

    Size:
        1240 x 1754 px

    Approx:
        A4 at 150 DPI
    """

    width = 1240
    height = 1754

    background = "#071923"
    white = "#effcff"
    muted = "#9bb9c1"
    cyan = "#67e8f9"
    teal = "#2dd4bf"
    gold = "#f6d365"

    image = Image.new(
        "RGB",
        (width, height),
        background
    )

    draw = ImageDraw.Draw(image)

    # --------------------------------------------------------
    # Decorative background circles
    # --------------------------------------------------------

    draw.ellipse(
        (-250, -250, 450, 450),
        fill="#0b3440"
    )

    draw.ellipse(
        (900, 1250, 1500, 1850),
        fill="#0b3038"
    )

    # --------------------------------------------------------
    # Outer poster border
    # --------------------------------------------------------

    draw.rounded_rectangle(
        (45, 45, width - 45, height - 45),
        radius=42,
        outline="#1d4b57",
        width=4
    )

    # --------------------------------------------------------
    # Fonts
    # --------------------------------------------------------

    eyebrow_font = get_font(
        28,
        bold=True
    )

    brand_font = get_font(
        72,
        bold=True
    )

    restaurant_font = get_font(
        38,
        bold=False
    )

    title_font = get_font(
        58,
        bold=True
    )

    message_font = get_font(
        31,
        bold=False
    )

    table_label_font = get_font(
        28,
        bold=True
    )

    table_font = get_font(
        76,
        bold=True
    )

    footer_font = get_font(
        23,
        bold=False
    )

    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    draw_centered_text(
        draw,
        "GROUP OF BBN",
        120,
        eyebrow_font,
        cyan,
        width
    )

    # Title is intentionally split into the established brand lines when possible.
    draw_centered_text(draw, "Coastal Pearl", 165, brand_font, white, width)

    draw_centered_text(
        draw,
        "Samudrathali Restaurant",
        255,
        restaurant_font,
        muted,
        width
    )

    # --------------------------------------------------------
    # DIGITAL MENU TITLE
    # --------------------------------------------------------

    draw_centered_text(draw, "DIGITAL MENU", 370, title_font, gold, width)
    draw_centered_text(draw, message[:42], 445, message_font, white, width)

    draw_centered_text(
        draw,
        "View our menu directly from your table",
        495,
        footer_font,
        muted,
        width
    )

    # --------------------------------------------------------
    # QR CODE
    # --------------------------------------------------------

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=14,
        border=4
    )

    qr.add_data(menu_url)

    qr.make(
        fit=True
    )

    qr_image = qr.make_image(
        fill_color="#071923",
        back_color="#ffffff"
    ).convert("RGB")

    # QR size
    qr_size = 760

    qr_image = qr_image.resize(
        (qr_size, qr_size),
        Image.Resampling.LANCZOS
    )

    qr_x = (
        width - qr_size
    ) // 2

    qr_y = 590

    # White QR card
    card_padding = 28

    draw.rounded_rectangle(
        (
            qr_x - card_padding,
            qr_y - card_padding,
            qr_x + qr_size + card_padding,
            qr_y + qr_size + card_padding
        ),
        radius=35,
        fill="#ffffff"
    )

    image.paste(
        qr_image,
        (qr_x, qr_y)
    )

    # --------------------------------------------------------
    # TABLE NUMBER
    # --------------------------------------------------------

    table_label_y = 1420

    draw_centered_text(
        draw,
        "TABLE",
        table_label_y,
        table_label_font,
        cyan,
        width
    )

    draw_centered_text(
        draw,
        str(table_number),
        table_label_y + 42,
        table_font,
        white,
        width
    )

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    draw_centered_text(
        draw,
        "Enjoy your meal 🌊",
        1570,
        footer_font,
        muted,
        width
    )

    # --------------------------------------------------------
    # Export PNG to memory
    # --------------------------------------------------------

    output = io.BytesIO()

    image.save(
        output,
        format="PNG",
        dpi=(150, 150),
        optimize=True
    )

    output.seek(0)

    return output