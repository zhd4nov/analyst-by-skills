# Сценарии Маршрутизации Оркестратора

Использовать этот файл как минимальный набор проверочных сценариев для MVP.

Каждый сценарий задает:
- тип входа
- пример входа
- ожидаемый полный оркестрационный маршрут
- ожидаемые артефакты
- ключевое правило принятия решения

## Общие ожидания для полного прогона

Если сценарий доходит до финальной агрегации, маршрут должен включать не только профильные скиллы, но и служебных агентов:
- `artifact-persistence-agent` сохраняет `Вход` до первого профильного скилла и фиксирует новые или обновленные артефакты после каждого этапа
- `traceability-auditor-agent` проверяет трассируемость перед downstream-переходами и перед финальной агрегацией
- `routing-guardian-agent` проверяет допустимость каждого предложенного перехода и финальной агрегации
- первый вызов `artifact-persistence-agent` выполняется в режиме `create_run`, сохраняет `product/input.md` и возвращает `current_run_path`
- все последующие вызовы `artifact-persistence-agent` выполняются в режиме `update_run` с тем же `current_run_path`
- каждый вызов `traceability-auditor-agent` должен завершаться сохранением `service/traceability-audit.md` через `artifact-persistence-agent`
- каждый вызов `routing-guardian-agent` должен завершаться сохранением `service/routing-decision.md` через `artifact-persistence-agent`
- переход к следующему профильному этапу разрешен только после успешной файловой фиксации измененных артефактов, `passed` от обязательного аудита трассируемости и `allow` от контроля маршрута
- после успешной финальной агрегации оркестратор обязан сам предложить финализирующее интервью `scope-finalizer-agent`
- если пользователь согласился на интервью, оркестратор запускает `scope-finalizer-agent`, фиксирует ответы, пересобирает затронутые артефакты и повторно выполняет аудит трассируемости и контроль маршрута
- если пользователь отказался от интервью, оркестратор не вызывает `scope-finalizer-agent`
- после отказа от интервью или после завершенного интервью с успешной пересборкой оркестратор обязан сам спросить, нужен ли `Kickoff brief`
- `kickoff-briefing-agent` запускается только после отдельного явного согласия пользователя на подготовку brief
- если пользователь отказался от brief, оркестратор завершает работу текущими финальными артефактами и не вызывает `kickoff-briefing-agent`

Минимальный набор итоговых файлов полного прогона:
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

Опциональные post-pipeline файлы:
- `product/kickoff-brief.md` создается только если пользователь явно согласился на подготовку brief после завершения или отказа от интервью.
- Ответы финализирующего интервью не создают отдельный файл; они фиксируются в `product/clarification-log.md` и связанных канонических артефактах.

Сценарии ниже считаются валидными только при выполнении всех служебных стыков: новые и обновленные продуктовые артефакты фиксируются в `product/`, каждый аудит фиксируется в `service/traceability-audit.md`, каждый контроль маршрута фиксируется в `service/routing-decision.md`, а переход к следующему профильному этапу выполняется только после этих фиксаций.

`product/canonical-rules.md` ожидается как проверяемый артефакт во всех сценариях, где сформированы или доступны `Канонические правила`. Если маршрут начинается с достаточно полного входа и правила не выделялись отдельным слоем, аудит трассируемости должен явно зафиксировать, что `product/canonical-rules.md` не применялся на этом прогоне, а downstream-этапы не достраивали факты из непроверенного пересказа.

---

## Сценарий 1: Сырой ввод без акторов и целей

### Тип входа
- Сырой ввод

### Пример входа
- "Нужно сделать нормальный процесс согласования командировок, чтобы было быстрее и без писем."

### Ожидаемый маршрут ядра
1. `artifact-persistence-agent` в режиме `create_run` сохраняет `product/input.md` и возвращает `current_run_path`
2. `requirements-elicitor`
3. `artifact-persistence-agent` в режиме `update_run` сохраняет `product/clarification-log.md`, `product/clarified-requirements.md`, `product/canonical-rules.md`, `product/assumptions.md`, `product/open-questions.md`
4. `traceability-auditor-agent`
5. `artifact-persistence-agent` в режиме `update_run` сохраняет `service/traceability-audit.md`
6. `routing-guardian-agent` проверяет переход к `spec-structurer`
7. `artifact-persistence-agent` в режиме `update_run` сохраняет `service/routing-decision.md`
8. `spec-structurer`
9. `artifact-persistence-agent` в режиме `update_run` сохраняет `product/specification.md`
10. `traceability-auditor-agent`
11. `artifact-persistence-agent` в режиме `update_run` сохраняет `service/traceability-audit.md`
12. `routing-guardian-agent` проверяет переход к `story-extractor`
13. `artifact-persistence-agent` в режиме `update_run` сохраняет `service/routing-decision.md`
14. `story-extractor`
15. `artifact-persistence-agent` в режиме `update_run` сохраняет `product/user-stories.md`
16. `traceability-auditor-agent`
17. `artifact-persistence-agent` в режиме `update_run` сохраняет `service/traceability-audit.md`
18. `routing-guardian-agent` проверяет переход к `story-quality-reviewer`
19. `artifact-persistence-agent` в режиме `update_run` сохраняет `service/routing-decision.md`
20. `story-quality-reviewer`
21. `artifact-persistence-agent` в режиме `update_run` сохраняет `product/story-readiness.md`
22. `traceability-auditor-agent`
23. `artifact-persistence-agent` в режиме `update_run` сохраняет `service/traceability-audit.md`
24. `routing-guardian-agent` проверяет переход к `requirements-gap-analyzer`
25. `artifact-persistence-agent` в режиме `update_run` сохраняет `service/routing-decision.md`
26. `requirements-gap-analyzer`
27. `artifact-persistence-agent` в режиме `update_run` сохраняет `product/gap-risk-report.md`
28. `traceability-auditor-agent`
29. `artifact-persistence-agent` в режиме `update_run` сохраняет `service/traceability-audit.md`
30. `routing-guardian-agent` проверяет финальную агрегацию
31. `artifact-persistence-agent` в режиме `update_run` сохраняет `service/routing-decision.md`
32. Оркестратор возвращает финальный комплект основного пайплайна и предлагает финализирующее интервью
33. После отказа от интервью или успешного интервью с пересборкой оркестратор спрашивает, нужен ли `Kickoff brief`

