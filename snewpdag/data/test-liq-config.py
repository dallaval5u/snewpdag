#
# a test DAG for generating and analyzing two experiment alerts
#

[
  {
    "name": "Control", "class": "Pass",
    "kwargs": { "line": 100 }
  },

  {
    "name": "test_arr_time", "class": "gen.NeutrinoArrivalTime",
    "observe": ["Control"],
    "kwargs": {
      "detector_list": ["JUNO","SK"],
      "detector_location": "snewpdag/data/detector_location.csv"
    }
  },

  {"name": "test_offset_time", "class":"gen.TimeOffset",
   "observe": ["test_arr_time"],
   "kwargs": {"detector_location": "snewpdag/data/detector_location.csv"}
   },

##### test time diff module from entry neutrino time

  {"name": "test_det_time_SK", "class": "gen.DetectorTime",
   "observe": ["test_offset_time"],
   "kwargs": {"detector": "SK"}
   },


  {"name": "test_det_time_JUNO", "class": "gen.DetectorTime",
   "observe": ["test_offset_time"],
   "kwargs": {"detector": "JUNO"}
   },

  {"name": "test_nutime_extraction", "class": "gen.DeltaTCalculator",
   "observe": ["test_det_time_JUNO","test_det_time_SK"]
   },




  {
    "name": "JUNO-ts", "class": "gen.TimeSeries",
    "observe": [ "Control" ],
    "kwargs": {
      "mean": 1000,
      "sig_filetype": "tn", "sig_filename":
      "snewpdag/data/output_scint20kt_27_Shen_1D_solar_mass_progenitor.fits_1msbin.txt"
    }
  },

  { "name": "JUNO", "class": "gen.Combine", "observe": [ "JUNO-ts" ] },

  {
    "name": "JUNO-out", "class": "Pass",
    "observe": [ "JUNO" ],
    "kwargs": { "line": 1, "dump": 1 }
  },

  {
    "name": "JUNO-bin", "class": "BinnedAccumulator",
    "observe": [ "JUNO" ],
    "kwargs": {
      "in_field": "times",
      "nbins": 2000, "xlow": -10.0, "xhigh": 10.0,
      "out_xfield": "t", "out_yfield": "bins",
      'flags': [ 'overflow' ],
    }
  },

  {
    "name": "JUNO-bin-out", "class": "Pass",
    "observe": [ "JUNO-bin" ],
    "kwargs": { "line": 1, "dump": 1 }
  },

  {
    "name": "JUNO-bin-h",
    "class": "renderers.Histogram1D",
    "observe": [ "JUNO-bin" ],
    "kwargs": {
      "title": "JUNO time profile",
      "xlabel": "time [s]",
      "ylabel": "entries/0.1s",
      "filename": "output/gen-liq-{}-{}-{}.png"
    }
  },

  {
    "name": "SNOP-ts", "class": "gen.TimeSeries",
    "observe": [ "Control" ],
    "kwargs": {
      "mean": 100,
      "sig_filetype": "tn", "sig_filename":
      "snewpdag/data/output_scint20kt_27_Shen_1D_solar_mass_progenitor.fits_1msbin.txt"
    }
  },

  { "name": "SNOP", "class": "gen.Combine", "observe": [ "SNOP-ts" ] },

  {
    "name": "SNOP-out", "class": "Pass",
    "observe": [ "SNOP" ],
    "kwargs": { "line": 1, "dump": 1 }
  },

  {
    "name": "SNOP-bin", "class": "BinnedAccumulator",
    "observe": [ "SNOP" ],
    "kwargs": {
      "in_field": "times",
      "nbins": 2000, "xlow": -10.0, "xhigh": 10.0,
      "out_xfield": "t", "out_yfield": "bins",
      'flags': [ 'overflow' ],
    }
  },

  {
    "name": "SNOP-bin-out", "class": "Pass",
    "observe": [ "SNOP-bin" ],
    "kwargs": { "line": 1, "dump": 1 }
  },

  {
    "name": "SNOP-bin-h", "class": "renderers.Histogram1D",
    "observe": [ "SNOP-bin" ],
    "kwargs": {
      "title": "SNOP time profile",
      "xlabel": "time [s]",
      "ylabel": "entries/0.1s",
      "filename": "output/gen-liq-{}-{}-{}.png"
    }
  },

  {
    "name": "Diff", "class": "NthTimeDiff",
    "observe": [ "JUNO", "SNOP" ],
    "kwargs": { "nth": 1 }
  },

  {
    "name": "Diff-out", "class": "Pass",
    "observe": [ "Diff" ],
    "kwargs": { "line": 100, "dump": 1 }
  },

  {
    "name": "Diff-dt", "class": "Histogram1D",
    "observe": [ "Diff" ],
    "kwargs": {
      "in_field": "dt",
      "nbins": 100, "xlow": -0.1, "xhigh": 0.1,
    }
  },

  {
    "name": "Diff-dt-out", "class": "Pass",
    "observe": [ "Diff-dt" ],
    "kwargs": { "line": 100, "dump": 1 }
  },

  {
    "name": "Diff-dt-h",
    "class": "renderers.Histogram1D",
    "observe": [ "Diff-dt" ],
    "kwargs": {
      "title": "Time difference",
      "xlabel": "dt [s]",
      "ylabel": "entries/0.1s",
      "filename": "output/gen-liq-{}-{}-{}.png"
    }
  }
    ,

 #   {
 #       "name": "test_ki2_calculator", "class": "Chi2Calculator",
 #       "observe": ["JUNO", "SNOP"],
 #       "kwargs": {
 #           "detector_list": ["SNOP", "JUNO"],
 #           "detector_location": "snewpdag/data/detector_location.csv",
 #           "NSIDE": 32}
 #   }

]

