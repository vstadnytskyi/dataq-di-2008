#!/usr/bin/env python3
"""
Simple IOC based on caproto library.
It has
"""
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import caproto
from textwrap import dedent
from pdb import pm

from numpy import random, array, zeros, ndarray, nan, isnan
from time import time,sleep
from pickle import dumps, loads

from circular_buffer_numpy import circular_buffer

class DAQ():

    def __init__(self):
        self.io_push_queue = None
        self.io_pull_queue = None
        self.dt = 0.1
        from caproto.threading.client import Context
        ctx = Context()
        record_name = 'MacProBox'
        self.aio,self.dio = ctx.get_pvs(f'{record_name}:AIO',f'{record_name}:DIO')

    def io_pull(self):
        """
        """
        io_dict = {}
        if self.aio is not None:
            data = self.aio.read().data
            temp = data[0]*0.009155+100
            Vo = data[1]*5/32768
            io_dict["MATH0"] = temp
            io_dict["MATH1"] = 149.06*((Vo/5.06) - 0.1515)/(1-0.00205*temp)

            temp = data[2]*0.009155+100
            Vo = data[3]*5/32768
            io_dict["MATH2"] = temp
            io_dict["MATH3"] = 149.06*((Vo/5.06) - 0.1515)/(1-0.00205*temp)

            temp = data[4]*0.009155+100
            Vo = data[5]*5/32768
            io_dict["MATH4"] = temp
            io_dict["MATH5"] = 149.06*((Vo/5.06) - 0.1515)/(1-0.00205*temp)

            io_dict["MATH6"] = data[6]*0.009155+100
            io_dict["MATH7"] = data[7]*5/32768

        return io_dict

    def io_push(self, io_dict):

        if self.io_push_queue is not None:
            self.io_push_queue.put(io_dict)

    def run(self):
        from time import time, sleep
        self.running = True
        while self.running:
            io_dict = self.io_pull()
            self.io_push(io_dict=io_dict)
            sleep(self.dt)

    def start(self):
        from ubcs_auxiliary.multithreading import new_thread
        new_thread(self.run)


class Server(PVGroup):
    """
    An IOC with three uncoupled read/writable PVs

    Scalar PVs
    ----------
    CPU
    MEMORY
    BATTERY

    Vectors PVs
    -----------

    """

    MATH0 = pvproperty(value=0.0, read_only = True, dtype = float, units = 'C',precision = 2)
    MATH1 = pvproperty(value=0.0, read_only = True, dtype = float, units = '%',precision = 2)
    MATH2 = pvproperty(value=0.0, read_only = True, dtype = float, units = 'C',precision = 2)
    MATH3 = pvproperty(value=0.0, read_only = True, dtype = float, units = '%',precision = 2)
    MATH4 = pvproperty(value=0.0, read_only = True, dtype = float, units = 'C',precision = 2)
    MATH5 = pvproperty(value=0.0, read_only = True, dtype = float, units = '%',precision = 2)
    MATH6 = pvproperty(value=0.0, read_only = True, dtype = float, units = 'C',precision = 2)
    MATH7 = pvproperty(value=0.0, read_only = True, dtype = float, units = '%',precision = 2)

    @MATH0.startup
    async def MATH0(self, instance, async_lib):
        # This method will be called when the server starts up.
        print('* request method called at server startup')
        self.io_pull_queue = async_lib.ThreadsafeQueue()
        self.io_push_queue = async_lib.ThreadsafeQueue()
        daq.io_push_queue = self.io_push_queue

        # Loop and grab items from the response queue one at a time
        while True:
            io_dict = await self.io_push_queue.async_get()
            # Propagate the keypress to the EPICS PV, triggering any monitors
            # along the way
            for key in list(io_dict.keys()):
                if key == 'MATH0':
                    await self.MATH0.write(io_dict[key])
                elif key == 'MATH1':
                    await self.MATH1.write(io_dict[key])
                elif key == 'MATH2':
                    await self.MATH2.write(io_dict[key])
                elif key == 'MATH3':
                    await self.MATH3.write(io_dict[key])
                elif key == 'MATH4':
                    await self.MATH4.write(io_dict[key])
                elif key == 'MATH5':
                    await self.MATH5.write(io_dict[key])
                elif key == 'MATH6':
                    await self.MATH6.write(io_dict[key])
                elif key == 'MATH7':
                    await self.MATH7.write(io_dict[key])



daq = DAQ()
daq.start()

if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='MacProBoxSL:',
        desc=dedent(Server.__doc__))
    ioc = Server(**ioc_options)
    run(ioc.pvdb, **run_options)
