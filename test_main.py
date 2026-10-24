from pathlib import Path
from order import OrderItem, OrderStorage
from cli_tools import calc_subtotal, find_price, next_order_no

def test_dict_roundtrip():
    item = OrderItem(1,'拿铁',2,2800)

    first = item.to_dict()
    second = OrderItem.from_dict(first).to_dict()

    assert first == second

def test_load_all_empty_file(tmp_path: Path):
    path = tmp_path / 'nothing.json'

    storage = OrderStorage(str(path))
    result = storage.load_all()

    assert result == []

def test_append_and_load(tmp_path: Path):
    path = tmp_path / 'orders.json'
    storage = OrderStorage(str(path))

    storage.append(OrderItem(1, '拿铁', 2, 2800))
    storage.append(OrderItem(2, '可颂', 1, 1500))

    items = storage.load_all()

    assert len(items) == 2
    assert items[0].item_name == '拿铁'
    assert items[1].item_qty == 1
    assert items[1].item_price == 1500

def test_calc_subtotal():
    price = calc_subtotal(2, 2800)
    assert price == 5600

def test_find_price():
    assert find_price('拿铁') == 2800
    assert find_price('测试') == None

def test_next_order_no_empty(tmp_path:Path):
    storage = OrderStorage(str(tmp_path / "nothing.json")) 
    assert next_order_no(storage) == 1

def test_next_order_no_existing(tmp_path:Path):
    storage = OrderStorage(str(tmp_path / 'orders.json'))
    storage.append(OrderItem(1, '美式', 1, 2200))
    storage.append(OrderItem(2, '拿铁', 1, 2800))
    assert next_order_no(storage) == 3
