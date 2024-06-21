import uuid


def format_id(item_id, model):
    if isinstance(item_id, str) and "UUID" in model._meta.pk.get_internal_type():
        return uuid.UUID(item_id)
    return item_id
