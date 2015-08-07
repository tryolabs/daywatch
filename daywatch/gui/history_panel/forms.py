'''
Created on Aug 10, 2012

@author: alejandro
'''

from django import forms
from django.utils.translation import ugettext_lazy

from ..forms import PanelForm, COUNTRY_CHOICES_LIMITED, COMPANY_CHOICES, \
    CONCEPT_CHOICES, CATEGORY_CHOICES_TRANS


HISTORY_COMPARISON_PERIOD_CHOICES = (
    ('last_3_m', ugettext_lazy('Last 3 months')),
    ('last_4_m', ugettext_lazy('Last 4 months')),
    ('last_6_m', ugettext_lazy('Last 6 months')),
)


class HistoryPanelExportForm(PanelForm):
    '''
    A Form for History Panel that adds an "Export to XLS" button.
    '''
    xls_export = forms.BooleanField(required=False, widget=forms.HiddenInput())

    def __init__(self, user, *args, **kwargs):
        super(HistoryPanelExportForm, self).__init__(user, *args, **kwargs)


class HistoryComparisonForm(forms.Form):

    #country = forms.ChoiceField(choices=COUNTRY_CHOICES)
    country = forms.ChoiceField(choices=COUNTRY_CHOICES_LIMITED)
    concept = forms.ChoiceField(choices=CONCEPT_CHOICES)
    period = forms.ChoiceField(choices=HISTORY_COMPARISON_PERIOD_CHOICES)
    all_companies = forms.BooleanField(required=False)
    players = forms.MultipleChoiceField(
        required=False, choices=COMPANY_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )
    all_categories = forms.BooleanField(required=False)
    categories = forms.MultipleChoiceField(
        required=False,
        choices=CATEGORY_CHOICES_TRANS,
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, user, *args, **kwargs):
        '''
        limit the choice of owner to the currently logged in users hats
        '''

        super(HistoryComparisonForm, self).__init__(*args, **kwargs)

        # get different list of choices here
        choices = []
        user_profile = user.get_profile()
        for country_code, country_name in COUNTRY_CHOICES_LIMITED:
            if user_profile.has_full_access_for_country(country_code) or \
            user_profile.has_trial_access_for_country(country_code):
                choices.append((country_code, country_name))
        self.fields["country"].choices = choices
