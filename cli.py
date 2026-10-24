import shutil

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
    for no in MENU:
        name, price = MENU[no]
        print(f'{no}.{name} ￥{price/100:.2f}')
    print()
