from __future__ import annotations

import unittest
from pathlib import Path

from scripts.validate_run import Validator


FIXTURES_DIR = Path(__file__).parent / "fixtures"


class ValidateRunFixtureTest(unittest.TestCase):
    def test_valid_minimal_run_passes(self) -> None:
        self.assert_errors("valid-minimal-run", [])

    def test_missing_service_report_fails(self) -> None:
        self.assert_errors(
            "invalid-missing-service-report",
            [
                ("service/traceability-audit.md", "отсутствует обязательный служебный отчет"),
            ],
        )

    def test_story_without_source_fails(self) -> None:
        self.assert_errors(
            "invalid-story-without-source",
            [
                ("product/user-stories.md", "US-01: отсутствует поле или раздел `Источник`"),
            ],
        )

    def test_canonical_rule_with_missing_cl_reference_fails(self) -> None:
        self.assert_errors(
            "invalid-cr-missing-cl-reference",
            [
                (
                    "product/canonical-rules.md",
                    "CR-01: ссылка на несуществующую запись `CL-99`",
                ),
            ],
        )

    def test_failed_traceability_audit_fails(self) -> None:
        self.assert_errors(
            "invalid-failed-audit",
            [
                ("service/traceability-audit.md", "не найден успешный статус аудита `Статус аудита: passed`"),
                ("service/traceability-audit.md", "найден failed-аудит трассируемости"),
            ],
        )

    def test_blocked_route_fails(self) -> None:
        self.assert_errors(
            "invalid-blocked-route",
            [
                ("service/routing-decision.md", "не найдено разрешающее маршрутное решение `Решение: allow`"),
                ("service/routing-decision.md", "найдена блокировка маршрута"),
            ],
        )

    def assert_errors(self, fixture_name: str, expected: list[tuple[str, str]]) -> None:
        findings = Validator(FIXTURES_DIR / fixture_name).validate()
        actual = [(finding.path, finding.message) for finding in findings if finding.level == "ERROR"]
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
