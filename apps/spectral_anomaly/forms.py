# Copyright 2016 United States Government as represented by the Administrator
# of the National Aeronautics and Space Administration. All Rights Reserved.
#
# Portion of this code is Copyright Geoscience Australia, Licensed under the
# Apache License, Version 2.0 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of the License
# at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# The CEOS 2 platform is licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django import forms

from .models import ResultType, Satellite
from apps.dc_algorithm.models import Compositor
from .tasks import spectral_indices_range_map
from apps.dc_algorithm.forms import DataSelectionForm as DataSelectionFormBase


class AdditionalOptionsForm(forms.Form):
    """
    Django form to be created for selecting information and validating input for:
        result_type
        band_selection
        title
        description
    Init function to initialize dynamic forms.
    """
    query_type = forms.ModelChoiceField(
        queryset=None,
        to_field_name="result_id",
        empty_label=None,
        help_text='Select the spectral index to use.',
        label='Spectral Index:',
        widget=forms.Select(attrs={'class': 'field-long tooltipped'}))

    compositor = forms.ModelChoiceField(
        queryset=None,
        to_field_name="id",
        empty_label=None,
        help_text='Select the method by which the "best" pixel will be chosen.',
        label="Compositing Method:",
        widget=forms.Select(attrs={'class': 'field-long tooltipped'}))

    composite_threshold_min = forms.FloatField(
        label='Min Composite Value',
        required=True,
        widget=forms.NumberInput(attrs={'class': 'field-divided',
                                        'step': "any"}))

    composite_threshold_max = forms.FloatField(
        label='Max Composite Value',
        required=True,
        widget=forms.NumberInput(attrs={'class': 'field-divided',
                                        'step': "any"}))

    change_threshold_min = forms.FloatField(
        label='Min Change Value (Optional)',
        required=False,
        widget=forms.NumberInput(attrs={'class': 'field-divided',
                                        'step': "any"}))

    change_threshold_max = forms.FloatField(
        label='Max Change Value (Optional)',
        required=False,
        widget=forms.NumberInput(attrs={'class': 'field-divided',
                                        'step': "any"}))

    def __init__(self, *args, **kwargs):
        datacube_platform = kwargs.pop('datacube_platform', None)
        super(AdditionalOptionsForm, self).__init__(*args, **kwargs)
        self.fields["query_type"].queryset = ResultType.objects.all()
        self.fields["compositor"].queryset = Compositor.objects.all()

    def clean(self):
        query_type = self.cleaned_data['query_type'].result_id
        composite_threshold_min = self.cleaned_data['composite_threshold_min']
        composite_threshold_max = self.cleaned_data['composite_threshold_max']
        change_threshold_min = self.cleaned_data['change_threshold_min']
        change_threshold_max = self.cleaned_data['change_threshold_max']

        # Determine possible value ranges.
        composite_allow_min, composite_allow_max = spectral_indices_range_map[query_type]
        change_allow_min = composite_allow_min - composite_allow_max
        change_allow_max = composite_allow_max - composite_allow_min

        # 1. Handle the composite value range fields.
        # 1.1. Ensure the composite value range fields are within
        #      the possible range for the selected spectral index.
        composite_out_of_range_message = \
            'The min and max composite values must be in the range [{}, {}]'\
            .format(composite_allow_min, composite_allow_max)
        if not composite_allow_min <= composite_threshold_min <= composite_allow_max:
            self.add_error('composite_threshold_min', composite_out_of_range_message)
        if not composite_allow_min <= composite_threshold_max <= composite_allow_max:
            self.add_error('composite_threshold_max', composite_out_of_range_message)
        # 1.2. Ensure the minimum is less than the maximum.
        if not composite_threshold_min < composite_threshold_max:
            self.add_error('composite_threshold_min',
                           'The min composite value must be less than the max composite value.')
        # 2. Handle the change value range fields.
        if change_threshold_min is not None and change_threshold_max is not None:
            # 2.1. Ensure the change value range fields are within
            #      the possible range for the selected spectral index.
            change_out_of_range_message = \
                'The min and max change values must be in the range [{}, {}]'\
                .format(change_allow_min, change_allow_max)
            if not change_allow_min <= change_threshold_min <= change_allow_max:
                self.add_error('change_threshold_min', change_out_of_range_message)
            if not change_allow_min <= change_threshold_max <= change_allow_max:
                self.add_error('change_threshold_max', change_out_of_range_message)
            # 2.2. Ensure the minimum is less than the maximum.
            if not change_threshold_min < change_threshold_max:
                self.add_error('change_threshold_min',
                               'The min change value must be less than the max change value.')
        elif (change_threshold_min is not None) ^ (change_threshold_max is not None):
            self.add_error('change_threshold_min', 'Either, neither, or both the min and max '
                                                    'change value fields may be specified.')


