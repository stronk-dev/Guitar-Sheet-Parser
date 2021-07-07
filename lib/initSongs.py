#!/usr/bin/env python3
##
# @file initSongs.py
#
# @brief Iterate through input folders and create a list of Song objects
#
# @section description Description
# Initializes the Song objects for each supported input file found
# Currently only supports .txt files, which are read as-is into a string
#
# @section notes Notes
# - 
#
# @section todo TODO
# - Set a max recursion depth on the os.walk function
# - Support both paths to folders (like now) and to files directly
#   When the input is a file, check if it is .txt and init it
# - Input locations should be set in a config file (init to CWD, overwrite by CMD arguments)
# - Use config supportedExtensions

import lib.dataStructures
import lib.config
import os

"""!@brief Creates and inits a Song object
    This function creates a new Song object and sets the internal variables correctly
    Output folder name is derived from the name of the input file
    @param filePath path to the input file
    @return intialised Song object
"""
def initSong(filePath):
  thisSong = lib.dataStructures.Song()
  thisSong.inputFile = filePath
  # set base folder name - depending on selected outputs the output folder name changes
  thisSong.outputLocation = filePath[:filePath.rfind('.')]
  # title is just the name of the .txt file
  thisSong.title = thisSong.outputLocation[filePath.rfind('/')+1:]
  #print("Finished init for input file '{}'.\nBase output folder is '{}'\nSong title is '{}'\n".format(thisSong.inputFile, thisSong.outputLocation, thisSong.title))
  return thisSong
 
"""!@brief Returns the list of all Song objects created
    This function gets all supported input files in the specified input location(s)
    For each of these files it creates a Song object, ready to be read and then parsed
    @param configObj configparser object
    @return list of intialised Song objects
"""
def getSongObjects():
  # Get config variables
  configObj = lib.config.config['input']
  # path to song folders, which MAY contain a .txt source file
  txtFileLocations = []
  # list of Song objects
  songList = []
  # go through all input locations. find .txt files.
  for inputFolder in configObj['inputfolders'].split(','):
    #print("Walking directory '{}'".format(inputFolder))
    for root, dirs, files in os.walk(inputFolder):
      for name in files:
        if(name[name.rfind('.'):] in configObj['supportedextensions']):
          filePath = os.path.join(root, name)
          #print("Found .txt file '{}'".format(filePath))
          txtFileLocations.append(filePath)
        #else:
          #print("Skipping file '{}' for it is not a .txt file".format(name))
  
  # create list of Song objects
  while(txtFileLocations):
    filePath = txtFileLocations.pop()
    if (filePath != ""):
      songList.append(initSong(filePath))
  return songList
