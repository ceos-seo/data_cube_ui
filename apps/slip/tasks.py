from django.db.models import F

from celery.task import task
from celery import chain, group, chord
from celery.utils.log import get_task_logger
from datetime import datetime, timedelta
import shutil
import xarray as xr
import numpy as np
import os
import imageio
from collections import OrderedDict

from utils.data_access_api import DataAccessApi
from utils.dc_utilities import (create_cfmask_clean_mask, create_bit_mask, write_geotiff_from_xr, write_png_from_xr,
                                add_timestamp_data_to_xr, clear_attrs)
from utils.dc_chunker import (create_geographic_chunks, generate_baseline, combine_geographic_chunks)
from utils.dc_slip import compute_slip, mask_mosaic_with_slip
from utils.dc_mosaic import create_mosaic

from .models import SlipTask
from apps.dc_algorithm.models import Satellite

logger = get_task_logger(__name__)


@task(name="slip.get_acquisition_list")
def get_acquisition_list(task, area_id, platform, date):
    dc = DataAccessApi(config=task.config_path)
    # lists all acquisition dates for use in single tmeslice queries.
    product = Satellite.objects.get(datacube_platform=platform).product_prefix + area_id
    acquisitions = dc.list_acquisition_dates(product, platform, time=(datetime(1900, 1, 1), date))
    return acquisitions


@task(name="slip.run")
def run(task_id):
    """Responsible for launching task processing using celery asynchronous processes

    Chains the parsing of parameters, validation, chunking, and the start to data processing.
    """
    chain(
        parse_parameters_from_task.s(task_id),
        validate_parameters.s(task_id), perform_task_chunking.s(task_id), start_chunk_processing.s(task_id))()
    return True


@task(name="slip.parse_parameters_from_task")
def parse_parameters_from_task(task_id):
    """Parse out required DC parameters from the task model.

    See the DataAccessApi docstrings for more information.
    Parses out platforms, products, etc. to be used with DataAccessApi calls.

    If this is a multisensor app, platform and product should be pluralized and used
    with the get_stacked_datasets_by_extent call rather than the normal get.

    Returns:
        parameter dict with all keyword args required to load data.

    """
    task = SlipTask.objects.get(pk=task_id)

    parameters = {
        'platform': task.platform,
        'time': (task.time_start, task.time_end),
        'longitude': (task.longitude_min, task.longitude_max),
        'latitude': (task.latitude_min, task.latitude_max),
        'measurements': task.measurements
    }

    parameters['product'] = Satellite.objects.get(
        datacube_platform=parameters['platform']).product_prefix + task.area_id

    task.execution_start = datetime.now()
    task.update_status("WAIT", "Parsed out parameters.")

    return parameters


@task(name="slip.validate_parameters")
def validate_parameters(parameters, task_id):
    """Validate parameters generated by the parameter parsing task

    All validation should be done here - are there data restrictions?
    Combinations that aren't allowed? etc.

    Returns:
        parameter dict with all keyword args required to load data.
        -or-
        updates the task with ERROR and a message, returning None

    """
    task = SlipTask.objects.get(pk=task_id)
    dc = DataAccessApi(config=task.config_path)

    acquisitions = dc.list_acquisition_dates(**parameters)

    if len(acquisitions) < 1:
        task.complete = True
        task.update_status("ERROR", "There are no acquistions for this parameter set.")
        return None

    if len(acquisitions) < task.baseline_length + 1:
        task.complete = True
        task.update_status("ERROR", "There are an insufficient number of acquisitions for your baseline length.")
        return None

    validation_parameters = {**parameters}
    validation_parameters.pop('time')
    validation_parameters.pop('measurements')
    validation_parameters.update({'product': 'terra_aster_gdm_' + task.area_id, 'platform': 'TERRA'})
    if len(dc.list_acquisition_dates(**validation_parameters)) < 1:
        task.complete = True
        task.update_status("ERROR", "There is no elevation data for this parameter set.")
        return None

    task.update_status("WAIT", "Validated parameters.")

    if not dc.validate_measurements(parameters['product'], parameters['measurements']):
        parameters['measurements'] = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'pixel_qa']

    dc.close()
    return parameters


