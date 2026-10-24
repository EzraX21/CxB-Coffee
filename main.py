from order import OrderItem, OrderStorage
from cli import MENU, show_menu
from questionary import select, text

FILE = 'orders.json'

def next_order_no(storage: OrderStorage) -> int:
    """返回下一个可用的订单号,现有最大号 + 1,没有订单时为 1."""

    items = storage.load_all()
    max_no = 0
    for item in items:
        if item.order_no > max_no:
            max_no = item.order_no
    return max_no + 1

def check_qty(value: str):
    """合法返回 True,不合法返回错误提示."""
    if not value.isdigit():
        return "请输入数字"
    if int(value) <= 0:
        return "数量要大于 0"
    return True

def find_price(item: str) -> int | None:
    for no in MENU:
        item_name, price = MENU[no]
        if item_name == item:
            return price
    return None

def calc_subtotal( qty: int, price: int) -> int:
    return qty * price

def main() -> None:
    storage = OrderStorage(FILE)
    items = []
    cur_order_no =next_order_no(storage)
    show_menu()

    while True:
        
        
        options = []
        for d in MENU:
            options.append(MENU[d][0])
        options.append('退出/合计')
        
        choice_item = select('请选择你想买的商品',choices=options).ask()

        if choice_item is None or choice_item == '退出/合计':
            break

        item_price = find_price(choice_item)
        if item_price is None:
            print('没有这个商品')
            continue
        qty_text = text('数量', default="1", validate=check_qty).ask()
        qty = int(qty_text)
        items.append(OrderItem(cur_order_no, choice_item, qty, item_price))
    
    if len(items) == 0:
        print("没有点任何商品")
        return

    total = 0
    for it in items:
        subtotal = calc_subtotal(it.item_qty, it.item_price)
        print(f'{it.item_name} x {it.item_qty} ￥{subtotal/100:.2f}')
        total += subtotal

    print(f'合计: ￥{total/100:.2f}')

    for it in items:
        storage.append(it)

    print(f'订单号 #{cur_order_no:03d} 已保存')


if __name__ == "__main__":
    main()