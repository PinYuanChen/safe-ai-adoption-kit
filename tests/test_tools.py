from safe_ai_kit.tools import lookup_order

def test_finds_a_shipped_order(orders):
    # Test case 1: Lookup existing order
    result = lookup_order("HL-10421", orders)
    assert result["status"] == "shipped"
    assert result["order_id"] == "HL-10421"

def test_finds_a_cancelled_order(orders):
    # Test case 2: Lookup existing order
    result = lookup_order("HL-10427", orders)
    assert result["status"] == "cancelled"
    assert result["order_id"] == "HL-10427"

def test_returns_error_for_nonexistent_order(orders):
    # Test case 3: Lookup non-existent order
    result = lookup_order("HL-10429", orders)
    assert "error" in result
    assert result["order_id"] == "HL-10429"