import ctypes
import time
from utils import Config
import os
import argparse
from random import gauss
import glob

# load pickle module
import pickle

class vista_chix(ctypes.Structure):
    _fields_ = [("chix", ctypes.c_ushort),
                  ("dbix", ctypes.c_ushort)]


class ControlSystem:
    def handle_error(self, error, chix):
        if error != 1:
            err_msg = ctypes.create_string_buffer(128)
            error = self.vsystem.vdbc_error_message(ctypes.byref(chix), err_msg, 128)
            raise RuntimeError(err_msg.value)

    def __init__(self, channels = [], elements = []):
        # TODO types indicated in config
        self.config = Config.load_json('/home/jmartinezmarin/repositories/pyControlSystem/pyControlSystem/config.json')
        self.vsystem = ctypes.cdll.LoadLibrary(self.config.vsystem)
        self.vdb_types = Config.load_json(self.config["vdb_types"])
        self.vdb_elements = Config.load_json(self.config["vdb_elements"])
        folder = self.config["folder"]

        if os.path.isdir(folder):
            if self.config["new"]:
                folders = glob.glob(os.path.join(folder, '*'))
                n = len(folders)
                folder = os.path.join(folder, n)
                os.makedirs(folder)
        else:
            os.makedirs(folder)

        self.folder = folder

        self.fcups = Config.load_json(self.config["fcups"])['BEAMLINE']

        self.ch_names = self.config.channels  + channels + self._elements2channels(elements) + self._elements2channels(self.fcups)

        print(self.ch_names)

        self.chixs = {ch_name: vista_chix() for ch_name in self.ch_names}
        for name in self.ch_names:
            error = self.vsystem.vdbc_channel_index(ctypes.c_char_p(bytes(name, 'ascii')), ctypes.byref(self.chixs[name]))
            print(error, self.chixs[name].chix)
            #self.handle_error(error, self.chixs[i])

        print(self.chixs)
        self.start_time = time.time()
        self.rates = []
        self.times = []

    def _elements2channels(self, elements):
        channels = []
        for element in elements:
            element_type = self.vdb_elements[element]['type']
            element_db = self.vdb_elements[element]['db']
            if element_type == 'fcup':
                fcup_channels = [f"BEAM_MEAS_VDB::{element}:SELECT_METER",
                f"BEAM_MEAS_VDB::{element}:DISPLAY_METER",
                f"{element_db}::{element}:FCOUT_DISPLAY",
                f"{element_db}::{element}:FCIN_DISPLAY",
                f"{element_db}::{element}:SELECT"]
                for fcup_channel in fcup_channels:
                    channels.append(fcup_channel)
            elif element_type == 'bpm':
                bpm_channels = [f"{element_db}::{element}:SELECT"]
                for bpm_channel in bpm_channels:
                    channels.append(bpm_channel)
            elif element_type == 'setting':
                monitor = element.replace('CONTROL', 'MONITOR')
                setting_channels = [f"{element_db}::{element}", f"{element_db}::{monitor}"]
                for setting_channel in setting_channels:
                    channels.append(setting_channel)
        return channels
    
    def _element2channel(self, element, action=''):
        element_db = self.vdb_elements[element]['db']
        if len(action)>0:
            return f"{element_db}::{element}:{action}" 
        else: 
            return f"{element_db}::{element}"
        
    def _ch_val(self, element):
        vdb_type = self.vdb_types[self.vdb_elements[element]['type']]
        ch_val = None
        if vdb_type == 'float':
            ch_val = ctypes.c_float()
        elif vdb_type == 'double':
            ch_val = ctypes.c_double()
        return ch_val

    def read_element(self, element):
        vdb_type = self.vdb_types[self.vdb_elements[element]['type']]
        ch_val = self._ch_val(element)
        ch_name = self._element2channel(element)
        print('channel_name: ', ch_name)
        if vdb_type == 'float':
            error = self.vsystem.vdb_rget(ctypes.byref(self.chixs[ch_name]), ctypes.byref(ch_val))
        elif vdb_type == 'double':
            error = self.vsystem.vdb_dget(ctypes.byref(self.chixs[ch_name]), ctypes.byref(ch_val))
        else:
            error = None
        #self.handle_error(error, self.chixs[ch_name])
        print(error, 'error', ch_name)
        print(ch_name, ch_val.value)
        return ch_val

    # TODO
    def read_channel(self, ch_name):
        #ch_val = ctypes.c_float()
        ch_val = ctypes.c_double()
        #d->r
        error = self.vsystem.vdb_dget(ctypes.byref(self.chixs[ch_name]), ctypes.byref(ch_val))
        #self.handle_error(error, self.chixs[ch_name])
        print(error, 'error', ch_name)
        print(ch_name, ch_val.value)
        self.times.append(time.time())
        return ch_val

    def read_monitor(self, bpm, name=''):
        ch_name = self._element2channel(bpm, 'SELECT')
        ch_val = ctypes.c_bool() 
        error = self.vsystem.vdb_internal_bget(ctypes.byref(self.chixs[ch_name]), ctypes.byref(ch_val))
        if bool(ch_val) == False:
            print('selecting...', ch_name)
            error = self.vsystem.vdb_btoggle(ctypes.byref(self.chixs[ch_name]))
            print(error, ch_name)
        ch_val = ctypes.c_int(-10000)
        error = self.vsystem.vdb_iput(ctypes.byref(self.chixs['BEAM_DIGITIZE_VDB::T4020:BPM_AVERAGED']), ctypes.byref(ch_val))
        print(error, 'BEAM_DIGITIZE_VDB::T4020:BPM_STATUS')
        os.system(f"db_capture -snap -dir=./{self.folder}/*.snp -file=snap_{bpm}_{name}.snp BEAM_DIGITIZE_VDB::T4020:BPM_AVERAGED")
        os.system(f"db_capture -snap -dir=./{self.folder}/*.snp -file=snap_{bpm}_{name}_fd.snp BEAM_DIGITIZE_VDB::T4020:BPM_FIDUCIAL")
        return self.folder
    
    def select_fcup_meter(self, fcup_name):
        ch_name = f"BEAM_MEAS_VDB::{fcup_name}:DISPLAY_METER"
        ch_val = ctypes.c_bool() 
        error = self.vsystem.vdb_internal_bget(ctypes.byref(self.chixs[ch_name]), ctypes.byref(ch_val))
        print(ch_name, ch_val, error)
        if bool(ch_val) == False:
            print('selecting fcup meter...')
            ch_name = f"BEAM_MEAS_VDB::{fcup_name}:SELECT_METER"
            error = self.vsystem.vdb_btoggle(ctypes.byref(self.chixs[ch_name]))
            print(error, ch_name)
            ch_val = ctypes.c_bool() 
            error = self.vsystem.vdb_internal_bget(ctypes.byref(self.chixs[ch_name]), ctypes.byref(ch_val))
            print(ch_name, ch_val, error)
        
        if bool(ch_val) == False:
            print(f'{fcup_name} not selected')

    def check_status_fcup(self, fcup_name):
        ch_name = f"FC_VDB::{fcup_name}:FCOUT_DISPLAY"
        ch_val_out = ctypes.c_bool() 
        error = self.vsystem.vdb_internal_bget(ctypes.byref(self.chixs[ch_name]), ctypes.byref(ch_val_out))
        print(ch_name, ch_val_out, error)
        ch_name = f"FC_VDB::{fcup_name}:FCIN_DISPLAY"
        ch_val_in = ctypes.c_bool() 
        error = self.vsystem.vdb_internal_bget(ctypes.byref(self.chixs[ch_name]), ctypes.byref(ch_val_in))
        print(ch_name, ch_val_in, error)
        #print(bool(ch_val_out), bool(ch_val_in), '|', not bool(ch_val_out), not bool(ch_val_in))
        if ((bool(ch_val_out) & bool(ch_val_in)) | ((not bool(ch_val_out)) & (not bool(ch_val_in)))):
            print(f'{fcup_name} in and out ?')
            return None
        elif ~bool(ch_val_out) & bool(ch_val_in):
            print(f'{fcup_name} in')
            return 'IN'
        else:
            print(f'{fcup_name} out')
            return 'OUT'
        
    def insert_fcup(self, fcup_name):
        self.select_fcup_meter(fcup_name)
        fcup_status = self.check_status_fcup(fcup_name)
        
        if fcup_status == 'OUT':
            ch_name = f"FC_VDB::{fcup_name}:SELECT"
            error = self.vsystem.vdb_btoggle(ctypes.byref(self.chixs[ch_name]))
            print(error, ch_name)
            fcup_status = self.check_status_fcup(fcup_name)
            for i in range(10):
                if fcup_status == 'IN':
                    print(f"{fcup_name} inserted")
                    break
                else:
                    print('waiting...')
                    time.sleep(0.5)
                    fcup_status = self.check_status_fcup(fcup_name)
    
    def remove_fcup(self, fcup_name):
        self.select_fcup_meter(fcup_name)
        fcup_status = self.check_status_fcup(fcup_name)
        
        if fcup_status == 'IN':
            ch_name = f"FC_VDB::{fcup_name}:SELECT"
            error = self.vsystem.vdb_btoggle(ctypes.byref(self.chixs[ch_name]))
            print(error, ch_name)
            fcup_status = self.check_status_fcup(fcup_name)
            for i in range(10):
                if fcup_status == 'OUT':
                    print(f"{fcup_name} removed")
                    break
                else:
                    print('waiting...')
                    time.sleep(0.5)
                    fcup_status = self.check_status_fcup(fcup_name)
        
    def read_current(self, fcup_name):   
        fcups = self.fcups[:self.fcups.index(fcup_name)]
        for fcup in fcups:
            self.remove_fcup(fcup)
        self.select_fcup_meter(fcup_name)
        fcup_status = self.check_status_fcup(fcup_name)
        print(fcup_status)
        if fcup_status == 'OUT':
            self.insert_fcup(fcup_name)
            fcup_status = self.check_status_fcup(fcup_name)
            print(fcup_status)

        current_values = []
        if fcup_status == 'IN':
            ch_name = f"KEITHLEY_VDB::READ:MONITOR" 
            for i in range(5):
                ch_val = ctypes.c_double() 
                error = self.vsystem.vdb_dget(ctypes.byref(self.chixs[ch_name]), ctypes.byref(ch_val))
                print(ch_name, ch_val, error)
                time.sleep(0.5)
                current_values.append(ch_val)
                error = self.vsystem.vdb_dget(ctypes.byref(self.chixs[ch_name]), ctypes.byref(ch_val))
                print(ch_name, ch_val, error)
            #external_value = ch_val
            #error = self.vsystem.vdb_internal_dget(ctypes.byref(self.chixs[ch_name]), ctypes.byref(ch_val))
            #print('internal', ch_name, ch_val, error)
            #internal_value = ch_val
            #time.sleep(0.5)
        return current_values

    def write_element(self, element, value):
        vdb_type = self.vdb_types[self.vdb_elements[element]['type']]
        if vdb_type == 'float':
            ch_name = self._element2channel(element)
            ch_val = ctypes.c_float(value)

            error = self.vsystem.vdb_rput(ctypes.byref(self.chixs[ch_name]), ctypes.byref(ch_val))
            #self.handle_error(error, self.chixs[i])
            print(error, 'error')
            print(ch_name, ch_val.value)
        else:
            print('type not supported yet')



if __name__ == "__main__":

    '''parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('-c', '--channels', help='channels list', nargs='*', default=[])
    #parser.add_argument('foo-bar', help='Hyphens are cumbersome in positional arguments')

    args = parser.parse_args()

    channels = args.channels#.replace(" ", "")[1:-1].split(',')'''

    
    test = ControlSystem(elements=['QDP301:CONTROL_Y', 'QDP301:MONITOR_Y', 'PMP301'])
    print('start reading...')
    value = test.read_element('QDP301:CONTROL_Y')
    

    print(value)

    value = test.read_element('QDP301:MONITOR_Y')
    

    print(value)

    print('reading_fcup')

    print(test.ch_names)
    values = test.read_current('FCP301')

    print(values)


    test.read_monitor('PMP301', name='test')
  