@task(name="slip.perform_task_chunking")
def perform_task_chunking(parameters, task_id):
    """Chunk parameter sets into more manageable sizes

    Uses functions provided by the task model to create a group of
    parameter sets that make up the arg.

    Args:
        parameters: parameter stream containing all kwargs to load data

    Returns:
        parameters with a list of geographic and time ranges

    """

    if parameters is None:
        return None

    task = SlipTask.objects.get(pk=task_id)
    dc = DataAccessApi(config=task.config_path)

    dates = dc.list_acquisition_dates(**parameters)
    task_chunk_sizing = task.get_chunk_size()

    geographic_chunks = create_geographic_chunks(
        longitude=parameters['longitude'],
        latitude=parameters['latitude'],
        geographic_chunk_size=task_chunk_sizing['geographic'])

    time_chunks = generate_baseline(dates, task.baseline_length)

    logger.info("Time chunks: {}, Geo chunks: {}".format(len(time_chunks), len(geographic_chunks)))

    dc.close()
    task.update_status("WAIT", "Chunked parameter set.")
    return {'parameters': parameters, 'geographic_chunks': geographic_chunks, 'time_chunks': time_chunks}


@task(name="slip.start_chunk_processing")
def start_chunk_processing(chunk_details, task_id):
    """Create a fully asyncrhonous processing pipeline from paramters and a list of chunks.

    The most efficient way to do this is to create a group of time chunks for each geographic chunk,
    recombine over the time index, then combine geographic last.
    If we create an animation, this needs to be reversed - e.g. group of geographic for each time,
    recombine over geographic, then recombine time last.

    The full processing pipeline is completed, then the create_output_products task is triggered, completing the task.

    """

    if chunk_details is None:
        return None

    parameters = chunk_details.get('parameters')
    geographic_chunks = chunk_details.get('geographic_chunks')
    time_chunks = chunk_details.get('time_chunks')

    task = SlipTask.objects.get(pk=task_id)
    task.total_scenes = len(geographic_chunks) * len(time_chunks) * (task.get_chunk_size()['time'] if
                                                                     task.get_chunk_size()['time'] is not None else 1)
    task.scenes_processed = 0
    task.update_status("WAIT", "Starting processing.")

    logger.info("START_CHUNK_PROCESSING")

    processing_pipeline = group([
        group([
            processing_task.s(
                task_id=task_id,
                geo_chunk_id=geo_index,
                time_chunk_id=time_index,
                geographic_chunk=geographic_chunk,
                time_chunk=time_chunk,
                **parameters) for time_index, time_chunk in enumerate(time_chunks)
        ]) | recombine_time_chunks.s(task_id=task_id) for geo_index, geographic_chunk in enumerate(geographic_chunks)
    ]) | recombine_geographic_chunks.s(task_id=task_id)

    processing_pipeline = (processing_pipeline | create_output_products.s(task_id=task_id)).apply_async()
    return True


