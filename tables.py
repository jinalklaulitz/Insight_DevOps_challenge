from flask_table import Table, Col

class Success(Table):
    id = Col('id',show = False)
    name = Col('name')
    quantity = Col('quantity')
    description = Col('description')
    date_added = Col('date_added')
