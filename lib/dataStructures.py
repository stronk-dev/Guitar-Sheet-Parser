# !/usr/bin/python
# This file hosts the classes for storing song data
import re

# TODO: move to separate file with helper functions like this
def stripEmptyLines(inputString):
  nonEmptyLines = ""
  lines = inputString.split("\n")
  for line in lines:
    if line.strip() != "":
      nonEmptyLines += line + "\r\n"
  return nonEmptyLines
# read .txt input TODO: move to separate input functions if we want to support multiple types of inputs some day, like web or PDF 
def readSourceFile(inputFile):
  with open(inputFile, 'r') as file:
    return file.read()
    
def isChordType(inputString):
  if not inputString:
    return
  #print("Checking '{}' for line type".format(inputString))
  # Assume CHORD line if any NUMBER character
  if any(char.isdigit() for char in inputString):
    #print("'{}' is a CHORD line, since it contains a number".format(inputString))
    return True
  # Assume CHORD line if any character {/, #, (, ), }
  chordSpecificCharacterString = r"/#"
  if any(elem in inputString for elem in chordSpecificCharacterString):
    #print("'{}' is a CHORD line, since it contains a chord specific character".format(inputString))
    return True
  # Assume LYRIC line if any TEXT character OTHER THAN {a, b, c, d, e, f, g, h, b, x, m}
  lyricSpecificCharacterString = r"abcdefghbxm"
  for char in inputString:
    if char.isalpha():
      if not char.lower() in lyricSpecificCharacterString:
        #print("'{}' is a LYRIC line, since it contains lyric specific text characters".format(inputString))
        return False
  # Assume LYRIC line if any character {.}
  lyricSpecialChars = r"."
  if any(elem in inputString for elem in lyricSpecialChars):
    #print("'{}' is a LYRIC line, since it contains lyric specific special characters".format(inputString))
    return False
  # Else warn and assume chord line
  #print("Unable to identify if '{}' is a lyric or chord line. Assuming it is a chord line. Please improve the isChordType function".format(inputString))
  return True
  

class Section:
  def __init__(self):
    # List of lines of lyrics strings
    self.lyrics = []
    # List of lines of chord strings
    self.chords = []
    # section type string
    self.header = ""
    # string of chord and lyric data
    self.rawData = ""
    # Flag for succesfully parsed
    self.isParsed = False
    
  # Parses self.rawData into lyrics and chord strings
  def parseMe(self):
    isFirstLine = True
    # Input sections may have chord-only or lyric-only sections
    # So we have to insert empty lines if we have subsequent chord or lyric lines
    lines = self.rawData.split('\r\n')
    for line in lines:
      # Determine lyric or chord line
      currentIsChord = isChordType(line)
      # Initially just fill in the first line correctly
      if isFirstLine:
        isFirstLine = False
        if currentIsChord:
          self.chords.append(line)
        else:
          self.lyrics.append(line)
      # We want alternating lines, so if the prev is of the same type
      # we need to insert an empty line of the other type
      elif currentIsChord == prevWasChord:
        if currentIsChord:
          #print("Inserting empty Lyric line")
          self.chords.append(line)
          self.lyrics.append("")
        else:
          #print("Inserting empty Chord line")
          self.lyrics.append(line)
          self.chords.append("")
      # also insert the current line
      elif currentIsChord:
        #print("Inserting empty Lyric line")
        self.chords.append(line)
      else:
        self.lyrics.append(line)
        
      prevWasChord = currentIsChord
    # Simple check to see if it worked
    if abs(len(self.lyrics) - len(self.chords)) > 1:
      print("Unable to parse section, since there is a mismatch between the amount of chord and lyric lines.")
      return
    # Add a final empty line if necessary
    elif len(self.lyrics) > len(self.chords):
      self.chords.append("")
    elif len(self.lyrics) < len(self.chords):
      self.lyrics.append("")
    self.isParsed = True
    
    
class Song:
  def __init__(self):
    # Src file
    self.inputFile = ""
    # Path to folder
    self.outputLocation = ""
    # Title - based on input file
    self.title = ""
    # List of Section objects
    self.sections = []
    # Meta info: the text before the first section
    self.metadata = ""
    # String of entire input
    self.rawData = ""
    # Flag for succesfully parsed
    self.isParsed = False
    
  # Parses self.rawData into Section objects and metadata
  def parseMe(self):
    # Fill raw data
    self.rawData = readSourceFile(self.inputFile)
    # Clean up input
    parseData = stripEmptyLines(self.rawData)
    #print("Clean data='{}'\n".format(parseData))
    # While !EOF: build sections (untill []).
    delimiterIndex = parseData.find("[")
    if delimiterIndex == -1:
      print("Cannot parse input file, since it is not delimited by '[<sectionName>]' entries")
      return
    # Start with metadata
    self.metadata = parseData[:delimiterIndex]
    #print("Set '{}' as metadata".format(self.metadata))
    parseData = parseData[delimiterIndex:]
    # We are now at the start of the first section, at the '[' character
    while parseData:
      thisSection = Section()
      # Get first line
      delimiterIndex = parseData.find("]\r\n")
      if delimiterIndex == -1:
        print("Cannot parse input file, delimitor did not match '[<sectionName>]'")
        return
      # Set header to first line
      thisSection.header = parseData[:delimiterIndex+3]
      parseData = parseData[delimiterIndex+3:]
      # Find next section
      delimiterIndex = parseData.find("[")
      # If EOF, current buffer is final section
      if delimiterIndex == -1:
        # Set current section data to remaining buffer
        thisSection.rawData = parseData
        parseData = ""
      else:
        # Set thisSection's data and remove it from the buffer
        thisSection.rawData = parseData[:delimiterIndex]
        #print("set rawData of '{}' to this section".format(thisSection.rawData))
        parseData = parseData[delimiterIndex:]
      # Finally parse section data
      thisSection.parseMe()
      if thisSection.isParsed:
        self.sections.append(thisSection)
      else:
        print("Aborting parse due to section not being parseable.")
        return
    self.isParsed = True
  
  
  
  
  
  
  
  
  
  
  
  
