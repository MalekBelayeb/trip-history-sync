from num2words import num2words


def convert_amount_to_words(amount):
    dinars = int(amount)
    millimes = round((amount - dinars) * 1000)

    result = (
        f"{num2words(dinars, lang='fr')} dinars et "
        f"{num2words(millimes, lang='fr')} millimes"
    )

    return result
