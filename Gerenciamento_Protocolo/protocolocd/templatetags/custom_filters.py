from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Filtro para obter um valor de dicionário através de uma chave.
    Uso: {{ dicionario|get_item:chave }}
    """
    if dictionary is None:
        return None
    return dictionary.get(str(key))

@register.filter
def sum_lists(dictionary_values):
    """
    Filtro para somar todas as listas em um dicionário de valores.
    Retorna uma lista única contendo todos os itens de todas as listas.
    Uso: {{ dicionario.values|sum_lists }}
    """
    if not dictionary_values:
        return []
    
    result = []
    for value in dictionary_values:
        if isinstance(value, list):
            result.extend(value)
    
    return result 