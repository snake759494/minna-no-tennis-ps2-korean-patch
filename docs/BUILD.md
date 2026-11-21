# 재빌드

## 준비
- Python 3, `pip install numpy Pillow scipy`
- 저장소 최상위에 원본 `Minna no Tennis (Japan, Asia).iso`(MD5 `91a919939101438296b99a39d3770fe9`)와 글꼴(`docs/FONT_CREDITS.md`)
- xdelta3 (`xdelta.exe`)

## 빌드
```powershell
python tools/ex.py "Minna no Tennis (Japan, Asia).iso" work/orig     # ISO 파일 추출(동영상·음성 제외)
cd work; python ../tools/unxb_all.py; cd ..                          # XB 아카이브 풀기 → work/xb
python tools/kfont.py work/xb/data/common/gffont16.bin work/gffont16_ko.bin   # 게임 글꼴에 한글 2,350자
$env:PYTHONIOENCODING = 'utf-8'; python tools/build.py                # → "Minna no Tennis (Japan, Asia) (Korean).iso"
```
`build.py` 출력을 파일로 넘길 때는 반드시 `PYTHONIOENCODING=utf-8`을 지정하세요. 지정하지 않으면 한글 출력에서 빌드가 멈추고 ISO가 갱신되지 않습니다.

그림 글자만 확인하려면 `python tools/build_img.py <경로 일부>`를 실행합니다. `work/prev/`에 원본(위)과 한글(아래) 비교 그림이 생깁니다.

## 차분 파일
```powershell
.\xdelta.exe -e -0 -S none -A -s "Minna no Tennis (Japan, Asia).iso" "Minna no Tennis (Japan, Asia) (Korean).iso" Minna_no_Tennis_PS2_KO_v1.4.xdelta
```

## 파일
- `translation/img_*.py`: TIM2 그림 글자 사양(파일 경로 → 상자 좌표·한국어·글꼴·색·지우기 방식). `_common.py`는 공용 도우미
- `translation/sign3d.py`: 메인 메뉴 3D 간판 텍스처, `bmps.py`: 타이틀 로고 자막·게임오버 말풍선 등 BMP
- `translation/menu_bin.tsv`, `menu_bin2.tsv`: MENU.BIN 문자열 `오프셋	한국어`(원래 칸 안에서 제자리 교체)
- `tools/build.py`: 전체 빌드, `build_img.py`·`imgtext.py`·`tim2.py` 그림 글자, `kfont.py`·`gffont.py` 게임 글꼴, `menubin.py` MENU.BIN, `xb.py` XB 아카이브, `mti.py` 3D 메뉴 텍스처, `iso.py`·`isopatch.py` 디스크
- `tools/emu.py`, `boxes.py`, `contact.py`, `sheet.py`, `sjscan.py`, `menustr.py`, `tm2png.py`: 검증·조사용 스크립트(개인 환경용)
- `SCPS-15113_A35F2139.pnach`: 16:9 와이드 패치
