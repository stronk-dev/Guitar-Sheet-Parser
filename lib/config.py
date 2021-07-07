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
        'supportedExtensions': ".txt",
        'maxDepth': 3
      }
    config['output'] = {'metafontfamily': 'fonts/CourierPrime-Regular.ttf',
        'metaFontWeight': 8,
        'lyricfontfamily': 'fonts/CourierPrime-Regular.ttf',
        'tablaturefontfamliy': 'fonts/CourierPrime-Bold.ttf',
        'songFontWeight': 14,
        'imageWidth': 595, 'imageHeight': 842,  # A4 at 72dpi
        'backgroundColour': '255,255,255',
        'fontColour': '0,0,0',
        'metadataColour': '128,128,128',
        'topMargin': 10,
        'leftMargin': 25
    }
  # (if CMD arguments: load CMD arguments to override specific settings)
  with open('config.ini', 'w') as configfile:
    config.write(configfile)