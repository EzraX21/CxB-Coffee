from order import OrderItem, OrderStorage
from pathlib import Path


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