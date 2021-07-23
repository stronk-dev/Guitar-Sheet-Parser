#!/usr/bin/env python3
##
# @file config.py
#
# @brief This program contains functions to load & create the program configuration
#
# @section description Description
# Contains the default values for all parameters
# Can create the config file update it with new settings
#
# @section notes Notes
# -
#
# @section todo TODO
# - if CMD arguments: load CMD arguments to override defaults

import os
import configparser


"""!@brief Load, creates and keeps the config up to date
"""
def initConfig():
  # Default config
  global config
  config = configparser.ConfigParser()
  # If a config file exists, load it
  if os.path.isfile('./config.ini'):
    config.read('config.ini')
  # Else load defaults
  else:
    config['input'] = {'inputFolders': os.getcwd(),
        'maxDepth': 2,
        'readtxt': 1,
        'readraw': 1
      }
    config['options'] = {'exporttoimg': 1,
        'exporttotxt': 0,
        'exporttoraw': 0
      }
    config['output'] = {'metafontfamily': 'fonts/CourierPrime-Regular.ttf',
        'metaFontWeight': 32,
        'lyricfontfamily': 'fonts/CourierPrime-Regular.ttf',
        'tablaturefontfamliy': 'fonts/CourierPrime-Bold.ttf',
        'imageppi': 144,
        'backgroundColour': '255,255,255',
        'fontColour': '0,0,0',
        'metadataColour': '128,128,128',
        'topMargin': 50,
        'leftMargin': 100,
        'rightMargin': 50,
        'tryToShrinkRatio' : 0.4,
        'lowestwhitespaceonwidthratioallowed': 0.90,
        'highestwhitespaceonwidthratioallowed': 0.40,
        'keepEmptyLines': 1,
        'writeheaderfile': 0,
        'minPages': 2
    }
  # (if CMD arguments: load CMD arguments to override specific settings)
  with open('config.ini', 'w') as configfile:
    config.write(configfile)