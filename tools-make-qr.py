# 포트폴리오 QR: 코코아·골드 팔레트, 둥근 모듈, 가운데 도넛
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import qrcode, os

URL = "https://mymama0928-hue.github.io/character-portfolio/"
OUT = r"C:\Users\angry\OneDrive\Desktop\캐릭터 크리에이터\포트폴리오\웹포트폴리오\assets"
COCOA = (43, 31, 28)
CREAM = (247, 238, 228)
GOLD = (201, 154, 82)
GOLD_L = (232, 201, 140)
SUGAR = (232, 166, 180)
INK = (58, 42, 34)

qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=1, border=0)
qr.add_data(URL)
qr.make(fit=True)
m = qr.get_matrix()
N = len(m)

S = 28          # 모듈 한 칸 픽셀
QZ = 4          # 여백(quiet zone) 모듈 수
size = (N + QZ * 2) * S


def finder_at(r, c):
    """파인더 패턴(모서리 큰 눈) 영역인지"""
    return (r < 7 and c < 7) or (r < 7 and c >= N - 7) or (r >= N - 7 and c < 7)


def rounded(d, box, rad, fill):
    d.rounded_rectangle(box, radius=rad, fill=fill)


def draw_qr(fg_data, fg_eye, bg, logo=True, square=False):
    img = Image.new("RGB", (size, size), bg)
    d = ImageDraw.Draw(img)
    off = QZ * S
    # 가운데 로고 자리 (H 보정: 전체의 ~16%)
    hole = int(N * 0.12) | 1
    h0, h1 = (N - hole) // 2, (N + hole) // 2
    for r in range(N):
        for c in range(N):
            if not m[r][c] or finder_at(r, c):
                continue
            if logo and h0 <= r <= h1 and h0 <= c <= h1:
                continue
            x, y = off + c * S, off + r * S
            if square:
                d.rectangle((x, y, x + S, y + S), fill=fg_data)
            else:
                d.rounded_rectangle((x, y, x + S, y + S), radius=int(S * 0.34), fill=fg_data)
    # 파인더: 둥근 네모 + 가운데 점
    for (r, c) in ((0, 0), (0, N - 7), (N - 7, 0)):
        x, y = off + c * S, off + r * S
        # 파인더는 각지게 유지 — 둥글리면 인식률이 크게 떨어짐(테스트로 확인)
        d.rectangle((x, y, x + 7 * S, y + 7 * S), fill=fg_eye)
        d.rectangle((x + S, y + S, x + 6 * S, y + 6 * S), fill=bg)
        d.rectangle((x + 2 * S, y + 2 * S, x + 5 * S, y + 5 * S), fill=fg_eye)
    if logo:
        # 가운데 도넛
        cx = size // 2
        rr = int((hole * S) * 0.46)
        d.ellipse((cx - rr - 6, cx - rr - 6, cx + rr + 6, cx + rr + 6), fill=bg)
        d.ellipse((cx - rr, cx - rr, cx + rr, cx + rr), fill=SUGAR)
        d.ellipse((cx - rr * 0.34, cx - rr * 0.34, cx + rr * 0.34, cx + rr * 0.34), fill=bg)
        sprinkles = [(-0.55, -0.2, 25), (0.1, -0.6, -20), (0.55, 0.15, 70), (-0.2, 0.58, -60), (0.35, 0.5, 15), (-0.5, 0.3, 80)]
        for sx, sy, ang in sprinkles:
            px, py = cx + sx * rr, cx + sy * rr
            d.line((px - 5, py, px + 5, py), fill=CREAM, width=5)
    return img


# 1) 인쇄·제출용 기본 QR (검정/흰색, 로고 없음 — 가장 잘 읽힘)
plain = draw_qr((0, 0, 0), (0, 0, 0), (255, 255, 255), logo=False, square=True)
plain.save(os.path.join(OUT, "qr-plain.png"))

# 2) 브랜드 QR (코코아 모듈 + 골드 눈 + 도넛)
brand = draw_qr(COCOA, GOLD, CREAM)
brand.save(os.path.join(OUT, "qr.png"))

# 3) 공유 카드 1080x1350
W, H = 1080, 1350
card = Image.new("RGB", (W, H), COCOA)
cd = ImageDraw.Draw(card)
for y in range(H):  # 아주 옅은 세로 그라데이션
    t = y / H
    cd.line((0, y, W, y), fill=(int(43 + 12 * t), int(31 + 9 * t), int(28 + 8 * t)))
f_lbl = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 24)
f_ttl = ImageFont.truetype("C:/Windows/Fonts/GARABD.TTF", 84)
f_nm = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 44)
f_sm = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 26)
f_url = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 24)


def spaced(draw, txt, font, xy, fill, sp, center_w=None):
    w = sum(draw.textlength(ch, font=font) + sp for ch in txt) - sp
    x, y = xy
    if center_w:
        x = (center_w - w) / 2
    for ch in txt:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + sp
    return w


spaced(cd, "AI CHARACTER CREATOR", f_lbl, (0, 110), (205, 187, 168), 6, center_w=W)
spaced(cd, "PORTFOLIO", f_ttl, (0, 156), GOLD_L, 7, center_w=W)

qcard = 640
qimg = brand.resize((qcard, qcard), Image.LANCZOS)
qx, qy = (W - qcard) // 2, 330
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(shadow).rounded_rectangle((qx - 24, qy - 24, qx + qcard + 24, qy + qcard + 24), radius=48, fill=(0, 0, 0, 120))
card = Image.alpha_composite(card.convert("RGBA"), shadow.filter(ImageFilter.GaussianBlur(24))).convert("RGB")
cd = ImageDraw.Draw(card)
plate = Image.new("RGB", (qcard + 48, qcard + 48), CREAM)
mask = Image.new("L", plate.size, 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, plate.size[0] - 1, plate.size[1] - 1), radius=48, fill=255)
card.paste(plate, (qx - 24, qy - 24), mask)
card.paste(qimg, (qx, qy))

ty = qy + qcard + 70
nm = "김지수"
cd.text(((W - cd.textlength(nm, font=f_nm)) / 2, ty), nm, font=f_nm, fill=CREAM)
sub = "SNS 마케터 & 콘텐츠 크리에이터"
cd.text(((W - cd.textlength(sub, font=f_sm)) / 2, ty + 66), sub, font=f_sm, fill=(205, 187, 168))
hint = "카메라로 스캔하면 포트폴리오가 열려요"
cd.text(((W - cd.textlength(hint, font=f_sm)) / 2, ty + 124), hint, font=f_sm, fill=GOLD_L)
u = URL.replace("https://", "")
cd.text(((W - cd.textlength(u, font=f_url)) / 2, ty + 172), u, font=f_url, fill=(150, 133, 118))
card.save(os.path.join(OUT, "qr-card.jpg"), quality=92, optimize=True)

print("modules", N, "version", qr.version)
for f in ("qr-plain.png", "qr.png", "qr-card.jpg"):
    p = os.path.join(OUT, f)
    print(f, os.path.getsize(p) // 1024, "KB", Image.open(p).size)
