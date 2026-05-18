# ROADMAP: развитие системы после тестового прогона `purchase-approval`

## 1. Назначение

Этот документ фиксирует направления развития системы `analyst-by-skills` после анализа тестового прогона `runs/purchase-approval`.

Цель roadmap — дать агентам и разработчикам список независимых задач, которые можно брать по одной и выполнять без повторного анализа всего прогона.

Главный вывод тестового прогона:

- продуктовые артефакты генерируются качественно;
- трассировка требований в целом работает;
- post-pipeline маршрут сработал;
- слабое место системы — доказуемость прохождения всех обязательных gates, полнота service history, калибровка story readiness и сохранение residual risks.

## 2. Текущее состояние

### Что работает хорошо

- `requirements-elicitor` корректно выявляет конфликтные и блокирующие вопросы.
- `scope-finalizer-agent` полезен: финальное интервью закрыло реальные пробелы, а не было формальностью.
- `Канонические правила` связывают ответы пользователя с downstream-артефактами.
- `Спецификация`, `Пользовательские истории`, `Статус готовности историй` и `Отчет о пробелах и рисках` формируются в согласованном комплекте.
- Post-pipeline документы создаются автоматически после финализации.
- `validate_run.py` проверяет базовую форму прогона и обязательные service metadata `isolated-subagent`.

### Основные проблемы

- Service reports не доказывают каждый обязательный route/audit gate.
- `routing-decision.md` может пропустить переход, например `story-extractor -> story-quality-reviewer`.
- `traceability-audit.md` может содержать только итоговый audit вместо audit на каждом обязательном переходе.
- Истории могут использовать CR в критериях или бизнес-правилах, но не указывать этот CR в блоке `Источник`.
- `Статус готовности историй: Высокий` не отделяет готовность требований от технической готовности delivery.
- Закрытые GAP теряют residual risks.
- `Kickoff brief` больше похож на summary, чем на рабочий сценарий встречи.
- Readiness questions могут быть полезны, но система должна явно защищать канон требований от их обратного попадания без нового requirements-processing.

## 3. Направления работ

## A. Доказуемость маршрута и service gates

### A1. Полная история route-control

Проблема: в тестовом прогоне не была явно зафиксирована проверка перехода `story-extractor -> story-quality-reviewer`. Это ослабляет доказуемость маршрута: результат может быть корректным, но service trail не подтверждает прохождение всех обязательных gates.

Цель: каждый обязательный downstream-переход должен иметь отдельную запись в `service/routing-decision.md`.

Задачи:

- Уточнить в `AGENTS.md`, что каждый достигнутый обязательный переход требует отдельной записи route-control.
- Уточнить `agents/routing-guardian-agent.md`, что он возвращает отчет не только по финальному решению, но и по каждому проверенному переходу.
- Обновить `scenarios/orchestrator-routing-scenarios.md`, добавив сценарий “пропущен route gate”.
- Обновить `scripts/validate_run.py`, чтобы он проверял наличие обязательных route stages.
- Добавить negative fixture `invalid-missing-route-gate`.
- Обновить valid fixtures и canonical example.

Минимальные обязательные route checks:

- `artifact-persistence-agent(create_run) -> first analytical stage`
- `requirements-elicitor -> spec-structurer`, если elicitor запускался
- `spec-structurer -> story-extractor`
- `story-extractor -> story-quality-reviewer`
- `story-quality-reviewer -> requirements-gap-analyzer`
- `requirements-gap-analyzer -> final-aggregation`
- `scope-finalizer-agent -> kickoff-briefing-agent`, если интервью проводилось
- `kickoff-briefing-agent -> delivery-readiness-agent`, если post-pipeline достигнут

Acceptance criteria:

- Валидатор падает, если достигнутый переход отсутствует в `routing-decision.md`.
- Historical `block` остается допустимым, если позже закрыт и итоговое решение `allow`.
- `make check` проходит.

### A2. Per-gate traceability audit

Проблема: в тестовом прогоне `traceability-audit.md` содержал итоговый audit и audit после scope-finalizer, но не доказывал, что аудит выполнялся перед каждым downstream-переходом.

Цель: каждый обязательный переход, где требуется audit, должен иметь отдельный audit block.

Задачи:

- Уточнить `agents/traceability-auditor-agent.md`: каждый audit сохраняется отдельным блоком `# Отчет аудита трассируемости`.
- Добавить в audit block обязательные поля:
  - `ID: TA-xx`
  - `Контракт агента`
  - `Режим запуска`
  - `Переданный контекст`
  - `Цель проверки`
  - `Текущий этап`
  - `Предложенный следующий этап`
  - `Проверенные артефакты`
  - `Статус аудита`
  - `Найденные нарушения`
  - `Рекомендуемый следующий шаг`
