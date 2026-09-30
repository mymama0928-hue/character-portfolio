# 지수랩 제안서 섹션(work08) 시트 만들기 — 기존 포트폴리오화.png 섹션과 같은 스타일
# 실행: python tools-build-work08.py  (웹포트폴리오 폴더에서)
import fitz, os, json
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(ROOT, "assets")
PDF = os.path.join(ROOT, "AI 콘텐츠 캐릭터 브랜딩 제안서.pdf")
SKETCH = os.path.join(ROOT, "캐릭터2 명_아이디_처음이.png")

BG = (225, 212, 188)      # 시트 배경
TEAL = (38, 124, 148)
CAP = (40, 40, 40)

# 1) PDF 페이지를 고해상도 JPG로 (탭해서 크게 보는 용도)
doc = fitz.open(PDF)
pages = []
for i, p in enumerate(doc):
    pix = p.get_pixmap(dpi=150)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    im.save(os.path.join(A, f"proposal-{i+1:02d}.jpg"), quality=86, optimize=True)
    pages.append(im)

# 2) 시트 합성 (2배 해상도: 2784px 폭)
SC = 2
W = 1392 * SC
M = 53 * SC                      # 좌우 여백 (원본 시트 기준 53px)


def noto(size, weight):
    f = ImageFont.truetype("C:/Windows/Fonts/NotoSansKR-VF.ttf", size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


f_ttl = noto(28 * SC, "Bold")
f_cap = noto(12 * SC, "Regular")

sketch = Image.open(SKETCH).convert("RGB")

gap = 30 * SC
row1_h = 370 * SC
sk_w = int(sketch.width * row1_h / sketch.height)
cover_w = int(pages[0].width * row1_h / pages[0].height)
row1_w = sk_w + gap + cover_w
x1 = (W - row1_w) // 2

thumb_w = (W - 2 * M - 2 * gap) // 3
thumb_h = int(thumb_w * pages[0].height / pages[0].width)

top = 60 * SC
y_title = top + 40 * SC
y_row1 = y_title + 75 * SC
y_cap1 = y_row1 + row1_h + 14 * SC
y_row2 = y_cap1 + 50 * SC
y_cap2 = y_row2 + thumb_h + 14 * SC
y_row3 = y_cap2 + 50 * SC
y_cap3 = y_row3 + thumb_h + 14 * SC
H = y_cap3 + 60 * SC

sheet = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(sheet)

# 왼쪽 위 아이콘: 아이디 얼굴
icon = sketch.crop((235, 95, 425, 285)).resize((80 * SC, 80 * SC), Image.LANCZOS)
sheet.paste(icon, (M - 10 * SC, top - 30 * SC))

# 오른쪽 위 헤더: 이전 시트(work05)의 헤더를 픽셀 그대로 복사 → 글꼴·밑줄이 완전히 같음
ref = Image.open(os.path.join(A, "work05.jpg")).convert("RGB")
hdr_crop = ref.crop((840, 52, 1392, 110))
hdr_img = hdr_crop.resize((hdr_crop.width * SC, hdr_crop.height * SC), Image.LANCZOS)
sheet.paste(hdr_img, (W - hdr_img.width, 52 * SC))

# 가운데 제목
ttl = "- 지수랩 AI 콘텐츠 캐릭터 브랜딩 제안서 -"
tw = d.textlength(ttl, font=f_ttl)
d.text(((W - tw) / 2, y_title), ttl, font=f_ttl, fill=TEAL)


def paste_fit(im, box):
    x, y, w, h = box
    sheet.paste(im.resize((w, h), Image.LANCZOS), (x, y))
    return box


def caption(text, cx, y):
    tw = d.textlength(text, font=f_cap)
    d.text((cx - tw / 2, y), text, font=f_cap, fill=CAP)


spots = []

# 1행: 드로잉 + 표지
paste_fit(sketch, (x1, y_row1, sk_w, row1_h))
caption("■ 와콤패드로 드로잉(포토샵 사용) — 강사 '아이디' · 사장님 '처음이'", x1 + sk_w / 2, y_cap1)
b = paste_fit(pages[0], (x1 + sk_w + gap, y_row1, cover_w, row1_h))
spots.append((1, b))
caption("■ 제안서 표지 — GPT Images 2.0 로 캐릭터 확정", x1 + sk_w + gap + cover_w / 2, y_cap1)

caps = ["■ 01 캐릭터 디자인 매뉴얼 (정면·측면·후면, 표정, 컬러)",
        "■ 02 카드뉴스 8장 — 참치집 사장님 이야기",
        "■ 마케팅 방안 ① 카드뉴스 연재",
        "■ 마케팅 방안 ② '내 가게 세 장면' 참여",
        "■ 마케팅 방안 ③ 업종별 질문 모집"]
for k in range(3):
    x = M + k * (thumb_w + gap)
    b = paste_fit(pages[k + 1], (x, y_row2, thumb_w, thumb_h))
    spots.append((k + 2, b))
    caption(caps[k], x + thumb_w / 2, y_cap2)

x0 = (W - (2 * thumb_w + gap)) // 2
for k in range(2):
    x = x0 + k * (thumb_w + gap)
    b = paste_fit(pages[k + 4], (x, y_row3, thumb_w, thumb_h))
    spots.append((k + 5, b))
    caption(caps[k + 3], x + thumb_w / 2, y_cap3)

out = os.path.join(A, "work08.jpg")
sheet.save(out, quality=88, optimize=True, subsampling=0)
print("sheet", sheet.size, os.path.getsize(out) // 1024, "KB")
pct = [{"page": p, "x": round(x / W * 100, 2), "y": round(y / H * 100, 2),
        "w": round(w / W * 100, 2), "h": round(h / H * 100, 2)} for p, (x, y, w, h) in spots]
print(json.dumps(pct, ensure_ascii=False))
