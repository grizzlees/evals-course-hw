"""Student-added HW1 tool: get_store_info (no LLM, no API keys)."""

from __future__ import annotations

from agent import tools
from agent.agent import TOOLS_BY_ROLE
from agent.auth import AuthContext

SHOPPER_1 = AuthContext(user_id=1, role="shopper")
MERCHANT_STORE_2 = AuthContext(user_id=9002, role="merchant", store_id=2)
SUPPORT = AuthContext(user_id=9501, role="support")


def test_store_override_wins_over_platform_default(world: dict) -> None:
    result = tools.get_store_info(SHOPPER_1, "Northwind Books")
    assert result["ok"] is True
    assert result["return_window_days"] == 45
    assert result["return_window_source"] == "store_policy"
    assert "store-northwind-books-policy" in result["policy_ids"]


def test_stricter_override_also_wins(world: dict) -> None:
    result = tools.get_store_info(MERCHANT_STORE_2, "juniper-home-goods")
    assert result["return_window_days"] == 14
    assert result["return_window_source"] == "store_policy"


def test_store_without_override_uses_platform_default(world: dict) -> None:
    result = tools.get_store_info(SUPPORT, "blue heron ceramics")
    assert result["return_window_days"] == 30
    assert result["return_window_source"] == "platform_default"
    assert result["restocking_fee"]["charged"] is False
    assert result["restocking_fee"]["max_percent"] is None
    assert result["policy_ids"] == ["cw-returns", "cw-store-overrides"]


def test_restocking_fee_only_for_opted_in_stores(world: dict) -> None:
    result = tools.get_store_info(SHOPPER_1, "Cascade Audio")
    fee = result["restocking_fee"]
    assert fee == {"charged": True, "max_percent": 15, "opened_items_only": True}
    assert "cw-restocking-fees" in result["policy_ids"]


def test_unknown_and_empty_store(world: dict) -> None:
    missing = tools.get_store_info(SHOPPER_1, "No Such Store")
    assert missing["ok"] is False
    assert missing["error"] == "not_found"
    assert "No Such Store" in missing["reason"]
    assert tools.get_store_info(SHOPPER_1, "  ")["error"] == "invalid_argument"


def test_registered_for_every_role() -> None:
    for role, role_tools in TOOLS_BY_ROLE.items():
        assert "get_store_info" in {t.name for t in role_tools}, role
