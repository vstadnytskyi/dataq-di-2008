"""
DATAQ USB Bulk driver level code
author: Valentyn Stadnytskyi
June 2018 - July 2020
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

class Driver(object):

    def __init__(self):
        #tested dec 17, 2017
        self.available_ports = []
        self.dev = None

        self.filters = {}
        self.filters['Last Point'] = 0
        self.filters['Average'] = 1
        self.filters['Maximum'] = 2
        self.filters['Minimum'] = 3

    def init(self,idProduct = 0x2008, serial_number = ''):
        """
        initialized the driver by discoving approproate device and connecting to it.
        """
        self.dev = self.discover(idProduct,serial_number)
        self.use_port()

        info("initialization of the driver is complete")

    def get_information(self):
        """
        auxiliary function to retrieve information about the connected USB device (on USB level).
        """
        dev_dict = {}
        epi_dict = {}
        if dev != None:
            dev_dict['DEV:address'] = self.dev.address
            dev_dict['DEV:bDeviceClass'] = self.dev.bDeviceClass
            dev_dict['DEV:bDescriptorType'] = self.dev.bDescriptorType
            dev_dict['DEV:bDeviceProtocol'] = self.dev.bDeviceProtocol
            dev_dict['DEV:bLength'] = self.dev.bLength
            dev_dict['DEV:bMaxPacketSize0'] = self.dev.bMaxPacketSize0
            dev_dict['DEV:bNumConfigurations'] = dev.bNumConfigurations
            dev_dict['DEV:manufacturer'] = self.dev.manufacturer
            dev_dict['DEV:serial_number'] = self.dev.serial_number
            dev_dict['DEV:speed'] = self.dev.speed
            dev_dict['DEV:product'] = self.dev.product

            #endpoint IN description
            epi_dict['EPI:bmAttributes'] = self.epi.bmAttributes
            epi_dict['EPI:wMaxPacketSize'] = self.epi.wMaxPacketSize
            epi_dict['EPI:bSynchAddress'] = self.epi.bSynchAddress
            epi_dict['EPI:bInterval'] = self.epi.bInterval
            epi_dict['EPI:bEndpointAddress'] = self.epi.bEndpointAddress
            epi_dict['EPI:bDescriptorType'] = self.epi.bDescriptorType
            epi_dict['EPI:bInterval'] = self.epi.bInterval
            epi_dict['EPI:bInterval'] = self.epi.bInterval
        return dev_dic,epi_dict

    def get_hardware_information(self):
        """
        auxiliary function to retrieve information about connected instrument.
        """
        dic = {}
        dic[b'Device Manufacturer'] = self.inquire(b'info 0 \r').split(b'info 0 ')[1][1:-2]
        dic[b'Device name'] = self.inquire(b'info 1 \r').split(b'info 1 ')[1][1:-1]
        dic[b'Firmware version'] = self.inquire(b'info 2 \r').split(b'info 2 ')[1][1:-1]
        dic[b'Serial Number'] = self.inquire(b'info 6 \r').split(b'info 6 ')[1][1:-1]
        dic[b'Sample Rate Divisor'] = self.inquire(b'info 9 \r').split(b'info 9 ')[1][1:-1]
        return dic

    def use_port(self):
        """
        configure endpoints for the USB backend.
        """
        import usb.core
        import usb.util

        self.dev.reset()

        # set the active configuration. With no arguments, the first
        # configuration will be the active one
        self.dev.set_configuration()

        # get an endpoint instance
        cfg = self.dev.get_active_configuration()
        intf = cfg[(0,0)]

        self.epo = usb.util.find_descriptor(
                                      intf,
                                      # match the first OUT endpoint
                                      custom_match = \
                                      lambda e: \
                                      usb.util.endpoint_direction(e.bEndpointAddress) == \
                                      usb.util.ENDPOINT_OUT)

        self.epi = usb.util.find_descriptor(
                                      intf,
                                      # match the first IN endpoint
                                      custom_match = \
                                      lambda e: \
                                      usb.util.endpoint_direction(e.bEndpointAddress) == \
                                      usb.util.ENDPOINT_IN)

        assert self.epo is not None
        assert self.epi is not None
        self.epi.wMaxPacketSize = 7200000
        self.epo.wMaxPacketSize = 7200000
        self.epi.bmAttributes = 1
        self.epi.bInterval = 100
        self.usb_buff = int(self.epi.wMaxPacketSize/100)


    def discover(self, idProduct = 0x2008, serial_number = None):
        """the function allows to discover DI-2008 device.

            returns: flag if a device(devices) are found.
            assigns: self.available_ports list entry
                    [0] - COM port namer
                    [1] - serial number
        """
        import usb.core
        flag = False
        dev = usb.core.find(idVendor=0x0683, idProduct=idProduct)
        if dev is None:
            raise ValueError('Device not found')
            flag = False
        else:
            if dev.serial_number[:8] == serial_number:
                flag = True
            else:
                raise ValueError(f'Device with serial number {serial_number} is not found')
                dev = None
        return dev


    """Set and Get persistent_property"""
    # functions for persistent properties if needed

    """Basic serial communication functions"""

    def read(self,N = 0, timeout = 1000):
        if N == 0:
            usb_buff = int(self.usb_buff)
        else:
            usb_buff = int(N)
        from time import sleep
        #tested dec 17, 2017
        string = b""
        try:
            data = self.dev.read(self.epi,usb_buff,timeout)
        except:
            error(traceback.format_exc())
            data = ''

        if len(data) != 0:
            for i in data:
                string += bytes([i])
        return string

    def readall(self):
        return self.read(self.usb_buff)

    def write(self,command):
        try:
            self.dev.write(self.epo,command)
        except:
            error(traceback.format_exc())

    def inquire(self,command):
        self.write(command)
        res = self.read(self.usb_buff)
        return res

    def config_digital(self, number = 127, echo = False):
        #tested dec 17, 2017
        string = 'endo ' + str(number)+'\r'
        flag = False
        self.write(string)
        a = self.readall()
        info('%r' % a)
        if echo == True:
            if a == 'endo ' + str(number)+'\r':
                flag = True
            else:
                flag = False
        else:
            flag = None
        return flag

    def set_digital(self, number = 127, echo = False):
        #tested dec 17, 2017
        string = 'dout ' + str(number)
        flag = False
        self.write(string)
        if echo == True:
            a = self.readall()
            debug('%r' % a)
            if a == 'dout ' + str(number):
                flag = True
            else:
                flag = False
        else:
            flag = None
        return flag

    def set_analog(self, channel_list, echo = False):
        """
        example:
        channel_list = ['T-thrmc','5','T-thrmc','5','T-thrmc','5','T-thrmc','5','digital']
        """
        import traceback
        flag = False
        cmd_string = ''
        cmd_resp = b''
        i = 0
        for item in channel_list:
            strngs = self.config_analog_channels(item,i)
            command = 'slist '+str(i)+' '+str(strngs)
            cmd_string += command+'\r'
            cmd_resp += self.inquire(command)
            i+=1
        cmd_string+='\x00'
        if cmd_resp == bytes(cmd_string, encoding = 'Latin-1'):
            flag = True
        if echo:
            print(cmd_resp)
            print(cmd_string)
        return flag

    def config_analog_channels(self,setting, channel):
        """
        takes a string input that specifies range
        """
        _config_dict_gain = {}
        _config_dict_gain['0.010'] = '00101'
        _config_dict_gain['0.025'] = '00100'
        _config_dict_gain['0.05'] = '00011'
        _config_dict_gain['0.1'] = '00010'
        _config_dict_gain['0.25'] = '00001' #works
        _config_dict_gain['0.5'] = '00000'
        _config_dict_gain['1'] = '01101'
        _config_dict_gain['2.5'] = '01100'
        _config_dict_gain['5'] = '01011' #
        _config_dict_gain['10'] = '01010'
        _config_dict_gain['25'] = '01001'
        _config_dict_gain['50'] = '01000'
        _config_dict_gain['B-thrmc'] = b'10000'
        _config_dict_gain['E-thrmc'] = b'10001'
        _config_dict_gain['J-thrmc'] = b'10010'
        _config_dict_gain['K-thrmc'] = b'10011'
        _config_dict_gain['N-thrmc'] = '10100'
        _config_dict_gain['R-thrmc'] = '10101'
        _config_dict_gain['S-thrmc'] = '10110'
        _config_dict_gain['T-thrmc'] = '10111'
        _config_dict_gain['digital'] = '00000'

        config_byte = str(int('000' + _config_dict_gain[setting] + '0000' + bin(channel)[2:].zfill(4),2))
        return config_byte

    def set_filter(self,filter = 'Average'):
        """
        self.filters['Last Point'] = 0
        self.filters['Average'] = 1
        self.filters['Maximum'] = 2
        self.filters['Minimum'] = 3
        """
        num = self.filters[filter]
        self.write('filter * '+str(num)+'\r')
        a = self.readall()
        b = self.readall()
        #print('%r' % (a + b))
        if echo == True:
            if (a+b) == 'filter * 0'+str(num)+'\r':
                flag = True
        else:
            flag = True

    def set_packet_size(self,size = 128):
        dic = {}
        dic[16] = 'ps 0'
        dic[32] = 'ps 1'
        dic[64] = 'ps 2'
        dic[128] = 'ps 3'
        self.inquire(dic[size])

    def set_sampling_rate(self, rate = 200, baserate = 200, dec = 0, echo = True):
        """
        Integer ranges for both variable are:
        4 ≤ srate ≤ 2232
        1 ≤ dec ≤ 32767
        The formula to calculate sample throughput rate differs by the number of enabled channels. For a single enabled analog channel:
        Sample rate throughput (Hz) = 8,000 ÷ (srate × dec)
        resulting in a sample throughput range of 2000 Hz at its fastest, and 0.000109 Hz, or 1 sample every 9141.99 seconds.
        The formula changes when two or more analog channels are enabled:
        Sample rate throughput (Hz) = 800 ÷ (srate × dec)
        resulting in a sample throughput range of 200 Hz at its fastest, and 0.000011 Hz, or 1 sample every 91419.93 seconds.
        """
        if dec == 0:
            dec = int(baserate/rate)

        flag = None
        string = 'srate ' + str(int(800/baserate))
        #self.ser.write('srate 6000000\r') # Supposedly sets it to read at 50kHz, Hz=60000000/srate
        a = self.inquire(string)
        string = 'dec ' + str(dec)
        b = self.inquire(string)

        #print('%r,%r' % (a,b))
        if echo == True:
            if a+b == 'srate '+str(int(800/baserate))+'\r\x00'+'dec '+ str(dec)+ '\r\x00':
                flag = True
        else:
            flag = True
        self.dec = dec
        self.sampling_rate = rate
        return flag

    def start_scan(self):
        info('The configured measurement(s) has(have) started')
        self.write('start 0\r')
        info("measurement ended")

    def stop_scan(self):
        self.write('stop\r')
        info("measurement ended")


    """Advance function"""
    def config_channels(self, rate = 200, conf_digital = 127, set_digital = 127, dec = 1, baserate = 200):
        x = self.config_digital(conf_digital, echo = True)
        a = self.set_digital(set_digital, echo = True)
        b = self.set_analog(echo = True)
        c = self.set_acquisition_rate(rate = rate, dec = dec, baserate = baserate, echo = True) #3000 gives maximum rate
        return x*a*b*c

    def get_readings(self, points_to_read = 64, to_read_analog = 8, to_read_digital = 1):
        from struct import pack, unpack
        to_read = int(to_read_analog)*2+int(to_read_digital)*2
        result = self.read(to_read*points_to_read)
        if b'stop' in result:
            flag = False
        else:
            flag = True
        try:

            data = asarray(unpack(('h'*to_read_analog+'BB')*points_to_read,result))
        except:
            error(traceback.format_exc())
            data = None



            #analog_data = asarray(unpack('h'*to_read_analog,res[0:to_read_analog*2])) #this will be
        #first N bytes (where N/2 is number of analog channels to read
        #see https://docs.python.org/2/library/struct.html for 'h' description
            #digital_data = array(unpack('B',res[-1:])[0])
        #This how we can format the integer to binary string ---->> bin(unpack('B',res[-1])[0])[2:].zfill(7).split()
        #this will unpack the very last byte as binary and make sure to
        #keep the leading zero. The very first zero 'D7' byte count 18 (see manual) is ommited.
        #will be shown as a string. We need to convert it to a numpy array for easier usage
        try:
            res = transpose(asarray(split(data,points_to_read)))
        except:
            error(traceback.format_exc())
            res = None
        return res, flag #(analog_data,digital_data)

    def blink(self):
        from time import sleep
        for i in range(8):
            self.inquire('led ' + str(i) + ' \r')
            sleep(1)
        self.inquire('led ' + str(7) + ' \r')


    """Test functions"""
    def self_test(self):
        self.inquire('led 7\r')
        self.tau = 0.001
        #dictionary with device parameters such as S\N, device name, ect
        self.dict = {}
        self.dict['Device name'] = self.inquire('info 1 \r').split('info 1 ')[1][1:-1]
        self.dict['Firmware version'] = self.inquire('info 2 \r').split('info 2 ')[1][1:-1]
        self.dict['Serial Number'] = self.inquire('info 6 \r').split('info 6 ')[1][1:-1]
        self.dict['Sample Rate Divisor'] = self.inquire('info 9 \r').split('info 9 ')[1][1:-1]
        #Useful variables
        #wait time after write (before) read. This seems to be not necessary.
        for i in self.dict.keys():
            print('%r, %r' % (i, self.dict[i]))
        print('information request complete: the DI-4108 with SN %r' %self.dict['Serial Number'])
        print('%r' % self.inquire('led 2\r'))

    def test1(self):
        self.self_test()
        self.config_channels()

        self.start_scan()
        while self._waiting()[0] <1:
            sleep(0.001)
        start_t = time()
        while time()-start_t<2:
            print("%0.5f %r %r" % (time()-start_t,self._waiting()[0],self.get_readings()))
        self.stop_scan()
        print('test 1 is Done. IN buffer has all data')
        print('data = dev.get_readings()')
        print('buffer waiting %r' % self._waiting()[0])

    def test2(self):
        self.self_test()
        self.config_channels()
        self.start_scan()
        sleep(6)
        self.stop_scan()
        sleep(1)
        while self._waiting()[0]>5:
            print('time %r and value %r'% (time(),self.get_readings()))
        print('test 2 is Done')

    def test3(self):
        self.self_test()
        self.config_channels()
        self.start_scan()
        sleep(6)
        self.stop_scan()
        print(self.waiting())
        sleep(1)
        while self.waiting()[0]>5:
            print(self.waiting()[0])
            print(self.get_readings())
        print('test 2 is Done')


    def echo_test1(self):
        self.config_channels()
        self.start_scan()
        while self.waiting()[0] <1:
            sleep(0.001)
        start_t = time()
        while time()- start_t <1:
            self.write('dout 0\r')
            self.write('dout 127 \r')
            sleep(0.06)
        self.stop_scan()
        print("%r" % self._waiting()[0])
        data = self.readall()
        print('%r' % data)

    def performance_test1(self):
        self.self_test()
        self.config_channels()

        self.start_scan()
        while self.waiting()[0] <10000:
            sleep(0.001)
        start_t = time()
        self.stop_scan()

        print('test 1 is Done. IN buffer has all data')
        print('data = dev.get_readings(10)')
        print('buffer waiting %r' % self._waiting()[0])
        print('t = Timer(lambda: dev.get_readings(N))')
        print('print t.timeit(number = M)')

    def performance_test2(self):
        self.self_test()
        self.config_channels()

        self.start_scan()
        start_t = time()
        self.lst = []
        time_st = time()
        while time()-start_t<10:
            if self._waiting()[0]> 512*16:
                data = self.get_readings(512)
                self.lst.append([time()-start_t,self._waiting()[0],(time() - time_st)*1000])
                print("%r %0.10f" % (self._waiting()[0], (time() - time_st)*1000))
            sleep(24/1000) #wait for 12.8 ms
        start_t = time()
        self.stop_scan()
        print('time between 4 kS = %0.5f' % mean(10.0/len(self.lst)))
        print('Sampling rate: %0.1f' % (512/mean(10.0/len(self.lst))))
        print('test 1 is Done. IN buffer has all data')
        print('data = dev.get_readings(10)')
        print('buffer waiting %r' % self._waiting()[0])
        print('t = Timer(lambda: dev.get_readings(N))')
        print('print t.timeit(number = M)')

if __name__ == "__main__": #for testing
    import logging
    from tempfile import gettempdir
    self = driver


    logging.basicConfig(#filename=gettempdir()+'/DI_USB_BULK_LL.log',
                        level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")
    print('self.self_test()')
    print('self.test1()')
    print('self.test2()')
    print('self.echo_test1()')
    print('self.performance_test1()')
    print('self.performance_test2()')
