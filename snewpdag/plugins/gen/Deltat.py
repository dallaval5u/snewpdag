"""
DeltaTCalculator: Look up detector1 and detector2 in data['neutrino_time'], and compute the time difference
                    between the observed t0s
Constructor Arguments:
    detector1: the name of the first detector
    detector2: name of the second detector
Output:
    Time difference between the respective t0s
"""

import logging
from snewpdag.dag import Node


class Deltat(Node):

    def __init__(self, detector1, detector2, **kwargs):
        self.detector1 = detector1
        self.detector2 = detector2
        super().__init__(**kwargs)

    def alert(self, data):
        if self.detector1 not in data["gen"]['neutrino_times']:
            logging.error("{} is not in the payload.".format(self.detector1))
            return True
        if self.detector2 not in data["gen"]['neutrino_times']:
            logging.error("{} is not in the payload.".format(self.detector2))
            return True
        #data['DeltaT'] = float(data["gen"]['neutrino_times'][self.detector1][0]) \
                         #- float(data["gen"]['neutrino_times'][self.detector2][0])

        #print(data['DeltaT'])
        x = float(data["gen"]['neutrino_times'][self.detector1][0])
        y = float(data["gen"]['neutrino_times'][self.detector2][0])
        print(x)
        print(y)

        return True
