"""경기 중 HUD (azuma/inpane/mtl, CourtPreview)"""
from _common import *
from img_menu1 import COURTS
D = 'data/azuma/inpane/mtl/'
C = 'data/azuma/inpane/CourtPreview/'
WB = dict(fill=(255, 255, 255), line=(30, 30, 30), ow=1.5)
MK = {'y': (255, 220, 0), 'o': (255, 150, 40), 'r': (255, 70, 70), 'b': (90, 170, 255)}
L = dict(align='l')
SPEC = {}
def put(f, items, **kw):
    SPEC[D + f + '.tm2'] = by_id(D + f + '.tm2', items, 4, 1, font='h', **kw)
put('KeyAssign_inpane', {0: ('스코어 화면', L), 1: ('스테이터스 화면', L), 2: ('다음', L), 3: ('취소', L), 4: ('종료', L)}, **WB)
put('KeyAssign_inpane3', {0: ('스킵', L), 1: ('리플레이', L), 2: ('카메라 전환', L), 3: ('데모 플레이 종료', L)}, **WB)
put('i_dialog_01', {0: '재개', 1: '메뉴로 돌아가기', 2: '같은 설정으로 재도전', 3: '세이브하고 끝내기', 4: '재시합', 5: '재도전', 6: '시합 재개'})
SPEC[D + 'i_gameinfo_00.tm2'] = [dict(box=(2, 24 * k, 254, 24 * k + 24), text=t, font='h', fill=(255, 255, 255), line=(30, 30, 30), ow=2, marks=MK)
                                for k, t in enumerate(['다음 포인트를 따면 {y|킵}!', '다음 포인트를 따면 {o|세트}!', '다음 포인트를 따면 {r|승리}!',
                                                       '다음 포인트를 따면 {y|브레이크}!', '다음 포인트를 뺏기면 {b|패배}!'])]
p = D + 'i_pause_result_02.tm2'
SPEC[p] = [dict(cbox=(24, 4, 130, 28), clear='inpaint', box=(24, 3, 140, 29), text='포즈', font='h', align='l', fill=(255, 255, 255), line=(20, 20, 60), ow=2),
           dict(cbox=(24, 36, 150, 60), clear='inpaint', box=(24, 35, 160, 61), text='시합 결과', font='h', align='l', fill=(255, 255, 255), line=(60, 30, 10), ow=2)]
SPEC[p] += by_id(p, {1: ('세트', L), 2: ('게임 매치', L)}, 4, 1, font='h', **WB)
SPEC[D + 'i_pause_result_16.tm2'] = [dict(box=(4, 0, 124, 32), text='포즈', font='h', fill=(255, 255, 255), line=(30, 40, 130), ow=2.5)]
put('i_replayinfo_01', {0: '리플레이'})
DANI = ['5급', '4급', '3급', '2급', '1급', '초단', '2단', '3단', '4단', '5단', '기사', '백작', '왕자', '왕', '천사', '신', '별', '네트', '베이스', '올', '빅']
SPEC[D + 'inpane_dani.tm2'] = [dict(cbox=(0, 24 * k, 33, 24 * k + 17), box=(0, 24 * k, 33, 24 * k + 17), text=t, font='h', align='l', size=14, fill=(255, 255, 255), line=(30, 30, 30), ow=2) for k, t in enumerate(DANI)]
put('inpane_finish', {0: '노터치', 1: '서비스 에이스', 2: '노터치', 3: '리턴 에이스', 4: '노터치', 5: '스매시 에이스', 6: ('온 더 라인', L)})
put('inpane_finish00', {0: '노터치', 1: '서비스 에이스'})
put('inpane_finish01', {0: '노터치', 1: '리턴 에이스'})
put('inpane_finish02', {0: '노터치', 1: '스매시 에이스'})
put('inpane_finish03', {0: ('온 더 라인', L)})
for f in ('inpane_kihontokuten00', 'inpane_kihontokuten01', 'inpane_tiebreak00', 'inpane_tiebreak01'):
    put(f, {(2, 129, 128, 191): '듀스', (128, 129, 256, 191): '어드밴\n티지'})
