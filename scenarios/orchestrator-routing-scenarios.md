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

Сценарии ниже считаются валидными только при выполнении всех служебных стыков: новые и обновленные продуктовые артефакты фиксируются в `product/`, каждый аудит фиксируется в `service/traceability-audit.md`, каждый контроль маршрута фиксируется в `service/routing-decision.md`, а переход к следующему профильному этапу выполняется только после этих фиксаций.

`product/canonical-rules.md` ожидается как проверяемый артефакт во всех сценариях, где сформированы или доступны `Канонические правила`. Если маршрут начинается с достаточно полного входа и правила не выделялись отдельным слоем, аудит трассируемости должен явно зафиксировать, что `product/canonical-rules.md` не применялся на этом прогоне, а downstream-этапы не достраивали факты из непроверенного пересказа.

---

## Сценарий 1: Сырой ввод без акторов и целей

### Тип входа
- Сырой ввод

### Пример входа
- "Нужно сделать нормальный процесс согласования командировок, чтобы было быстрее и без писем."

### Ожидаемый маршрут
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

### Ожидаемые артефакты
- полный набор файлов прогона
- `product/canonical-rules.md`
- `Отчет аудита трассируемости` со статусом `passed`
- `Отчет контроля маршрута` с итоговым `allow`

### Ключевое правило
- Если во входе отсутствуют явные акторы, цели и сценарии, оркестратор обязан начать с уточнения требований, а не переходить сразу к спецификации.

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
