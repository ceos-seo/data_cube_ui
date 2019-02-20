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

import logging
dj_logger = logging.getLogger(__name__)


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
        # if query_type in ['ndvi', 'ndbi', 'ndwi', 'evi']:
        #     composite_allow_min, composite_allow_max = -1.0, 1.0
        # else: # TODO: Determine the bounds of fractional coverage.
        #     composite_allow_min, composite_allow_max = -1.0, 1.0
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
            self.add_error('change_threshold_min', 'Either neither or both the min and max '
                                                    'change value fields may be specified.')


class DataSelectionForm(forms.Form):
    two_column_format = True

    title = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'class': 'hidden_form_title'}))
    description = forms.CharField(required=False,
                                  widget=forms.HiddenInput(attrs={'class': 'hidden_form_description'}))
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
        time_start = kwargs.pop('time_start', None)
        time_end = kwargs.pop('time_end', None)
        area = kwargs.pop('area', None)
        super(DataSelectionForm, self).__init__(*args, **kwargs)
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
        if area:
            self.fields['latitude_min'].widget.attrs.update({'min': area.latitude_min, 'max': area.latitude_max})
            self.fields['latitude_max'].widget.attrs.update({'min': area.latitude_min, 'max': area.latitude_max})
            self.fields['longitude_min'].widget.attrs.update({'min': area.longitude_min, 'max': area.longitude_max})
            self.fields['longitude_max'].widget.attrs.update({'min': area.longitude_min, 'max': area.longitude_max})

    def clean(self):
        cleaned_data = super(DataSelectionForm, self).clean()

        if not self.is_valid():
            return

        if cleaned_data.get('latitude_min') >= cleaned_data.get('latitude_max'):
            self.add_error(
                'latitude_min',
                "Please enter a valid pair of latitude values where the lower bound is less than the upper bound.")

        if cleaned_data.get('longitude_min') >= cleaned_data.get('longitude_max'):
            self.add_error(
                'longitude_min',
                "Please enter a valid pair of longitude values where the lower bound is less than the upper bound.")

        if cleaned_data.get('baseline_time_start') >= cleaned_data.get('baseline_time_end'):
            self.add_error('baseline_time_start',
                           "Please enter a valid start and end time for the baseline "
                           "time range where the start is before the end.")

        if cleaned_data.get('analysis_time_start') >= cleaned_data.get('analysis_time_end'):
            self.add_error('analysis_time_start',
                           "Please enter a valid start and end time for the analysis "
                           "time range where the start is before the end.")

        if not self.is_valid():
            return

        area = (cleaned_data.get('latitude_max') - cleaned_data.get('latitude_min')) * (
                cleaned_data.get('longitude_max') - cleaned_data.get('longitude_min'))

        if area > 4.0:
            self.add_error('latitude_min', 'Tasks over an area greater than four square degrees are not permitted.')
