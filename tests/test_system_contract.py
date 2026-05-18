from __future__ import annotations

import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


class SystemContractTest(unittest.TestCase):
    def test_agents_are_isolated_subagents_not_inline_roles(self) -> None:
        checked_paths = [
            ROOT_DIR / "AGENTS.md",
            ROOT_DIR / "README.md",
            ROOT_DIR / "scenarios" / "orchestrator-routing-scenarios.md",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in checked_paths)

        self.assertIn("isolated-subagent", combined)
        self.assertIn("отдельный запуск сабагента", combined)
        self.assertNotIn("оркестратор выполняет " + "соответствующую роль", combined)
        self.assertNotIn("Отсутствие отдельного " + "runtime-инструмента", combined)

    def test_agent_contracts_require_launch_metadata(self) -> None:
        required = {
            "artifact-persistence-agent.md": "Контракт агента: agents/artifact-persistence-agent.md",
            "traceability-auditor-agent.md": "Контракт агента: agents/traceability-auditor-agent.md",
            "routing-guardian-agent.md": "Контракт агента: agents/routing-guardian-agent.md",
            "scope-finalizer-agent.md": "Контракт агента: agents/scope-finalizer-agent.md",
            "kickoff-briefing-agent.md": "Контракт агента: agents/kickoff-briefing-agent.md",
            "delivery-readiness-agent.md": "Контракт агента: agents/delivery-readiness-agent.md",
        }

        for filename, marker in required.items():
            with self.subTest(filename=filename):
                text = (ROOT_DIR / "agents" / filename).read_text(encoding="utf-8")
                self.assertIn(marker, text)
                self.assertIn("Режим запуска: isolated-subagent", text)


if __name__ == "__main__":
    unittest.main()