### Ожидаемые артефакты
- полный набор файлов прогона
- `product/canonical-rules.md`
- `Отчет аудита трассируемости` со статусом `passed`
- `Отчет контроля маршрута` с итоговым `allow`

### Ключевое правило
- Если во входе отсутствуют явные акторы, цели и сценарии, оркестратор обязан начать с уточнения требований, а не переходить сразу к спецификации.
- Пост-пайплайновые шаги не являются частью ядра, но их предложения обязательны после валидной финальной агрегации.

---

## Сценарий 2: Заметки встречи с частично понятным контекстом

### Тип входа
- Заметки встречи

### Пример входа
- "На встрече решили, что клиент должен видеть статус возврата, склад меняет статус вручную, а поддержка не должна отвечать на типовые вопросы по возврату."

### Ожидаемый маршрут
1. `artifact-persistence-agent` в режиме `create_run` сохраняет `product/input.md` и возвращает `current_run_path`
2. `spec-structurer`
3. `artifact-persistence-agent` сохраняет `Спецификация` и сопутствующие артефакты
4. `traceability-auditor-agent`
5. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
6. `routing-guardian-agent` проверяет переход к `story-extractor`
7. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
8. `story-extractor`
9. `traceability-auditor-agent`
10. `routing-guardian-agent` проверяет переход к `story-quality-reviewer`
11. `story-quality-reviewer`
12. `traceability-auditor-agent`
13. `routing-guardian-agent` проверяет переход к `requirements-gap-analyzer`
14. `requirements-gap-analyzer`
15. `traceability-auditor-agent`
16. `routing-guardian-agent` проверяет финальную агрегацию

### Ожидаемые артефакты
- `Вход`
- `Спецификация`
- `Пользовательские истории`
- `Статус готовности историй`
- `Отчет о пробелах и рисках`
- `service/traceability-audit.md`
- `service/routing-decision.md`
- `product/canonical-rules.md`, если на этапе структурирования были выделены операциональные правила

### Ключевое правило
- Если вход уже содержит акторов, проблему и основной сценарий, оркестратор может не вызывать `requirements-elicitor` первым шагом, но служебные проверки и фиксация остаются обязательными.

---

## Сценарий 3: Почти готовая спецификация

### Тип входа
- Псевдо-спецификация

### Пример входа
- "Есть клиент, оператор склада и система возвратов. Клиент должен видеть актуальный статус возврата. Статусы приходят из складской системы. Частичный возврат пока не поддерживаем."

### Ожидаемый маршрут
1. `artifact-persistence-agent` в режиме `create_run` сохраняет `product/input.md` и возвращает `current_run_path`
2. `spec-structurer`
3. `artifact-persistence-agent` сохраняет `Спецификация` и сопутствующие артефакты
4. `traceability-auditor-agent`
5. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
6. `routing-guardian-agent` проверяет переход к `story-extractor`
7. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
8. `story-extractor`
9. `artifact-persistence-agent` сохраняет `Пользовательские истории`
10. `traceability-auditor-agent`
11. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
12. `routing-guardian-agent` проверяет переход к `story-quality-reviewer`
13. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
14. `story-quality-reviewer`
15. `artifact-persistence-agent` сохраняет `Статус готовности историй`
16. `traceability-auditor-agent`
17. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
18. `routing-guardian-agent` проверяет переход к `requirements-gap-analyzer`
19. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
20. `requirements-gap-analyzer`
21. `artifact-persistence-agent` сохраняет `Отчет о пробелах и рисках`
22. `traceability-auditor-agent`
23. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
24. `routing-guardian-agent` проверяет финальную агрегацию
25. `artifact-persistence-agent` сохраняет `service/routing-decision.md`

### Ожидаемые артефакты
- `Вход`
- `Спецификация`
- `Пользовательские истории`
- `Статус готовности историй`
- `Отчет о пробелах и рисках`
- `service/traceability-audit.md`
- `service/routing-decision.md`
- `product/canonical-rules.md`, если вход или `spec-structurer` выделил операциональные правила; иначе явная отметка аудита, что слой не применялся

### Ключевое правило
- Если вход уже похож на спецификацию, оркестратор должен нормализовать и структурировать его, а не возвращаться к полному elicitation без причины.

---

## Сценарий 4: Одна пользовательская история на входе

### Тип входа
- Пользовательская история

### Пример входа
- "Как менеджер, я хочу экспортировать заявки, чтобы работать удобнее."

### Ожидаемый маршрут
1. `artifact-persistence-agent` в режиме `create_run` сохраняет `product/input.md` и возвращает `current_run_path`
2. `requirements-elicitor`
3. `artifact-persistence-agent` сохраняет `Уточненные требования`, `Канонические правила`, `Открытые вопросы`
4. `traceability-auditor-agent`
5. `routing-guardian-agent` проверяет переход к `spec-structurer`
6. `spec-structurer`
7. `traceability-auditor-agent`
8. `routing-guardian-agent` проверяет переход к `story-extractor`
9. `story-extractor`
10. `traceability-auditor-agent`
11. `routing-guardian-agent` проверяет переход к `story-quality-reviewer`
12. `story-quality-reviewer`
13. `traceability-auditor-agent`
14. `routing-guardian-agent` проверяет переход к `requirements-gap-analyzer`
15. `requirements-gap-analyzer`
16. `traceability-auditor-agent`
17. `routing-guardian-agent` проверяет финальную агрегацию

