# ISKRA // MUSCA

*Two-scale embodied intelligence.*

Исследовательский проект и концепция игры о совместном восприятии мира.
ISKRA формулирует цели и проверяемые гипотезы, Bridge переводит их в параметры
нижнего контроллера, MUSCA воспринимает среду и управляет виртуальным телом.
Человек принимает значимые решения.

**Стадия:** локальный технический прототип на Python со скриптовым контроллером,
отдельным Bridge, терминальной загадкой «Шлюз» и тестами. В игровой стенд коннектом,
LLM и биологическая динамика не подключены. Для отдельной линии воспроизведения
Shiu закреплены и проверены исходники и данные; научные прогоны ещё не выполнены.
GATE-P01 v0.1 сейчас IN PROGRESS: завершена 1 из 12 запланированных human sessions; агрегатный вывод ещё не разрешён.

**Игровое направление принято 2026-09-18:** MUSCA развивается как одиночная
third-person action-RPG / souls-like. `Elden Ring` — ориентир по ощущению исследования
и боя, а не обещание такого же масштаба. MMO и multiplayer исключены из активного
roadmap. При этом поведение и ощущение связки HUMAN ↔ ISKRA ↔ Bridge ↔ MUSCA
сохраняются: меняется оболочка игры, а не её идентичность.

Датированный локальный снимок и границы проверки — в [статусе](docs/status/CURRENT.md).

## Два независимых вопроса

- **Исследование — [HYP]:** может ли биологическая топология связей дать измеримый
  выигрыш в заданной сенсомоторной задаче по сравнению с согласованными контролями?
- **Игра — [HYP]:** помогают ли разные способы машинного восприятия принимать
  интересные и осмысленные решения?

Успех одного направления не доказывает успех другого. Коннектом — карта связей;
динамику нейронов, сенсорные входы и перевод активности в движение нужно проверять
отдельно. Выбор исходной модели для воспроизведения не выбирает игровой backend.
Проект не заявляет о полной симуляции живого мозга.

## Документы

| Документ | Назначение |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Переданный пользователем локальный контракт Codex v0.1 |
| [Манифест](docs/PROJECT_CHARTER.md) | Цель, границы архитектуры, первый этап, эксперимент и успех |
| [Исследовательский протокол](docs/RESEARCH_PROTOCOL.md) | Сравнения, контроль смешивающих факторов и воспроизводимость |
| [SCI-R00/R01 preregistration](docs/research/SCI_R00_R01_REPRO_PLAN.md) | Первый строгий gate воспроизведения опубликованной модели Drosophila |
| [R00 source provenance](docs/status/2026-09-16-r00-source-provenance.md) | Solver/source/data hashes, artifact QC and strict-environment boundary |
| [Licensing decision](docs/LICENSING_DECISION.md) | Разделение лицензий кода, datasets и будущей игры; решение LICENSE ещё открыто |
| [GATE 0 CI receipt](docs/status/2026-09-16-gate0.md) | Commit/push/CI read-back для Windows/Python 3.14.6 baseline |
| [Игровое видение](docs/GAME_VISION.md) | Основной цикл, развитие восприятия и первый игровой срез |
| [Протокол игрового пилота](docs/PLAYTEST_PROTOCOL.md) | Условия, метрики и критерии до сбора игровых данных |
| [Сборка пилота](docs/PILOT_BUILD.md) | Локальный архив, проверка хешей и запуск сохранённой версии |
| [Интегрированный аудит](docs/status/2026-09-16-integrated-audit.md) | Свежий GitHub/DC read-back, четыре исправления, проверки и оставшиеся границы |
| Game direction 2026-09-18 | Accepted: solo souls-like roadmap; отдельный repo-status документ вне frozen GATE-P01 bundle |
| [ADR-0001](docs/adr/ADR-0001-project-boundaries.md) | Проект записи о границах и отложенных решениях |
| [ADR-0002](docs/adr/ADR-0002-local-prototype-runtime.md) | Python и дискретный мир для локального стенда |
| [ADR-0003](docs/adr/ADR-0003-bridge-contract.md) | Исполняемая граница Bridge и критерии проверки |
| [ADR-0004](docs/adr/ADR-0004-terminal-gate-puzzle.md) | Загадка, цена наблюдения и дополнительный контракт (содержит ответы) |
| [ADR-0005](docs/adr/ADR-0005-shiu-v630-reproduction-baseline.md) | Accepted: Shiu/FlyWire-v630 только как первый strict reproduction baseline |
| ADR-0012 | Accepted: одиночная souls-like/action-RPG вместо MMO; governance-файл хранится вне frozen GATE-P01 bundle |
| [Карта научных свидетельств](docs/RESEARCH_EVIDENCE.md) | Проверенные первоисточники и пределы переноса выводов |
| [Аудит](docs/status/2026-09-16-audit.md) | Найденные дефекты, исправления, GitHub и машинная проверка |
| [Локальный статус](docs/status/CURRENT.md) | Что записано, что проверено и что остаётся неизвестным |
| [Шаблон датасета](data/manifests/dataset.template.json) | Происхождение и неизменяемый снимок данных |
| [Шаблон эксперимента](experiments/manifests/experiment.template.json) | Вопрос, условия, критерии и след результатов |

