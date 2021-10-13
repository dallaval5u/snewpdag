"""
test_TimeDiff_Calculator - not sure of what it is actually doing (something to do with time
It is more to test the structure of a plugin
(taken from Wiktor's Chi2Calculator)
Configuration parameters:
    detector_list: list of strings, ["first_detector", "second_detector", ...]    \
                the list of detectors that we want to include in the calculations  \
                options: "HK", "IC", "JUNO", "KM3", "SK"                           / same as in NeutrinoArrivalTime
    detector_location: csv file name ('detector_location.csv')                  __/
Output json:
  undefined
"""
import csv
import logging
import numpy as np
import healpy as hp
from numpy.core.numeric import Inf
from scipy.stats import chi2
from datetime import datetime

from snewpdag.dag import Node


class test_TimeDiff_Calculator(Node):
    def __init__(self, detector_list, detector_location, **kwargs):
        self.detector_info = {}
        with open(detector_location, 'r') as f:
            detectors = csv.reader(f)
            for detector in detectors:
                name = detector[0]
                if name not in detector_list:
                    continue
                lon = np.radians(float(detector[1]))
                lat = np.radians(float(detector[2]))
                height = float(detector[3])
                sigma = float(detector[4])
                self.detector_info[name] = [lon, lat, height, sigma]
                self.map = {}
                self.measured_times = {}
                for detector in detector_list:
                    self.measured_times[detector] = None

        super().__init__(**kwargs)



    # Makes handling times easier
    def get_time_dicts(self):
        measured = dict(filter(lambda element: element[1] != None, self.measured_times.items())) ##R.D. returns only detectors that measured a time

        det_0 = ""
        sigma_0 = Inf

        for det in measured:
            if self.detector_info[det][3] < sigma_0:
                sigma_0 = self.detector_info[det][3]
                det_0 = det
        det0_time = measured.pop(det_0)

        measured_det_info = dict(filter(lambda element: element[0] in measured.keys(), self.detector_info.items()))
        det0_info = self.detector_info[det_0]

        return measured, measured_det_info, det0_time, det0_info


    # Generates unit vector for given latitude and longitude,
    # pointing towards sky
    # alpha range is (-pi, pi), delta range is (-pi/2, pi/2)
    def angles_to_unit_vec(self, lon, lat):
        x = np.cos(lon)*np.cos(lat)
        y = np.sin(lon)*np.cos(lat)
        z = np.sin(lat)
        return np.matrix([x, y, z]).getT()

    # Calculates detector position in cartesian coordinates
    def det_cartesian_position(self, det):
        ang_rot = 7.29e-5  # radians/s
        ang_sun = 2e-7  # radians/s   2pi/365days

        # take into account the time dependence of longitude
        # reference: arXiv:1304.5006
        arrival_date = datetime.fromtimestamp(self.arrival[0])
        decimal = self.arrival[1]*1e-9

        t_rot = arrival_date.hour*60*60 \
              + arrival_date.minute*60 + arrival_date.second + decimal

        t_sun = self.arrival[0] - 953582400 + decimal

        lon = det[0] + ang_rot*t_rot - ang_sun*t_sun - np.pi
        lat = det[1]
        r = 6.37e6 + det[2]

        return r*self.angles_to_unit_vec(lon, lat)

    # Calculates time_diff given detector names and supernova location
    def time_diff(self, det1, det2, n):
        c = 3.0e8  # speed of light /m*s^-1

        det1_pos = self.det_cartesian_position(det1)
        det2_pos = self.det_cartesian_position(det2)

        diff = float((det1_pos - det2_pos).getT() @ n)/c

        return diff


    def alert(self, data):
        time = data['neutrino_time']
        if 'detector_id' in data:
            det = data['detector_id']
        else:
            det = self.last_source

        self.measured_times[det] = time

        self.map[self.last_source] = data.copy()
        self.map[self.last_source]['history'] = data['history'].copy()
        self.map[self.last_source]['valid'] = True

        measured, measured_det_info, det0_time, det0_info = self.get_time_dicts()

        sum_s = det0_time[0]
        sum_ns = det0_time[1]
        for s, ns in measured.values():
            sum_s += s
            sum_ns += ns
        self.arrival = (sum_s/(len(measured)+1), sum_ns/(len(measured)+1))

        # Takes only the detectors for which time has been measured
        if len(measured) < 2:
            return False

        hlist = []
        for k in self.map:
            if self.map[k]['valid']:
                hlist.append(self.map[k]['history'])
        data['history'].combine(hlist)
        return data
