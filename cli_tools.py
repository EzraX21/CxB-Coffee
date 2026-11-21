import shutil

from order import OrderStorage

MENU = {
    1: ("拿铁", 2800),
    2: ("美式", 2200),
    3: ("可颂", 1500),
    4: ("卡布奇诺", 2500),
}

def show_title(name: str) -> str:
    """将传入的字符串name格式化.
    返回:
        格式化后的字符串.

    """
    width = shutil.get_terminal_size((80, 24)).columns
    return name.center(width, "=")

def show_menu() -> None:
    """接受常量MENU并格式化输出."""

    print(show_title(" CxB Coffee "))
    for no in MENU:  # noqa: PLC0206
        name, price = MENU[no]
        print(f'{no}.{name} ￥{price/100:.2f}')
    print()

def next_order_no(storage: OrderStorage) -> int:
    """返回下一个可用的订单号,现有最大号 + 1,没有订单时为 1."""

    return storage.max_order_no() + 1

def check_qty(value: str):
    """合法返回 True,不合法返回错误提示."""
    if not value.isdigit():
        return "请输入数字"
    if int(value) <= 0:
        return "数量要大于 0"
    return True

def check_order_no(value: str):
    """订单号校验: 合法返回 True,不合法返回错误提示."""
    if not value.isdigit():
        return "请输入数字"
    return True

def show_order(storage: OrderStorage, order_no: int) -> None:
    """按订单号打印一张订单的明细和合计."""

    items = storage.find_by_order_no(order_no)
    if not items:
        print(f'没有找到订单 #{order_no:03d}')
        return

    print(show_title(f" 订单 #{order_no:03d} "))
    total = 0
    for it in items:
        subtotal = calc_subtotal(it.item_qty, it.item_price)
        print(f'{it.item_name} x {it.item_qty} ￥{subtotal/100:.2f}')
        total += subtotal
    print(f'合计: ￥{total/100:.2f}\n')

def find_price(item: str) -> int | None:
    for no in MENU:  # noqa: PLC0206
        item_name, price = MENU[no]
        if item_name == item:
            return price
    return None

def calc_subtotal(qty: int, price: int) -> int:
    return qty * price