class DataSelectionForm(DataSelectionFormBase):
    baseline_time_start = forms.DateField(
        label='Baseline Start Date',
        widget=forms.DateInput(
            attrs={'class': 'datepicker field-divided',
                   'placeholder': '01/01/2010',
                   'required': 'required'}))
    baseline_time_end = forms.DateField(
        label='Baseline End Date',
        widget=forms.DateInput(
            attrs={'class': 'datepicker field-divided',
                   'placeholder': '01/02/2010',
                   'required': 'required'}))
    analysis_time_start = forms.DateField(
        label='Analysis Start Date',
        widget=forms.DateInput(
            attrs={'class': 'datepicker field-divided',
                   'placeholder': '01/01/2010',
                   'required': 'required'}))
    analysis_time_end = forms.DateField(
        label='Analysis End Date',
        widget=forms.DateInput(
            attrs={'class': 'datepicker field-divided',
                   'placeholder': '01/02/2010',
                   'required': 'required'}))

    def __init__(self, *args, **kwargs):
        time_start = kwargs.get('time_start')
        time_end = kwargs.get('time_end')
        super(DataSelectionForm, self).__init__(*args, **kwargs)
        # Remove undesired fields from the superclass form.
        self.fields.pop('time_start'); self.fields.pop('time_end')
        # meant to prevent this routine from running if trying to init from querydict.
        if time_start and time_end:
            self.fields['baseline_time_start'] = forms.DateField(
                initial=time_start.strftime("%m/%d/%Y"),
                label='Baseline Start Date',
                widget=forms.DateInput(attrs={'class': 'datepicker field-divided',
                                              'required': 'required'}))
            self.fields['baseline_time_end'] = forms.DateField(
                initial=time_end.strftime("%m/%d/%Y"),
                label='Baseline End Date',
                widget=forms.DateInput(attrs={'class': 'datepicker field-divided',
                                              'required': 'required'}))
            self.fields['analysis_time_start'] = forms.DateField(
                initial=time_start.strftime("%m/%d/%Y"),
                label='Analysis Start Date',
                widget=forms.DateInput(attrs={'class': 'datepicker field-divided',
                                              'required': 'required'}))
            self.fields['analysis_time_end'] = forms.DateField(
                initial=time_end.strftime("%m/%d/%Y") ,
                label='Analysis End Date',
                widget=forms.DateInput(attrs={'class': 'datepicker field-divided',
                                              'required': 'required'}))
    def clean(self):
        cleaned_data = super(DataSelectionForm, self).clean()

        baseline_time_start = cleaned_data.get('baseline_time_start')
        baseline_time_end = cleaned_data.get('baseline_time_end')
        if baseline_time_start >= baseline_time_end:
            self.add_error('baseline_time_start',
                           "Please enter a valid start and end time for the baseline "
                           "time range where the start is before the end.")

        analysis_time_start = cleaned_data.get('analysis_time_start')
        analysis_time_end = cleaned_data.get('analysis_time_end')
        if analysis_time_start >= analysis_time_end:
            self.add_error('analysis_time_start',
                           "Please enter a valid start and end time for the analysis "
                           "time range where the start is before the end.")

        # Limit the time range allowed.
        max_num_years = 5
        time_range_err_fmt = \
            'Tasks over a time range greater than {} year(s) are not permitted. ' \
            'The {} time range is too large.'.format(max_num_years, "{}")
        if self.check_time_range(baseline_time_start, baseline_time_end, max_num_years):
            self.add_error('baseline_time_start',
                           time_range_err_fmt.format('baseline'))
        if self.check_time_range(analysis_time_start, analysis_time_end, max_num_years):
            self.add_error('baseline_time_start',
                           time_range_err_fmt.format('analysis'))

        return cleaned_data
