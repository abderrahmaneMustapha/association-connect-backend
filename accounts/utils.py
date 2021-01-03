from .models import Member

def have_association_permission( association , user, permission):
    member = Member.objects.filter(user=user, association=association)
    is_member = member.exists()
    has_permission = user.has_perm(permission, association)
    if is_member :
        is_owner = member.first().is_owner
        is_archived = member.first().is_archived
        if (is_owner or has_permission) and not is_archived:
            return True
    
    return False

def have_group_permission( association, group , user, permission):
    member = Member.objects.filter(user=user, association=association)
    is_member = member.exists()
    has_permission = user.has_perm(permission, group)
    if is_member :
        is_owner = member.first().is_owner
        is_archived = member.first().is_archived
        if (is_owner or has_permission) and not is_archived:
            return True
    
    return False