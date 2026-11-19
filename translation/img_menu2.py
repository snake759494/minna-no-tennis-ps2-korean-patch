from _common import *
from img_menu1 import COURTS, DAN
M = 'data/menu/2d/'
SH = dict(shadow=(2, 2, (0, 0, 0), 0.6))
WB = dict(fill=(255, 255, 255), line=(30, 30, 30), ow=1.5)
SPEC = {}
# ---- 캐릭터 선택 ----
p = M + 'CharacterSelect2_00.tm2'
it = {10: '올라운드 플레이어', 15: '베이스라인 플레이어', 19: '네트 플레이어', 21: '빅 서버',
      31: '플랫', 33: '슬라이스', 34: '톱', 36: '스매시', 39: '발리',
      38: '올라운드', 40: '베이스라인', 43: '네트 플레이어', 44: '빅 서버',
      (2, 211, 112, 233): ('준비 OK!', dict(align='l')), (2, 235, 114, 256): ('선택 불가', dict(align='l')),
      (217, 141, 237, 159): '약', (241, 141, 261, 159): '강',
      (465, 400, 488, 440): ('초\n급', dict(size=16)), (488, 400, 512, 440): ('중\n급', dict(size=16)), (465, 441, 488, 479): ('상\n급', dict(size=16))}
for k, t in enumerate(['서브', '스트로크', '발리', '임팩트', '풋워크', '스태미나']):
    pass
SPEC[p] = by_id(p, it, 4, 0, font='h')
for k, t in enumerate(['서브', '스트로크', '발리', '임팩트', '풋워크', '스태미나']):
    SPEC[p].append(dict(cbox=(264, 5 + 16 * k, 368, 19 + 16 * k), clear='row', sx=262, box=(266, 4 + 16 * k, 366, 19 + 16 * k), text=t, font='h', size=13,
                        fill=(255, 255, 255), line=(40, 40, 40), ow=2))
SPEC[p] += [dict(cbox=(64, 4, 200, 28), clear='row', sx=40, box=(64, 4, 196, 27), text='단식', font='h', fill=(255, 255, 255), line=(60, 60, 60), ow=2),
            dict(cbox=(64, 36, 200, 60), clear='row', sx=40, box=(64, 36, 196, 59), text='복식', font='h', fill=(255, 255, 255), line=(60, 60, 60), ow=2)]
for y0, t in ((138, '양손'), (162, '오른손'), (186, '왼손')):
    SPEC[p].append(dict(cbox=(84, y0, 132, y0 + 20), clear='row', sx=133, box=(84, y0, 133, y0 + 20), text=t, font='h', fill=(255, 255, 255), line=(70, 50, 40), ow=1))
p = M + 'CharacterSelect2_02.tm2'
NAMES = ['엘레노어', '유키', '준', '카이토', '모모코', 'JJ', '캐롤', '록 불', '미란다', '류', '로라', '윌', '글로리아', '스즈키']
it = {}
for k, n in enumerate(NAMES):
    if k == 5: continue
    x0, y0, x1, y1 = boxes(p, 4, 0)[k]
    it[(min(x0, 12), y0, max(x1, 116), y1)] = n
SPEC[p] = by_id(p, it, 4, 0, font='h', **SH)
p = M + 'CharacterSelect2_04.tm2'
it = {6: '올라운드\n플레이어', 8: '베이스라인\n플레이어', 10: '네트 플레이어', 11: '빅 서버'}
for k, t in enumerate(['서브', '스트로크', '발리', '임팩트', '풋워크']):
    it[(1, 249 + 24 * k, 87, 268 + 24 * k)] = t
SPEC[p] = by_id(p, it, 4, 0, font='h', **SH)
# ---- 최종 확인 ----
p = M + 'Confirmation_00.tm2'
SPEC[p] = by_id(p, {40: '핸디\n없음', 53: '핸디\n없음', 48: 'COM약', 54: 'COM강',
                    46: ('전체 데이터 중 베스트', dict(align='l')), 51: ('베스트 스코어', dict(align='l')), 56: ('당신의 베스트', dict(align='l'))}, 4, 0, font='h')
SPEC[p] += [dict(cbox=(12, 195, 58, 212), clear='row', sx=62, box=(10, 195, 60, 212), text='앞', font='h', fill=(255, 255, 255), line=(40, 70, 40), ow=1.5),
            dict(cbox=(10, 217, 61, 236), clear='row', sx=64, box=(8, 217, 62, 236), text='뒤', font='h', fill=(255, 255, 255), line=(70, 70, 30), ow=1.5),
            dict(cbox=(398, 299, 480, 317), clear='row', sx=393, box=(396, 299, 480, 317), text='보이스 재생', font='h', fill=(255, 255, 255), line=(50, 80, 60), ow=1.5)]
p = M + 'Confirmation_01.tm2'
it = {k: (c, dict(align='l')) for k, c in enumerate(COURTS[:11])}
it.update({11: '잔디 코트', 12: '클레이 코트', 13: '하드 코트', 14: '치카', 17: '스즈키', 19: '카오리', 20: '테니보', 21: '안나',
           16: '점', (2, 488, 46, 511): '바운드', (49, 488, 95, 511): '구속'})
SPEC[p] = by_id(p, it, 4, 0, font='h', **WB)
p = M + 'Confirmation_03.tm2'
it = {0: '프리 게임', 3: '챌린지 모드', 7: '트레이닝 모드', 10: '모두의 테니스', 13: '코트 선택', 16: '상세 설정', 20: '핸디 설정',
      23: '이색 룰 설정', 26: '심판 선택', 1: '게임 수', 4: '세트 수', 8: '코트 선택', 11: '심판 선택', 14: '상세 설정',
      17: '시합 시작!', 21: '심판', 24: '설정 OK!', 27: '핸디 설정', 29: '준비 OK!', 2: '이색 룰 설정', 5: '없음',
      (390, 70, 477, 90): '추 ×1', (390, 102, 477, 122): '추 ×2', (390, 134, 477, 154): '추 ×3',
      18: '올라운드', 19: '베이스라인', 22: '네트 플레이어', 25: '빅 서버',
      30: '불규칙 바운드', 33: '슬로 모션', 36: '상공 카메라 앞·뒤 고정', 32: '불규칙 바운드', 35: '슬로 모션',
      39: '불규칙 바운드&슬로 모션'}
it = {k: (v, dict(align='l')) if k in (0, 3, 7, 10, 13, 16, 20, 23, 26, 1, 4, 8, 11, 14, 17, 21, 24, 27, 29, 2) else v for k, v in it.items()}
SPEC[p] = by_id(p, it, 4, 0, font='h')
for x0, t in ((10, '치카'), (98, '스즈키'), (186, '카오리'), (274, '테니보'), (362, '안나')):
    SPEC[p].append(dict(cbox=(x0 + 30, 433, x0 + 76, 451), clear='inpaint', box=(x0 + 24, 432, x0 + 77, 452), text=t, font='h',
                        fill=(255, 255, 255), line=(30, 30, 30), ow=1.5))
p = M + 'Confirmation_04.tm2'
it = {}
for k in range(9): it[(2, 2 + 24 * k, 95, 22 + 24 * k)] = (DAN[k], dict(align='l'))
for k in range(8): it[(98, 2 + 24 * k, 192, 22 + 24 * k)] = (DAN[9 + k], dict(align='l'))
SPEC[p] = by_id(p, it, 4, 0, font='h', **WB)
