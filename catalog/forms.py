
from django import forms
import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(
        help_text="Enter a date between now and 4 weeks(default is 3)")

    # clean and validate the input
    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']
        # check date is not in the past
        if data < datetime.date.today():
            raise ValidationError(
                _('Invalid date - renewal must be in the future'))

        # check renewal date is not more than 4 weeks
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(
                _('Invalid date- Renewal more than 4 weeks ahead'))

        # return cleaned data
        return data