### Ожидаемые артефакты
- полный набор файлов прогона
- `product/canonical-rules.md`
- `service/traceability-audit.md`
- `service/routing-decision.md`

### Ключевое правило
- Одна история не заменяет требования целиком. Если не определены контекст, границы и бизнес-цель, оркестратор должен вернуться к началу и восстановить фундамент.

---

## Сценарий 5: Смешанный и противоречивый ввод

### Тип входа
- Смешанный ввод

### Пример входа
- "Клиент должен сам отменять возврат. Возврат после отправки на склад отменять нельзя. Нужен экран возвратов и экспорт."

### Ожидаемый маршрут
1. `artifact-persistence-agent` в режиме `create_run` сохраняет `product/input.md` и возвращает `current_run_path`
2. `requirements-elicitor`
3. `artifact-persistence-agent` сохраняет `Лог уточнений`, `Уточненные требования`, `Канонические правила`, `Допущения` и `Открытые вопросы`
4. если нужен ответ пользователя: `routing-guardian-agent` блокирует переход к `spec-structurer`
5. `artifact-persistence-agent` сохраняет `service/routing-decision.md` со статусом `block`, пайплайн останавливается
6. после закрытия блокеров: `requirements-elicitor` обновляет уточненные артефакты
7. `artifact-persistence-agent` сохраняет обновленные артефакты
8. `traceability-auditor-agent`
9. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
10. `routing-guardian-agent` проверяет переход к `spec-structurer`
11. `artifact-persistence-agent` сохраняет `service/routing-decision.md` со статусом `allow`
12. `spec-structurer`
13. `artifact-persistence-agent` сохраняет `product/specification.md`
14. `traceability-auditor-agent`
15. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
16. `routing-guardian-agent` проверяет переход к `story-extractor`
17. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
18. `story-extractor`
19. `artifact-persistence-agent` сохраняет `product/user-stories.md`
20. `traceability-auditor-agent`
21. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
22. `routing-guardian-agent` проверяет переход к `story-quality-reviewer`
23. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
24. `story-quality-reviewer`
25. `artifact-persistence-agent` сохраняет `product/story-readiness.md`
26. `traceability-auditor-agent`
27. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
28. `routing-guardian-agent` проверяет переход к `requirements-gap-analyzer`
29. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
30. `requirements-gap-analyzer`
31. `artifact-persistence-agent` сохраняет `product/gap-risk-report.md`
32. `traceability-auditor-agent`
33. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
34. `routing-guardian-agent` проверяет финальную агрегацию
35. `artifact-persistence-agent` сохраняет `service/routing-decision.md`

### Ожидаемые артефакты
- `Вход`
- `Лог уточнений`
- `Уточненные требования`
- `product/canonical-rules.md`
- `Открытые вопросы`, если конфликт нельзя закрыть без пользователя
- `service/traceability-audit.md`
- `service/routing-decision.md`
- финальные артефакты только после закрытия блокеров

### Ключевое правило
- Если во входе есть явные противоречия или смешаны требования и решения, оркестратор должен сначала выявить и зафиксировать конфликт, а не строить истории поверх противоречивого основания.

---

## Сценарий 6: Истории готовы, но фундамент слабый

### Тип входа
- Пользовательские истории

### Пример входа
- "US-10: Экспорт заявок"
- "US-11: Настройка фильтров"

### Ожидаемый маршрут
1. `artifact-persistence-agent` в режиме `create_run` сохраняет `product/input.md` и возвращает `current_run_path`
2. `story-quality-reviewer`
3. `artifact-persistence-agent` сохраняет `Статус готовности историй` и `Открытые вопросы`
4. `traceability-auditor-agent`
5. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
6. `routing-guardian-agent` проверяет предложенный downstream-переход к `requirements-gap-analyzer`
7. если истории имеют низкую готовность из-за слабого фундамента: `routing-guardian-agent` возвращает `block` для downstream-перехода к `requirements-gap-analyzer`
8. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
9. оркестратор выбирает восстановительный переход к `spec-structurer` или `requirements-elicitor` в зависимости от того, хватает ли входа для спецификации
10. `routing-guardian-agent` проверяет восстановительный переход
11. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
12. `spec-structurer` или `requirements-elicitor`
13. `artifact-persistence-agent` сохраняет восстановленные артефакты, включая `Спецификация` и `Канонические правила`, если они сформированы
14. `traceability-auditor-agent`
15. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
16. `routing-guardian-agent` проверяет переход к `story-extractor`
17. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
18. `story-extractor`
19. `artifact-persistence-agent` сохраняет обновленные `Пользовательские истории`
20. `traceability-auditor-agent`
21. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
22. `routing-guardian-agent` проверяет переход к `story-quality-reviewer`
23. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
24. `story-quality-reviewer`
25. `artifact-persistence-agent` сохраняет итоговый `Статус готовности историй`
26. `traceability-auditor-agent`
27. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
28. `routing-guardian-agent` проверяет переход к `requirements-gap-analyzer`
29. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
30. `requirements-gap-analyzer`
31. `artifact-persistence-agent` сохраняет `Отчет о пробелах и рисках`
32. `traceability-auditor-agent`
33. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
34. `routing-guardian-agent` проверяет финальную агрегацию
35. `artifact-persistence-agent` сохраняет `service/routing-decision.md`

