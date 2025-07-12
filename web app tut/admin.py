from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
    
class CustomModelView(ModelView):
    can_create = True
    can_edit = True
    can_delete = True
    column_display_pk = True
    
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)
