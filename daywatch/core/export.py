import re
import unicodedata
from core.models import DayWatchItem
import os
import gc
from xlwt import Workbook


# FIXME: Not used often, might not be worth having
def queryset_iterator(queryset, chunksize=1000):
    '''''
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query
    sets.

    Source: http://djangosnippets.org/snippets/1949/
    '''
    pk = 0
    if queryset.count() == 0:
        return
        yield
    last_pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()


def files_wikipedia(a, b):

    path = '/home/raul/workspace/daywatch_platform_text_scraper/daywatch/core/resources/exports'

    for item in queryset_iterator(DayWatchItem.objects.filter(id__gt=a, id__lte=b), chunksize=250):
        if item.label == None or item.title == None:
            continue
#         if not ('Shoes' in item.label):
#             continue
        filename = item.label + ' - ' + item.title
        filename = filename.replace(':', '--')
        filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore')
        filename = unicode(re.sub('[^\w\s-]', '', filename).strip())
        # filename = re.sub('[-\s]+', '_', filename)
        filename = filename + '.txt'
        print filename
        temp_path = path
        for subpath in item.label.split(' : '):
            temp_path = os.path.join(temp_path, subpath)
            if not os.path.exists(temp_path):
                os.makedirs(temp_path)
                print temp_path
        # print temp_path
        try:
            f = open(os.path.join(temp_path, filename), 'w')
            if item.reviews == None:
                item.reviews = u''
            if item.description == None:
                item.description = u''
        except:
            print 'FILENAME ERROR'
            print filename
            continue
        try:
            s = item.name + u'\n' + item.label + u'\n' + item.description + u'\n\n' + item.reviews
            f.write(s.encode('utf8'))
            f.close()
        except:
            f.close()
            os.remove(os.path.join(temp_path, filename))
            print 'UNICODE ERROR'


def files_scielo(a, b):

    path = '/home/raul/workspace/daywatch_platform_text_scraper/daywatch/core/resources/exports'

    wb = Workbook(encoding='utf8')
    ws = wb.add_sheet('samples')

    TITLE_COL = 0
    ABSTRACT_COL = 1
    KEYWORDS_COL = 2
    HASH_ID_COL = 3
    LANGUAGE_COL = 4

    row = 0

    ws.write(row, TITLE_COL, "TITLE")
    ws.write(row, ABSTRACT_COL, "ABSTRACT")
    ws.write(row, KEYWORDS_COL, "KEYWORDS")
    ws.write(row, HASH_ID_COL, "HASH_ID")
    ws.write(row, LANGUAGE_COL, "LANGUAGE")

    row = 1

    for item in queryset_iterator(DayWatchItem.objects.filter(
                                            id__gt=a,
                                            id__lte=b,
                                            site_id=3,
                                            reviews='pt'), chunksize=250):

        ws.write(row, TITLE_COL, item.name)
        ws.write(row, ABSTRACT_COL, item.description)
        ws.write(row, KEYWORDS_COL, item.label)
        ws.write(row, HASH_ID_COL, item.hash_id)
        ws.write(row, LANGUAGE_COL, item.reviews)

        print row
        row += 1

    wb.save('dataset.xls')

