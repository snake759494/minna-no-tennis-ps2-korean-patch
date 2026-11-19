"""챌린지 랭크 진입 안내 패널 (wall/Challenge_rankNN)"""
from _common import *
import numpy as np
W = 'data/menu/2d/wall/'
MK = {'y': (255, 220, 0)}
DEBUG = []
TITLES = ['비기너', '아마추어', '세미프로', '프로', '재팬', '월드', '스페셜']
TCOL = [(120, 220, 240), (190, 235, 120), (245, 235, 90), (250, 170, 90), (230, 150, 235), (250, 140, 140), (250, 220, 120)]
BODY = [
    ['이 랭크의 상대는 아직 빈틈이 많으니까', '{y|좌우}로 흔들어서', '{y|빈 공간(오픈 코트)}에', '쳐 넣어 보자.', '샷 후에 {y|코트 중앙(센터)}으로', '돌아가는 것도 잊지 마.'],
    ['이 랭크에서는 상대도 좌우로', '흔들기를 걸어 와.', '이쪽은 {y|앞쪽과 깊은 쪽으로의 샷}도 섞어서', '넓은 코트를 더 효과적으로 쓰자.'],
    ['이 랭크의 상대는 특기 샷으로', '적극적으로 공격해 와.', '베이스라인에 있는 상대에게는 {y|앞으로 나가 발리},', '네트에 나오는 상대에게는 {y|깊게 로브}를 치거나 해서', '{y|상대의 약점}을 찔러 싸워 보자.'],
    ['여기부터의 상대는', '실력을 갈고닦은 강자들이야.', '정확한 위치 선정을 해 오니까,', '{y|코트 깊숙이 빠른 플랫},', '{y|넓은 앵글의 톱스핀}을', '나눠 쳐서 재빠르게 흔들어 보자.'],
    ['이 랭크의 상대는', '스페셜 샷을 써 와.', '어려운 곳으로 맞으면 {y|슬라이스}로 받아쳐 보자.', '공은 느린 대신 {y|자세를 가다듬기 쉽고},', '{y|상대 샷의 앵글도 좁힐} 수 있어.'],
    ['이 랭크는 장점을 살린', '수준 높은 싸움을 하는 강적 일색이야.', '고전하게 되면,', '적극적인 네트 플레이가 돌파구가 될 때가 있어.', '{y|공격은 최대의 방어이기도 해}.'],
    ['여기까지 온 당신은', '이미 {y|일류 모두의 테니스 플레이어}!', '최강의 상대가 모인 이 랭크에서', '모두의 테니스 정상을 노리며,', '{y|지금까지의 싸움에서 익힌 모든 것을}', '{y|쏟아부어} 싸워 보자!'],
]
def wmask(rgb):
    c = rgb.astype(int); lum = c.mean(-1); sat = c.max(-1) - c.min(-1)
    return (lum > 205) & (sat < 40)
def ymask(rgb):
    c = rgb.astype(int)
    return (c[..., 0] > 200) & (c[..., 1] > 160) & (c[..., 2] < 90)
def bands(m, y0, y1, x0, x1):
    rows = m[y0:y1, x0:x1].sum(1) >= 3; out = []; y = 0
    while y < len(rows):
        if rows[y]:
            s = y
            while y < len(rows) and rows[y:y + 4].any(): y += 1
            if y - s >= 8: out.append((s + y0, y + y0))
        y += 1
    return out
SPEC = {}
for k in range(7):
    p = W + 'Challenge_rank%02d.tm2' % k
    rgb = tim2.read(open(os.path.join(R, 'work', 'xb', p), 'rb').read())[0]['rgba'][..., :3]
    m = wmask(rgb) | ymask(rgb)
    bs = bands(m, 116, 336, 60, 520)
    if len(bs) != len(BODY[k]): DEBUG.append((k, len(bs), len(BODY[k]), bs))
    clr, txt = [], []
    for (y0, y1), t in zip(bs, BODY[k]):
        xs = np.where(m[y0:y1, 55:525].any(0))[0] + 55
        clr.append(dict(cbox=(int(xs[0]) - 3, y0 - 3, int(xs[-1]) + 4, y1 + 3), clear='tinpaint', hi=190, lo=120, tcols=[(240, 200, 30), (200, 150, 20)], dil=2, box=(0, 0, 1, 1), text=''))
        txt.append(dict(box=(64, y0 - 2, 516, y1 + 2), text=t, font='h', fill=(255, 255, 255), line=(60, 60, 60), ow=2, marks=MK, clear='n'))
    ty0, ty1 = 72, 102
    xs = [[150, 422], [143, 432], [145, 430], [165, 410], [145, 435], [143, 433], [140, 430]][k]
    clr.append(dict(cbox=(int(xs[0]) - 2, ty0 - 3, int(xs[-1]) + 3, ty1 + 3), clear='inpaint', box=(0, 0, 1, 1), text=''))
    txt.append(dict(box=(int(xs[0]) - 2, ty0 - 2, int(xs[-1]) + 3, ty1 + 2), text=TITLES[k] + ' 랭크에 온 걸 환영해', font='h', fill=TCOL[k], line=(50, 35, 25), ow=2, clear='n'))
    clr.append(dict(cbox=(276, 338, 326, 364), clear='tinpaint', hi=190, lo=120, dil=2, box=(0, 0, 1, 1), text=''))
    txt.append(dict(box=(270, 339, 332, 363), text='다음', font='h', fill=(255, 255, 255), line=(60, 60, 60), ow=2, clear='n'))
    SPEC[p] = clr + txt
if __name__ == '__main__':
    for d in DEBUG: print(d)
