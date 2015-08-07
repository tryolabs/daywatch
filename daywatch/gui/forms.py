from django import forms
from django.utils.translation import ugettext_lazy
from django.contrib.auth.forms import PasswordResetForm

from core.models import Country, SITE_MODEL, Category, has_access, ITEM_MODEL
from core.settings import DW_DATE_FORMAT
from core.utils import field_list, numeric_field_list
from captcha.fields import ReCaptchaField


PERIOD_CHOICES = (
    ('last_7_d', ugettext_lazy('Last 7 days')),
    ('last_15_d', ugettext_lazy('Last 15 days')),
    ('last_30_d', ugettext_lazy('Last 30 days')),
    ('custom', ugettext_lazy('Custom')),
)

RESULT_TYPE_CHOICES = (
    ('sales', ugettext_lazy('Sales')),
    ('offered', ugettext_lazy('# Items Offered')),
    ('sold', ugettext_lazy('# Items Sold')),
)

ITEM_FIELDS = tuple([(field_name, field_name.replace('_', ' ').title())
                     for (field_name, field_type)
                     in field_list(ITEM_MODEL)])

NUMERIC_FIELDS = tuple([(field_name, field_name.replace('_', ' ').title())
                        for field_name in numeric_field_list(ITEM_MODEL)])


class PasswordResetReCaptchaForm(PasswordResetForm):
    captcha = ReCaptchaField(attrs={'theme': 'clean'})


class CountryCompanyForm(forms.Form):
    country = forms.ChoiceField()
    all_companies = forms.BooleanField(required=False)
    players = forms.MultipleChoiceField(required=False,
                                        widget=forms.CheckboxSelectMultiple)

    def __init__(self, user, *args, **kwargs):
        super(CountryCompanyForm, self).__init__(*args, **kwargs)

        user_profile = user.get_profile()
        # Filter countries the user has access to
        country_choices = []
        for country in Country.objects.all():
            if has_access(user, country):
                country_choices.append((country.code, country.name))
        self.fields["country"].choices = country_choices
        # Filter sites in those countries
        site_choices = []
        for site in SITE_MODEL.objects.all():
            if has_access(user, site.country):
                site_choices.append((site.id, site.name))
        self.fields["players"].choices = site_choices

CATEGORY_CHOICES = tuple([(category.id, category.name) for category in
                          Category.objects.all() if category.id != 1])

DATE_ATTRS = {'class': 'date_field'}


class PanelForm(CountryCompanyForm):
    result_type = forms.ChoiceField(choices=RESULT_TYPE_CHOICES)
    period = forms.ChoiceField(choices=PERIOD_CHOICES)
    start_date = forms.DateField(required=False,
                                 input_formats=[DW_DATE_FORMAT],
                                 widget=forms.TextInput(attrs=DATE_ATTRS))
    end_date = forms.DateField(required=False, input_formats=[DW_DATE_FORMAT],
                               widget=forms.TextInput(attrs=DATE_ATTRS))
    all_categories = forms.BooleanField(required=False)
    categories = forms.MultipleChoiceField(required=False,
                                           choices=CATEGORY_CHOICES,
                                           widget=forms.CheckboxSelectMultiple)


class SpidersPanelForm(CountryCompanyForm):
    period = forms.ChoiceField(choices=PERIOD_CHOICES)
    start_date = forms.DateField(required=False, input_formats=['%Y/%m/%d'])
    end_date = forms.DateField(required=False, input_formats=['%Y/%m/%d'])


class ItemsPanelForm(CountryCompanyForm):
    period = forms.ChoiceField(choices=PERIOD_CHOICES)
    fields = forms.MultipleChoiceField(choices=ITEM_FIELDS,
                                       widget=forms.CheckboxSelectMultiple)


class FieldForm(CountryCompanyForm):
    period = forms.ChoiceField(choices=PERIOD_CHOICES)
    fields = forms.MultipleChoiceField(choices=NUMERIC_FIELDS,
                                       widget=forms.CheckboxSelectMultiple)

SUM = 'sum'
AVERAGE = 'average'

METRIC_CHOICES = tuple([(metric, metric.title())
                        for metric in [SUM, AVERAGE]])


class TrendsPanelForm(FieldForm):
    start_date = forms.DateField(required=False, input_formats=['%Y/%m/%d'])
    end_date = forms.DateField(required=False, input_formats=['%Y/%m/%d'])
    period = forms.ChoiceField(choices=PERIOD_CHOICES)
    metric = forms.ChoiceField(choices=METRIC_CHOICES)
