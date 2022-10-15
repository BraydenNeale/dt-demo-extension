import logging
import json
from enum import Enum
import requests
from ruxit.api.base_plugin import BasePlugin
from ruxit.api.exceptions import ConfigException,NothingToReportException,AuthException

logger = logging.getLogger(__name__)

EXTENSION_NAME = 'custom.extension.demo.file.stats'
METRIC_PREFIX = 'demo.file.stats'

class State(Enum):
    GOOD = 1
    OTHER = 0

    @staticmethod
    def from_str(status_str: str):
        if status_str.lower() in ['active', 'alive']:
            return State.GOOD
        else: 
            return State.OTHER

class FileStatsDemo(BasePlugin):
    def initialize(self, **kwargs):
        config = kwargs.get('config')
        debug_logging = config.get('debug')

        if debug_logging:
            logger.setLevel(logging.DEBUG)

        self.FILE_NAME = config.get('file_name')
        self.PASSWORD = config.get('example_password')
        self.GROUP = config.get('group')
        self.METRIC_URL = config.get('dynatrace_tenant', 'http://localhost:14499')
        self.DYNATRACE_TOKEN = config.get('dynatrace_token')

        self._validate_config()

    def query(self, **kwargs):
        metric_count = 0
        try:
            with open(self.FILE_NAME, 'r') as fp:
                metrics = self._get_server_metrics(fp)
                post_mint_metric('\n'.join(metrics), self.METRIC_URL, self.DYNATRACE_TOKEN)
                metric_count += len(metrics)
        except OSError as e:
            message = f'Could not open file, check path and permissions: {self.FILE_NAME} - {e}'
            logger.error(message)
            raise ConfigException(message)
        except Exception as e:
            message = f'Exception during query: {e.__class__.__name__} - {e}'
            logger.error(message)
            raise(e)

        if metric_count == 0:
            raise NothingToReportException('No metrics were returned')

    def _validate_config(self):
        logger.debug(f'CONFIG: file_name={self.FILE_NAME}, group={self.GROUP}')
        if not self.FILE_NAME:
            raise ConfigException('File name path is required')

        # if not self.password:
        #     raise AuthException('Password required')

    def _get_server_metrics(self, fp):
        metrics = []

        json_data = json.load(fp)
        server_id = json_data.get('serverId')
        dimensions = {'server.id': server_id, 'group': self.GROUP}

        # Server
        server_metrics = {}
        server_metrics['cpu'] = json_data.get('cpu')
        server_metrics['temperature'] = json_data.get('temperature')
        
        total_memory = int(json_data.get('totalMem', 0))
        used_memory = int(json_data.get('memUsed', 0))
        server_metrics['memory'] = calculate_space_percent(total_memory, used_memory)

        for key,val in server_metrics.items():
            # e.g. demo.file.stats.cpu,server.id="hostname1",group="test" 45
            metric_key = f'{METRIC_PREFIX}.{key}'
            metrics.append(build_mint_metric(metric_key, dimensions, val))

        # Disk
        prefix = 'disk'
        for disk in json_data.get('disks', []):
            disk_dimensions = {**dimensions, 'disk.drive': disk.get('drive')}
            total_space = int(disk.get('totalDisk', 0))
            used_space= int(disk.get('DiskUsed', 0))

            # demo.file.stats.disk.used,server.id="hostname1",group="test",disk.drive="C" 85.0
            disk_space_key = f'{METRIC_PREFIX}.{prefix}.used'
            metrics.append(build_mint_metric(disk_space_key, disk_dimensions, calculate_space_percent(total_space, used_space)))

        # Processes
        prefix = 'process'
        for process in json_data.get('processes', []):
            process_status = process.get('status', '').lower()
            process_dimensions = {**dimensions, 'process.name': process.get('name'), 'process.status': process_status}

            # demo.file.stats.process.status server.id="hostname1",group="group",process.name="gateway,status="active" 1
            status_key = f'{METRIC_PREFIX}.{prefix}.status'
            metric_val = State.from_str(process_status).value
            metrics.append(build_mint_metric(status_key, process_dimensions, metric_val))

        return metrics

def calculate_space_percent(total, used):
    value = 0

    if total > 0:
        value = (used / total) * 100

    return value

def build_mint_metric(metric_key, dimensions, value, timestamp=''):
    # metric.key,dimensions payload
    # my.custom.metric,team="teamA",businessapp="hr" 1000 
    dimension_list = []
    for k,v in dimensions.items():
        dimension_list.append(f'{k}="{v}"')
    
    dimension_str = ','.join(dimension_list)
    metric_str = f'{metric_key},{dimension_str} {value} {timestamp}'.strip()
    return metric_str

def post_mint_metric(payload, url, token=None):
    ingest = '/metrics/ingest'
    request_url = f'{url}{ingest}'
    headers = { 
		'Accept': 'application/json', 
		'Content-type': 'text/plain',
	}

    if token:
        headers['Authorization'] = f'Api-Token {token}'

    logger.info(payload)
    response = requests.post(request_url, payload, headers=headers)
    response.raise_for_status()