### Ожидаемые артефакты
- `Вход`
- промежуточный `Статус готовности историй`
- `Открытые вопросы`
- `service/routing-decision.md` с блокировкой downstream-перехода
- `service/routing-decision.md` с разрешением восстановительного перехода
- при возврате назад: `Спецификация`
- `product/canonical-rules.md`, если фундамент восстановлен через уточнение требований
- обновленные `Пользовательские истории`
- `service/traceability-audit.md`
- `Отчет о пробелах и рисках`

### Ключевое правило
- Если истории есть, но у них слабая ценность, нет источника или неясен контекст, `routing-guardian-agent` должен заблокировать переход дальше, пока оркестратор не восстановит фундамент через спецификацию или уточнение.

---

## Сценарий 7: Новые открытые вопросы возникли на этапе спецификации

### Тип входа
- Частично уточненные требования

### Пример входа
- "Пользователь должен видеть статус цели и процент прогресса. Еще нужны статусы `не начата`, `в процессе`, `на паузе`, `просрочена`, `завершена`."

### Ожидаемый маршрут
1. `artifact-persistence-agent` в режиме `create_run` сохраняет `product/input.md` и возвращает `current_run_path`
2. `spec-structurer`
3. `artifact-persistence-agent` сохраняет промежуточную `Спецификацию` и новые `Открытые вопросы`
4. `traceability-auditor-agent`
5. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
6. `routing-guardian-agent` проверяет предложенный переход к `story-extractor`
7. если появились новые критичные `Открытые вопросы`: `routing-guardian-agent` возвращает `block`
8. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
9. `requirements-elicitor` пытается закрыть новые вопросы
10. `artifact-persistence-agent` сохраняет обновленные `Лог уточнений`, `Уточненные требования`, `Канонические правила` и `Открытые вопросы`
11. после закрытия вопросов: повторный вызов `spec-structurer`
12. `artifact-persistence-agent` сохраняет итоговую `Спецификация`
13. `traceability-auditor-agent`
14. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
15. `routing-guardian-agent` возвращает `allow` для перехода к `story-extractor`
16. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
17. `story-extractor`
18. `artifact-persistence-agent` сохраняет `product/user-stories.md`
19. `traceability-auditor-agent`
20. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
21. `routing-guardian-agent` проверяет переход к `story-quality-reviewer`
22. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
23. `story-quality-reviewer`
24. `artifact-persistence-agent` сохраняет `product/story-readiness.md`
25. `traceability-auditor-agent`
26. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
27. `routing-guardian-agent` проверяет переход к `requirements-gap-analyzer`
28. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
29. `requirements-gap-analyzer`
30. `artifact-persistence-agent` сохраняет `product/gap-risk-report.md`
31. `traceability-auditor-agent`
32. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
33. `routing-guardian-agent` проверяет финальную агрегацию
34. `artifact-persistence-agent` сохраняет `service/routing-decision.md`

### Ожидаемые артефакты
- промежуточная `Спецификация`
- новые `Открытые вопросы`
- `service/routing-decision.md` со статусом `block`, затем `allow`
- обновленные `Уточненные требования`
- обновленный `product/canonical-rules.md`, если вопросы закрыты новыми правилами
- итоговая `Спецификация`
- `service/traceability-audit.md`
- финальные артефакты полного прогона

### Ключевое правило
- Если новые `Открытые вопросы` впервые появились на этапе `spec-structurer`, `routing-guardian-agent` обязан заблокировать downstream-переход до попытки немедленного уточнения.

---

## Сценарий 8: Новые открытые вопросы возникли на этапе извлечения историй

### Тип входа
- Спецификация с недостаточно определенными границами пользовательской ценности

### Пример входа
- "Пользователь может настроить уведомления. Система должна поддерживать уведомления по важным событиям."

### Ожидаемый маршрут
1. `artifact-persistence-agent` в режиме `create_run` сохраняет `product/input.md` и возвращает `current_run_path`
2. `spec-structurer`
3. `artifact-persistence-agent` сохраняет `Спецификация`
4. `traceability-auditor-agent`
5. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
6. `routing-guardian-agent` проверяет переход к `story-extractor`
7. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
8. `story-extractor`
9. `artifact-persistence-agent` сохраняет промежуточные `Пользовательские истории` и новые `Открытые вопросы`
10. `traceability-auditor-agent`
11. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
12. `routing-guardian-agent` проверяет предложенный переход к `story-quality-reviewer`
13. если появились новые критичные `Открытые вопросы`: `routing-guardian-agent` возвращает `block`
14. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
15. `requirements-elicitor` пытается закрыть вопросы
16. `artifact-persistence-agent` сохраняет обновленные `Лог уточнений`, `Уточненные требования`, `Канонические правила` и `Открытые вопросы`
17. после закрытия вопросов: повторный вызов `story-extractor`
18. `artifact-persistence-agent` сохраняет итоговые `Пользовательские истории`
19. `traceability-auditor-agent`
20. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
21. `routing-guardian-agent` возвращает `allow` для перехода к `story-quality-reviewer`
22. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
23. `story-quality-reviewer`
24. `artifact-persistence-agent` сохраняет `product/story-readiness.md`
25. `traceability-auditor-agent`
26. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
27. `routing-guardian-agent` проверяет переход к `requirements-gap-analyzer`
28. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
29. `requirements-gap-analyzer`
30. `artifact-persistence-agent` сохраняет `product/gap-risk-report.md`
31. `traceability-auditor-agent`
32. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
33. `routing-guardian-agent` проверяет финальную агрегацию
34. `artifact-persistence-agent` сохраняет `service/routing-decision.md`

