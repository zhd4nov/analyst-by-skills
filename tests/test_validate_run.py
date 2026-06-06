from __future__ import annotations

import shutil
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

from scripts.validate_run import Validator


FIXTURES_DIR = Path(__file__).parent / "fixtures"


class ValidateRunFixtureTest(unittest.TestCase):
    def test_valid_minimal_run_passes(self) -> None:
        self.assert_errors("valid-minimal-run", [])

    def test_confirmed_scope_marker_passes(self) -> None:
        self.assert_errors("valid-confirmed-scope-marker", [])

    def test_historical_route_block_can_be_closed_by_allow(self) -> None:
        self.assert_errors("valid-historical-route", [])

    def test_missing_service_report_fails(self) -> None:
        self.assert_errors(
            "invalid-missing-service-report",
            [
                ("service/traceability-audit.md", "отсутствует обязательный служебный отчет"),
            ],
        )

    def test_missing_launch_metadata_fails(self) -> None:
        self.assert_errors(
            "invalid-missing-launch-metadata",
            [
                (
                    "service/traceability-audit.md",
                    "отсутствует метаданное запуска `Контракт агента: agents/traceability-auditor-agent.md`",
                ),
                (
                    "service/traceability-audit.md",
                    "отсутствует метаданное запуска `Режим запуска: isolated-subagent`",
                ),
                (
                    "service/traceability-audit.md",
                    "отсутствует метаданное запуска `Переданный контекст`",
                ),
                (
                    "service/routing-decision.md",
                    "отсутствует метаданное запуска `Контракт агента: agents/routing-guardian-agent.md`",
                ),
                (
                    "service/routing-decision.md",
                    "отсутствует метаданное запуска `Режим запуска: isolated-subagent`",
                ),
                (
                    "service/routing-decision.md",
                    "отсутствует метаданное запуска `Переданный контекст`",
                ),
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
                ("service/routing-decision.md", "не найдено итоговое решение маршрута `allow`"),
                ("service/routing-decision.md", "найдены незакрытые блокировки маршрута"),
            ],
        )

    def test_missing_audit_history_fails(self) -> None:
        self.assert_errors(
            "invalid-missing-audit-history",
            [
                ("service/traceability-audit.md", "не найдено ни одного блока аудита `## Аудит`"),
            ],
        )

    def test_missing_route_history_fails(self) -> None:
        self.assert_errors(
            "invalid-missing-route-history",
            [
                ("service/routing-decision.md", "не найдено ни одного блока проверки маршрута"),
            ],
        )

    def test_unclosed_route_block_fails(self) -> None:
        self.assert_errors(
            "invalid-unclosed-route-block",
            [
                (
                    "service/routing-decision.md",
                    "история маршрута содержит незакрытый `block` без последующего `allow`",
                ),
            ],
        )

    def test_open_blocking_gap_with_high_story_readiness_fails(self) -> None:
        self.assert_errors(
            "invalid-blocking-gap-high-readiness",
            [
                ("product/gap-risk-report.md", "финальный прогон содержит незавершенный статус артефакта"),
                ("product/gap-risk-report.md", "GAP-01: открыт блокирующий пробел"),
                (
                    "product/gap-risk-report.md",
                    "GAP-01: связанная история `US-01` имеет статус `Высокий`",
                ),
            ],
        )

    def test_unconfirmed_scope_creep_marker_fails(self) -> None:
        self.assert_errors(
            "invalid-unconfirmed-scope-creep",
            [
                (
                    "product/specification.md",
                    "неподтвержденный scope-creep маркер `Черновик` без явного источника или out-of-scope фиксации",
                ),
            ],
        )

    def test_open_questions_in_final_run_fail(self) -> None:
        with TemporaryDirectory() as directory:
            run_path = Path(directory) / "run-with-open-question"
            shutil.copytree(FIXTURES_DIR / "valid-minimal-run", run_path)
            (run_path / "product" / "open-questions.md").write_text(
                "# Открытые вопросы\n\nСтатус: complete\n\n- Как определяется исполнитель заявки?\n",
                encoding="utf-8",
            )

            findings = Validator(run_path).validate()
            actual = [(finding.path, finding.message) for finding in findings if finding.level == "ERROR"]

        self.assertIn(
            (
                "product/open-questions.md",
                "финальная агрегация невозможна: есть незакрытые открытые вопросы",
            ),
            actual,
        )

    def test_gap_report_references_empty_open_questions_fails(self) -> None:
        with TemporaryDirectory() as directory:
            run_path = Path(directory) / "run-with-gap-link-to-empty-open-questions"
            shutil.copytree(FIXTURES_DIR / "valid-minimal-run", run_path)
            (run_path / "product" / "gap-risk-report.md").write_text(
                "# Отчет о пробелах и рисках\n\n"
                "Статус: complete\n\n"
                "## Пробел\n"
                "ID: GAP-01\n"
                "Статус пробела: открыт\n"
                "Источник пробела\n"
                "- Спецификация: Валидационные правила\n"
                "- Финальная фиксация открытых вопросов: product/open-questions.md\n"
                "Область: обязательность полей\n"
                "Описание пробела: Не определено, какие поля обязательны.\n"
                "Почему это важно: Без правила нельзя проверить форму.\n"
                "Риск: средний\n"
                "Влияние: Возможна доработка валидации.\n"
                "Что нужно уточнить: Перечень обязательных полей.\n"
                "Предлагаемое решение: Получить решение владельца продукта.\n"
                "Блокирует разработку: нет\n",
                encoding="utf-8",
            )

            findings = Validator(run_path).validate()
            actual = [(finding.path, finding.message) for finding in findings if finding.level == "ERROR"]

        self.assertIn(
            (
                "product/gap-risk-report.md",
                "GAP-01: ссылка на `product/open-questions.md` недопустима, потому что открытые вопросы явно отсутствуют",
            ),
            actual,
        )

    def test_assumptions_claim_no_dialog_with_cl_entries_fails(self) -> None:
        with TemporaryDirectory() as directory:
            run_path = Path(directory) / "run-with-invalid-assumptions-note"
            shutil.copytree(FIXTURES_DIR / "valid-minimal-run", run_path)
            (run_path / "product" / "assumptions.md").write_text(
                "# Допущения\n\n"
                "Статус: complete\n\n"
                "Нет.\n\n"
                "Неподтвержденные рабочие гипотезы не фиксировались как допущения, "
                "потому что уточняющий диалог в текущем прогоне не проводился.\n",
                encoding="utf-8",
            )

            findings = Validator(run_path).validate()
            actual = [(finding.path, finding.message) for finding in findings if finding.level == "ERROR"]

        self.assertIn(
            (
                "product/assumptions.md",
                "артефакт противоречит `Логу уточнений`: указано, что уточняющий диалог не проводился",
            ),
            actual,
        )

    def test_incomplete_final_artifact_status_fails(self) -> None:
        with TemporaryDirectory() as directory:
            run_path = Path(directory) / "run-with-incomplete-artifact"
            shutil.copytree(FIXTURES_DIR / "valid-minimal-run", run_path)
            story_readiness_path = run_path / "product" / "story-readiness.md"
            story_readiness_path.write_text(
                story_readiness_path.read_text(encoding="utf-8").replace("Статус: complete", "Статус: incomplete"),
                encoding="utf-8",
            )

            findings = Validator(run_path).validate()
            actual = [(finding.path, finding.message) for finding in findings if finding.level == "ERROR"]

        self.assertIn(
            ("product/story-readiness.md", "финальный прогон содержит незавершенный статус артефакта"),
            actual,
        )

    def test_partial_post_pipeline_package_fails(self) -> None:
        with TemporaryDirectory() as directory:
            run_path = Path(directory) / "run-with-partial-team-package"
            shutil.copytree(FIXTURES_DIR / "valid-minimal-run", run_path)
            team_path = run_path / "team"
            team_path.mkdir()
            (team_path / "kickoff-brief.md").write_text(
                "# Kickoff brief\n\nКонтракт агента: agents/kickoff-briefing-agent.md\n\n"
                "Режим запуска: isolated-subagent\n\n"
                "Переданный контекст: compact team envelope\n",
                encoding="utf-8",
            )

            findings = Validator(run_path).validate()
            actual = [(finding.path, finding.message) for finding in findings if finding.level == "ERROR"]

        self.assertIn(
            (
                "team/delivery-readiness-pack.md",
                "post-pipeline пакет начат, но отсутствует обязательный командный артефакт",
            ),
            actual,
        )

    def test_runs_root_is_not_a_run_directory(self) -> None:
        with TemporaryDirectory() as directory:
            runs_root = Path(directory) / "runs"
            runs_root.mkdir()

            findings = Validator(runs_root).validate()
            actual = [(finding.path, finding.message) for finding in findings if finding.level == "ERROR"]

        self.assertEqual(
            [
                (
                    str(runs_root),
                    "передан корневой каталог `runs/`; ожидается отдельный каталог прогона `runs/<run-name>`",
                ),
            ],
            actual,
        )

    def test_canonical_artifact_in_run_root_fails(self) -> None:
        with TemporaryDirectory() as directory:
            run_path = Path(directory) / "purchase-approval"
            run_path.mkdir()
            (run_path / "input.md").write_text("Вход", encoding="utf-8")

            findings = Validator(run_path).validate()
            actual = [(finding.path, finding.message) for finding in findings if finding.level == "ERROR"]

        self.assertIn(
            (
                "input.md",
                "канонический артефакт лежит в корне прогона, а не в `product/`, `service/` или `team/`",
            ),
            actual,
        )

    def assert_errors(self, fixture_name: str, expected: list[tuple[str, str]]) -> None:
        findings = Validator(FIXTURES_DIR / fixture_name).validate()
        actual = [(finding.path, finding.message) for finding in findings if finding.level == "ERROR"]
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
