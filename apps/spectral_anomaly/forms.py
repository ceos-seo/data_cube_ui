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
    # TODO: Add/remove/modify fields that are used to create your query here.
    # e.g. if there is no type, anim, or compositor, remove everything here.
    #if you need a property on the Task model called Color Scale, create that here.

    #these are done in the init funct.
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

    baseline_threshold_min = forms.FloatField(
        label='Min Baseline Value',
        widget=forms.NumberInput(attrs={'class': 'field-divided',
                                        'step': "any",
                                        'required': 'required'}))

    baseline_threshold_max = forms.FloatField(
        label='Max Baseline Value',
        widget=forms.NumberInput(attrs={'class': 'field-divided',
                                        'step': "any",
                                        'required': 'required'}))

    change_threshold_min = forms.FloatField(
        label='Min Change Value (Optional)',
        widget=forms.NumberInput(attrs={'class': 'field-divided',
                                        'step': "any"}))

    change_threshold_max = forms.FloatField(
        label='Max Change Value (Optional)',
        widget=forms.NumberInput(attrs={'class': 'field-divided',
                                        'step': "any"}))

    def __init__(self, *args, **kwargs):
        datacube_platform = kwargs.pop('datacube_platform', None)
        super(AdditionalOptionsForm, self).__init__(*args, **kwargs)
        self.fields["query_type"].queryset = ResultType.objects.all()
        self.fields["compositor"].queryset = Compositor.objects.all()

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