### Ожидаемые артефакты
- `Спецификация`
- промежуточные `Пользовательские истории`
- новые `Открытые вопросы`
- `service/routing-decision.md` со статусом `block`, затем `allow`
- обновленные `Уточненные требования`, если вопросы удалось закрыть
- обновленный `product/canonical-rules.md`, если вопросы закрыты новыми правилами
- итоговые `Пользовательские истории`
- `service/traceability-audit.md`
- финальные артефакты полного прогона

### Ключевое правило
- Если на этапе `story-extractor` нельзя определить границы истории, критерии приемки или источник без домыслов, `routing-guardian-agent` обязан заблокировать переход к `story-quality-reviewer`.

---

## Сценарий 9: Новые открытые вопросы возникли на этапе проверки историй

### Тип входа
- Пользовательские истории с формально заполненными полями, но без достаточного основания для проверки

### Пример входа
- "US-11: Экспорт заявок. Менеджер экспортирует заявки. Критерий приемки: файл скачивается."

### Ожидаемый маршрут
1. `artifact-persistence-agent` в режиме `create_run` сохраняет `product/input.md` и возвращает `current_run_path`
2. `story-quality-reviewer`
3. `artifact-persistence-agent` сохраняет промежуточные `Пользовательские истории`, `Статус готовности историй` и новые `Открытые вопросы`
4. `traceability-auditor-agent`
5. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
6. `routing-guardian-agent` проверяет предложенный переход к `requirements-gap-analyzer`
7. если появились новые критичные `Открытые вопросы`: `routing-guardian-agent` возвращает `block`
8. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
9. `requirements-elicitor` пытается закрыть вопросы
10. `artifact-persistence-agent` сохраняет обновленные `Лог уточнений`, `Уточненные требования`, `Канонические правила` и `Открытые вопросы`
11. после закрытия вопросов: повторный вызов `story-quality-reviewer`
12. `artifact-persistence-agent` сохраняет итоговый `Статус готовности историй`
13. `traceability-auditor-agent`
14. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
15. `routing-guardian-agent` возвращает `allow` для перехода к `requirements-gap-analyzer`
16. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
17. `requirements-gap-analyzer`
18. `artifact-persistence-agent` сохраняет `Отчет о пробелах и рисках`
19. `traceability-auditor-agent`
20. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
21. `routing-guardian-agent` проверяет финальную агрегацию
22. `artifact-persistence-agent` сохраняет `service/routing-decision.md`

### Ожидаемые артефакты
- промежуточные `Пользовательские истории`
- `Статус готовности историй`
- новые `Открытые вопросы`
- `service/routing-decision.md` со статусом `block`, затем `allow`
- обновленные релевантные артефакты после закрытия вопросов
- `product/canonical-rules.md`, если вопросы закрыты новыми правилами
- итоговый `Статус готовности историй`
- `service/traceability-audit.md`
- `Отчет о пробелах и рисках`

### Ключевое правило
- Если на этапе `story-quality-reviewer` нельзя проверить готовность истории без новой информации, `routing-guardian-agent` обязан заблокировать переход к `requirements-gap-analyzer`.

---

## Сценарий 10: Файловая фиксация нового прогона

### Тип входа
- Любой вход, запускающий пайплайн требований

### Предусловие
- В `runs/` уже существует каталог `return-status`

### Пример входа
- "Клиент должен видеть статус возврата в личном кабинете."

### Ожидаемый маршрут
1. `artifact-persistence-agent` в режиме `create_run`
2. профильный скилл по состоянию входа
3. `artifact-persistence-agent` возвращает `current_run_path`
4. `artifact-persistence-agent` в режиме `update_run` с тем же `current_run_path` после каждого завершенного или промежуточного этапа
5. если были вызваны `traceability-auditor-agent` или `routing-guardian-agent`, `artifact-persistence-agent` сохраняет их отчеты как файлы текущего прогона

### Ожидаемые артефакты
- `runs/return-status-v2/product/input.md`
- промежуточные или завершенные файлы артефактов текущего прогона
- `runs/return-status-v2/service/traceability-audit.md`, если был выполнен аудит трассируемости
- `runs/return-status-v2/service/routing-decision.md`, если был выполнен контроль маршрута
- список файлов, которые еще не созданы, если соответствующие артефакты еще не начинались

### Ключевое правило
- В режиме `create_run`, если каталог задачи уже существует, `artifact-persistence-agent` обязан создать новый каталог-версию. В режиме `update_run` агент обязан обновлять только переданный `current_run_path` и не создавать следующую версию.

---

## Сценарий 11: Аудит трассируемости блокирует переход дальше

### Тип входа
- Спецификация и пользовательские истории с нарушенной трассируемостью

### Предусловие
- В `Канонических правилах` есть правило `CR-03` с назначением `Использовать дальше -> Пользовательские истории`
- В `Пользовательских историях` нет покрытия `CR-03`
- Одна из историй не содержит конкретный `Источник`

### Пример входа
- `CR-03`: завершенная цель должна фиксировать дату завершения
- `US-02`: пользователь завершает цель
- `Источник`: не указан

### Ожидаемый маршрут
1. `story-extractor`
2. `traceability-auditor-agent`
3. `artifact-persistence-agent` сохраняет `service/traceability-audit.md` со статусом `failed`
4. если аудит вернул `failed`: повторный вызов `story-extractor`
5. после исправления: повторный вызов `traceability-auditor-agent`
6. `artifact-persistence-agent` сохраняет `service/traceability-audit.md` со статусом `passed`
7. `routing-guardian-agent` проверяет переход к `story-quality-reviewer`
8. `artifact-persistence-agent` сохраняет `service/routing-decision.md` со статусом `allow`
9. только после `passed` и `allow`: `story-quality-reviewer`

