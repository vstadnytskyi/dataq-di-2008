"""
DATAQ USB Bulk device level code
author: Valentyn Stadnytskyi
June 2018 - June 2018

1.0.0 - designed for usb Bulk protocol.
1.0.1 - dec is added to the communication

"""

from numpy import nan, mean, std, asarray, array, concatenate, delete, round, vstack, hstack, zeros, transpose, split
from time import time, sleep, clock
import sys
import os.path
import struct
from pdb import pm
from time import gmtime, strftime
import logging
from struct import pack, unpack
from timeit import Timer
from logging import info,warn, debug, error
import traceback
__version__ = '1.0.1'

class Device(object):

    def __init__(self):
        self.io_push_queue = None

    def init(self):
        """
        initializes device level. takes configuration dictionary supplied by configuration file saved in yaml format.
        """
        info("initialization of the device is complete")

        from circular_buffer_numpy.circular_buffer import CircularBuffer
        self.buffer = CircularBuffer(shape = (10000,10), dtype = 'int16')

        from dataq_di_2008 import Driver
        driver = Driver()
        config = self.config
        driver.init(idProduct = config['PID'],serial_number = config['serial number'])
        driver.stop_scan()
        driver.set_sampling_rate(config['sample rate'])
        driver.set_analog(channel_list = config['channel config'])
        driver.config_digital(number = config['digital config'])
        driver.set_packet_size(size = config['packet size'])
        self.network_name = config['network name']
        self.driver = driver
        # self.driver.stop_scan()
        # self.driver.start_scan()


    def close(self):
        """
        ordely stop of all operations
        """
        pass

    def kill(self):
        """
        orderly exit and shutdown of the device
        """
        pass

    def start(self):
        from ubcs_auxiliary.multithreading import new_thread
        new_thread(self.run)

    def stop(self):
        self.running = False


    def run(self):
        self.running = True
        while self.running:
            self.run_once()

    def run_once(self):
        from numpy import mean
        data,flag = self.get_readings(points_to_read=64)
        self.buffer.append(data)
        io_dict = {}
        io_dict['DIO'] = data[-1,-1]
        io_dict['AIO'] = list(mean(data[:,:-2],axis=0))
        for i in range(8):
            io_dict[f'CH{i}'] = mean(data[:,i])
        self.io_push(io_dict = io_dict)

    def get_readings(self, points_to_read = 1, to_read_analog = 8, to_read_digital = 1):
        to_read = int(to_read_analog+to_read_digital)*2
        result = self.driver.read(to_read*points_to_read, timeout = 4000)
        if b'stop' in result:
            flag = False
        else:
            flag = True
        try:
            data = asarray(unpack(('h'*to_read_analog+'BB')*points_to_read,result))
        except:
            error(traceback.format_exc())
            data = None
        try:
            res = asarray(split(data,points_to_read))
        except:
            error(traceback.format_exc())
            res = None
        return res, flag #(analog_data,digital_data)


    def io_push(self, io_dict):
        if self.io_push_queue is not None:
            self.io_push_queue.put(io_dict)

    """Test functions"""

from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import caproto
from textwrap import dedent

class Server(PVGroup):
    """
    An IOC with three uncoupled read/writable PVs

    Scalar PVs
    ----------

    Vectors PVs
    -----------
    AIO
    DIO

    """

    AIO = pvproperty(value=[0.0]*8)
    DIO = pvproperty(value=0, units = 'counts')

    CH0 = pvproperty(value=0, units = 'counts')
    CH1 = pvproperty(value=0, units = 'counts')
    CH2 = pvproperty(value=0, units = 'counts')
    CH3 = pvproperty(value=0, units = 'counts')
    CH4 = pvproperty(value=0, units = 'counts')
    CH5 = pvproperty(value=0, units = 'counts')
    CH6 = pvproperty(value=0, units = 'counts')
    CH7 = pvproperty(value=0, units = 'counts')


    @AIO.startup
    async def AIO(self, instance, async_lib):
        # This method will be called when the server starts up.
        self.io_pull_queue = async_lib.ThreadsafeQueue()
        self.io_push_queue = async_lib.ThreadsafeQueue()
        device.io_push_queue = self.io_push_queue

        # Loop and grab items from the response queue one at a time
        while True:
            io_dict = await self.io_push_queue.async_get()
            # Propagate the keypress to the EPICS PV, triggering any monitors
            # along the way
            for key in list(io_dict.keys()):
                if key == 'AIO':
                    await self.AIO.write(io_dict[key])
                elif key == 'DIO':
                    await self.DIO.write(io_dict[key])
                elif key == 'CH0':
                    await self.CH0.write(io_dict[key])
                elif key == 'CH1':
                    await self.CH1.write(io_dict[key])
                elif key == 'CH2':
                    await self.CH2.write(io_dict[key])
                elif key == 'CH3':
                    await self.CH3.write(io_dict[key])
                elif key == 'CH4':
                    await self.CH4.write(io_dict[key])
                elif key == 'CH5':
                    await self.CH5.write(io_dict[key])
                elif key == 'CH6':
                    await self.CH6.write(io_dict[key])
                elif key == 'CH7':
                    await self.CH7.write(io_dict[key])

def read_config_file(filename):
    import yaml
    import os
    flag =  os.path.isfile(filename)
    if flag:
        with open(filename,'r') as handle:
            config = yaml.safe_load(handle.read())  # (2)
    else:
        config = {}
    return config, flag


if __name__ == "__main__": #for testing
    import logging
    from tempfile import gettempdir
    config, flag = read_config_file('/tmp/config_template.conf')

    device = Device()
    device.config = config
    device.init()
    device.driver.stop_scan()
    print(device.driver.read(1000))
    print(device.driver.read(1000))
    device.driver.start_scan()
    device.start()


    logging.basicConfig(#filename=gettempdir()+'/DI_USB_BULK_DL.log',
                        level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")
    ioc_options, run_options = ioc_arg_parser(
        default_prefix=f"{config['network name']}:",
        desc=dedent(Server.__doc__))
    ioc = Server(**ioc_options)
    run(ioc.pvdb, **run_options)
