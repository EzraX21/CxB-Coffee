from questionary import select, text

from cli_tools import (
    MENU,
    calc_subtotal,
    check_order_no,
    check_qty,
    find_price,
    next_order_no,
    show_menu,
    show_order,
)
from order import OrderItem, OrderStorage

FILE = 'orders.db'


def main() -> None:
    storage = OrderStorage(FILE)
    items = []
    cur_order_no = next_order_no(storage)
    show_menu()

    while True:
        options = [MENU[no][0] for no in MENU]
        options += ['查询订单', '退出/合计']

        choice_item = select('请选择你想买的商品', choices=options).ask()

        if choice_item is None or choice_item == '退出/合计':
            break

        if choice_item == '查询订单':
            order_no_text = text('订单号', validate=check_order_no).ask()
            if order_no_text is None:
                continue
            show_order(storage, int(order_no_text))
            continue

        item_price = find_price(choice_item)
        if item_price is None:
            print('没有这个商品')
            continue
        qty_text = text('数量', default="1", validate=check_qty).ask()
        if qty_text is None:
            continue
        items.append(OrderItem(cur_order_no, choice_item, int(qty_text), item_price))

    if len(items) == 0:
        print("没有点任何商品")
        return

    total = 0
    for it in items:
        subtotal = calc_subtotal(it.item_qty, it.item_price)
        print(f'{it.item_name} x {it.item_qty} ￥{subtotal/100:.2f}')
        total += subtotal

    print(f'合计: ￥{total/100:.2f}')

    # 一张订单的所有条目一次性写入：中途出错不会留下半张订单
    storage.append_many(items)

    print(f'订单号 #{cur_order_no:03d} 已保存')


if __name__ == "__main__":
    main()
