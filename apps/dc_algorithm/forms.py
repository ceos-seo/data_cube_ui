from django import forms

from .models import Satellite

# This is the maximum number of tasks per user across all apps.
# A value of `None` indicates no limit.
MAX_NUM_TASKS_PER_USER = None
# This is the maximum number of years in a query.
MAX_NUM_YEARS = 100

class DataSelectionForm(forms.Form):
    two_column_format = True

    title = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'class': 'hidden_form_title'}))
    description = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'class': 'hidden_form_description'}))
    satellite = forms.ModelChoiceField(
        queryset=Satellite.objects.all(), widget=forms.HiddenInput(attrs={'class': 'hidden_form_satellite'}))
    area_id = forms.CharField(widget=forms.HiddenInput(attrs={'class': 'hidden_form_id'}))

    latitude_min = forms.FloatField(
        label='Min Latitude',
        widget=forms.NumberInput(attrs={'class': 'field-divided',
                                        'step': "any",
                                        'required': 'required'}))
    latitude_max = forms.FloatField(
        label='Max Latitude',
        widget=forms.NumberInput(attrs={'class': 'field-divided',
                                        'step': "any",
                                        'required': 'required'}))
    longitude_min = forms.FloatField(
        label='Min Longitude',
        widget=forms.NumberInput(attrs={'class': 'field-divided',
                                        'step': "any",
                                        'required': 'required'}))
    longitude_max = forms.FloatField(
        label='Max Longitude',
        widget=forms.NumberInput(attrs={'class': 'field-divided',
                                        'step': "any",
                                        'required': 'required'}))
    time_start = forms.DateField(
        label='Start Date',
        widget=forms.DateInput(
            attrs={'class': 'datepicker field-divided',
                   'placeholder': '01/01/2010',
                   'required': 'required'}))
    time_end = forms.DateField(
        label='End Date',
        widget=forms.DateInput(
            attrs={'class': 'datepicker field-divided',
                   'placeholder': '01/02/2010',
                   'required': 'required'}))

    def __init__(self, *args, **kwargs):
        time_start = kwargs.pop('time_start', None)
        time_end = kwargs.pop('time_end', None)
        area = kwargs.pop('area', None)
        self.user_id = kwargs.pop('user_id', None)
        self.user_history = kwargs.pop('user_history', None)
        self.task_model_class = kwargs.pop('task_model_class', None)
        super(DataSelectionForm, self).__init__(*args, **kwargs)
        #meant to prevent this routine from running if trying to init from querydict.
        if time_start and time_end:
            self.fields['time_start'] = forms.DateField(
                initial=time_start.strftime("%m/%d/%Y"),
                label='Start Date',
                widget=forms.DateInput(attrs={'class': 'datepicker field-divided',
                                              'required': 'required'}))
            self.fields['time_end'] = forms.DateField(
                initial=time_end.strftime("%m/%d/%Y"),
                label='End Date',
                widget=forms.DateInput(attrs={'class': 'datepicker field-divided',
                                              'required': 'required'}))
        if area:
            self.fields['latitude_min'].widget.attrs.update({'min': area.latitude_min, 'max': area.latitude_max})
            self.fields['latitude_max'].widget.attrs.update({'min': area.latitude_min, 'max': area.latitude_max})
            self.fields['longitude_min'].widget.attrs.update({'min': area.longitude_min, 'max': area.longitude_max})
            self.fields['longitude_max'].widget.attrs.update({'min': area.longitude_min, 'max': area.longitude_max})

    def clean(self):
        cleaned_data = super(DataSelectionForm, self).clean()

        latitude_min, latitude_max = cleaned_data.get('latitude_min'), cleaned_data.get('latitude_max')
        longitude_min, longitude_max = cleaned_data.get('longitude_min'), cleaned_data.get('longitude_max')

        if latitude_min > latitude_max and longitude_min > longitude_max:
            self.add_error(
                None,
                "Please enter a valid pair of latitude and longitude values where the lower bounds "
                "are less than or equal to the upper bounds.")

        if latitude_min > latitude_max:
            self.add_error(
                'latitude_min',
                "Please enter a valid pair of latitude values where the lower bound is less than or equal to the upper bound.")

        if longitude_min > longitude_max:
            self.add_error(
                'longitude_min',
                "Please enter a valid pair of longitude values where the lower bound is less than or equal to the upper bound.")

        # The start and end time fields are removed in some apps (e.g. spectral_anomaly),
        # so we may not perform checks on these fields.
        time_start, time_end = cleaned_data.get('time_start'), cleaned_data.get('time_end')
        if time_start is not None and time_end is not None and (time_start >= time_end):
            self.add_error('time_start',
                           "Please enter a valid start and end time range where the start is before the end.")

        area = (latitude_max - latitude_min) * (longitude_max - longitude_min)

        # Limit the area allowed.
        max_area = 1
        if area > max_area:
            self.add_error('latitude_min', 'Tasks over an area greater than {} '
                                           'square degree(s) are not permitted.'.format(max_area))

        # Limit the time range allowed.
        if time_start is not None and time_end is not None:
            # For some apps, the time extent is not relevant to resource consumption
            # (e.g. if data is only loaded for the first and last years).
            from apps.coastal_change.models import CoastalChangeTask
            if self.task_model_class not in [CoastalChangeTask]:
                if self.check_time_range(time_start, time_end, MAX_NUM_YEARS):
                    self.add_error('time_start', 'Tasks over a time range greater than {} '
                                                 'year(s) are not permitted.'.format(MAX_NUM_YEARS))

        # Limit each user to some number of queued tasks across all apps.
        if MAX_NUM_TASKS_PER_USER is not None:
            num_running_tasks = self.task_model_class.get_queryset_from_history(
                self.user_history, complete=False).count()
            if num_running_tasks >= MAX_NUM_TASKS_PER_USER:
                self.add_error(None, 'You may only run {} task(s) at a time.'.format(MAX_NUM_TASKS_PER_USER))

        return cleaned_data

    def check_time_range(self, time_start, time_end, max_num_years=5):
        """
        Determines if the time range [time_start, time_end] exceeds an upper bound.
        If so, returns `True`.

        Parameters
        ----------
        time_start, time_end: datetime.date
        max_num_years: float (default 5)
            The maximum number of years the time range can have.
        """
        year_diff = time_end.year - time_start.year
        month_diff = time_end.month - time_start.month
        day_diff = time_end.day - time_start.day
        return (year_diff > max_num_years) or \
               (year_diff == max_num_years and month_diff > 0) or \
               (year_diff == max_num_years and month_diff == 0 and day_diff > 0)