- Обновить `validate_run.py` для проверки обязательных audit blocks.
- Добавить negative fixture `invalid-missing-audit-gate`.

Acceptance criteria:

- Один общий audit не считается заменой per-gate audit trail.
- Валидатор падает при отсутствии обязательного audit block.
- Valid fixtures и example проходят.

### A3. Единый формат service history

Проблема: service reports человекочитаемы, но недостаточно структурированы для надежной проверки.

Цель: сделать service reports машинно-проверяемыми без потери читаемости.

Задачи:

- Зафиксировать единый формат записи route-control:
  - `ID`
  - `Текущий этап`
  - `Предложенный следующий этап`
  - `Проверяемое основание`
  - `Проверенные условия`
  - `Решение`
  - `Причина блокировки`
  - `Требуемое действие`
- Зафиксировать единый формат audit entry.
- Обновить templates или agent contracts, где этот формат должен быть описан.
- Обновить validator на обязательные поля.

Acceptance criteria:

- Каждый route block и audit block имеет ID.
- Валидатор проверяет обязательные поля.
- Старые исторические runs не обязаны мигрироваться, но fixtures/examples должны быть актуализированы.

## B. Трассировка историй и канонических правил

### B1. Локальная трассировка CR в историях

Проблема: история может использовать каноническое правило в критериях приемки или бизнес-правилах, но не перечислить его в блоке `Источник`. В тестовом прогоне это проявилось на US-04: доступ финансового контролера был добавлен после CL-07/CR-18/CR-19, но источник истории не стал полностью самодостаточным.

Цель: если история использует CR внутри тела, этот CR должен быть указан в блоке `Источник`.

Задачи:

- Обновить `skills/story-extractor/SKILL.md`.
- Обновить `skills/story-quality-reviewer/SKILL.md`.
- Обновить `agents/traceability-auditor-agent.md`.
- Расширить validator или unit tests на проверку локальных CR sources.
- Добавить negative fixture `invalid-story-uses-cr-without-source`.

Acceptance criteria:

- Если `CR-xx` встречается в критериях, бизнес-правилах или зависимостях истории, он должен быть указан в блоке `Источник`.
- Раздел “Покрытие канонических правил” не заменяет локальный источник истории.
- История с нарушением получает ошибку validator или reviewer defect.

### B2. Source markers для новых фактов в критериях приемки

Проблема: не все критерии приемки имеют локальные source markers. Это нормально для критериев, прямо выведенных из источников истории, но опасно для новых фактов.

Цель: разделить derived criteria и criteria with new factual content.

Задачи:

- Уточнить в `story-quality-reviewer`, что не нужно механически требовать источник на каждой строке.
- Ввести правило: если критерий добавляет новый факт, которого нет в источниках истории, нужен локальный `Источник`.
- Добавить negative fixture с критерием, который содержит новый неподтвержденный факт.

Acceptance criteria:

- Reviewer не засоряет истории избыточными source markers.
- Новый факт без источника ловится.
- Derived criteria остаются допустимыми без локального marker, если источник очевиден из блока `Источник`.

## C. Калибровка story readiness

### C1. Разделить requirements readiness и delivery readiness

Проблема: все истории получили `Высокий`, хотя у некоторых остались технические зависимости. Для требований это нормально, но команда может прочитать `Высокий` как “можно сразу брать в разработку без выравнивания”.

Цель: разделить готовность требований и влияние на delivery.

Задачи:

- Обновить `templates/story-readiness-template.md`.
- Обновить `skills/story-quality-reviewer/SKILL.md`.
- Ввести два поля:
  - `Готовность требований: Высокий | Средний | Низкий`
  - `Delivery readiness impact: none | needs_technical_alignment | blocks_delivery`
- Добавить блок `Технические зависимости`.
- Обновить `delivery-readiness-agent.md`, чтобы он использовал этот блок.

Acceptance criteria:

- История может иметь `Готовность требований: Высокий` и `Delivery readiness impact: needs_technical_alignment`.
- Технические зависимости не превращаются автоматически в продуктовые открытые вопросы.
- Readiness pack подхватывает technical alignment items.

### C2. Уточнить значение статуса `Высокий`

Проблема: сейчас `Высокий` смешивает наличие источников, приемку, отсутствие GAP и техническую реализуемость.

Цель: сделать статус `Высокий` аналитически точным.

Правило: `Высокий` означает:

- есть источник;
- есть актор;
- есть потребность;
- есть ценность;
- есть проверяемые критерии приемки;
- нет блокирующих открытых вопросов требований;
- нет незакрытых GAP, влияющих на поведение истории.

Технические неизвестные не понижают `Готовность требований`, если они не меняют scope или поведение продукта.

Acceptance criteria:

- Story readiness объясняет, почему статус высокий.
- Technical concerns выводятся отдельно.
- Delivery readiness не смешивается с requirements readiness.

## D. GAP и residual risks

### D1. Сохранять остаточные риски после закрытия GAP

Проблема: после закрытия GAP-01/GAP-02 residual risks почти исчезли из gap report, хотя внешние зависимости остались важными для delivery.

Цель: закрытый GAP должен сохранять residual risk, если риск реализации или интеграции остается.

Задачи:

- Обновить `templates/gap-risk-report-template.md`.
- Обновить `skills/requirements-gap-analyzer/SKILL.md`.
- Добавить поля:
  - `Остаточный риск: нет | низкий | средний | высокий`
  - `Причина остаточного риска`
  - `Куда передать: delivery-readiness | backlog | no-action`
- Обновить `delivery-readiness-agent.md`, чтобы он переносил residual risks в темы выравнивания.

Acceptance criteria:

- GAP может быть закрытым и неблокирующим, но иметь residual risk.
- Закрытый GAP с внешним справочником или внешним курсом не теряет риск.
- Валидатор проверяет наличие residual risk fields у закрытых GAP.

### D2. Разделить product GAP и delivery risk

Проблема: командные technical questions могут быть полезными, но не должны возвращаться в `Открытые вопросы` текущих требований без нового requirements-processing.

Цель: четко отделить пробелы требований от технических вопросов реализации.

Задачи:

- Уточнить `requirements-gap-analyzer`: GAP — только про требования, scope, поведение, данные, роли, источники.
- Уточнить `delivery-readiness-agent`: technical alignment questions не являются каноническими open questions.
- Добавить сценарий в `orchestrator-routing-scenarios.md`.

Acceptance criteria:

- Technical question в readiness pack не делает продуктовый комплект incomplete.
- Если technical question меняет требование, он должен идти в новый requirements-processing или change request.

## E. Post-pipeline handoff

### E1. Усилить kickoff brief

Проблема: текущий `Kickoff brief` получился кратким summary, но не полноценным сценарием 20-30 минутной встречи.

Цель: сделать brief рабочим handoff-документом, а не пересказом требований.

Задачи:

- Обновить `templates/kickoff-brief-template.md`.
- Обновить `agents/kickoff-briefing-agent.md`.
- Обязательные разделы:
  - цель встречи;
  - ожидаемый результат встречи;
  - что команда должна подтвердить;
  - темы выравнивания;
  - решения, которые нельзя менять без change request;
  - handoff checklist;
  - вопросы команды к аналитике.

Acceptance criteria:

- Brief содержит 3-5 тем выравнивания.
- Brief не дублирует спецификацию.
- Brief не добавляет новые требования.
- Brief остается пригодным для чтения за 5-7 минут.

### E2. Защитить канон от readiness questions

Проблема: readiness pack может содержать вопросы команды, например про технический источник справочника. Эти вопросы полезны, но не должны становиться требованиями.

Цель: явно маркировать readiness questions как non-canonical.

Задачи:

- Уточнить `delivery-readiness-agent.md`.
- Добавить в readiness template строку: `Статус вопросов команды: не являются каноническими требованиями до отдельного уточнения или change request`.
- Обновить сценарии.

Acceptance criteria:

- Readiness questions не попадают в `product/open-questions.md`.
- Командные вопросы не блокируют финальный комплект, если не меняют требования.

## F. Validator и regression coverage

### F1. Проверка полноты route gates

Цель: validator должен ловить отсутствие обязательного route gate.

Задачи:

- Добавить список обязательных stage pairs.
- Проверять наличие stage pair в `routing-decision.md`.
- Учитывать, что `requirements-elicitor` может быть пропущен для хорошего входа.
- Учитывать post-pipeline gates только если существуют `team/` артефакты или CL от `scope-finalizer-agent`.

Acceptance criteria:

- `invalid-missing-route-gate` падает.
- Valid fixtures проходят.

### F2. Проверка полноты audit gates

Цель: validator должен ловить отсутствие обязательного traceability audit.

Задачи:

- Проверять audit blocks по `Текущий этап` и `Предложенный следующий этап`.
- Проверять launch metadata в каждом block.
- Проверять `Статус аудита: passed` для финального разрешающего audit.