### Ожидаемые артефакты
- промежуточные `Пользовательские истории`
- отчет `traceability-auditor-agent` со статусом `failed`
- `runs/<name-of-task>/service/traceability-audit.md`
- список нарушений трассируемости
- доработанные `Пользовательские истории`
- отчет `traceability-auditor-agent` со статусом `passed`
- `runs/<name-of-task>/service/routing-decision.md`

### Ключевое правило
- Если у истории нет источника или каноническое правило, предназначенное для историй, не покрыто, оркестратор не имеет права переходить к `story-quality-reviewer`.

---

## Сценарий 12: Контроль маршрута блокирует недопустимый переход

### Тип входа
- Результат этапа с новым критичным `Открытым вопросом`

### Предусловие
- `spec-structurer` сформировал промежуточную `Спецификацию`
- На входе этапа новых `Открытых вопросов` не было
- На выходе этапа появился новый критичный `Открытый вопрос`
- Оркестратор предложил следующий шаг `story-extractor`

### Пример входа
- `Спецификация`: пользователь может завершить цель
- Новый `Открытый вопрос`: можно ли завершить цель без шагов?
- Предложенный следующий этап: `story-extractor`

### Ожидаемый маршрут
1. `spec-structurer`
2. `artifact-persistence-agent` сохраняет промежуточные артефакты
3. `routing-guardian-agent`
4. `artifact-persistence-agent` сохраняет `service/routing-decision.md` со статусом `block`
5. если контроль маршрута вернул `block`: `requirements-elicitor`
6. после закрытия вопроса: повторный вызов `spec-structurer`
7. повторная проверка через `routing-guardian-agent`
8. `artifact-persistence-agent` сохраняет `service/routing-decision.md` со статусом `allow`
9. только после `allow`: `story-extractor`

### Ожидаемые артефакты
- промежуточная `Спецификация`
- новые `Открытые вопросы`
- решение `routing-guardian-agent` со статусом `block`
- `runs/<name-of-task>/service/routing-decision.md`
- обновленные артефакты после уточнения
- решение `routing-guardian-agent` со статусом `allow`

### Ключевое правило
- Если на текущем этапе появились новые критичные `Открытые вопросы`, `routing-guardian-agent` обязан заблокировать переход к downstream-этапу.

---

## Сценарий 13: После успешного ядра оркестратор сразу предлагает финализирующее интервью

### Тип входа
- Полный успешный прогон с готовыми финальными артефактами

### Предусловие
- `traceability-auditor-agent` завершился со статусом `passed`
- `routing-guardian-agent` завершился со статусом `allow`
- Основной пайплайн завершен и финальные артефакты сформированы
- Все обязательные продуктовые и служебные артефакты текущего прогона сохранены

### Пример входа
- В `Спецификации` остаются формулировки, которые трактуются двояко в пределах текущих границ
- Пользователь еще не отвечал, готов ли он пройти короткое финализирующее интервью

### Ожидаемый маршрут
1. Оркестратор возвращает финальный комплект основного пайплайна и сразу спрашивает пользователя, готов ли он пройти интервью
2. Оркестратор объясняет цель и тему интервью: уточнение границ без расширения scope
3. Оркестратор явно сообщает, что новые пожелания вне текущих границ будут зафиксированы как `out-of-scope`
4. Если пользователь отказался: оркестратор не вызывает `scope-finalizer-agent` и переходит к обязательному вопросу о `Kickoff brief`
5. Если пользователь согласен: оркестратор вызывает `scope-finalizer-agent`
6. `scope-finalizer-agent` проводит короткое интервью только по существенным неоднозначностям текущих артефактов
7. `artifact-persistence-agent` сохраняет обновленные `Лог уточнений` и связанные артефакты
8. Оркестратор повторно вызывает затронутые профильные скиллы по `impact_map`
9. `traceability-auditor-agent` повторно проверяет затронутые артефакты
10. `artifact-persistence-agent` сохраняет `service/traceability-audit.md`
11. `routing-guardian-agent` подтверждает допустимость итоговой финальной агрегации
12. `artifact-persistence-agent` сохраняет `service/routing-decision.md`
13. Оркестратор возвращает обновленный финальный комплект артефактов и переходит к обязательному вопросу о `Kickoff brief`

### Ожидаемые артефакты
- обновленный `Лог уточнений` с ответами интервью
- при необходимости обновленные `Допущения` и `Открытые вопросы`
- пересобранные финальные продуктовые артефакты, включающие интервью-уточнения
- обновленные служебные отчеты `service/traceability-audit.md` и `service/routing-decision.md`
- если пользователь отказался от интервью, эти обновленные артефакты не создаются

### Ключевое правило
- Предложение интервью обязательно сразу после успешной финальной агрегации; само интервью запускается только по явному согласию пользователя.
- Отказ от интервью не завершает весь post-pipeline маршрут: после отказа оркестратор обязан спросить, нужен ли `Kickoff brief`.
- Интервью может уточнять только границы текущего scope; любые новые пожелания вне границ фиксируются как `out-of-scope` и не включаются как обязательства текущего прогона.
- `scope-finalizer-agent` не предлагает новые возможности и не ведет discovery; каждый вопрос должен быть необходимым и достаточным для снятия конкретной неоднозначности в текущих артефактах.
- Интервью ограничено 5 содержательными вопросами и завершается раньше, если существенные неоднозначности закрыты.

---

## Сценарий 14: Kickoff brief формируется после валидного финального комплекта

### Тип входа
- Полный успешный прогон с готовыми финальными артефактами

### Предусловие
- `traceability-auditor-agent` завершился со статусом `passed`
- `routing-guardian-agent` завершился со статусом `allow`
- Финальная агрегация уже выполнена
- Все обязательные продуктовые и служебные артефакты текущего прогона сохранены

