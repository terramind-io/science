# 플라이쨩 (Fly-chan)

**한국어** | [English](README.en.md)

**초파리의 뇌를 가진 소녀를 키우는 3D 다마고치.**

> **▶ 바로 해보기: https://fkfkfk0406.github.io/fly-chan/** (설치 없이 브라우저에서. 처음 열 때 뇌 데이터 약 100 MB를 받아요)
>
> 게임은 한국어와 영어를 지원해요. 첫 화면이나 일기 맨 아래에서 언어를 고를 수 있어요.

진짜 초파리 전뇌 커넥톰(FlyWire v783, 뉴런 138,639개)을 브라우저에서 LIF 모델로 실시간 시뮬레이션합니다. 방 안의 플라이쨩이 딸기를 먹을지, 깜짝 놀라 뛰어오를지, 더듬이를 손질할지는 대본이 아니라 그 뇌의 하강·운동 뉴런이 정합니다.

![방](docs/images/room.jpg)

| 뇌 보기 | 휴대폰 | 추억과 오늘 |
|---|---|---|
| <img src="docs/images/brain.jpg" alt="뇌 패널" width="480"> | <img src="docs/images/mobile.jpg" alt="휴대폰 화면" width="180"> | <img src="docs/images/mobile-album.jpg" alt="출석과 오늘의 부탁" width="180"> |

| 실사 초파리 모습 | 딸기를 먹는 중 (주둥이 뻗기) | 🤚 살금살금 손 뻗기 |
|---|---|---|
| <img src="docs/images/fly-talk.jpg" alt="실사 초파리 대화" width="320"> | <img src="docs/images/fly-feed.jpg" alt="실사 초파리 섭식" width="320"> | <img src="docs/images/game-reach.jpg" alt="손 뻗기 미니게임" width="320"> |

## 무엇을 할 수 있나요

**돌보기**
- 🍓 간식, 💬 대화, ✋ 쓰다듬기, 🧹 청소, 💡 불 끄기. 배부름·기운·기분·청결·애정 게이지가 시간이 지나면 변하고, 앱을 닫아 둔 시간(최대 72시간)도 반영됩니다.
- 🧠 뇌 보기: 13만 개 뉴런 점 구름, 하강·운동 뉴런 발화율, 핵심 뉴런 스파이크 래스터, 지금 행동의 원인.

**관계**
- 낯섦 → 친구 → 호감 → 두근두근 → 연인. 애정은 하루에 조금씩만 오르고, 함께한 날과 그 순간의 기분까지 맞아야 다음 단계로 갑니다.
- 단계마다 선택지 이벤트, 단계별 대화 주제, 처음 만날 때 정하는 이름과 호칭(받침에 맞는 조사까지).
- 오래 혼자 두면 삐져서 등을 돌리고, 쓰다듬기·좋아하는 간식·대화·선물로 달래야 합니다. 자리를 비운 동안에는 편지를 남겨 둬요.

**매일**
- 💖 하트: 함께 있을 때도, 자리를 비운 동안에도 모입니다. 상점에서 간식 재고, 꾸미기(리본·목도리·화분·액자), 선물을 삽니다.
- 🎞️ 추억과 오늘: 연속 출석 보상, 날마다 바뀌는 오늘의 부탁 3개, 본 장면 다시 보기, 사진 앨범.
- 📔 일기와 업적, 📷 사진(방 액자에 걸림).
- 외형: 기본 VRM 소녀, **실사 초파리**(해부학 3D 모델의 몸 마디 66곳을 관절로 움직이고, 뇌 출력으로 삼각 보행·앞다리 그루밍·주둥이 뻗기·날갯짓), 내 VRM 파일 불러오기.

**놀이**
- 🤚 **살금살금 손 뻗기:** 손이 다가오는 속도가 실제 루밍 감지 뉴런(LPLC2) 입력이 됩니다. 너무 빨리 다가가면 진짜 Giant Fiber가 켜져서 도망가요. 가까울수록 같은 속도도 더 무섭게 느낍니다.
- 🧺 **딸기 받기:** 30초 동안 딸기를 받고 🍄은 피하기.
- 🥚 이스터에그도 몇 개 숨어 있어요.

## 뇌와 게임은 이렇게 연결됩니다

![뇌와 게임의 연결](docs/images/brain-game.png)

먹이를 고르는 취향도 대본이 아닙니다. 간식을 먹는 동안의 MN9 최고 발화율을 기록해 일기에 "뇌가 알려 준 취향"으로 보여 줍니다.

## 실행

### 웹

