from __future__ import unicode_literals, print_function

from django.contrib.contenttypes.models import ContentType

from .decorators import register_service, generic_ajax_func, require_staff

@register_service
@generic_ajax_func
def hello_world(request, p):
    return "Hello world! " + p

@register_service
@require_staff
@generic_ajax_func
def set_model_order(request, 
                    app_label, 
                    parent_model_name, 
                    parent_model_pk,
                    relation_name,
                    order
                   ):
    t = ContentType.objects.get(app_label=app_label, model=parent_model_name)
    parent_model_class = t.model_class()
    parent_model = parent_model_class.objects.get(pk=parent_model_pk)
    order_list = [int(x) for x in order.split(",")]
    assert getattr(parent_model, relation_name + "_set"). \
            filter(pk__in=order_list).count() == len(order_list)

    setter = getattr(parent_model, "set_{}_order".format(relation_name))
    setter(order_list)
    return True

