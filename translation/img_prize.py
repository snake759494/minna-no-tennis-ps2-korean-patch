"""상품 획득·랭크업 연출 텍스처 (data/azuma/inpane/mtl/prize/)"""
from _common import *
from img_menu1 import COURTS
from img_menu2 import NAMES
from img_menu4 import COS
P = 'data/azuma/inpane/mtl/prize/'
L = dict(align='l')
SPEC = {}
for f, t in (('black_get', '블랙 컬러 획득'), ('blackcos_get', '블랙 코스프레 획득'), ('chara_get', '캐릭터 획득'),
             ('cos_get', '코스프레 의상 획득'), ('court_get', '코트 획득'), ('umpire_get', '심판 획득')):
    p = P + 'frame/' + f + '.tm2'; SPEC[p] = by_id(p, {(1, 0, 223, 31): t}, 4, 1, font='h')
p = P + 'frame/chara_name.tm2'; SPEC[p] = by_id(p, {k: n for k, n in enumerate(NAMES)}, 4, 1, font='h')
p = P + 'frame/cos_name.tm2'; SPEC[p] = by_id(p, {k: n for k, n in enumerate(COS)}, 4, 1, font='h')
p = P + 'frame/court_name.tm2'; SPEC[p] = by_id(p, {k: n for k, n in enumerate(COURTS[:11])}, 4, 1, font='h')
p = P + 'frame/umpire_name.tm2'; SPEC[p] = by_id(p, {k: n for k, n in enumerate(['치카', '스즈키', '카오리', '테니보', '안나'])}, 4, 1, font='h')
R = P + 'rank/'
p = R + 'RankUp_02.tm2'
RK = ['노비스 랭크', '미들 랭크', '어드밴스드 랭크', '시니어 랭크', '그랜드 랭크', '에이스 랭크', '스타 랭크']
bx = [(3, 2, 292, 47), (3, 50, 261, 95), (2, 98, 296, 143), (3, 147, 261, 191), (1, 193, 295, 240), (2, 244, 259, 287), (2, 292, 261, 335)]
SPEC[p] = by_id(p, {b: (t, L) for b, t in zip(bx, RK)}, 4, 1, font='h') + by_id(p, {(366, 96, 512, 120): '랭크업!'}, 4, 1, font='h')
p = R + 'RankUp_03.tm2'
SPEC[p] = by_id(p, {(4, 1, 46, 24): ('남은', L), (50, 1, 96, 24): ('승으로', L), (98, 1, 232, 24): ('랭크업!', L)}, 4, 1, font='h')
SPEC[p].insert(0, dict(cbox=(4, 1, 232, 24), clear='a', box=(4, 1, 232, 24), text=''))
p = R + 'RankUp_04.tm2'; SPEC[p] = by_id(p, {0: ('챌린지 모드', L)}, 4, 1, font='h')
p = R + 'RankUp_05.tm2'
SPEC[p] = by_id(p, {0: '랭크업 시험이 출현했습니다!', (1, 35, 355, 62): '단위가 올랐습니다!', 2: '랭크업 시험이 출현했습니다!', (1, 99, 355, 126): '단위가 올랐습니다!'}, 4, 1, font='h')
p = R + 'RankUp_06.tm2'
rows = [(1, 25), (25, 48), (48, 71), (73, 96), (97, 120), (120, 143), (168, 191), (193, 216)]
tx = ['이 캐릭터를', '이 캐릭터의 코스프레를', '이 심판을', '이 코트를', '이 캐릭터의', '이 코스프레의', '사용할 수 있게 되었습니다.', '블랙 컬러가 추가되었습니다.']
SPEC[p] = [dict(cbox=(0, 0, 256, 220), clear='a', box=(0, 0, 256, 220), text='')] + by_id(p, {(0, a, 256, b): t for (a, b), t in zip(rows, tx)}, 4, 1, font='h')
p = R + 'RankUp_08.tm2'
SPEC[p] = by_id(p, {(250, 44, 306, 72): ('점으로', L), (249, 84, 372, 111): ('했습니다!', L),
                    (450, 40, 512, 72): '쾌승', (450, 81, 511, 113): '승리', (450, 120, 512, 152): '신승'}, 4, 1, font='h')
SPEC[p].append(dict(cbox=(64, 34, 160, 59), clear='tinpaint', hi=190, dil=1, box=(66, 35, 158, 58), text='시합 평가', font='h', fill=(255, 255, 255), line=(70, 60, 40), ow=1.5))