Шаблоны содержат незаполненные поля и не являются регистрацией готового опыта.
Правила их заполнения описаны в исследовательском протоколе.

## Запуск локального прототипа

Законченная терминальная загадка:

```powershell
py -3.14 -m musca --puzzle --mode light_chemical
```

Сначала `go` направляет MUSCA к шлюзу. У шлюза можно исследовать состав (`scan`),
выбрать янтарный (`amber`) или кобальтовый (`cobalt`) реагент, отказаться (`leave`)
либо выйти (`quit`). Правила, цена пробы и последствия объясняются на экране.
Человек делает выбор; интерпретатор предлагает гипотезу и пересматривает её
по наблюдениям. Моторные направления по-прежнему выбирает нижний контроллер.

Для сравнения доступен `--mode light`; оба режима подходят к шлюзу безопасно.
`--layout a` и `--layout b` задают разные скрытые варианты для ведущего.
`--output experiments/results/my-gate.json` сохраняет новую локальную квитанцию;
не показывайте диагностический JSON игроку до завершения. `--demo` и `--json`
не совмещаются с загадкой: автоматического выбора за человека нет.
Пилот с игроками ещё не запускался; [манифест](experiments/manifests/gate-p01.json)
имеет статус `draft_not_run` и требует фиксации версии перед сбором данных.

Для сохранения нового снимка кода и протокола без перезаписи существующего:

```powershell
py -3.14 scripts/pilot_bundle.py freeze --output experiments/results/my-pilot-build.zip
py -3.14 scripts/pilot_bundle.py verify experiments/results/my-pilot-build.zip
```

Команды не запускают игровые сессии. Архив содержит явный список проектных
файлов и контрольные суммы; результаты игроков в него не включаются.
Порядок запуска из снимка описан в [инструкции](docs/PILOT_BUILD.md).

Исходный технический сценарий обхода опасности:

Из корня репозитория, в PowerShell, с уже установленным Python 3.14:

```powershell
py -3.14 -m musca --mode light_chemical
```

`go` — исследовать источник, `wait` — остановиться и наблюдать, `quit` — завершить.
После нового предупреждения игра возвращает выбор человеку. Направления каждого
шага выбирает нижний контроллер; интерфейс не принимает моторные команды.
Повторное `go` продолжает действующее намерение. После остановки `wait` даёт пройти
четырём неподвижным тикам; это также позволяет принять новое намерение движения.

Автоматическая демонстрация с заранее заданным намерением и проверка:

```powershell
py -3.14 -m musca --demo --mode light
py -3.14 -m musca --demo --mode light_chemical
py -3.14 -m unittest discover -s tests -v
```

На фиксированной сцене `light` достигает опасной клетки за 2 тика,
`light_chemical` обходит её и достигает источника за 6. У второго режима больше
информации. Это инженерный пример, не доказательство научного преимущества
или интереса игроков. Тик — условный шаг, не биологическая секунда.

Для новой локальной квитанции:

```powershell
py -3.14 -m musca --demo --mode light_chemical --json --output experiments/results/my-run.json
```

Существующий файл не перезаписывается. JSON содержит диагностическую карту,
координаты, решения, действия, события, хеши исходников и версию Python;
интерпретатору карта и координаты не передаются. Время и сведения о среде отделены
от детерминированного результата. Чтения произвольного журнала команд через CLI
пока нет: `--demo` повторяет встроенный пример.

