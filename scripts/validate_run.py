#!/usr/bin/env python3
"""Minimal contract validator for saved requirements pipeline runs."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


PRODUCT_FILES = {
    "input": "product/input.md",
    "clarification_log": "product/clarification-log.md",
    "clarified_requirements": "product/clarified-requirements.md",
    "canonical_rules": "product/canonical-rules.md",
    "assumptions": "product/assumptions.md",
    "open_questions": "product/open-questions.md",
    "specification": "product/specification.md",
    "user_stories": "product/user-stories.md",
    "story_readiness": "product/story-readiness.md",
    "gap_risk_report": "product/gap-risk-report.md",
}

SERVICE_FILES = {
    "traceability_audit": "service/traceability-audit.md",
    "routing_decision": "service/routing-decision.md",
}

SPECIFICATION_MARKERS = [
    "Контекст / Проблема",
    "Бизнес-цель",
    "Границы объема",
    "Акторы",
    "Пользовательские сценарии",
    "Функциональные требования",
    "Бизнес-правила",
    "Данные / Сущности",
    "Ограничения",
    "Допущения",
    "Открытые вопросы",
]

STORY_REQUIRED_MARKERS = [
    "ID:",
    "Название:",
    "Источник",
    "Актор:",
    "Потребность:",
    "Ценность:",
    "Сценарий:",
    "Критерии приемки",
    "Бизнес-правила",
    "Зависимости",
    "Открытые вопросы",
]

GAP_REQUIRED_MARKERS = [
    "ID:",
    "Источник пробела",
    "Область:",
    "Описание пробела:",
    "Почему это важно:",
    "Риск:",
    "Влияние:",
    "Что нужно уточнить:",
    "Предлагаемое решение:",
    "Блокирует разработку:",
]


@dataclass
class Finding:
    level: str
    path: str
    message: str


class Validator:
    def __init__(self, run_path: Path) -> None:
        self.run_path = run_path
        self.findings: list[Finding] = []
        self.cache: dict[str, str] = {}

    def error(self, relative_path: str, message: str) -> None:
        self.findings.append(Finding("ERROR", relative_path, message))

    def warn(self, relative_path: str, message: str) -> None:
        self.findings.append(Finding("WARN", relative_path, message))

    def read(self, relative_path: str) -> str:
        if relative_path not in self.cache:
            path = self.run_path / relative_path
            self.cache[relative_path] = path.read_text(encoding="utf-8")
        return self.cache[relative_path]

    def exists(self, relative_path: str) -> bool:
        return (self.run_path / relative_path).is_file()

    def validate(self) -> list[Finding]:
        self.validate_run_shape()
        if self.has_required_files(PRODUCT_FILES):
            self.validate_clarification_log()
            self.validate_canonical_rules()
            self.validate_specification()
            self.validate_user_stories()
            self.validate_story_readiness()
            self.validate_gap_report()
        if self.has_required_files(SERVICE_FILES):
            self.validate_traceability_audit()
            self.validate_routing_decision()
        return self.findings

    def validate_run_shape(self) -> None:
        if not self.run_path.exists():
            self.error(str(self.run_path), "каталог прогона не найден")
            return
        if not self.run_path.is_dir():
            self.error(str(self.run_path), "путь прогона не является каталогом")
            return
        for dirname in ("product", "service"):
            if not (self.run_path / dirname).is_dir():
                self.error(dirname, f"отсутствует каталог `{dirname}/`")
        for relative_path in PRODUCT_FILES.values():
            if not self.exists(relative_path):
                self.error(relative_path, "отсутствует обязательный продуктовый артефакт")
        for relative_path in SERVICE_FILES.values():
            if not self.exists(relative_path):
                self.error(relative_path, "отсутствует обязательный служебный отчет")

    def has_required_files(self, files: dict[str, str]) -> bool:
        return all(self.exists(path) for path in files.values())

    def validate_clarification_log(self) -> None:
        path = PRODUCT_FILES["clarification_log"]
        text = self.read(path)
        cl_ids = self.ids(text, "CL")
        if not cl_ids:
            self.warn(path, "не найдено ни одной записи `CL-xx`; допустимо только если уточнений не было")
            return
        for block in self.blocks(text, "Запись"):
            block_id = self.first_id(block, "CL")
            if not block_id:
                self.error(path, "запись лога уточнений без `ID: CL-xx`")
                continue
            for marker in ("Этап:", "Вопрос:", "Почему задан:", "Ответ пользователя:", "Что закрыто или изменено"):
                if marker not in block:
                    self.error(path, f"{block_id}: отсутствует поле `{marker}`")

    def validate_canonical_rules(self) -> None:
        path = PRODUCT_FILES["canonical_rules"]
        text = self.read(path)
        cl_ids = self.ids(self.read(PRODUCT_FILES["clarification_log"]), "CL")
        cr_ids = self.ids(text, "CR")
        if not cr_ids:
            self.error(path, "не найдено ни одного канонического правила `CR-xx`")
            return
        for block in self.blocks(text, "Правило"):
            block_id = self.first_id(block, "CR")
            if not block_id:
                self.error(path, "каноническое правило без `ID: CR-xx`")
                continue
            for marker in ("Тип:", "Формулировка:", "Источник:", "Использовать дальше"):
                if marker not in block:
                    self.error(path, f"{block_id}: отсутствует поле `{marker}`")
            for cl_ref in self.ids(block, "CL"):
                if cl_ref not in cl_ids:
                    self.error(path, f"{block_id}: ссылка на несуществующую запись `{cl_ref}`")

    def validate_specification(self) -> None:
        path = PRODUCT_FILES["specification"]
        text = self.read(path)
        for marker in SPECIFICATION_MARKERS:
            if marker not in text:
                self.error(path, f"отсутствует обязательный раздел `{marker}`")

    def validate_user_stories(self) -> None:
        path = PRODUCT_FILES["user_stories"]
        text = self.read(path)
        story_blocks = self.blocks(text, "История")
        stories = []
        for block in story_blocks:
            story_id = self.first_id(block, "US")
            if not story_id:
                self.error(path, "история без `ID: US-xx`")
                continue
            stories.append(story_id)
            for marker in STORY_REQUIRED_MARKERS:
                if marker not in block:
                    self.error(path, f"{story_id}: отсутствует поле или раздел `{marker}`")
        if not stories:
            self.error(path, "не найдено ни одной пользовательской истории `US-xx`")

        cr_to_stories = self.canonical_rules_for_stories()
        if cr_to_stories:
            if "Покрытие канонических правил" not in text:
                self.error(path, "отсутствует раздел `Покрытие канонических правил в историях`")
            for cr_id in sorted(cr_to_stories):
                if cr_id not in text:
                    self.error(path, f"правило `{cr_id}` не отражено в покрытии канонических правил")

    def validate_story_readiness(self) -> None:
        path = PRODUCT_FILES["story_readiness"]
        text = self.read(path)
        story_ids = self.ids(self.read(PRODUCT_FILES["user_stories"]), "US")
        for story_id in sorted(story_ids):
            if story_id not in text:
                self.error(path, f"для истории `{story_id}` отсутствует статус готовности")
        if not re.search(r"Статус готовности:\s*(Высокий|Средний|Низкий)", text):
            self.error(path, "не найдено ни одного статуса готовности: Высокий, Средний или Низкий")

    def validate_gap_report(self) -> None:
        path = PRODUCT_FILES["gap_risk_report"]
        text = self.read(path)
        gap_blocks = [block for block in self.blocks(text, "Пробел") if self.first_id(block, "GAP")]
        if not gap_blocks:
            if "не выявлено" not in text.lower():
                self.error(path, "нет `GAP-xx` и нет явной строки о том, что существенные пробелы не выявлены")
            return
        for block in gap_blocks:
            gap_id = self.first_id(block, "GAP") or "GAP-??"
            for marker in GAP_REQUIRED_MARKERS:
                if marker not in block:
                    self.error(path, f"{gap_id}: отсутствует поле или раздел `{marker}`")

    def validate_traceability_audit(self) -> None:
        path = SERVICE_FILES["traceability_audit"]
        text = self.read(path)
        if "Статус аудита: passed" not in text:
            self.error(path, "не найден успешный статус аудита `Статус аудита: passed`")
        if re.search(r"Статус аудита:\s*failed", text):
            self.error(path, "найден failed-аудит трассируемости")

    def validate_routing_decision(self) -> None:
        path = SERVICE_FILES["routing_decision"]
        text = self.read(path)
        if "Решение: allow" not in text:
            self.error(path, "не найдено разрешающее маршрутное решение `Решение: allow`")
        if re.search(r"Решение:\s*block", text):
            self.error(path, "найдена блокировка маршрута")

    def canonical_rules_for_stories(self) -> set[str]:
        text = self.read(PRODUCT_FILES["canonical_rules"])
        result = set()
        for block in self.blocks(text, "Правило"):
            cr_id = self.first_id(block, "CR")
            if cr_id and "Пользовательские истории" in block:
                result.add(cr_id)
        return result

    @staticmethod
    def ids(text: str, prefix: str) -> set[str]:
        return set(re.findall(rf"\b{prefix}-\d+\b", text))

    @staticmethod
    def first_id(text: str, prefix: str) -> str | None:
        match = re.search(rf"\b{prefix}-\d+\b", text)
        return match.group(0) if match else None

    @staticmethod
    def blocks(text: str, title: str) -> list[str]:
        pattern = re.compile(rf"(?m)^#+\s+{re.escape(title)}\s*$|^{re.escape(title)}\s*$")
        starts = [match.start() for match in pattern.finditer(text)]
        if not starts:
            return []
        starts.append(len(text))
        return [text[starts[index] : starts[index + 1]] for index in range(len(starts) - 1)]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a saved requirements pipeline run against minimal contracts."
    )
    parser.add_argument("run_path", help="Path to a run directory, for example runs/goal-progress-v6")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    run_path = Path(args.run_path)
    validator = Validator(run_path)
    findings = validator.validate()
    errors = [finding for finding in findings if finding.level == "ERROR"]
    warnings = [finding for finding in findings if finding.level == "WARN"]

    status = "failed" if errors else "passed"
    print(f"Contract validation: {status}")
    print(f"Run: {run_path}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")

    for finding in findings:
        print(f"- [{finding.level}] {finding.path}: {finding.message}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
