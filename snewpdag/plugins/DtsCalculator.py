"""
DtsCalculator: compute neutrino time differences between the detector with the smallest sigma
 and each detector sending an alert.

Arguments:
    detector_location: filename of detector database for DetectorDB

Input payload:
    data['gen']['neutrino_times'] (we will probably not have this in non-mc data)
    data[neutrino_time] = observed burst time for a detector (s,ns). For mc trials use
    the DetectorTime.py plugin to generate this.

Output payload:
    dt: time tuple (s,ns) of t1-t2.
      t1: burst time tuple (s,ns) of det1.
      t2: burst time tuple (s,ns) of det2.
      bias: bias in dt in nanoseconds, given as bias1-bias2.
      var: variance (stddev**2) of dt in nanoseconds.
      dsig1: sigma1, in nanoseconds, for covariance calculation.
      dsig2: - sigma2, in nanoseconds, for covariance calculation.
"""

import logging
from snewpdag.dag import Node, DetectorDB
from snewpdag.dag.lib import subtract_time

class DtsCalculator(Node):
        def __init__(self, detector_location, **kwargs):
            self.valid = {}  # dict with flags indicating valid data from sources
            self.times = {}  # dict with neutrino time for each alerting detector
            self.dets_names = {}
            self.sigma_dict = {} # dict storing uncertainties for each alerting detector
            self.bias_dict = {}
            self.map = {}
            self.db = DetectorDB(detector_location)
            super().__init__(**kwargs)

        def find_nu_times(self, data):
            '''
            Extract neutrino time for each detector
            '''
            index = self.last_watch_index()
            self.valid[index] = False
            index_detector = data['detector_names'].index(data['det_data'])
            if index in self.times:
                burst_time = self.times[index]
            else:
                burst_time = None

            if data['neutrino_times'][index_detector] is tuple:
                self.times[index] = data['neutrino_times'][index]
            else:
                #### From this kind of data '22/01/01 12:30:55:678999' get a tuple (s, ms)
                time_tuple = (int(data['neutrino_times'][index_detector].split(':')[-2]), int(data['neutrino_times'][index_detector].split(':')[-1])*1000)
                self.times[index] = time_tuple
                logging.info(time_tuple)

            ############################### Use fake names because we do not have a properties table with DM detectors
            fake_names = ['JUNO', 'KM3', 'SK', 'SNOP', 'KL']
            self.dets_names[index] = fake_names[index]
            ###############################

            # extract uncertainty and bias
            if 'sigma' in data:
                self.sigma_dict[index] = data['sigma']
            else:
                self.sigma_dict[index] = self.db.get(fake_names[index]).sigma

            if 'bias' in data:
                self.bias_dict[index] = data['bias']
            else:
                self.bias_dict[index] = self.db.get(fake_names[index]).bias

            # check whether an experiment is revoking its data:
            if self.times[index] != burst_time:
                if self.times[index] is None:
                    if self.valid[index]:
                        self.valid[index] = False
                        data['action'] = 'revoke'
                        return data
                else:
                    self.valid[index] = True
            #print(self.valid)
            #print(self.valid.values())
            #print(self.dets_names)
            return False

        def compute_dts(self, data):
            '''
            Compute time differences between the detector with the smallest sigma and each of the other detectors
            '''
            logging.info('COMPUTINGDTS')
            best_detector_index = min(self.sigma_dict, key=self.sigma_dict.get)
            best_detector_name = self.dets_names[best_detector_index]
            best_det_time = self.times[best_detector_index]

            #print(self.sigma_dict)
            for i in list(self.times.keys()):
                if self.times[i] != best_det_time:
                    if 'dts' not in data:
                        data['dts'] = {(best_detector_name, self.dets_names[i]): {'dt':
                        tuple(subtract_time(best_det_time, self.times[i])),
                                't1': best_det_time, 't2': self.times[i], 'dsig1': min(self.sigma_dict.values()),
                                'dsig2': -self.sigma_dict[i], 'bias': self.bias_dict[best_detector_index] - self.bias_dict[i],
                                 'var': min(self.sigma_dict.values()) ** 2 + self.sigma_dict[i] ** 2}}

                    else:
                        data['dts'].update({(best_detector_name, self.dets_names[i]): {'dt':
                        tuple(subtract_time(best_det_time, self.times[i])),
                                't1': best_det_time, 't2': self.times[i],
                                 'dsig1': min(self.sigma_dict.values()), 'dsig2': -self.sigma_dict[i]},
                                 'bias': self.bias_dict[best_detector_index] - self.bias_dict[i],
                                 'var': min(self.sigma_dict.values()) ** 2 + self.sigma_dict[i] ** 2})
            logging.info(data)
            return data

        #def compute_dts(self, data):
        #    '''
        #    Compute time differences between every detector pairs
        #    '''
        #    # compute and store dts in a 2d list:
        #    DeltaTsMatrix = [[0 for j in range(sum(self.valid.values()))] for i in range(sum(self.valid.values()))]
        #    for i in range(sum(self.valid.values())):
        #        for j in range(i + 1, sum(self.valid.values())):
        #            DeltaTsMatrix[i][j] = np.subtract(self.times[i], self.times[j])
        #            # add to the payload:
        #            if 'dts' not in data:
        #                data['dts'] = {(self.dets_names[i], self.dets_names[j]): {
        #                    'dt': tuple(lib.normalize_time_difference(DeltaTsMatrix[i][j])), \
        #                    't1': self.times[i], 't2': self.times[j]}}
        #            else:
        #                data['dts'].update({(self.dets_names[i], self.dets_names[j]): {
        #                    'dt': tuple(lib.normalize_time_difference(DeltaTsMatrix[i][j])), \
        #                    't1': self.times[i], 't2': self.times[j]}})
        #    # data['dt_uncertainties'] = {"Diff_t0s": max(self.uncertainties)}
        #    return data

        def alert(self, data):
            # keep tracking of histories
            source = self.last_source
            self.map[source] = data.copy()
            self.map[source]['history'] = data['history'].copy()  # keep local copy
            self.map[source]['valid'] = True

            # extract neutrino time for each detector:
            self.find_nu_times(data)

            # compute the dts if we have two or more valid inputs
            if sum(self.valid.values()) == data['number_of_coinc_dets'] and sum(self.valid.values()) > 1:
                self.compute_dts(data)
                # update history
                hlist = []
                for k in self.map:
                    if self.map[k]['valid']:
                        hlist.append(self.map[k]['history'])
                data['history'].combine(hlist)
                #data['action'] = 'revoke' if len(hlist) == 0 else 'alert'
                return data

            # not enough inputs
            return False

        def revoke(self, data):
            index = self.last_watch_index()
            revoke = self.valid[index]
            if revoke:
                self.valid[index] = False
            return revoke

        def reset(self, data):
            reset = False
            if sum(self.valid.values()) >= 1:
                reset = True
            for i in range(len(self.valid)):
                self.valid[i] = False
            return reset

        def report(self, data):
            return True