#
# a test DAG for generating and analyzing two experiment alerts
#

[
  {
    "name": "Control", "class": "Pass",
    "kwargs": { "line": 100 }
  },

# {
#       "name": "test_importer", "class": "gen.test_import_node_json",
#       "observe": ["Control"],
#       "kwargs": {
#           "msgs_file": "snewpdag/plugins/gen/subscribed_messages.json",
#   }
# },




 #   "name": "test_arr_time", "class": "gen.NeutrinoArrivalTime",
 #   "observe": ["Control"],
 #   "kwargs": {
 #     "detector_list": ["JUNO","SK", "KM3"],
 #     "detector_location": "snewpdag/data/detector_location.csv"
 #   }
 # },
#
 # {"name": "test_offset_time", "class":"gen.TimeOffset",
 #  "observe": ["test_arr_time"],
 #  "kwargs": {"detector_location": "snewpdag/data/detector_location.csv"}
 #  },

##### test time diff module from entry neutrino time

 # {"name": "test_det_time_SK", "class": "gen.DetectorTime",
 #  "observe": ["test_offset_time"],
 #  "kwargs": {"detector": "SK"}
 #  },


 # {"name": "test_det_time_JUNO", "class": "gen.DetectorTime",
 #  "observe": ["test_det_time_SK"],
 #  "kwargs": {"detector": "JUNO"}
 #  },

###### t_true - t_observed distribution

 # {"name": "t_true-t_obs", "class": "gen.TtrueTobservedDistrPlotter",
 #  "observe": ["test_det_time_JUNO"],
 #  },



 # {"name": "test_det_time_KM3", "class": "gen.DetectorTime",
 #  "observe": ["test_det_time_JUNO"],
 #  "kwargs": {"detector": "KM3"}
 #  },

    {"name": "KM3_val", "class": "gen.KM3_validator",
     "observe": ["Control"]
     },
    {"name": "JUNO_val", "class": "gen.JUNO_validator",
     "observe": ["Control"]
     } ,

  {"name": "test_nutime_extraction", "class": "DtsCalculator",
   "observe": ["KM3_val", "JUNO_val"],
   "kwargs": {'detector_location': 'snewpdag/data/detector_location.csv'}
   },
##
# # {
# #   "name": "Control2", "class": "Pass",
# #   "observe": ["test_nutime_extraction"],
# #   "kwargs": {"line": 100}
# # },
#
# # {"name": "test_nutime_extraction2", "class": "gen.DeltaTCalculator",
# #  "observe": ["test_det_time_JUNO", "test_det_time_KM3"]
# #  },
#
#
#  #{"name": "best_dt", "class": "gen.ChooseBestDt",
#  # "observe": ["test_nutime_extraction"]
#  # },
#
 {"name": "Diffpoin", "class": "DiffPointing", "observe": ["test_nutime_extraction"],
  "kwargs": {
    "detector_location": "snewpdag/data/detector_location.csv",
    "nside": 32,
    "min_dts": 0,
  }
  }]
