# Проверочная Матрица Маршрутизации Оркестратора

Этот файл не является вторым полным контрактом. Полный маршрут и gates задает `AGENTS.md`, детализацию агентов задают `agents/*.md`, детализацию профильных этапов задают `skills/*/SKILL.md`.

Матрица ниже нужна для ревью поведения оркестратора на типовых входах и сбоях. Каждый сценарий фиксирует только отличие от базового маршрута, ключевой риск и ожидаемый outcome.

## Общие Ожидания

Базовый core-route:

```text
artifact-persistence-agent(create_run)
requirements-elicitor, если вход неполный
spec-structurer
story-extractor
story-quality-reviewer
requirements-gap-analyzer
final traceability audit
final routing control
final aggregation
mandatory offer: scope-finalizer-agent
optional offer: kickoff brief
if brief accepted: kickoff-briefing-agent -> delivery-readiness-agent
```

Сервисные стыки обязательны для всех применимых сценариев:
- новые и обновленные продуктовые артефакты сохраняются в `product/`;
- служебные отчеты сохраняются в `service/`;
- командные post-pipeline документы сохраняются в `team/`;
- downstream-переход выполняется только после успешной фиксации, обязательного аудита и route-control;
- ответы `scope-finalizer-agent` не создают отдельный файл, а фиксируются в `product/clarification-log.md` и пересобранных downstream-артефактах;
- исторические `block` допустимы в `service/routing-decision.md`, если итоговое решение `allow` и незакрытых блокировок нет.

Обязательные итоговые артефакты успешного core-route:
- `product/input.md`
- `product/clarification-log.md`
- `product/clarified-requirements.md`
- `product/canonical-rules.md`
- `product/assumptions.md`
- `product/open-questions.md`
- `product/specification.md`
- `product/user-stories.md`
- `product/story-readiness.md`
- `product/gap-risk-report.md`
- `service/traceability-audit.md`
- `service/routing-decision.md`

Post-pipeline артефакты:
- `team/kickoff-brief.md` создается только после отдельного согласия пользователя на brief;
- `team/delivery-readiness-pack.md` и `team/scenario-map.mmd` обязательны, если brief заказан;
- `team/state-model.mmd` создается только если в спецификации есть подтвержденная модель состояний.

## Сценарии

