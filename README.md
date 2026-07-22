# Session Grid Bot — chạy free bằng GitHub Actions (không cần server/PC)

Bot vẽ lưới 5x5, mỗi 30 phút random đánh dấu 5 ô, gửi ảnh vào nhóm Telegram.
GitHub sẽ tự động chạy script này giúp bạn theo lịch, hoàn toàn miễn phí.

**Lưu ý:** cách này KHÔNG có lệnh `/play`, `/history` tương tác trực tiếp
trong Telegram (vì không có tiến trình luôn lắng nghe). Lịch sử các phiên
được lưu trong file `history.json` ngay trong repo GitHub — bạn xem trực
tiếp trên GitHub bất cứ lúc nào.

## Bước 1: Tạo bot Telegram + lấy Chat ID

(Giống hướng dẫn trước)
1. Chat với **@BotFather** trên Telegram → `/newbot` → lấy **BOT_TOKEN**.
2. Thêm bot vào nhóm, gửi 1 tin nhắn bất kỳ trong nhóm.
3. Mở trình duyệt: `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Tìm `"chat":{"id": ...}` → đó là **CHAT_ID**.

## Bước 2: Tạo tài khoản GitHub (nếu chưa có)

Vào https://github.com/join, đăng ký miễn phí.

## Bước 3: Tạo repository mới

1. Vào https://github.com/new
2. Đặt tên repo, ví dụ `session-grid-bot`
3. Chọn **Private** (để người khác không xem được cấu hình/lịch sử của bạn) — vẫn dùng GitHub Actions free bình thường với repo private.
4. Bấm **Create repository**.

## Bước 4: Upload code lên repo

Cách dễ nhất — dùng giao diện web, không cần biết lệnh `git`:

1. Trong repo vừa tạo, bấm **"uploading an existing file"** (hoặc "Add file" → "Upload files").
2. Kéo thả toàn bộ các file mình gửi vào:
   - `send_session.py`
   - `requirements.txt`
   - `history.json`
   - `.github/workflows/session_bot.yml` (giữ nguyên cấu trúc thư mục `.github/workflows/` — nếu giao diện upload không giữ được thư mục con, xem "Cách dùng Git" bên dưới)
3. Bấm **Commit changes**.

### Cách dùng Git (nếu bạn quen dòng lệnh, đảm bảo giữ đúng cấu trúc thư mục)

```bash
git clone https://github.com/<username>/session-grid-bot.git
cd session-grid-bot
# copy 4 file/thư mục vào đây, giữ nguyên cấu trúc .github/workflows/session_bot.yml
git add .
git commit -m "Init session bot"
git push
```

## Bước 5: Cấu hình Secrets (BOT_TOKEN, CHAT_ID)

1. Trong repo, vào **Settings** → **Secrets and variables** → **Actions**.
2. Bấm **New repository secret**:
   - Name: `BOT_TOKEN` → Value: token bot của bạn → **Add secret**
   - Bấm New repository secret lần nữa:
   - Name: `CHAT_ID` → Value: chat id nhóm của bạn → **Add secret**

Secrets được mã hoá, không ai xem lại được kể cả bạn (chỉ dùng được trong workflow).

## Bước 6: Chạy thử thủ công để kiểm tra

1. Vào tab **Actions** trong repo.
2. Bấm workflow **"Send Session Grid"** ở cột trái.
3. Bấm **Run workflow** → **Run workflow** (nút xanh).
4. Đợi khoảng 20-30 giây, refresh trang, xem trạng thái chạy (dấu ✅ xanh là thành công, ❌ đỏ là lỗi — bấm vào xem log lỗi).
5. Kiểm tra nhóm Telegram xem đã nhận được ảnh chưa.

## Bước 7: Xong — để tự động chạy

Sau khi chạy thử thành công, workflow sẽ **tự động chạy mỗi 5 phút** theo lịch đã đặt trong file `.github/workflows/session_bot.yml` (`cron: "*/5 * * * *"`), không cần bạn làm gì thêm, không cần mở máy tính hay app nào cả.

## Xem lịch sử các phiên

Vào repo → mở file `history.json` → xem toàn bộ lịch sử (thời gian + ô trúng của từng phiên), tự động được cập nhật sau mỗi lần chạy.

## Lưu ý quan trọng

- **GitHub Actions free có giới hạn 2,000 phút chạy/tháng** cho repo Private (Public repo thì không giới hạn). Với lịch chạy **mỗi 30 phút** (48 lần/ngày × 30 ngày = 1,440 lần/tháng, mỗi lần tính tối thiểu 1 phút) → tốn khoảng **1,440 phút/tháng**, nằm trong hạn mức free, còn dư khoảng 560 phút phòng hờ.
- Nếu sau này muốn chạy dày hơn (vd mỗi 5-10 phút), nên chuyển repo sang **Public** (Actions minutes không giới hạn với public repo) — token/CHAT_ID vẫn an toàn vì nằm trong Secrets riêng, không lộ ra ngoài dù repo public.
- GitHub Actions cron **không đảm bảo chạy đúng giờ tuyệt đối**, có thể trễ 1-5 phút vào giờ cao điểm — đây là giới hạn chung của GitHub, không phải lỗi code.
