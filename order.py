import json


class OrderItem:
    """一行订单条目.

    属性:
        order_no: 所属订单号，同一张订单的多行共用同一个号.
        item_name: 商品名.
        item_qty: 数量.
        item_price: 单价，单位：分.
    """
    def __init__(self,order_no: int, item_name: str, item_qty: int, item_price: int) -> None:
        self.order_no = order_no
        self.item_name = item_name
        self.item_qty = item_qty
        self.item_price = item_price

    def to_dict(self) -> dict:
        """将一个订单类实例转化成可保存的字典对象.
        返回:

            对应字典对象.
        """
        return {'order_no':self.order_no,
                'item_name':self.item_name,
                'item_qty': self.item_qty,
                'item_price':self.item_price}

    @classmethod
    def from_dict(cls,data: dict) -> OrderItem:
        """将一个订单字典转化成一个订单类实例.
        返回:

            对应订单类实例.
        """
        return cls(
            order_no = data['order_no'],
            item_name = data['item_name'],
            item_qty = data['item_qty'],
            item_price = data['item_price']
        )

class OrderStorage:
    """负责订单条目在 JSON 文件里的读写.

    只处理"存到哪、怎么存",不处理任何订单业务规则.
    文件不存在时视为还没有订单,读出来是空列表.
    """
    def __init__(self, path: str) -> None:
        self.path = path

    def load_all(self) -> list[OrderItem]:
        """读取全部订单条目,文件不存在时返回空列表."""

        datas = []
        try:
            with open(self.path,'r',encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = []

        for d in data:
            data_line = OrderItem.from_dict(d)
            datas.append(data_line)

        return datas

    def append(self,item:OrderItem) -> None:
        """追加一条订单条目到文件末尾,已有记录不会被覆盖."""

        all_items = self.load_all()
        all_items.append(item)
        item = []  # pyright: ignore[reportAssignmentType]
        for d in all_items:
            item.append(d.to_dict())  # pyright: ignore[reportAttributeAccessIssue]

        with open(self.path,'w',encoding='utf-8') as f:
            json.dump(item ,f ,ensure_ascii=False ,indent=4)
