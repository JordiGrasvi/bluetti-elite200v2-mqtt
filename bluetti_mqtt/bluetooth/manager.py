import asyncio
import logging
from typing import Dict, List
from bleak import BleakScanner
from bluetti_mqtt.core import DeviceCommand
from .client import BluetoothClient
from .encryption import is_device_using_encryption


class MultiDeviceManager:
    clients: Dict[str, BluetoothClient]

    def __init__(self, addresses: List[str]):
        self.addresses = addresses
        self.clients = {}

    async def run(self):
        logging.info(f'Connecting to clients: {self.addresses}')

        # Perform a blocking scan just to speed up initial connect
        # We also need some info from the advertisement data
        devices = await BleakScanner.discover(return_adv=True)

        # Start client loops
        self.clients = {}
        for address in self.addresses:
            if (scan_record := devices.get(address)) is not None:
                encryped = is_device_using_encryption(scan_record[1].manufacturer_data)
                self.clients[address] = BluetoothClient(address, encryped)
            else:
                logging.warning(f"Address {address} not found in scan data")

        await asyncio.gather(*[c.run() for c in self.clients.values()])

    def is_ready(self, address: str):
        if address in self.clients:
            return self.clients[address].is_ready
        else:
            return False

    def get_name(self, address: str):
        if address in self.clients:
            return self.clients[address].name
        else:
            raise Exception('Unknown address')

    async def perform(self, address: str, command: DeviceCommand):
        if address in self.clients:
            return await self.clients[address].perform(command)
        else:
            raise Exception('Unknown address')

    async def perform_nowait(self, address: str, command: DeviceCommand):
        if address in self.clients:
            await self.clients[address].perform_nowait(command)
        else:
            raise Exception('Unknown address')
