import time
from xml.etree import ElementTree

import requests

from core.abstract.input import ExternalDataSource, EnergyData, Device


# Todo: Review, this is base only
class DataLogger(ExternalDataSource):
    """
    Eumel DataLogger api access implementation
    """

    def __init__(self, ip, user, password):
        """
        :param ip: Data loggers network IP
        :param user:
        :param password:
        """
        self.eumel_api_url = ip + '/rest'
        self.auth = (user, password)

    def read_state(self) -> EnergyData:
        # To read from Comment line 42 and uncomment 43
        # tree = ElementTree.parse('test_examples/EumelXMLOutput.xml')
        http_packet = requests.get(self.eumel_api_url, auth=self.auth)
        raw = http_packet.content
        tree = ElementTree.parse(raw)
        tree_root = tree.getroot()
        tree_header = tree_root[0].attrib
        tree_leaves = {child.attrib['id']: child.text for child in tree_root[0][0]}
        device = Device(
            manufacturer=tree_header['man'],
            model=tree_header['mod'],
            serial_number=tree_header['sn'])
        access_timestamp = int(time.time())
        time_format = '%Y-%m-%dT%H:%M:%SZ'
        accumulated_power = int(tree_leaves['TotWhImp'].replace('.', ''))
        measurement_timestamp = int(time.mktime(time.strptime(tree_header['t'], time_format)))
        return EnergyData(device, access_timestamp, raw, accumulated_power, measurement_timestamp)