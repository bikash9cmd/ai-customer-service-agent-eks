"""Unit tests for the MCP tool functions.

Run from this directory:
    pip install -r requirements.txt pytest
    python -m pytest tests
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import server  # noqa: E402


# --- check_inventory ---------------------------------------------------------

def test_exact_name_is_case_insensitive():
    result = server.check_inventory("wireless mouse")
    assert result == {"product": "Wireless Mouse", "in_stock": True, "quantity": 156}


def test_unique_partial_name_matches():
    assert server.check_inventory("stand")["product"] == "Laptop Stand"


def test_ambiguous_partial_name_returns_candidates():
    result = server.check_inventory("laptop")
    assert "error" in result
    assert sorted(result["candidates"]) == ["Laptop Pro 15", "Laptop Stand"]


def test_exact_name_wins_over_longer_partial_matches(monkeypatch):
    monkeypatch.setattr(server, "INVENTORY", {"Monitor Arm": 5, "Monitor": 3})
    assert server.check_inventory("Monitor") == {
        "product": "Monitor", "in_stock": True, "quantity": 3,
    }


def test_blank_name_is_rejected():
    for blank in ("", "   "):
        result = server.check_inventory(blank)
        assert "error" in result and "product" not in result


def test_unknown_product():
    assert "error" in server.check_inventory("Toaster")


def test_zero_stock_reports_not_in_stock(monkeypatch):
    monkeypatch.setattr(server, "INVENTORY", {"Webcam HD Pro": 0})
    assert server.check_inventory("webcam")["in_stock"] is False


# --- lookup_order ------------------------------------------------------------

def test_lookup_order_trims_and_uppercases_id():
    result = server.lookup_order("  ord-67890 \n")
    assert result["order_id"] == "ORD-67890"
    assert result["total"] == "$129.97"


def test_lookup_unknown_order():
    assert "error" in server.lookup_order("ORD-00000")


# --- initiate_return ---------------------------------------------------------

def test_return_accepts_padded_id():
    result = server.initiate_return(" ord-12345 ", "Screen flickers")
    assert result["return_id"] == "RET-12345"
    assert result["order_id"] == "ORD-12345"
    assert result["status"] == "approved"


def test_return_rejected_for_unshipped_order():
    assert "error" in server.initiate_return("ORD-11111", "Changed my mind")


def test_return_unknown_order():
    assert "error" in server.initiate_return("ORD-99999", "Damaged")