설치 없이 해보려면 [웹버전](https://fkfkfk0406.github.io/fly-chan/)을 열면 됩니다. 직접 실행하려면:

```bash
npm install
python -m venv pipeline/.venv
pipeline/.venv/Scripts/python -m pip install pandas pyarrow numpy   # macOS/Linux: pipeline/.venv/bin/python
npm run data      # 원본 약 140 MB 다운로드 → public/data/ 에 약 91 MB 바이너리 생성, VRM 다운로드
npm run dev       # http://localhost:5173
```

휴대폰에서 보려면 `npx vite --host`로 켜고 같은 와이파이에서 `http://<PC IP>:5173`으로 접속합니다.

### 데스크톱 앱 (Windows)

작은 창으로 띄워 두고 트레이에 상주하는 버전입니다([Tauri](https://tauri.app), [Rust](https://rustup.rs) 필요).

```bash
npm run desktop         # 개발 실행 (public/data 를 그대로 사용)
npm run desktop:build   # 설치 파일 → src-tauri/target/release/bundle/nsis/
```

- 설치 파일에는 뇌 데이터·VRM이 들어 있지 않고, 첫 실행 때 [Releases `data-v783`](https://github.com/fkfkfk0406/fly-chan/releases/tag/data-v783)에서 한 번(약 104 MB) 받아 둡니다.
- ✕는 트레이로 숨기기입니다. 트레이 메뉴에서 항상 위, 컴퓨터 켜면 같이 시작, 종료를 고릅니다.
- 숨겨 둔 동안은 뇌 시뮬을 멈추고, 다시 열면 지난 시간만큼 배고픔 등이 반영됩니다.
- 설치된 앱은 켤 때와 6시간마다 새 버전을 확인하고, "업데이트"를 누르면 받아서 다시 실행합니다. 육성 저장과 받아 둔 뇌 데이터는 그대로 남아요.
- "나중에"를 누르면 하루 동안 다시 묻지 않고, 같은 버전을 두 번 설치했는데도 버전이 그대로면(설치가 먹히지 않는 경우) 더 묻지 않고 Releases 에서 직접 받으라고 안내합니다. 지금 돌고 있는 버전은 제목 줄에 표시됩니다.

**새 버전 배포 (관리자용)**

```bash
npm run release   # package.json 버전을 올려 커밋·태그(v0.1.1 …)를 만들고 푸시
```

태그가 올라가면 GitHub Actions(`.github/workflows/release.yml`)가 설치 파일을 빌드·서명해서 Releases에 올리고, 앱이 읽는 `latest.json`도 함께 올립니다. 같은 태그로 `.github/workflows/pages.yml`이 웹버전을 GitHub Pages에 다시 올립니다(뇌 데이터·VRM은 `RELEASE_TAG` 릴리스에서 받아 함께 올림).
- 서명 키: 개인 키는 저장소 Secret `TAURI_SIGNING_PRIVATE_KEY`, 공개 키는 `src-tauri/tauri.conf.json`에 있습니다. 개인 키를 잃어버리면 이미 설치된 앱에 업데이트를 보낼 수 없습니다.
- 뇌 데이터를 바꿀 때는 새 태그(예: `data-v784`)로 **사전 릴리스(prerelease)** 로 올리고 `src/util/assets.ts`의 `RELEASE_TAG`를 바꿉니다. 앱이 새 데이터를 받고 예전 것은 지웁니다. 사전 릴리스로 올려야 앱 업데이트 확인(`releases/latest`)을 가로채지 않습니다.

### 개발용 옵션

| 주소 뒤에 | 효과 |
|---|---|
| `?time=60` | 돌봄 시간 60배속 (1분 = 1시간) |
| `?hearts=999` | 하트 999개로 시작 |
| `?dt=0.25` | 적분 간격 (기본 0.5 ms) |
| `?adapt=300:1` | 발화 빈도 적응 켜기 (τw 300 ms, 발화당 1 mV) |

- `npm test`: LIF 엔진(합성 네트워크, 실제 커넥톰에서 논문 결과 재현), 돌봄·대본·출석·삐짐 테스트
- `npm run probe -- sugar:150`: 감각 그룹을 자극하고 가장 많이 발화한 하강·운동 뉴런 출력
- `scripts/`: 속도 측정(`bench`), 미각 안전성(`taste_probe`, `snack-safety`), pC1·시계·루밍 보정(`pc1-probe`, `clock-probe`, `loom-probe`), 적응(`adapt`)

단축키: F 밥, T 대화, P 쓰다듬기, C 청소, L 불, B 뇌 보기, Space/Enter 대사 넘기기, Esc 패널 닫기

## 구조

| 경로 | 역할 |
|---|---|
| `src/sim/` | LIF 엔진(`lif-engine.ts`), 커넥톰 로드와 시뮬 루프(Web Worker) |
| `src/world/` | 방·간식 정의와 감각 입력 변환, 생체시계 |
| `src/behavior/Controller.ts` | 하강 뉴런 발화율 → 행동 (VNC 역할을 절차적으로 대신) |
| `src/care/` | 돌봄 상태·관계 단계·하트·상점·업적, 출석·오늘의 부탁 |
| `src/story/` | 대본, 연출 감독, 이름 조사 처리, 편지·삐짐, 추억, 이스터에그 |
| `src/body/` | VRM 리그, 실사 초파리 아바타(`RealFlyAvatar.ts`), 애니메이션, 3D 방 |
| `src/ui/`, `src/brain/`, `src/fx/` | 대화창·미니게임, 뇌 시각화·래스터, 파티클·효과음 |
| `src-tauri/` | 데스크톱 앱 (창·트레이) |
| `pipeline/` | 원본 데이터 → `public/data` 바이너리와 뉴런 그룹, flybody 모델 → `public/fly` |
| `docs/PROGRESS.md` | 진행 상황과 다음 할 일 |

## 뇌 모델

Shiu et al. 2024 (Nature) Brian2 모델과 같은 방정식과 파라미터를 씁니다.
- `dv/dt = (v0 − v + g)/τm`, `dg/dt = −g/τs`, 시냅스당 0.275 mV, 지연 1.8 ms, 불응기 2.2 ms
- 정확해로 적분하고 휴지에서 벗어난 뉴런만 갱신해, 브라우저에서 실시간에 가깝게 돌아갑니다.

테스트로 확인한 재현 결과(`tests/lif-engine.test.ts`): 당 GRN → MN9, 쓴맛 동시 자극 → MN9 억제, JO-F → 그루밍 DN, LPLC2 → Giant Fiber, 자극이 없으면 조용함.

## 한계와 설계상 선택

- **VNC가 없습니다.** FlyWire는 뇌만 포함하므로 보행 리듬, 벽·침대 피하기, 먹이·침대·사용자에게 가는 드라이브는 절차적으로 만듭니다. 섭식·그루밍·도약은 뇌 출력이 결정하고, 전진·후진·회전 DN 발화는 속도와 회전에 더해집니다. 뇌 패널의 "원인" 줄에 어느 쪽인지 표시합니다.
- **후각은 뺐습니다.** 식초 계열 ORN을 10 Hz로만 자극해도 자극을 끊은 뒤 약 1만 개 뉴런이 계속 발화합니다. 원인은 Kenyon cell이 아니라 더듬이엽 국소 뉴런(ALLN)으로, 신경전달물질 예측 신뢰도가 평균 0.46으로 낮아 억제성 뉴런이 흥분성으로 들어간 경우가 많습니다(`scripts/persist.ts`).
- **한 번에 한 가지 맛만 넣습니다.** 두 맛을 동시에 넣으면(특히 Ir94e + 쓴맛) 폭주해서, 입에 닿은 간식 중 가장 가까운 하나만 자극합니다. 물 GRN은 200 Hz, Ir94e는 100 Hz로 씁니다.
- **적응은 옵션입니다.** 원 모델에 없는 적응 전류를 넣을 수 있지만, 폭주를 멈출 만큼 세게 걸면 섭식 반응도 거의 사라져 기본값은 끔입니다(`scripts/adapt.ts`).

  | 설정 | 당 150 Hz 3초 동안 MN9 | 냄새를 끊은 뒤 300~600 ms 발화 |
  |---|---|---|
  | 적응 없음 | 112 → 92 Hz | 262,413 |
  | τw 300 ms, b 1 mV | 44 → 30 Hz | 85,090 |
  | τw 500 ms, b 2 mV | 16 → 4 Hz | 0 |

- **pC1·시계 뉴런:** 앱의 감각 입력으로는 pC1이 켜지지 않아 설렘 수치로 직접 구동합니다. 시계 뉴런은 하강 뉴런에 영향을 주지 않아 표시용이고, 밤에 졸린 건 게임 규칙입니다.
- **dt 0.5 ms**는 Brian2 기본값(0.1 ms)보다 거칠지만 재현 테스트는 0.25와 0.5 ms에서 모두 통과합니다. 수만 개 뉴런이 한꺼번에 켜지면 시뮬이 실시간보다 느려지고, 세계도 같은 비율로 느려집니다.

## 출처

- **FlyWire 커넥톰 v783:** Dorkenwald et al. 2024, Schlegel et al. 2024 (Nature). 연결 행렬은 [philshiu/Drosophila_brain_model](https://github.com/philshiu/Drosophila_brain_model), 주석·좌표는 [flyconnectome/flywire_annotations](https://github.com/flyconnectome/flywire_annotations)에서 받습니다.
- **LIF 모델:** Shiu et al. 2024, *A Drosophila computational brain model reveals sensorimotor processing*, Nature.
- **초파리 3D 모델:** [TuragaLab/flybody](https://github.com/TuragaLab/flybody) (Vaxenburg et al., Apache License 2.0). `pipeline/build_fly_model.py`로 GLB와 관절 정보로 변환했습니다(`public/fly/NOTICE.txt`).
- **캐릭터:** pixiv `VRM1_Constraint_Twist_Sample` (VRM Public License 1.0: 사용·상업 이용·수정·재배포 허용). `public/models/fly-chan.vrm`을 다른 VRM으로 바꿔도 동작하고, 불러오지 못하면 도형 인형으로 대체합니다.
