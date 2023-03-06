from django import template


class CensorException(Exception):
    pass


register = template.Library()


TO_CENSOR = {
    'редиска': 'редиска',
    'синхрофазотрон': 'синхрофазотрон',
    'экзистенциальный': 'экзистенциальный',
    'ройбуш': 'ройбуш',
    'амфиболичность': 'амфиболичность',
    'кот': 'кот',
}

@register.filter()
def censor(value):
    try:
        if not isinstance(value, str):
            raise CensorException('Цензурироваться может только строковой тип данных (str).')

        for word in list(TO_CENSOR.keys()):
            if word in value:
                value = value.replace(word, f'{word[0]}{"*" * (len(word) - 1)}')
            if word.capitalize() in value:
                value = value.replace(word.capitalize(), f'{word[0]}{"*" * (len(word) - 1)}')

        return value


    except CensorException as e:
        print(e)

