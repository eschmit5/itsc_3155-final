from . import customers, menu_items, order_details, orders, payments, promotions, ratings, resources

from ..dependencies.database import engine


def index():
    customers.Base.metadata.create_all(engine)
    ratings.Base.metadata.create_all(engine)
    payments.Base.metadata.create_all(engine)
    orders.Base.metadata.create_all(engine)
    order_details.Base.metadata.create_all(engine)
    menu_items.Base.metadata.create_all(engine)
    resources.Base.metadata.create_all(engine)
    promotions.Base.metadata.create_all(engine)