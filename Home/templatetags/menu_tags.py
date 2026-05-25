from django import template
from Home.models import Menus
from django.db.models import Prefetch

register = template.Library()

@register.simple_tag
def get_menu(position):
    try:
        # Fetch the active menu for the position
        menu = Menus.objects.get(menu_position=position, status=True, deleted_at__isnull=True)
        
        # Build the tree structure
        # (Reusing the build_tree logic for frontend to minimize DB hits)
        items = menu.items.all().order_by('menu_order')
        
        item_dict = {item.id: item for item in items}
        roots = []
        for item in items:
            item.children = [] # Initialize children list
        
        for item in items:
            if item.parent_id:
                parent = item_dict.get(item.parent_id.id)
                if parent:
                    parent.children.append(item)
                else:
                    roots.append(item) # Parent missing
            else:
                roots.append(item)
                
        return roots
    except Menus.DoesNotExist:
        return []
