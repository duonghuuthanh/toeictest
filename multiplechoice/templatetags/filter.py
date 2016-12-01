from django import template

register = template.Library()

@register.filter(name='option_label')
def get_option_label(value):
    label = ["A", "B", "C", "D"]
    return label[value]