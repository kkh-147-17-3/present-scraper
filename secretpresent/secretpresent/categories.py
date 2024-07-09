from sqlalchemy import null
from sqlalchemy.orm import joinedload

from secretpresent.models.db_connect import session_local

from secretpresent.models.product import NaverShoppingCategory

db = session_local()

categories = (db.query(NaverShoppingCategory)
              .options(joinedload(NaverShoppingCategory.child_categories))
              .filter(NaverShoppingCategory.parent_category_id == null())
              .all())


