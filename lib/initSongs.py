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
# - 

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

"""!@brief Creates a list of files found in a directory and its subdirectories
    @param root path to the root. If it is a file it returns itself
            if it is a folder it returns its contents
    @param depth max recursion depth, defaults to 2
    @return list of paths to files
"""
def walkDirectory(root, depth):
  pathList = []
  #print("Walking directory '{}'".format(root))
  def do_scan(start_dir,output,depth=2):
      for f in os.listdir(start_dir):
          ff = os.path.join(start_dir,f)
          if os.path.isdir(ff):
              if depth>= 0:
                  do_scan(ff,output,depth-1)
          else:
              output.append(ff)
  do_scan(root,pathList,depth)
  return pathList
 
"""!@brief Returns the list of all Song objects created
    This function gets all supported input files in the specified input location(s)
    For each of these files it creates a Song object, ready to be read and then parsed
    @param configObj configparser object
    @return list of intialised Song objects
"""
def getSongObjects():
  # Get config variables
  configObj = lib.config.config['input']
  recursionDepth = int(configObj['maxDepth'])
  # path to song folders, which MAY contain a .txt source file
  txtFileLocations = []
  # list of Song objects
  songList = []
  # get all files we can find, then filter on supported extensions
  for inputFolder in configObj['inputfolders'].split(','):
    for filePath in walkDirectory(inputFolder, recursionDepth):
      if(filePath[filePath.rfind('.'):] in configObj['supportedextensions']):
        #print("Found .txt file '{}'".format(filePath))
        txtFileLocations.append(filePath)
      #else:
        #print("Skipping file '{}' for it is not a .txt file".format(filePath))
  # create list of Song objects
  while(txtFileLocations):
    filePath = txtFileLocations.pop()
    if (filePath != ""):
      songList.append(initSong(filePath))
  return songList