Сторонних пакетов нет, установка зависимостей не требуется. Проверенная версия
интерпретатора записана в [.python-version](.python-version); сам Windows launcher
не обязан читать этот файл, фактическая версия входит в квитанцию. Другие ОС
пока не проверены. Ошибка обратной телеметрии останавливает эпизод и сохраняет
в квитанции уже выполненное действие без выдуманных наблюдений.

Текущий GATE-P01 продолжает проверять perception/decision петлю на своей замороженной
версии. Следующий отдельный продуктовый этап — небольшой single-player souls-like
combat/exploration slice с сохранённой ролью ISKRA/MUSCA; для него нужен новый игровой
протокол, а не подмена оставшихся сессий GATE-P01. Биологический опыт остаётся отдельной
линией и требует собственных данных, динамики и согласованных контролей.
MMO/multiplayer не входят в активный roadmap.

## Проверка manifest-контрактов

Структурная проверка зарегистрированных manifests:

```powershell
py -3.14 scripts/validate_manifests.py --level schema data/manifests/SCI-DATA-SHIU-FW630.candidate.json experiments/manifests/SCI-R00-SHIU-ENV-DATA.candidate.json experiments/manifests/SCI-R01-SHIU-SUGAR.candidate.json experiments/manifests/SCI-R01-SHIU-SUGAR.run.json experiments/manifests/SCI-R02-SHIU-MN9-LATERALITY-200HZ.candidate.json experiments/manifests/SCI-R02-SHIU-MN9-LATERALITY-200HZ.run.json experiments/manifests/gate-p01.json
```

Перед R01 execution использовался более строгий local gate:

```powershell
py -3.14 scripts/validate_manifests.py --level runnable --repo-root . experiments/manifests/SCI-R01-SHIU-SUGAR.run.json
```

Исторический `SCI-R01-SHIU-SUGAR.candidate.json` остаётся замороженным preregistration
candidate со статусом `draft_not_run`. После operational SCI-R00 PASS был создан отдельный
frozen `SCI-R01-SHIU-SUGAR.run.json`; его `ready_to_run` фиксирует pre-execution envelope
и не переписывается после просмотра результата. `schema PASS` подтверждает форму документа,
а `runnable PASS` на конкретном research-host подтверждает лишь готовность входов/метаданных.

Runnable дополнительно требует существующий local_storage; not_applicable допускается только с явной причиной.

[FACT local] SCI-R01 strict tutorial sugar execution завершён как engineering **PASS**:
30/30 trials, `406978` spike rows, `430` active neurons. Output SHA-256:
`657f4ae3d54f90bb0c2a5f13db4156449fec0b24cff74efb84afe03035e6c9e2`.
Execution receipt SHA-256:
`38d7ed8bf191fce5f0495b8e3561483f5fcbe2da4a3140bcad069e7cdb8eec5d`.
Independent artifact verification also PASS; details are in
`docs/status/2026-09-19-r01-execution.md`.

This R01 result is **not** a Nature-figure reproduction, biological validation,
topology-superiority result, commercial clearance or game-value result.

[FACT local] SCI-R02 subsequently **PASSED** its separately preregistered bilateral
200 Hz MN9-laterality reproduction gate: both 30-trial hemisphere conditions met all
frozen primary criteria. Execution receipt SHA-256:
`91016e6339a17ad658f48ba814d47d7e51f9866f7e010537bc0a57b86399668d`.
Independent verification SHA-256:
`1437673a23eb0650a39f100108953a79e64cf0e6b418060ac3c57d6180a086fe`.
See `docs/status/2026-09-19-r02-execution.md`.

R02 PASS is still **not** biological validation or topology-superiority evidence;
matched-control topology testing remains a separate preregistered gate.

## SCI-R00 read-only preflight

Before any neuroscience environment/data materialization, run:

```powershell
py -3.14 scripts/research_r00_preflight.py --repo-root .
```

The preflight is intentionally non-mutating. It reports governance, manifest,
host-tooling and storage blockers and performs zero installs/downloads/simulations.
ADR-0005 принят. SCI-R00 operational strict environment/data smoke теперь имеет
локальный PASS с датированным receipt в `docs/status/2026-09-18-r00-execution.md`.
GitHub-hosted CI без project-local solver по-прежнему ожидаемо видит `host_solver`;
это CI-проверка fail-closed preflight semantics, а не опровержение локального R00 PASS.

The strict Shiu reproduction lineage requires a conda-compatible solver for the
pinned `environment_full.yml`. `uv` may coexist on the host but is not treated as
a silent replacement for that original environment contract.
