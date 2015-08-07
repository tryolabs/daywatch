# -*- coding: utf-8 -*-

from core.settings import ML_AUTH_TOKEN, ML_CATEGORIZERS
from core.models import Category, ITEM_MODEL
from core.utils import make_logger


ML_BASE = 'https://api.monkeylearn.com/api/v1/categorizer/'
ML_SINGLE_URL = '/classify_text/'
ML_BATCH_URL = '/classify_batch_text/'

HEADERS = {
    'Authorization': 'Token ' + ML_AUTH_TOKEN,
    'Content-Type': 'application/json'
}


logger = make_logger()


def _classification_url(lang_code):
    return ML_BASE + ML_CATEGORIZERS[lang_code] + ML_SINGLE_URL


def _batch_classification_url(lang_code):
    return ML_BASE + ML_CATEGORIZERS[lang_code] + ML_BATCH_URL


def _extract_final_category(category_list):
    """
    Returns the leaf category for the category list returned by Monkeylearn.
    """
    ncategories = len(category_list)
    category_name = category_list[ncategories-1][0]
    if category_name == "Videogames":
        return Category.objects.get(name="Video Games")
    else:
        try:
            return Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            logger.exception("Category doesn't exist: %s.", category_name)
            return None


def classify(text, lang_code):
    """
    Classify a single piece of text, given the language.
    """
    r = requests.post(
        _classification_url(lang_code),
        headers=HEADERS,
        data=json.dumps({'text': text}),
    )
    data = r.json()[0]
    return _extract_final_category(data)


def classify_batch(text_list, lang_code):
    """
    Classify a list of texts, given the language.
    """
    data = {
        'func': 'absolute',
        'threshold': '0',
        'text_list': text_list
    }

    response = requests.post(
        _batch_classification_url(lang_code),
        headers=HEADERS,
        data=json.dumps(data),
    )

    if response.status_code != 200:
        logger.error(
            "Monkeylearn returned non-200 status code: %s.",
            response.status_code
        )
        raise Exception(
            "Unable to classify batch, service returned: %s." % response.text
        )

    output = json.loads(response.text)

    return [_extract_final_category(cat_list) for cat_list in output]


def classify_item(item):
    """
    Classify an Item, saving its new category.
    """

    text = item.offer + ' ' + item.description
    category = classify(text)
    item.category = category
    item.save()