@task(name="slip.processing_task", acks_late=True)
def processing_task(task_id=None,
                    geo_chunk_id=None,
                    time_chunk_id=None,
                    geographic_chunk=None,
                    time_chunk=None,
                    **parameters):
    """Process a parameter set and save the results to disk.

    Uses the geographic and time chunk id to identify output products.
    **params is updated with time and geographic ranges then used to load data.
    the task model holds the iterative property that signifies whether the algorithm
    is iterative or if all data needs to be loaded at once.

    Computes a single SLIP baseline comparison - returns a slip mask and mosaic.

    Args:
        task_id, geo_chunk_id, time_chunk_id: identification for the main task and what chunk this is processing
        geographic_chunk: range of latitude and longitude to load - dict with keys latitude, longitude
        time_chunk: list of acquisition dates
        parameters: all required kwargs to load data.

    Returns:
        path to the output product, metadata dict, and a dict containing the geo/time ids
    """

    chunk_id = "_".join([str(geo_chunk_id), str(time_chunk_id)])
    task = SlipTask.objects.get(pk=task_id)

    logger.info("Starting chunk: " + chunk_id)
    if not os.path.exists(task.get_temp_path()):
        return None

    metadata = {}

    def _get_datetime_range_containing(*time_ranges):
        return (min(time_ranges) - timedelta(microseconds=1), max(time_ranges) + timedelta(microseconds=1))

    time_range = _get_datetime_range_containing(time_chunk[0], time_chunk[-1])

    dc = DataAccessApi(config=task.config_path)
    updated_params = {**parameters}
    updated_params.update(geographic_chunk)
    updated_params.update({'time': time_range})
    data = dc.get_dataset_by_extent(**updated_params)

    #grab dem data as well
    dem_parameters = {**updated_params}
    dem_parameters.update({'product': 'terra_aster_gdm_' + task.area_id, 'platform': 'TERRA'})
    dem_parameters.pop('time')
    dem_parameters.pop('measurements')
    dem_data = dc.get_dataset_by_extent(**dem_parameters)

    if 'time' not in data or 'time' not in dem_data:
        return None

    #target data is most recent, with the baseline being everything else.
    target_data = data.isel(time=-1, drop=True)
    baseline_data = data.isel(time=slice(None, -1))

    clear_mask = create_cfmask_clean_mask(data.cf_mask) if 'cf_mask' in data else create_bit_mask(data.pixel_qa, [1, 2])
    combined_baseline = task.get_processing_method()(baseline_data, clean_mask=clear_mask[:-1, :, :])

    target_data['time'] = [0]
    target_data = create_mosaic(target_data, clean_mask=clear_mask[-1, :, :])

    slip_data = compute_slip(combined_baseline, target_data, dem_data)
    target_data['slip'] = slip_data

    metadata = task.metadata_from_dataset(
        metadata,
        target_data,
        clear_mask[-1, :, :],
        updated_params,
        time=data.time.values.astype('M8[ms]').tolist()[-1])

    task.scenes_processed = F('scenes_processed') + 1
    task.save()

    path = os.path.join(task.get_temp_path(), chunk_id + ".nc")
    clear_attrs(target_data)
    target_data.to_netcdf(path)
    logger.info("Done with chunk: " + chunk_id)
    return path, metadata, {'geo_chunk_id': geo_chunk_id, 'time_chunk_id': time_chunk_id}


@task(name="slip.recombine_time_chunks")
def recombine_time_chunks(chunks, task_id=None):
    """Recombine processed chunks over the time index.

    Open time chunked processed datasets and recombine them using the same function
    that was used to process them. This assumes an iterative algorithm - if it is not, then it will
    simply return the data again.

    Args:
        chunks: list of the return from the processing_task function - path, metadata, and {chunk ids}

    Returns:
        path to the output product, metadata dict, and a dict containing the geo/time ids

    """
    logger.info("RECOMBINE_TIME")
    #sorting based on time id - earlier processed first as they're incremented e.g. 0, 1, 2..
    chunks = chunks if isinstance(chunks, list) else [chunks]
    chunks = [chunk for chunk in chunks if chunk is not None]
    if len(chunks) == 0:
        return None

    total_chunks = sorted(chunks, key=lambda x: x[0])
    task = SlipTask.objects.get(pk=task_id)
    geo_chunk_id = total_chunks[0][2]['geo_chunk_id']
    time_chunk_id = total_chunks[0][2]['time_chunk_id']
    metadata = {}

    combined_data = None
    combined_slip = None
    for index, chunk in enumerate(reversed(total_chunks)):
        metadata.update(chunk[1])
        data = xr.open_dataset(chunk[0], autoclose=True)
        if combined_data is None:
            combined_data = data.drop('slip')
            combined_slip = data.slip.copy(deep=True)
            continue
        #give time an indice to keep mosaicking from breaking.
        data['time'] = [0]
        clear_mask = create_cfmask_clean_mask(data.cf_mask) if 'cf_mask' in data else create_bit_mask(data.pixel_qa,
                                                                                                      [1, 2])
        # modify clean mask so that only slip pixels that are still zero will be used. This will show all the pixels that caused the flag.
        clear_mask[combined_slip.values == 1] = False
        combined_data = create_mosaic(data.drop('slip'), clean_mask=clear_mask, intermediate_product=combined_data)
        combined_slip.values[combined_slip.values == 0] = data.slip.values[combined_slip.values == 0]

    combined_data['slip'] = combined_slip
    path = os.path.join(task.get_temp_path(), "recombined_time_{}.nc".format(geo_chunk_id))
    combined_data.to_netcdf(path)
    logger.info("Done combining time chunks for geo: " + str(geo_chunk_id))
    return path, metadata, {'geo_chunk_id': geo_chunk_id, 'time_chunk_id': time_chunk_id}


