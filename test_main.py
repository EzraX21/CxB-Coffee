import sqlite3
from pathlib import Path

import pytest

from cli_tools import calc_subtotal, find_price, next_order_no
from order import OrderItem, OrderStorage


def test_dict_roundtrip():
    item = OrderItem(1, '拿铁', 2, 2800)

    first = item.to_dict()
    second = OrderItem.from_dict(first).to_dict()

    assert first == second


def test_load_all_empty_db(tmp_path: Path):
    storage = OrderStorage(str(tmp_path / 'nothing.db'))

    assert storage.load_all() == []


def test_append_and_load(tmp_path: Path):
    storage = OrderStorage(str(tmp_path / 'orders.db'))

    storage.append(OrderItem(1, '拿铁', 2, 2800))
    storage.append(OrderItem(2, '可颂', 1, 1500))

    items = storage.load_all()

    assert len(items) == 2
    assert items[0].item_name == '拿铁'
    assert items[1].item_qty == 1
    assert items[1].item_price == 1500


def test_data_persists_after_reopen(tmp_path: Path):
    path = str(tmp_path / 'orders.db')

    OrderStorage(path).append(OrderItem(1, '拿铁', 1, 2800))

    # 换一个新实例重新打开同一个数据库文件
    items = OrderStorage(path).load_all()

    assert len(items) == 1
    assert items[0].item_name == '拿铁'


def test_append_many(tmp_path: Path):
    storage = OrderStorage(str(tmp_path / 'orders.db'))

    storage.append_many([
        OrderItem(1, '拿铁', 1, 2800),
        OrderItem(1, '可颂', 2, 1500),
    ])

    assert len(storage.load_all()) == 2


def test_find_by_order_no(tmp_path: Path):
    storage = OrderStorage(str(tmp_path / 'orders.db'))
    storage.append_many([
        OrderItem(1, '拿铁', 1, 2800),
        OrderItem(1, '可颂', 2, 1500),
        OrderItem(2, '美式', 1, 2200),
    ])

    order_1 = storage.find_by_order_no(1)

    assert len(order_1) == 2
    assert [it.item_name for it in order_1] == ['拿铁', '可颂']
    assert storage.find_by_order_no(99) == []


def test_negative_qty_rejected_by_database(tmp_path: Path):
    storage = OrderStorage(str(tmp_path / 'orders.db'))

    with pytest.raises(sqlite3.IntegrityError):
        storage.append(OrderItem(1, '拿铁', 0, 2800))


def test_calc_subtotal():
    price = calc_subtotal(2, 2800)
    assert price == 5600


def test_find_price():
    assert find_price('拿铁') == 2800
    assert find_price('测试') is None


def test_next_order_no_empty(tmp_path: Path):
    storage = OrderStorage(str(tmp_path / 'nothing.db'))
    assert next_order_no(storage) == 1


def test_next_order_no_existing(tmp_path: Path):
    storage = OrderStorage(str(tmp_path / 'orders.db'))
    storage.append(OrderItem(7, '美式', 1, 2200))
    storage.append(OrderItem(3, '拿铁', 1, 2800))
    assert next_order_no(storage) == 8