Acceptance criteria:

- `invalid-missing-audit-gate` падает.
- Existing `invalid-failed-audit` продолжает падать по failed audit.

### F3. Проверка story CR local sources

Цель: validator или unit tests должны ловить CR, использованный в истории, но отсутствующий в источниках истории.

Задачи:

- Для каждого story block выделять `Источник`.
- Искать `CR-xx` в теле истории.
- Если CR встречается в теле, но не в source section, возвращать ошибку.

Acceptance criteria:

- `invalid-story-cr-not-in-source` падает.
- Valid fixtures проходят.

### F4. Проверка residual risk fields

Цель: закрытые GAP должны сохранять residual risk fields.

Задачи:

- Если `Статус пробела: закрыт`, требовать:
  - `Остаточный риск`
  - `Причина остаточного риска`
  - `Куда передать`
- Для `Остаточный риск: нет` разрешить краткую причину.

Acceptance criteria:

- Closed GAP без residual risk fields падает.
- Existing gap fixtures обновлены.

## G. Canonical examples

### G1. Обновить `examples/trip-approval`

Проблема: canonical example должен демонстрировать актуальный стандарт качества service trail.

Задачи:

- После A-F обновить `examples/trip-approval/service/traceability-audit.md`.
- Обновить `examples/trip-approval/service/routing-decision.md`.
- Обновить `examples/trip-approval/README.md`, добавив описание полного audit/route trail.

Acceptance criteria:

- `make validate-example` проходит.
- Example можно использовать как образец для новых прогонов.

### G2. Добавить example с historical block

Цель: показать, что исторический `block` допустим, если он закрыт последующим `allow`.

Задачи:

- Создать или обновить example run, где:
  - route guardian сначала блокирует переход;
  - после исправления появляется allow;
  - итоговое решение `allow`;
  - `Незакрытые блокировки: нет`.

Acceptance criteria:

- Validator принимает historical block с закрытием.
- Validator отклоняет незакрытый block.

## H. Следующий системный тест

### H1. Новый тестовый вход для проверки улучшений

Цель: после внедрения улучшений выполнить новый тестовый прогон, который специально проверяет service gates.

Требования к входу:

- конфликт маршрута;
- факт без надежного источника;
- вопрос, который появляется на этапе спецификации;
- техническая зависимость, которая должна стать residual risk;
- post-finalizer вопрос по scope boundary;
- один historical route block, который должен закрыться allow.

Acceptance criteria:

- В новом прогоне есть полный route trail.
- В новом прогоне есть per-gate audit trail.
- Есть хотя бы один закрытый historical block.
- Есть closed GAP with residual risk.
- Readiness questions не попали в product open questions.

## 4. Приоритеты выполнения

### P0. Доказуемость gates

- A1
- A2
- A3
- F1
- F2

Причина: без этого невозможно строго доказать корректность маршрута.

### P1. Качество трассировки и readiness

- B1
- B2
- C1
- C2
- F3

Причина: это повышает надежность downstream-артефактов и уменьшает риск скрытых домыслов.

### P2. GAP, residual risks и handoff

- D1
- D2
- E1
- E2
- F4

Причина: это улучшает пригодность результата для команды и delivery.

### P3. Examples и повторный прогон

- G1
- G2
- H1

Причина: выполнять после изменения контрактов и validator, чтобы examples отражали новый стандарт.

## 5. Definition of Done для roadmap

Roadmap считается выполненным, когда:

- `validate_run.py` проверяет обязательные route gates и audit gates.
- Service reports имеют полную историю обязательных проверок.
- Story readiness отделяет готовность требований от delivery alignment.
- GAP report сохраняет residual risks.
- Kickoff brief стал рабочим handoff-документом.
- Readiness questions явно non-canonical.
- Canonical examples обновлены.
- Новый системный тестовый прогон проходит validator и демонстрирует все ключевые улучшения.

## 6. Общие правила для агентов, которые берут задачи из roadmap

- Перед изменениями выполнять `РЕМОНТ`.
- Не менять продуктовые runs старых прогонов, кроме специально выбранных fixtures/examples.
- Не смешивать задачи из разных workstream без необходимости.
- После каждой задачи запускать минимум:
  - `python3 -m unittest discover -s tests`
  - релевантный `python3 scripts/validate_run.py <fixture-or-example>`
- После завершения workstream запускать:
  - `make check`
- В commit message указывать workstream ID, например:
  - `A1: Validate complete route gate history`
  - `C1: Split requirements and delivery readiness`