put('inpane_tiebreak02', {0: '타이브레이크'})
put('inpane_match', {0: '매치 포인트'})
put('inpane_set', {0: '세트 포인트'})
# 미니 스코어 라벨: 흰 외곽(1px) + 진한 테두리(2px) + 그라데이션 본체 (원본 구조 재현, 원본 잉크 0~69 안)
for f, t, fl, ln in (('inpane_mini0', '게임 :', [(255, 175, 70), (250, 140, 20)], (70, 42, 18)),
                     ('inpane_mini1', '세 트 :', [(255, 135, 135), (245, 95, 95)], (99, 33, 32))):
    b = dict(box=(0, 0, 70, 23), text=t, font='h', align='l', size=21, vpad=0.5)
    SPEC[D + f + '.tm2'] = [dict(b, cbox=(0, 0, 80, 24), clear='a', fill=(255, 255, 255), line=(255, 255, 255), ow=3),
                            dict(b, clear='n', fill=fl, line=ln, ow=2, box=(0, 0, 70, 23))]
put('inpane_pause02', {0: ('포즈', L), 2: ('세트', L), 3: ('게임', L)}, **WB)
for f in ('inpane_duce00', 'inpane_duce01'):
    put(f, {0: '듀스!', (64, 97, 128, 127): '번째'})
put('inpane_start01', {0: ('세트', L), 2: ('게임', L)}, **WB)
put('inpane_start02', {(0, 0, 32, 32): '제', (52, 0, 143, 32): '세트'})
put('inpane_team', {0: ('A팀', L), 1: ('B팀', L)}, **WB)
put('inpane_team1', {0: ('A 팀', L), 2: ('B 팀', L)}, **WB)
put('result_game', {0: '게임', 1: '게임'})
put('result_set', {0: '세트', 1: '세트'})
put('result_gameset03', {(284, 0, 346, 26): '세트'})
put('result_gameset05', {0: '쾌승', 1: '완패', 2: '승리', 3: '패배', 4: '신승', 5: '석패'})
for f in ('result_verBlue', 'result_verRed'):
    put(f, {0: '서버', 1: '리시버', 2: '서버', 3: '리시버'})
put('result_status01', {2: '스테이터스', 3: '서브 최고 속도', 4: '포인트 획득 수', 5: '미스 샷', 6: '더블 폴트', 7: '서비스 에이스',
                        (40, 226, 160, 248): ('저스트 임팩트율', dict(align='l', cbox=(20, 226, 160, 248))), 9: '네트 플레이율', 10: '포핸드 샷 비율', 11: '시합 평가/100점',
                        12: ('최다 랠리 수', L), 13: ('시합 시간 :', L), (50, 28, 70, 47): '회', (98, 28, 118, 47): '점'}, **WB)
put('info', {12: '예', 13: '아니오', 15: '예', 16: '아니오'})
p = C + 'CourtPreview_00.tm2'
SPEC[p] = by_id(p, {(0, 0, 136, 19): ('<잔디 코트>', L), (0, 20, 136, 39): ('<클레이 코트>', L), (0, 40, 136, 59): ('<하드 코트>', L),
                    (138, 0, 177, 19): '바운드', (138, 20, 177, 39): '구속', 3: ('스킵', L)}, 4, 1, font='h', **WB)
for k in range(12):
    p = C + 'CourtPreview_name%02d.tm2' % (k + 1)
    SPEC[p] = [dict(box=(2, 0, 300, 26), text=COURTS[k], font='h', align='l', fill=(255, 215, 100), line=(40, 25, 5), ow=2)]
SPEC['data/azuma/chara_eff/npc/clap.tm2'] = [dict(cbox=(0, 0, 64, 32), clear='a', box=(1, 2, 63, 30), text='짝짝', font='h', fill=[(255, 240, 80), (250, 160, 20)], line=(90, 40, 10), ow=2.5)]