### Варианты предложения
- Оркестратор предложил интервью `scope-finalizer-agent`, пользователь явно отказался, финальный комплект валиден и сохранен
- Интервью `scope-finalizer-agent` было проведено, затронутые артефакты пересобраны, повторные аудит и контроль маршрута завершились успешно, обновленный финальный комплект валиден и сохранен

### Пример входа
- Команда хочет получить короткий документ для kickoff-встречи без изменения канонических требований
- Документ нужен как основа встречи: передать контекст, выровнять понимание и собрать вопросы команды для доработки аналитики

### Ожидаемый маршрут
1. Оркестратор проверяет, что финальный комплект текущего прогона валиден и сохранен
2. Оркестратор проверяет, что интервью уже было предложено и либо отклонено, либо завершено с повторной проверкой
3. Оркестратор сам спрашивает пользователя, хочет ли он подготовить kickoff brief для передачи контекста команде
4. Если пользователь отказался, оркестратор завершает работу текущими финальными артефактами
5. Если пользователь согласился, оркестратор вызывает `kickoff-briefing-agent` с флагом `after_interview_declined` или `after_scope_finalizer` и `brief_requested: true`
6. `kickoff-briefing-agent` формирует `Kickoff brief` по `templates/kickoff-brief-template.md`
7. Если противоречий нет, агент возвращает сигнал `complete`
8. `artifact-persistence-agent` сохраняет `Kickoff brief` в `product/kickoff-brief.md`
9. Оркестратор возвращает пользователю ссылку на brief как дополнительный продуктовый файл, не подменяя финальные артефакты

### Ожидаемые артефакты
- неизмененные канонические артефакты основного пайплайна
- опциональный `product/kickoff-brief.md`

### Ключевые правила
- `kickoff-briefing-agent` не запускает профильные этапы и не меняет канонические артефакты
- после завершения или отказа от интервью оркестратор обязан сам спросить, нужен ли kickoff brief
- `kickoff-briefing-agent` не запускается до обязательного предложения интервью и отдельного явного согласия пользователя на подготовку brief
- out-of-scope в brief берется только из `Спецификации` и связанных записей `Лога уточнений`
- brief не должен выглядеть как сокращенная спецификация: ID правил, ID историй и трассировка выносятся из основного текста в компактный справочный блок
- brief должен оставлять место для вопросов команды; важные вопросы, поднятые на встрече, являются входом для последующей доработки аналитики
- brief должен читаться как сценарий 20-30 минутной встречи, укладываться примерно в 700-1000 слов и ограничивать количество принятых решений и тем для выравнивания
- если агент обнаружил критичное противоречие, он возвращает `needs_orchestrator_decision`, а brief сохраняется как `incomplete` либо не используется как финальный kickoff-документ

---

## Сценарий 15: Запрос на обслуживание системы без команды `РЕМОНТ`

### Тип входа
- Пользователь просит проанализировать или изменить устройство репозитория, контракты, шаблоны, скиллы, агентов, сценарии, примеры, тесты или правила системы

### Предусловие
- В текущей сессии не было явной команды `РЕМОНТ`

### Пример входа
- "Проанализируй текущее состояние системы"
- "Добавь новый агент"
- "Поправь контракт оркестрации"
- "Почему система игнорирует директиву `РЕМОНТ`?"

### Ожидаемый маршрут
1. Оркестратор определяет, что запрос относится к обслуживанию системы
2. Оркестратор не запускает продуктовый pipeline
3. Оркестратор не анализирует устройство системы и не предлагает изменения
4. Оркестратор задает единственный вопрос: `Это работа над системой. Перейти в режим system-maintenance? Для подтверждения напишите РЕМОНТ.`
5. До получения команды `РЕМОНТ` маршрут останавливается

### Ожидаемые артефакты
- Артефакты не создаются и не изменяются
- Файлы репозитория не редактируются

### Ключевое правило
- Любая работа над системой без явной команды `РЕМОНТ` блокируется до подтверждения режима `system-maintenance`.

---

## Сценарий 16: Оркестратор не предложил финализирующее интервью после успешного ядра

### Тип входа
- Полный успешный прогон с готовыми финальными артефактами

### Предусловие
- Итоговый аудит трассируемости имеет статус `passed`
- Итоговый контроль маршрута имеет статус `allow`
- Все обязательные продуктовые и служебные артефакты сохранены
- Оркестратор пытается завершить работу или перейти к brief без предложения интервью

### Пример входа
- Финальный ответ содержит `Спецификация`, `Пользовательские истории`, `Отчет о пробелах и рисках`, но не содержит вопроса о финализирующем интервью.

### Ожидаемый маршрут
1. Оркестратор признает маршрут незавершенным
2. Оркестратор не вызывает `kickoff-briefing-agent`
3. Оркестратор задает пользователю обязательный вопрос о финализирующем интервью
4. Дальнейшие post-pipeline шаги выполняются только после ответа пользователя

### Ожидаемые артефакты
- Новые продуктовые артефакты не создаются
- `product/kickoff-brief.md` не создается
- Финальный комплект ядра остается валидным и сохраненным

### Ключевое правило
- Успешная финальная агрегация не является последним действием оркестратора: предложение `scope-finalizer-agent` обязательно.

---

## Сценарий 17: `scope-finalizer-agent` задает лишние или наводящие вопросы

### Тип входа
- Валидный финальный комплект после успешного ядра

### Предусловие
- Пользователь согласился на финализирующее интервью
- Агент задает вопрос, который предлагает новую возможность, не привязан к конкретной неоднозначности или превышает лимит 5 содержательных вопросов

### Пример входа
- Агент спрашивает: "Хотите ли добавить отзыв заявки, уведомления или историю изменений?", хотя эти темы не представлены как текущие неоднозначности финальных артефактов.

