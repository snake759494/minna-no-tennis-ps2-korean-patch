from _common import *
from img_menu1 import DAN, RANKS
M = 'data/menu/2d/'
WB = dict(fill=(255, 255, 255), line=(30, 30, 30), ow=1.5)
SPEC = {}
# ---- 옵션 ----
p = M + 'Option_00.tm2'
SPEC[p] = by_id(p, {1: '사운드', 5: '쇼트 리플레이 재생', 6: '오프닝', 8: '무비', 9: '엔딩', 11: '로딩 중 배경',
                    12: '모노', 14: '진동', 15: '스테레오', 17: '오토 세이브', 18: '샷 타깃 표시', 19: '적게',
                    20: '상공 카메라 설정', 21: '많게', 22: '앞쪽 고정', 23: '앞·뒤 양쪽'}, 4, 1, font='h', **WB)
# ---- 세이브/로드 ----
p = M + 'SaveLoad_00.tm2'
it = {}
for k, i in enumerate([6, 9, 12, 15, 18, 21, 23, 25, 26, 27]): it[i] = DAN[k]
for k, i in enumerate([7, 10, 13, 16, 19, 22, 24]): it[i] = DAN[10 + k]
for k, i in enumerate([3, 5, 8, 11, 14, 17, 20]): it[i] = RANKS[k]
SPEC[p] = by_id(p, it, 4, 1, font='h', **WB)
# ---- 스테이터스 ----
p = M + 'Status_01.tm2'
it = {}
for k, i in enumerate([4, 8, 12, 16, 20, 24, 28, 32, 35]): it[i] = (DAN[k], dict(align='l'))
for k, i in enumerate([5, 9, 13, 17, 21, 25, 29, 33]): it[i] = (DAN[9 + k], dict(align='l'))
for k, i in enumerate([6, 10, 14, 18, 22, 26, 30]): it[i] = (['비기너', '아마추어', '세미프로', '프로', '재팬', '월드', '스페셜'][k], dict(align='l'))
L = dict(align='l')
it.update({1: ('랭크', L), 3: ('등급', L), 7: ('시합 횟수', L), 11: ('서브 최고 속도', L), 15: ('서비스 게임 킵률', L),
           (384, 166, 512, 188): ('저스트 임팩트율', L), 23: ('네트 플레이율', L), 27: ('포핸드 샷 비율', L),
           31: ('미스 샷 비율', L), 34: ('더블 폴트율', L), 36: ('이름:', L),
           (2, 23, 20, 43): '회', (24, 23, 44, 43): '점', (176, 23, 214, 43): '시합',
           37: ('생애 성적', L)})
SPEC[p] = by_id(p, it, 4, 1, font='h', **WB)
SPEC[p].append(dict(box=(0, 377, 117, 408), text='생애 성적', font='h', align='l', fill=(255, 255, 255), line=(255, 255, 255), ow=3))
for e in SPEC[p]:
    if e.get('align') == 'l': b = e['box']; e.setdefault('cbox', b); e['box'] = (b[0] + 3, b[1], min(512, b[2] + 3), b[3])

# ---- 키 안내 / 저장 말풍선 ----
for p, it in ((M + 'KeyAssign_SaveLoad.tm2', {0: '데이터 삭제', 1: '랭크 표시', 2: '등급 표시'}),
              (M + 'KeyAssign_item.tm2', {0: '컬러 선택'}),
              (M + 'KeyAssign_CharacterSelect2.tm2', {0: '파라미터 표시', 1: '코스튬 선택', 2: '코스튬 선택'}),
              (M + 'SaveLoad_01.tm2', {(0, 97, 104, 142): '데이터를\n만드는 중', 2: '완료했어!'})):
    SPEC[p] = padl([dict(e, align='l') for e in by_id(p, it, 4, 1, font='h', **WB)], 8 if 'KeyAssign' in p else 3, 256)

p = M + 'SaveLoad_03.tm2'
SPEC[p] = [dict(cbox=(b[0] - 9, b[1] - 1, b[2] + 9, b[3] + 5), clear='inpaint', box=(b[0] - 6, b[1] - 2, b[2] + 6, b[3] + 2), text=t, font='h', fill=c, line=(40, 40, 40), ow=2.5)
           for b, t, c in (((50, 107, 121, 131), '세이브', (160, 210, 245)), ((217, 107, 290, 131), '로드', (250, 175, 205)),
                           ((32, 252, 132, 276), '아이템', (160, 235, 180)), ((191, 252, 314, 276), '스테이터스', (250, 185, 120)))]
SPEC[p] = [dict(cbox=c, clear='grayw', lo=104, box=b, text=t, font='h', size=13, fill=(255, 255, 255), line=(70, 70, 70), ow=1, rot=-32)
           for c, b, t in (((80, 28, 128, 72), (78, 32, 128, 70), '세이브'), ((244, 26, 296, 70), (244, 30, 296, 68), '로드'))] + SPEC[p]
