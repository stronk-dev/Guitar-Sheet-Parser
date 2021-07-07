# !/usr/bin/python
# Iterate through input folders and create a list of Song objects
import lib.dataStructures
import os

# For now manually whitelist folders to convert
whitelist = ["/mnt/koios/Band/1-sugmesties", "/mnt/koios/Band/2-oefenen", "/mnt/koios/Band/3-uitgewerkt"]

def initSong(filePath):
  thisSong = lib.dataStructures.Song()
  thisSong.inputFile = filePath
  # set base folder name - depending on selected outputs the output folder name changes
  thisSong.outputLocation = filePath[:filePath.rfind('.')]
  # title is just the name of the .txt file
  thisSong.title = thisSong.outputLocation[filePath.rfind('/')+1:]
  #print("Finished init for input file '{}'.\nBase output folder is '{}'\nSong title is '{}'\n".format(thisSong.inputFile, thisSong.outputLocation, thisSong.title))
  return thisSong
 

def getSongObjects():
  # path to song folders, which MAY contain a .txt source file
  txtFileLocations = []
  # list of Song objects
  songList = []
  
  # get all subdirectories
  for inputFolder in whitelist:
    for root, dirs, files in os.walk(inputFolder):
      for name in files:
        if(name[name.rfind('.'):] == ".txt"):
          filePath = os.path.join(root, name)
          #print("Found .txt file '{}'".format(filePath))
          txtFileLocations.append(filePath)
        #else:
          #print("Skipping file '{}' for it is not a .txt file".format(name))
  
  # go through all input locations. find .txt files. for each .txt file initSong. return list
  while(txtFileLocations):
    filePath = txtFileLocations.pop()
    if (filePath != ""):
      songList.append(initSong(filePath))
  return songList