| ID | Сценарий | Ключевой риск | Ожидаемый route outcome | Обязательные артефакты / сигналы |
| --- | --- | --- | --- | --- |
| 01 | Сырой ввод без акторов и целей | Оркестратор перескочит к спецификации без уточнения | Сначала `requirements-elicitor`; при нехватке данных `needs_user_answer`; после ответа обычный core-route | `product/input.md`; после уточнения `clarification-log`, `clarified-requirements`, `canonical-rules`; downstream только после audit+route allow |
| 02 | Заметки встречи с частично понятным контекстом | Частичная ясность будет принята за полный scope | `requirements-elicitor` закрывает недостающие акторы/цели/границы либо останавливается с вопросами | Открытые вопросы фиксируются только после попытки уточнения; завершенный переход требует `canonical-rules` |
| 03 | Почти готовая спецификация | Система потеряет служебные gates из-за высокого качества входа | Допустим прямой `spec-structurer`, но сохранение, аудит и route-control остаются обязательными | Если `canonical-rules` не выделялись, аудит явно фиксирует неприменимость слоя |
| 04 | Одна пользовательская история на входе | История станет готовой без восстановления спецификации | Вход сначала нормализуется до спецификации; затем истории извлекаются заново или сверяются | История без источника или без спецификации не считается финальной |
| 05 | Смешанный и противоречивый ввод | Противоречие будет замаскировано редактурой | `requirements-elicitor` или `spec-structurer` возвращает вопросы; route-control блокирует downstream до закрытия | `service/routing-decision.md` содержит `block`, затем `allow` после исправления |
| 06 | Истории готовы, но фундамент слабый | Готовность историй подменит слабую трассируемость | Система возвращается к уточнению/структурированию фундамента; истории не идут в финал без источников | `story-readiness` не может быть `Высокий` при фундаментальном GAP |
| 07 | Новые вопросы возникли на этапе спецификации | Новые `Открытые вопросы` будут перенесены дальше | `routing-guardian-agent` блокирует `spec-structurer -> story-extractor`; вопросы возвращаются в `requirements-elicitor` | Промежуточная спецификация и вопросы сохраняются как незавершенные при необходимости |
| 08 | Новые вопросы возникли на этапе извлечения историй | Неполные истории попадут на review | `story-extractor -> story-quality-reviewer` блокируется; вопросы возвращаются в `requirements-elicitor`; затем повторный `story-extractor` | Обновленные правила и истории проходят audit+route-control |
| 09 | Новые вопросы возникли на этапе проверки историй | Reviewer понизит качество, но pipeline пойдет дальше без уточнения | `story-quality-reviewer -> requirements-gap-analyzer` блокируется до попытки закрыть вопросы | `story-readiness` и `open-questions` фиксируются; после ответа reviewer вызывается повторно |
| 10 | Файловая фиксация нового прогона | Новый прогон перезапишет старый каталог | `artifact-persistence-agent(create_run)` выбирает новый versioned каталог и возвращает `current_run_path` | Все update-сохранения используют тот же `current_run_path` |
| 11 | Аудит трассируемости блокирует переход | Артефакт без источника пройдет дальше | `traceability-auditor-agent -> failed`; route-control блокирует; артефакт возвращается профильному скиллу | Failed audit сохраняется в `service/traceability-audit.md`; downstream запрещен до passed-аудита |
| 12 | Контроль маршрута блокирует недопустимый переход | Оркестратор сам разрешит переход без guardian | `routing-guardian-agent -> block`; выполняется требуемое действие; повторная проверка может дать `allow` | `service/routing-decision.md` отделяет историю проверок от итогового решения |
| 13 | После успешного ядра предлагается финализирующее интервью | Интервью будет забыто | После финальной агрегации оркестратор обязан предложить `scope-finalizer-agent` | Без предложения интервью post-pipeline route невалиден |
| 14 | Brief и delivery readiness после opt-in | Командные документы создадут без отдельного согласия | После отказа/завершения интервью оркестратор отдельно спрашивает про brief; при согласии запускает оба post-pipeline агента | `team/kickoff-brief.md`, `delivery-readiness-pack.md`, `scenario-map.mmd`, применимый `state-model.mmd` |
| 15 | Запрос на обслуживание системы без `РЕМОНТ` | Оркестратор начнет maintenance без preflight | Задать ровно preflight-вопрос и остановиться | Никаких файловых изменений, анализа системы или maintenance-сценариев |
| 16 | Оркестратор не предложил интервью после успешного ядра | Финальный handoff неполный | Route считается дефектным; нужно вернуться к обязательному предложению интервью | Командные документы не запускаются до корректной точки |
| 17 | `scope-finalizer-agent` задает лишние/наводящие вопросы | Интервью расширит scope | Агент задает только вопросы с source anchor и scope effect; лишнее запрещено | Нарушение возвращается на доработку; новые пожелания фиксируются out-of-scope |
| 18 | Командные документы запускаются без согласия | Post-pipeline подменит пользовательский opt-in | `kickoff-briefing-agent` и `delivery-readiness-agent` не вызываются | Файлы `team/` отсутствуют |
| 19 | `kickoff-briefing-agent` обнаружил противоречие | Brief станет новым каноном поверх конфликта | Агент возвращает `needs_orchestrator_decision`; brief не используется как финальный | `team/kickoff-brief.md` отсутствует или `incomplete`; readiness не запускается до решения |
| 20 | Обязательный служебный агент недоступен | Оркестратор заменит контроль ручной проверкой | Pipeline останавливается с сообщением о недоступном контроле | Промежуточные артефакты сохраняются как `incomplete`, если возможно |
| 21 | Пользователь отказался от интервью и brief | Система продолжит post-pipeline без opt-in | Core-route завершается текущими финальными артефактами | `team/kickoff-brief.md` и `team/delivery-readiness-pack.md` отсутствуют |
| 22 | Delivery readiness как обязательное дополнение к brief | Система завершит post-pipeline после одного brief | После successful brief обязательно вызывается `delivery-readiness-agent` | Readiness pack и Mermaid-визуализации сохраняются в `team/` |
| 23 | Delivery readiness пытается принять технические решения | Командный pack станет backlog/API/design spec | Агент возвращается на доработку или `needs_orchestrator_decision`; технические решения удаляются, неподтвержденные элементы идут в вопросы | До исправления `team/delivery-readiness-pack.md` отсутствует или `incomplete`; `candidate` допустим только для зон работы, выведенных из требований |

## Быстрые Инварианты Для Ревью

- Если появился новый существенный вопрос, downstream-переход должен быть `block`.
- Если аудит трассируемости `failed`, downstream-переход запрещен.
- Если route-control `block`, оркестратор выполняет требуемое действие, а не выбирает другой маршрут.
- Если пользовательский ответ изменил требования, он попадает в `Лог уточнений` и downstream-артефакты пересобираются.
- Если `scope-finalizer-agent` подтвердил или исключил элемент, это проходит тот же контур сохранения, пересборки, аудита и route-control.
- Если ordered post-pipeline consent отсутствует, файлы в `team/` не создаются.