### Ожидаемый маршрут
1. Оркестратор останавливает post-pipeline интервью как дефект процесса
2. Оркестратор не принимает ответ на такой вопрос как основание для расширения scope
3. Если уже получены валидные ответы на допустимые вопросы, оркестратор сохраняет только их в `Лог уточнений`
4. Если агент создал недопустимые уточнения, оркестратор не передает их в downstream-пересборку
5. Оркестратор возвращает пользователю краткое объяснение остановки и продолжает только с подтвержденными границами

### Ожидаемые артефакты
- Недопустимые предложения агента не попадают в `Канонические правила`
- Новые функции не появляются в `Спецификации` как обязательства текущего прогона
- При необходимости создается или обновляется `Открытые вопросы` только для действительно незакрытых границ

### Ключевое правило
- `scope-finalizer-agent` уточняет рамки, а не проводит discovery и не предлагает новые возможности.

---

## Сценарий 18: Brief запускается без отдельного согласия пользователя

### Тип входа
- Валидный финальный комплект после отказа от интервью или после завершенного интервью

### Предусловие
- Оркестратор еще не спросил пользователя, хочет ли он подготовить `Kickoff brief`
- Или пользователь отказался от brief
- Оркестратор пытается вызвать `kickoff-briefing-agent`

### Пример входа
- После отказа от интервью система сразу формирует `product/kickoff-brief.md`.

### Ожидаемый маршрут
1. Оркестратор считает вызов `kickoff-briefing-agent` недопустимым
2. `kickoff-briefing-agent` не вызывается
3. `product/kickoff-brief.md` не создается
4. Оркестратор задает обязательный вопрос о brief, если он еще не был задан
5. Если пользователь отказался от brief, оркестратор завершает работу текущими финальными артефактами

### Ожидаемые артефакты
- `product/kickoff-brief.md` отсутствует
- Канонические продуктовые артефакты остаются без изменений

### Ключевое правило
- `Kickoff brief` готовится только после отдельного явного opt-in пользователя: `brief_requested: true`.

---

## Сценарий 19: `kickoff-briefing-agent` обнаружил противоречие в финальном комплекте

### Тип входа
- Валидный на первый взгляд финальный комплект

### Предусловие
- Пользователь явно согласился подготовить brief
- В артефактах есть противоречие между `Внутри объема` и `Вне объема`, или brief не может нейтрально пересказать границы без нового решения

### Пример входа
- В `Спецификации / Границы объема` один раздел говорит, что отзыв заявки входит в MVP, а другой раздел фиксирует отзыв как out-of-scope.

### Ожидаемый маршрут
1. Оркестратор вызывает `kickoff-briefing-agent` с `brief_requested: true`
2. `kickoff-briefing-agent` возвращает `needs_orchestrator_decision`
3. Оркестратор не использует brief как финальный kickoff-документ
4. Если файл сохраняется, `artifact-persistence-agent` сохраняет его со статусом `incomplete`
5. Оркестратор возвращает проблему на корректный этап ядра или останавливается с вопросом пользователю, если без ответа противоречие не закрыть

### Ожидаемые артефакты
- `product/kickoff-brief.md` отсутствует или сохранен как `incomplete`
- Противоречие явно описано со ссылкой на конфликтующие артефакты
- Канонические артефакты не меняются самим `kickoff-briefing-agent`

### Ключевое правило
- Brief не должен сглаживать противоречия и не имеет права менять канонический комплект требований.

---

## Сценарий 20: Обязательный служебный агент недоступен

### Тип входа
- Любой этап, где контракт требует служебный контроль

### Предусловие
- Для перехода нужен `traceability-auditor-agent`, `routing-guardian-agent` или `artifact-persistence-agent`
- Нужный агент недоступен

### Пример входа
- `story-extractor` сформировал `Пользовательские истории`, но `traceability-auditor-agent` недоступен перед переходом к `story-quality-reviewer`.

### Ожидаемый маршрут
1. Оркестратор останавливает pipeline
2. Оркестратор сообщает пользователю, какой контроль невозможно выполнить
3. Оркестратор не заменяет недоступного агента ручной проверкой
4. Оркестратор не выполняет downstream-переход как валидный
5. Уже сформированные промежуточные артефакты сохраняются как `incomplete`, если доступен `artifact-persistence-agent`

### Ожидаемые артефакты
- Нет нового downstream-артефакта, зависящего от пропущенного контроля
- Если сохранение возможно: соответствующие промежуточные файлы имеют статус `incomplete` или причину остановки
- Если недоступен `artifact-persistence-agent`: новые файловые артефакты не считаются валидно зафиксированными

### Ключевое правило
- Обязательные служебные агенты нельзя подменять ручной проверкой оркестратора.

---

## Сценарий 21: Пользователь отказался от интервью и от brief

### Тип входа
- Полный успешный прогон с готовыми финальными артефактами

### Предусловие
- Финальный комплект ядра валиден и сохранен
- Оркестратор предложил финализирующее интервью
- Пользователь отказался от интервью
- Оркестратор спросил, нужен ли `Kickoff brief`
- Пользователь отказался от brief

### Пример входа
- Пользователь отвечает: "Интервью не нужно. Бриф тоже не нужен."

### Ожидаемый маршрут
1. Оркестратор не вызывает `scope-finalizer-agent`
2. Оркестратор не вызывает `kickoff-briefing-agent`
3. Оркестратор завершает работу текущими финальными артефактами

### Ожидаемые артефакты
- Канонический финальный комплект ядра сохранен
- `product/kickoff-brief.md` не создается
- Новые записи `Лога уточнений` не создаются, если отказ не меняет требования

### Ключевое правило
- Отказ от post-pipeline шагов не делает основной результат невалидным.
