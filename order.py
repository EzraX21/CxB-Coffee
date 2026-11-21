import sqlite3
from contextlib import closing
from typing import Any

# 建表语句。IF NOT EXISTS 保证重复调用不会报错；
# CHECK 是数据库层的最后一道防线，即使有人绕过 cli_tools 直接调 storage 也写不进脏数据。
_SCHEMA = """
CREATE TABLE IF NOT EXISTS order_items (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    order_no   INTEGER NOT NULL,
    item_name  TEXT    NOT NULL,
    item_qty   INTEGER NOT NULL CHECK (item_qty > 0),
    item_price INTEGER NOT NULL CHECK (item_price >= 0)
);

CREATE INDEX IF NOT EXISTS idx_order_items_order_no
    ON order_items (order_no);
"""


class OrderItem:
    """一行订单条目.

    属性:
        order_no: 所属订单号，同一张订单的多行共用同一个号.
        item_name: 商品名.
        item_qty: 数量.
        item_price: 单价，单位：分.
    """

    def __init__(self, order_no: int, item_name: str, item_qty: int, item_price: int) -> None:
        self.order_no = order_no
        self.item_name = item_name
        self.item_qty = item_qty
        self.item_price = item_price

    def to_dict(self) -> dict[str, Any]:
        """将一个订单类实例转化成可保存的字典对象（导出/调试用）.

        返回:

            对应字典对象.
        """
        return {
            'order_no': self.order_no,
            'item_name': self.item_name,
            'item_qty': self.item_qty,
            'item_price': self.item_price,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OrderItem:
        """将一个订单字典转化成一个订单类实例.

        返回:

            对应订单类实例.
        """
        return cls(
            order_no=data['order_no'],
            item_name=data['item_name'],
            item_qty=data['item_qty'],
            item_price=data['item_price'],
        )

    def __repr__(self) -> str:
        return (
            f"OrderItem(order_no={self.order_no}, item_name={self.item_name!r}, "
            f"item_qty={self.item_qty}, item_price={self.item_price})"
        )


class OrderStorage:
    """负责订单条目在 SQLite 数据库里的读写.

    只处理"存到哪、怎么存、怎么查"，不处理任何订单业务规则。
    数据库文件不存在时会自动创建，此时读出来是空列表。
    """

    def __init__(self, path: str) -> None:
        self.path = str(path)
        self._init_db()

    # ---- 内部 ----

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        # 让查询结果可以按列名访问：row["order_no"]
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        # `with conn` 只负责提交/回滚，不负责关闭连接；
        # closing() 负责关闭。两个一起用才不会泄漏连接。
        with closing(self._connect()) as conn, conn:
            conn.executescript(_SCHEMA)

    @staticmethod
    def _row_to_item(row: sqlite3.Row) -> OrderItem:
        return OrderItem(
            order_no=row['order_no'],
            item_name=row['item_name'],
            item_qty=row['item_qty'],
            item_price=row['item_price'],
        )

    # ---- 写 ----

    def append(self, item: OrderItem) -> None:
        """追加一条订单条目."""
        self.append_many([item])

    def append_many(self, items: list[OrderItem]) -> None:
        """在一个事务里追加多条订单条目.

        要么全部写入，要么一条都不写——不会出现"存了半张订单"的情况。
        """
        if not items:
            return
        rows = [
            (it.order_no, it.item_name, it.item_qty, it.item_price)
            for it in items
        ]
        with closing(self._connect()) as conn, conn:
            conn.executemany(
                "INSERT INTO order_items (order_no, item_name, item_qty, item_price)"
                " VALUES (?, ?, ?, ?)",
                rows,
            )

    # ---- 读 ----

    def load_all(self) -> list[OrderItem]:
        """读取全部订单条目."""
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT order_no, item_name, item_qty, item_price"
                " FROM order_items ORDER BY id"
            ).fetchall()
        return [self._row_to_item(row) for row in rows]

    def find_by_order_no(self, order_no: int) -> list[OrderItem]:
        """按订单号查询一张订单的所有条目，找不到时返回空列表."""
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT order_no, item_name, item_qty, item_price"
                " FROM order_items WHERE order_no = ? ORDER BY id",
                (order_no,),
            ).fetchall()
        return [self._row_to_item(row) for row in rows]

    def max_order_no(self) -> int:
        """返回现有最大订单号；没有任何订单时返回 0."""
        with closing(self._connect()) as conn:
            row = conn.execute("SELECT MAX(order_no) FROM order_items").fetchone()
        return row[0] or 0
