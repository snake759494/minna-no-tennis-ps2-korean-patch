from _common import *
M = 'data/menu/2d/'
Y = (255, 215, 40)
TX = dict(font='h', align='l', fill=(255, 255, 255), line=(70, 70, 70), ow=2, marks={'y': Y}, clear='n')
SPEC = {}
p = M + 'Challenge_06.tm2'
# (텍스트, 원문 줄 오른쪽 끝)
LINES = [('{y|챌린지 모드}는', 230), ('각 랭크에 설정된 승리 수를 달성하면', 405), ('{y|랭크업}할 수 있는 모드야.', 360), None,
         ('게다가 시합에서 이기면', 250), ('사용할 수 있는 {y|캐릭터}와 {y|코스튬}, {y|코트}와 {y|심판}을', 458),
         ('얻을 수 있어!', 320), ('랭크업에 성공하면', 290), ('다음 랭크에서 더 강한 상대가 도전을 기다리고 있다고!', 528)]
ents = []
for k, L in enumerate(LINES):
    if L is None: continue
    t, xe = L
    yc = 102 + 30 * k if k < 4 else 208 + 30 * (k - 4)
    ents.append(dict(cbox=(36, yc - 15, xe + 4, yc + 15), clear='tinpaint', tcols=[(240, 200, 40), (200, 150, 20)], box=(0, 0, 1, 1), text=''))
for k, L in enumerate(LINES):
    if L is None: continue
    t, xe = L
    yc = 102 + 30 * k if k < 4 else 208 + 30 * (k - 4)
    ents.append(dict(box=(42, yc - 13, 530, yc + 13), text=t, **TX))
ents.append(dict(cbox=(326, 36, 604, 66), clear='tinpaint', box=(326, 35, 604, 67), text='챌린지 모드 진행 방법',
                 font='h', fill=(255, 255, 255), line=(40, 50, 70), ow=2))
ents.append(dict(cbox=(543, 362, 592, 390), clear='tinpaint', box=(540, 362, 594, 390), text='다음',
                 font='h', fill=(255, 255, 255), line=(40, 40, 40), ow=2))
SPEC[p] = ents
