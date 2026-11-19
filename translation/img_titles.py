# 메뉴 상단 제목 바 (512x64, 가로 줄무늬 탭). 글자: 흰→밝은회색 본체 + 진회색(40) 외곽선 + 그림자
import os, sys, glob
import numpy as np
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, 'tools')); import tim2
from scipy import ndimage
T = 'data/menu/2d/'
_M = None
for fn in sorted(glob.glob(os.path.join(R, 'work', 'xb', T, 'Title_*.tm2'))):
    a = tim2.read(open(fn, 'rb').read())[0]['rgba'].astype(int)
    if a.shape[1] != 512: continue
    m = (a[..., :3].max(-1) - a[..., :3].min(-1)) > 40
    _M = m if _M is None else (_M | m)
_M = ndimage.binary_fill_holes(ndimage.binary_closing(_M, np.ones((5, 5)))) & _M | ndimage.binary_fill_holes(_M)
def bar(text):
    return [dict(cbox=(0, 0, 512, 40), clear='mask', mask=_M, box=(66, 4, 288, 33), text=text, font='h',
                 fill=[(255, 255, 255), (255, 255, 255), (205, 205, 210)], line=(40, 40, 40), ow=2, shadow=(2, 2, (20, 20, 20), 0.55))]
def bar2(a, b):
    e = bar(a); e[0]['box'] = (62, 4, 166, 33)
    e2 = dict(e[0]); e2.update(clear='n', box=(166, 9, 304, 33), text=b); e2.pop('cbox', None); e2.pop('mask', None)
    return e + [e2]
SPEC = {
    T + 'Title_Challenge.tm2': bar('챌린지 모드'),
    T + 'Title_CharacterSelect2.tm2': bar('캐릭터 선택'),
    T + 'Title_Confirmation.tm2': bar('최종 확인'),
    T + 'Title_Confirmation_00.tm2': bar('최종 확인(챌린지)'),
    T + 'Title_Confirmation_01.tm2': bar2('최종 확인', '(모두의 테니스)'),
    T + 'Title_Confirmation_02.tm2': bar('최종 확인(트레이닝)'),
    T + 'Title_MainMenu.tm2': bar('메인 메뉴'),
    T + 'Title_NameEntry.tm2': bar('플레이 데이터 작성'),
    T + 'Title_Option.tm2': bar('옵션'),
    T + 'Title_PlayerSelect.tm2': bar('게임 선택'),
    T + 'Title_SaveLoad.tm2': bar('세이브&로드'),
    T + 'Title_SaveLoad_00.tm2': bar('게임 스타트'),
    T + 'Title_SaveLoad_01.tm2': bar('세이브'),
    T + 'Title_SaveLoad_02.tm2': bar('로드'),
    T + 'Title_SaveLoad_03.tm2': bar('데이터'),
    T + 'Title_Status.tm2': bar('스테이터스'),
    T + 'Title_item.tm2': bar('아이템'),
}