#
#
#  {
#    "name": "JUNO-ts", "class": "gen.TimeSeries",
#    "observe": [ "test_nutime_extraction" ],
#    "kwargs": {
#      "detector": "JUNO",
#      "mean": 1000,
#      "sig_filetype": "tn", "sig_filename":
#      "snewpdag/data/output_scint20kt_27_Shen_1D_solar_mass_progenitor.fits_1msbin.txt"
#    }
#  },
#
# #{
# #  "name": "SNOP-ts", "class": "gen.TimeSeries",
# #  "observe": ["Control"],
# #  "kwargs": {
# #    "detector": "SNOP",
# #    "mean": 100,
# #    "sig_filetype": "tn", "sig_filename":
# #      "snewpdag/data/output_scint20kt_27_Shen_1D_solar_mass_progenitor.fits_1msbin.txt"
# #  }
# #},
#
# ##{ "name": "JUNO", "class": "gen.Combine", "observe": [ "JUNO-ts" ] },
##
# ##{
# ##  "name": "JUNO-out", "class": "Pass",
# ##  "observe": [ "JUNO" ],
# ##  "kwargs": { "line": 1, "dump": 1 }
# ##},
##
# ##{
# ##  "name": "JUNO-bin", "class": "BinnedAccumulator",
# ##  "observe": [ "JUNO" ],
# ##  "kwargs": {
# ##    "in_field": "times",
# ##    "nbins": 2000, "xlow": -10.0, "xhigh": 10.0,
# ##    "out_xfield": "t", "out_yfield": "bins",
# ##    'flags': [ 'overflow' ],
# ##  }
# ##},
#
# ##{
# ##  "name": "JUNO-bin-out", "class": "Pass",
# ##  "observe": [ "JUNO-bin" ],
# ##  "kwargs": { "line": 1, "dump": 1 }
# ##},
##
# ##{
# ##  "name": "JUNO-bin-h",
# ##  "class": "renderers.Histogram1D",
# ##  "observe": [ "JUNO-bin" ],
# ##  "kwargs": {
# ##    "title": "JUNO time profile",
# ##    "xlabel": "time [s]",
# ##    "ylabel": "entries/0.1s",
# ##    "filename": "output/gen-liq-{}-{}-{}.png"
# ##  }
# ##},
#
#
#
# #{ "name": "SNOP", "class": "gen.Combine", "observe": [ "SNOP-ts" ] },
#
# #{
# #  "name": "SNOP-out", "class": "Pass",
# #  "observe": [ "SNOP" ],
# #  "kwargs": { "line": 1, "dump": 1 }
# #},
#
# #{
# #  "name": "SNOP-bin", "class": "BinnedAccumulator",
# #  "observe": [ "SNOP" ],
# #  "kwargs": {
# #    "in_field": "times",
# #    "nbins": 2000, "xlow": -10.0, "xhigh": 10.0,
# #    "out_xfield": "t", "out_yfield": "bins",
# #    'flags': [ 'overflow' ],
# #  }
# #},
#
# #{
# #  "name": "SNOP-bin-out", "class": "Pass",
# #  "observe": [ "SNOP-bin" ],
# #  "kwargs": { "line": 1, "dump": 1 }
# #},
#
# #{
# #  "name": "SNOP-bin-h", "class": "renderers.Histogram1D",
# #  "observe": [ "SNOP-bin" ],
# #  "kwargs": {
# #    "title": "SNOP time profile",
# #    "xlabel": "time [s]",
# #    "ylabel": "entries/0.1s",
# #    "filename": "output/gen-liq-{}-{}-{}.png"
# #  }
# #},
#
# # {
# #   "name": "Diff", "class": "NthTimeDiff",
# #   "observe": [ "JUNO", "SNOP" ],
# #   "kwargs": { "nth": 1 }
# # },
#
# ##{
# ##  "name": "Diff-out", "class": "Pass",
# ##  "observe": [ "Diff" ],
# ##  "kwargs": { "line": 100, "dump": 1 }
# ##},
##
# ##{
# ##  "name": "Diff-dt", "class": "Histogram1D",
# ##  "observe": [ "Diff" ],
# ##  "kwargs": {
# ##    "in_field": "dt",
# ##    "nbins": 100, "xlow": -0.1, "xhigh": 0.1,
# ##  }
# ##},
#
#
###### t_true - t_observed time distribution
### {
###   "name": "Ttrue_Tobs", "class": "Histogram1D",
###   "observe": ["t_true-t_obs"],
###   "kwargs": {
###     "in_field": "bias",
###     "nbins": 1000, "xlow": -0.02, "xhigh": 0.02,
###   }
### },
##
### {
###   "name": "Ttrue_Tobs-h",
###   "class": "renderers.Histogram1D",
###   "observe": ["Ttrue_Tobs"],
###   "kwargs": {
###     "title": "Tobs-Ttrue [JUNO] - 1000MC",
###     "xlabel": "dt [s]",
###     "ylabel": "entries",
###     "filename": "output/gen-liq-{}-{}-{}.png"
###   }
### },
##
###### best_dt histogram
##
##  #{
##  #  "name": "Best-dt", "class": "Histogram1D",
##  #  "observe": ["best_dt"],
##  #  "kwargs": {
##  #    "in_field": "best_dt",
##  #    "nbins": 100, "xlow": -0.1, "xhigh": 0.1,
##  #  }
##  #},
##
##  #{
##  #  "name": "Best-dt-h",
##  #  "class": "renderers.Histogram1D",
##  #  "observe": ["Best-dt"],
##  #  "kwargs": {
##  #    "title": "Observed-dt [JUNO-SK] -100MC",
##  #    "xlabel": "dt [s]",
##  #    "ylabel": "entries/0.1s",
##  #    "filename": "output/gen-liq-{}-{}-{}.png"
##  #  }
##  #},
##
##  {
##    "name": "Diff-dt-out", "class": "Pass",
##    "observe": [ "Diff-dt" ],
##    "kwargs": { "line": 100, "dump": 1 }
##  },
##
##  {
##    "name": "Diff-dt-h",
##    "class": "renderers.Histogram1D",
##    "observe": [ "Diff-dt" ],
##    "kwargs": {
##      "title": "Time difference",
##      "xlabel": "dt [s]",
##      "ylabel": "entries/0.1s",
##      "filename": "output/gen-liq-{}-{}-{}.png"
##    }
##  }
##    ,
##
## #   {
## #       "name": "test_ki2_calculator", "class": "Chi2Calculator",
## #       "observe": ["JUNO", "SNOP"],
## #       "kwargs": {
## #           "detector_list": ["SNOP", "JUNO"],
## #           "detector_location": "snewpdag/data/detector_location.csv",
## #           "NSIDE": 32}
## #   }
#
#]
#
