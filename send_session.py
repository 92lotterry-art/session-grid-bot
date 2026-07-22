"""
Session Grid Sender (one-shot script cho GitHub Actions)
-----------------------------------------------------------
Script này CHẠY 1 LẦN rồi thoát (không giữ tiến trình chạy nền):
  1. Random chọn 5/25 ô trong lưới 5x5.
  2. Vẽ thành ảnh PNG.
  3. Gửi ảnh vào nhóm/kênh Telegram (qua Bot API, dùng requests, không cần
     thư viện python-telegram-bot).
  4. Lưu lại phiên đó vào file history.json (nằm trong repo, được GitHub
     Actions commit lại sau mỗi lần chạy để giữ lịch sử).

Biến môi trường bắt buộc (set qua GitHub Secrets, xem README):
  BOT_TOKEN
  CHAT_ID
"""

import os
import sys
import json
import random
import requests
from datetime import datetime, timezone, timedelta
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# ----------------------- CONFIG -----------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
GRID_ROWS = 5
GRID_COLS = 5
NUM_CELLS = GRID_ROWS * GRID_COLS
NUM_MARKED = 5
HISTORY_PATH = os.path.join(os.path.dirname(__file__), "history.json")
VN_TZ = timezone(timedelta(hours=7))  # giờ Việt Nam
# --------------------------------------------------------


def load_history():
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(history):
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def draw_grid_image(marked_cells, session_id, now):
    cell_size = 130
    gap = 10
    padding = 20
    header_height = 60
    grid_w = cell_size * GRID_COLS + gap * (GRID_COLS - 1)
    grid_h = cell_size * GRID_ROWS + gap * (GRID_ROWS - 1)
    width = grid_w + padding * 2
    height = grid_h + padding * 2 + header_height

    bg_color = (24, 26, 32)
    card_color = (76, 110, 219)       # xanh dương (thẻ chưa trúng)
    card_shadow = (55, 82, 173)       # xanh đậm hơn (đổ bóng đáy thẻ)
    marked_color = (255, 178, 26)     # cam/vàng (thẻ trúng)
    marked_shadow = (204, 133, 0)
    text_color = (235, 235, 235)
    q_color = (110, 140, 230)         # màu dấu ? mờ trên nền xanh
    marked_text_color = (40, 24, 0)

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font_header = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26
        )
        font_q = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(cell_size * 0.5)
        )
        font_num = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(cell_size * 0.4)
        )
    except Exception:
        font_header = font_q = font_num = ImageFont.load_default()

    header_text = f"Phien #{session_id}  -  {now.strftime('%H:%M:%S %d/%m/%Y')}"
    bbox = draw.textbbox((0, 0), header_text, font=font_header)
    text_w = bbox[2] - bbox[0]
    draw.text(((width - text_w) / 2, 15), header_text, fill=text_color, font=font_header)

    # đánh số 1..5 cho các ô trúng theo thứ tự ngẫu nhiên (không phải theo vị trí ô)
    order_map = {cell: idx + 1 for idx, cell in enumerate(marked_cells)}

    grid_top = header_height
    shadow_h = 10
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            cell_num = row * GRID_COLS + col + 1
            x0 = padding + col * (cell_size + gap)
            y0 = grid_top + row * (cell_size + gap)
            x1 = x0 + cell_size
            y1 = y0 + cell_size

            is_marked = cell_num in order_map
            base = marked_color if is_marked else card_color
            shadow = marked_shadow if is_marked else card_shadow

            # đổ bóng đáy thẻ
            draw.rounded_rectangle([x0, y0 + shadow_h, x1, y1 + shadow_h], radius=18, fill=shadow)
            # thân thẻ
            draw.rounded_rectangle([x0, y0, x1, y1 - shadow_h], radius=18, fill=base)

            if is_marked:
                label = str(order_map[cell_num])
                font = font_num
                fill = marked_text_color
            else:
                label = "?"
                font = font_q
                fill = q_color

            lbbox = draw.textbbox((0, 0), label, font=font)
            lw, lh = lbbox[2] - lbbox[0], lbbox[3] - lbbox[1]
            tx = x0 + (cell_size - lw) / 2
            ty = y0 + (cell_size - shadow_h - lh) / 2 - lbbox[1]
            draw.text((tx, ty), label, fill=fill, font=font)

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def send_photo_telegram(image_buf, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    files = {"photo": ("session.png", image_buf, "image/png")}
    data = {"chat_id": CHAT_ID, "caption": caption}
    resp = requests.post(url, data=data, files=files, timeout=30)
    resp.raise_for_status()
    return resp.json()


def main():
    if not BOT_TOKEN or not CHAT_ID:
        print("Thiếu BOT_TOKEN hoặc CHAT_ID (biến môi trường / GitHub Secrets).")
        sys.exit(1)

    history = load_history()
    session_id = (history[-1]["id"] + 1) if history else 1
    marked = sorted(random.sample(range(1, NUM_CELLS + 1), NUM_MARKED))
    now = datetime.now(VN_TZ)

    image_buf = draw_grid_image(marked, session_id, now)

    # ====== TEXT MẪU - BẠN SỬA LẠI Ở ĐÂY THEO Ý MÌNH ======
    # Mỗi dòng dưới đây sẽ hiện thành 1 dòng riêng trong caption Telegram.
    # Muốn thêm dòng: thêm 1 dòng f"..." mới vào list.
    # Muốn xoá dòng: xoá dòng đó khỏi list.
    extra_lines = [
        "👉 Chúc bạn may mắn!",
        "👉 Admin: @thaotranggroup",
        "📢 Nhận khuyến măi mỗi ngày.",
        "📢 Theo dõi kênh để không bỏ lỡ phiên mới.",
    ]
    # ==========================================================

    caption_lines = [
        f"🎲 Phiên #{session_id}",
        f"Ô trúng: {', '.join(map(str, marked))}",
        *extra_lines,
    ]
    caption = "\n".join(caption_lines)

    send_photo_telegram(image_buf, caption)

    history.append(
        {
            "id": session_id,
            "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "marked_cells": marked,
        }
    )
    # chỉ giữ 500 phiên gần nhất để file không phình to
    history = history[-500:]
    save_history(history)

    print(f"Đã gửi phiên #{session_id}, ô trúng: {marked}")


if __name__ == "__main__":
    main()