@task(name="slip.recombine_geographic_chunks")
def recombine_geographic_chunks(chunks, task_id=None):
    """Recombine processed data over the geographic indices

    For each geographic chunk process spawned by the main task, open the resulting dataset
    and combine it into a single dataset. Combine metadata as well, writing to disk.

    Args:
        chunks: list of the return from the processing_task function - path, metadata, and {chunk ids}

    Returns:
        path to the output product, metadata dict, and a dict containing the geo/time ids
    """
    logger.info("RECOMBINE_GEO")
    total_chunks = [chunks] if not isinstance(chunks, list) else chunks
    total_chunks = [chunk for chunk in total_chunks if chunk is not None]
    geo_chunk_id = total_chunks[0][2]['geo_chunk_id']
    time_chunk_id = total_chunks[0][2]['time_chunk_id']

    metadata = {}
    task = SlipTask.objects.get(pk=task_id)

    chunk_data = []

    for index, chunk in enumerate(total_chunks):
        metadata = task.combine_metadata(metadata, chunk[1])
        chunk_data.append(xr.open_dataset(chunk[0], autoclose=True))

    combined_data = combine_geographic_chunks(chunk_data)

    path = os.path.join(task.get_temp_path(), "recombined_geo_{}.nc".format(time_chunk_id))
    combined_data.to_netcdf(path)
    logger.info("Done combining geographic chunks for time: " + str(time_chunk_id))
    return path, metadata, {'geo_chunk_id': geo_chunk_id, 'time_chunk_id': time_chunk_id}


@task(name="slip.create_output_products")
def create_output_products(data, task_id=None):
    """Create the final output products for this algorithm.

    Open the final dataset and metadata and generate all remaining metadata.
    Convert and write the dataset to variuos formats and register all values in the task model
    Update status and exit.

    Args:
        data: tuple in the format of processing_task function - path, metadata, and {chunk ids}

    """
    logger.info("CREATE_OUTPUT")
    full_metadata = data[1]
    dataset = xr.open_dataset(data[0], autoclose=True)
    task = SlipTask.objects.get(pk=task_id)

    task.result_path = os.path.join(task.get_result_path(), "slip_result.png")
    task.result_mosaic_path = os.path.join(task.get_result_path(), "mosaic.png")
    task.data_path = os.path.join(task.get_result_path(), "data_tif.tif")
    task.data_netcdf_path = os.path.join(task.get_result_path(), "data_netcdf.nc")
    task.final_metadata_from_dataset(dataset)
    task.metadata_from_dict(full_metadata)

    bands = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'cf_mask',
             'slip'] if 'cf_mask' in dataset else ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'pixel_qa', 'slip']

    dataset.to_netcdf(task.data_netcdf_path)
    write_geotiff_from_xr(task.data_path, dataset.astype('int32'), bands=bands)

    write_png_from_xr(task.result_path, mask_mosaic_with_slip(dataset), bands=['red', 'green', 'blue'], scale=(0, 4096))
    write_png_from_xr(task.result_mosaic_path, dataset, bands=['red', 'green', 'blue'], scale=(0, 4096))

    logger.info("All products created.")
    task.update_bounds_from_dataset(dataset)
    task.complete = True
    task.execution_end = datetime.now()
    task.update_status("OK", "All products have been generated. Your result will be loaded on the map.")
    shutil.rmtree(task.get_temp_path())
    return True
