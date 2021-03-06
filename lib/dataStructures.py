#!/usr/bin/env python3
##
# @file dataStructures.py
#
# @brief This file contains the internal data structures required for each tablature file
#
# @section description Description
# -
#
# @section notes Notes
#

import re
import lib.config
from PIL import ImageFont
import logging

A4 = {'width': 210, 'height': 297}
A5 = {'width': 210, 'height': 148}

"""!@brief Removes empty lines and makes sure every line ends with \r\n
    @param inputString raw txt input
    @return string of parsed input
"""
def stripEmptyLines(inputString, keepEmptyLines):
  nonEmptyLines = ""
  lines = inputString.split("\n")
  for line in lines:
    if keepEmptyLines or line.strip() != "":
      nonEmptyLines += line + "\r\n"
  return nonEmptyLines

"""!@brief Opens a .txt file and loads it's contents into buffer
    @param inputFile path to .txt file
    @return .txt file raw contents
"""
def readSourceFile(inputFile):
  with open(inputFile, 'r') as file:
    return file.read()

"""!@brief Returns whether the string is a line of lyrics or a line of tablature data
    @param inputString single line of text
    @return True if it is tablature data, False if it is lyric data
"""
def isTablatureData(inputString):
  if not inputString:
    return
  logging.debug("Checking '{}' for line type".format(inputString))
  # Assume tablature line if any character {/, #, (, ), }
  tablatureSpecificCharacterString = r"/#"
  if any(elem in inputString for elem in tablatureSpecificCharacterString):
    logging.debug("'{}' is a tablature line, since it contains a tablature specific character".format(inputString))
    return True
  # Assume LYRIC line if any TEXT character OTHER THAN {a, b, c, d, e, f, g, h, b, x, m, j, n}
  lyricSpecificCharacterString = r"abcdefghbxmjn"
  for char in inputString:
    if char.isalpha():
      if not char.lower() in lyricSpecificCharacterString:
        logging.debug("'{}' is a lyric line, since it contains lyric specific text characters".format(inputString))
        return False
  # Assume tablature line if any digit
  if any(char.isdigit() for char in inputString):
    logging.debug("'{}' is a tablature line, since it contains a number".format(inputString))
    return True
  # Assume LYRIC line if any character {.}
  lyricSpecialChars = r"."
  if any(elem in inputString for elem in lyricSpecialChars):
    logging.debug("'{}' is a lyric line, since it contains lyric specific special characters".format(inputString))
    return False
  # Else warn and assume tablature line
  # logging.warn("Unable to identify if '{}' is a lyric or tablature line. Assuming it is a tablature line. Please improve the isTablatureData function".format(inputString))
  return True

"""!@brief Class containing Section specific data
"""
class Section:
  def __init__(self):
    # List of lines of lyrics strings
    self.lyrics = []
    # List of lines of tablature strings
    self.tablatures = []
    # section type string
    self.header = ""
    # string of tablature and lyric data
    self.rawData = ""
    # Flag for succesfully parsed
    self.isParsed = False
    # Expected dimensions of this section
    self.expectedWidth = -1
    self.expectedHeight = -1

  """!@brief Calculates dimensions of rendered text
    @return None
  """
  def calculateSectionDimensions(self, fontTablature, fontLyrics):
    lineIterator = 0
    amountOfLines = len(self.lyrics)
    heightSum = 0
    maxWidth = 0
    # consider section title
    logging.debug("Init size with header '{}'".format(self.header))
    headerWidth, headerHeight = fontTablature.getsize(self.header)
    heightSum += headerHeight
    maxWidth = headerWidth
    while lineIterator < amountOfLines:
      # Get chord&lyric line dimensions
      lyricTextWidth, lyricTextHeight = fontLyrics.getsize(self.lyrics[lineIterator])
      tablatureTextWidth, chordTextHeight = fontTablature.getsize(self.tablatures[lineIterator])
      heightSum += lyricTextHeight + chordTextHeight
      if lyricTextWidth > maxWidth:
        logging.debug("Found line '{}' with a width of {}".format(self.lyrics[lineIterator], lyricTextWidth))
        maxWidth = lyricTextWidth
      if tablatureTextWidth > maxWidth:
        logging.debug("Found line '{}' with a width of {}".format(self.tablatures[lineIterator], tablatureTextWidth))
        maxWidth = tablatureTextWidth
      lineIterator += 1
    logging.debug("Setting section to W:{} H:{}".format(maxWidth, heightSum))
    self.expectedWidth = maxWidth
    self.expectedHeight = heightSum
    
  """!@brief Converts raw buffered data into separate Lyric and tablature lines
      @return None
  """
  # Parses self.rawData into lyrics and tablature strings
  def initSections(self):
    isFirstLine = True
    # Input sections may have tablature-only or lyric-only sections
    # So we have to insert empty lines if we have subsequent tablature or lyric lines
    lines = self.rawData.splitlines(True)
    for line in lines:
      # Empty line whitespace
      if not line:
        self.lyrics.append("")
        self.tablatures.append("") 
        continue 
      # Determine lyric or tablature line
      currentIsTablature = isTablatureData(line)
      logging.debug("Have line {} isTab={}, isLyric={}".format(line, currentIsTablature, not currentIsTablature))
      # Initially just fill in the first line correctly
      if isFirstLine:
        isFirstLine = False
        if currentIsTablature:
          self.tablatures.append(line)
        else:
          self.lyrics.append(line)
      # We want alternating lines, so if the prev is of the same type
      # we need to insert an empty line of the other type
      elif currentIsTablature == prevWasTablature:
        if currentIsTablature:
          logging.debug("Inserting empty Lyric line")
          self.tablatures.append(line)
          self.lyrics.append("")
        else:
          logging.debug("Inserting empty tablature line")
          self.lyrics.append(line)
          self.tablatures.append("")
      # also insert the current line
      elif currentIsTablature:
        logging.debug("Inserting empty Lyric line")
        self.tablatures.append(line)
      else:
        self.lyrics.append(line)
      # move on to next line, save current type
      prevWasTablature = currentIsTablature
    # Simple check to see if it probably exported correctly
    if abs(len(self.lyrics) - len(self.tablatures)) > 1:
      logging.error("Unable to parse section {}, since there is a mismatch between the amount of lyrics ({}) and tablature ({}) lines.".format(self.header, len(self.lyrics), len(self.tablatures)))
      return
    # Add a trailing empty line if necessary
    elif len(self.lyrics) > len(self.tablatures):
      self.tablatures.append("")
    elif len(self.lyrics) < len(self.tablatures):
      self.lyrics.append("")
    self.isParsed = True

"""!@brief Class containing Sections which fit on 1 page
"""
class Page:
  def __init__(self):
    self.sections = []
    self.totalHeight = -1

"""!@brief Class containing Song specific data
""" 
class Song:
  def __init__(self):
    # Src file
    self.inputFile = ""
    # Path to folder
    self.outputLocation = ""
    self.fileExtension = ""
    # Title - based on input file
    self.title = ""
    # List of Section objects
    self.sections = []
    # Meta info: the text before the first section
    self.metadata = ""
    self.metadataWidth = -1
    self.metadataHeight = -1
    # String of entire input
    self.rawData = ""
    # List of pages, which contain sections which fit on a page
    self.pages = []
    # Flag for succesfully parsed
    self.isParsed = False
    configObj = lib.config.config['output']
    self.verticalMargin = int(configObj['verticalMargin'])
    self.horizontalMargin = int(configObj['horizontalMargin'])
    self.extraHorizontalMargin = int(configObj['extraHorizontalMargin'])
    self.fontColour = tuple(int(var) for var in configObj['fontColour'].split(','))
    self.backgroundColour = tuple(int(var) for var in configObj['backgroundColour'].split(','))
    self.metadataColour = tuple(int(var) for var in configObj['metadataColour'].split(','))
    self.ppi = int(configObj['imageppi'])
    # 0.03937 pixels per minimeter per ppi
    self.imageWidth = int(self.ppi * A4['width'] * 0.03937)
    self.imageHeight = int(self.ppi * A4['height'] * 0.03937)
    # With a PPI of 72, a font size of 14-18 is a good starting point (PPI / 4 or 4.5)
    # Since font size is then shrunk and grown to fit whitespace we do not need to be as accurate
    # PPI of 144 -> fontSize of 32
    self.fontSize = int(self.ppi / 4)
    self.fontLyrics = ImageFont.truetype(configObj['lyricfontfamily'], self.fontSize)
    self.fontTablature = ImageFont.truetype(configObj['tablaturefontfamliy'], self.fontSize)
    self.fontFamilyLyrics = configObj['lyricfontfamily']
    self.fontFamilyTablature = configObj['tablaturefontfamliy']
    self.metadataFontsize = int(configObj['metaFontWeight'])
    self.metadataFontFamily = configObj['metafontfamily']
    self.fontMetadata = ImageFont.truetype(self.metadataFontFamily, self.metadataFontsize)
    # Allowed whitespace to total width ratios. Makes stuff smaller but fit on less pages, probably
    # percentage of missing whitespace on total page height it wants before it tries to resize down
    self.tryToShrinkRatio = float(configObj['tryToShrinkRatio'])
    # Setting this makes sure that the largest section on the page fills at least this percentage of total width
    # The higher this is, the more it is allowed to shrink
    self.longestLineWhitespaceRatioAllowed = float(configObj['longestLineWhitespaceRatioAllowed'])
    # Some lines are very small, so the highest whitespace can be very large. 
    # It is advised to keep this ratio high for that reason
    self.shortestLineWhitespaceRatioAllowed = float(configObj['shortestLineWhitespaceRatioAllowed'])
    # Strip empty lines from input or keep em
    self.keepEmptyLines = configObj['keepEmptyLines'] == '1'
    # Strip empty lines from input or keep em
    self.writeMetadata = configObj['writeheaderfile'] == '1'
    # Don't go under this number
    self.minPages = int(configObj['minPages'])
    self.preferEvenPageNumbers = int(configObj['preferEvenPageNumbers'])
    self.maxPages = max(int(configObj['minPages']), int(configObj['maxPages']))


  """!@brief Calculates dimensions of metadata
    @param section lib.dataStructures.Section object
    @return None
  """
  def calculateMetadataDimensions(self):
    # metadata starts topMargin removed from top
    currentHeight = self.verticalMargin
    maxWidth = 0
    for line in self.metadata.split('\n'):
      line = line.rstrip()
      if not line:
        continue
      metadataTextWidth, metadataTextHeight = self.fontMetadata.getsize(line)
      if metadataTextWidth > maxWidth:
        logging.debug("Found line '{}' with a width of {}".format(line, metadataTextWidth))
        maxWidth = metadataTextWidth
      currentHeight += metadataTextHeight
    self.metadataWidth = maxWidth
    self.metadataHeight = currentHeight
    logging.debug("metadata dimensions are {}h : {}w".format(currentHeight, maxWidth))

  """!@brief Resizes all sections by a specified amount
    Also recalculates all section sizes afterwards
    @param mutator amount of fontSize to add/dec from current font size
    @return None
  """
  def resizeAllSections(self, mutator):
    logging.debug("Resizing font by {} to {}".format(mutator, self.fontSize))
    self.fontSize += mutator
    self.fontLyrics = ImageFont.truetype(self.fontFamilyLyrics, self.fontSize)
    self.fontTablature = ImageFont.truetype(self.fontFamilyTablature, self.fontSize)
    self.prerenderSections()

  """!@brief Resizes metadata and recalcs its size
    @param mutator amount of fontSize to add/dec from current font size
    @return None
  """
  def resizeMetadata(self, mutator):
    self.metadataFontsize += mutator
    self.fontMetadata = ImageFont.truetype(self.metadataFontFamily, self.metadataFontsize)
    self.calculateMetadataDimensions()

  """!@brief Calculates the expected dimensions of all sections
    @return None
  """
  def prerenderSections(self):
    self.calculateMetadataDimensions()
    for section in self.sections:
      section.calculateSectionDimensions(self.fontTablature, self.fontLyrics)

  """!@brief Calculates the expected dimensions of all sections
    @return None
  """
  def fitSectionsByWidth(self):
    self.prerenderSections()
    while not self.checkOverflowX():
      logging.debug("Resizing down to prevent overflow on the width of the page")
      self.resizeAllSections(-1)
    while not self.checkOverflowMetadata():
      logging.debug("Resizing down to prevent metadata overflow on the width of the page")
      self.resizeMetadata(-1)

  """!@brief Checks whether we are overflowing on the width of the page
    @return True if everything OK, False if overflowing
  """
  def checkOverflowX(self):
    for section in self.sections:
      if section.expectedWidth > self.imageWidth - self.extraHorizontalMargin - self.horizontalMargin - self.horizontalMargin:
        logging.debug("There is an overflow on width: this section has a width of {}, but we have {} ({}-{}-{}*2) amount of space".format(section.expectedWidth, self.imageWidth - self.extraHorizontalMargin - self.horizontalMargin - self.horizontalMargin, self.imageWidth, self.extraHorizontalMargin, self.horizontalMargin))
        return False
    return True
  
  """!@brief Checks whether the metadata is overflowing on the width of the page
    @return True if everything OK, False if overflowing
  """
  def checkOverflowMetadata(self):
    if self.metadataWidth > self.imageWidth - self.extraHorizontalMargin - self.horizontalMargin - self.horizontalMargin:
      return False
    return True

  """!@brief Resizes the page to fit reminaing whitespace, and increases the number of pages to stay above the minimum amount of pages
    @return None
  """
  def increaseToMinPages(self):
    targetPageAmount = max(len(self.pages), self.minPages)
    if (targetPageAmount % 2) != 0 and self.preferEvenPageNumbers:
      targetPageAmount += 1
      logging.info("Increasing target page amount to {} to make it an even number".format(targetPageAmount))
    originalFontsize = self.fontSize
    logging.debug("Starting font size increase with {} pages and {} font size".format(targetPageAmount, originalFontsize))
    self.resizeAllSections(+1)
    self.sectionsToPages()
    currentPageAmount = len(self.pages)
    # Increase fontSize as long as we stay under the target max pages
    while ((currentPageAmount <= targetPageAmount) and self.checkOverflowX()):
      self.resizeAllSections(+1)
      self.sectionsToPages()
      currentPageAmount = len(self.pages)
      logging.debug("Current page amount is {} with font size {}".format(currentPageAmount, self.fontSize))
    # Now undo latest increase to go back to target page amount
    self.resizeAllSections(-1)
    self.sectionsToPages()
    currentPageAmount = len(self.pages)
    if targetPageAmount != currentPageAmount:
      logging.warning("Oops! While resizing up we changed the amount of pages from {} to {}".format(targetPageAmount, currentPageAmount))
    if self.fontSize != originalFontsize:
      logging.debug("Managed to change the font size from {} to {}".format(originalFontsize, self.fontSize))
      
  
  """!@brief Tries to fill in the whitespace on the current render
    It will compare the size of existing whitespace with the size of the first section on the next page
    While the amount we are short is within X% of the current image height, resize down
    @return True if we should resize down, False if we are fine
  """
  def canFillWhitespace(self):
    amountOfPages = len(self.pages)
    currentPageIt = 0
    totalHorizontalMargin = self.extraHorizontalMargin + self.horizontalMargin + self.horizontalMargin
    imageWidthWithoutMargins = self.imageWidth - totalHorizontalMargin
    if not amountOfPages:
      return False
    # Stop resizing if we are creating too much widespace on the width
    smallestWhitespace = self.imageHeight
    biggestWhitespace = -1
    for page in self.pages:
      for section in page.sections:
          # We have 2* horizontal whitespace
          whitespaceOnWidth = self.imageWidth - totalHorizontalMargin - section.expectedWidth
          if whitespaceOnWidth < smallestWhitespace:
            smallestWhitespace = whitespaceOnWidth
          if whitespaceOnWidth > biggestWhitespace:
            biggestWhitespace = whitespaceOnWidth
    # Sections vary in width, some are very small to begin with
    logging.debug("The shortest line has {} whitespace, the largest line {}. The image is {} wide with {} total horizontal margins (={}), resulting in a {} min ratio and {} max ratio, with a min limit of {} and a max limit of {}".format(biggestWhitespace, smallestWhitespace, self.imageWidth, totalHorizontalMargin, imageWidthWithoutMargins, biggestWhitespace / imageWidthWithoutMargins, smallestWhitespace / imageWidthWithoutMargins, self.shortestLineWhitespaceRatioAllowed, self.longestLineWhitespaceRatioAllowed))
    # Make sure small lines fill the page enough
    if biggestWhitespace / imageWidthWithoutMargins > self.shortestLineWhitespaceRatioAllowed:
      logging.debug("Stopping resizing down, since the smallest section has {}% whitespace on the width of the image".format((biggestWhitespace / imageWidthWithoutMargins )* 100))
      return False
    # Make sure the longest lines fill the page enough
    if smallestWhitespace / imageWidthWithoutMargins > self.longestLineWhitespaceRatioAllowed:
      logging.debug("Stopping resizing down, since we largest section has {}% whitespace on the width of the image".format((smallestWhitespace / imageWidthWithoutMargins )* 100))
      return False
    # Make sure the longest lines fill the page enough
    if self.fontSize < int(self.ppi / 6):
      logging.debug("Stopping resizing down, since the font size is becoming too small at {}".format(self.fontSize))
      return False
    # get first section on next page, if we have a next page to begin with
    while currentPageIt < amountOfPages - 1:
      curPage = self.pages[currentPageIt]
      nextPage = self.pages[currentPageIt + 1]
      nextFirstSection = nextPage.sections[0]
      whitespace = self.imageHeight - curPage.totalHeight
      amountWeAreShort = nextFirstSection.expectedHeight - whitespace
      shortInPercentages = amountWeAreShort / self.imageHeight
      logging.debug("Whitespace {} vs next section height {}".format(whitespace, nextFirstSection.expectedHeight))
      logging.debug("We are {} short to fit the next image (total image height {} => {}% of total height)".format(amountWeAreShort, self.imageHeight, shortInPercentages*100))
      # Since we also resize based on minimum required whitespaces, we can be a bit more aggressive with this
      if shortInPercentages < self.tryToShrinkRatio:
        return True
      currentPageIt += 1
    return False
      

  """!@brief Fits current sections into pages
    @return None
  """
  def sectionsToPages(self):
    # If we are keeping whitespace, don't count the whitespace in between sections
    sectionWhitespace = self.verticalMargin
    if self.keepEmptyLines:
      sectionWhitespace = 0
    self.prerenderSections()
    self.pages = []
    # First page contains metadata
    currentHeight = self.verticalMargin
    currentHeight += self.metadataHeight
    currentHeight += sectionWhitespace
    curPage = Page()
    # Now fit all sections
    for section in self.sections:
      if (section.expectedHeight == -1 or section.expectedWidth == -1):
        logging.critical("Warning: this file was not processed correctly. The expected dimensions are not set")
        self.pages = []
        return
      # See if the section would fit on the current page - if it does not, we have a filled page
      if currentHeight + section.expectedHeight > self.imageHeight:
        curPage.totalHeight = currentHeight
        self.pages.append(curPage)
        currentHeight = sectionWhitespace
        curPage = Page()
      # Add setion header size and size of lines of data
      headerWidth, headerHeight = self.fontTablature.getsize(section.header)
      currentHeight += headerHeight
      currentHeight += section.expectedHeight
      curPage.sections.append(section)
      # Margin between each section
      currentHeight += sectionWhitespace
    # No more sections left, so the current buffered image is ready to be written to file
    curPage.totalHeight = currentHeight
    self.pages.append(curPage)

  """!@brief Parses self.rawData into Section objects and metadata
    Assumes the raw data is preprocessed, so it parses it using set rules instead of guessing line attributes
      @return None
  """
  def initPreprocessed(self):
    # Get raw data
    self.rawData = readSourceFile(self.inputFile)
    parseData = self.rawData
    # While not EOF: build sections until new section found.
    delimiterIndex = parseData.find("[")
    if delimiterIndex == -1:
      logging.error("Cannot parse input file, since it is not delimited by '[<sectionName>]' entries")
      return
    # Start with metadata
    self.metadata = parseData[:delimiterIndex]
    logging.debug("Set '{}' as metadata".format(self.metadata))
    parseData = parseData[delimiterIndex:]
    # We are now at the start of the first section, at the '[' character
    lines = parseData.splitlines(True)
    if not len(lines):
      return
    logging.debug("We found {} lines of data".format(len(lines)))
    # Init first section by popping the delimiter
    thisSection = Section()
    thisSection.header = lines.pop(0)
    # First line is always tab->lyric
    isTabLine = True
    logging.debug("First header is '{}'".format(thisSection.header))
    for line in lines:
      # If it is a [header], it is a new section
      if line[0] == '[':
        # Store prev section
        thisSection.initSections()
        if thisSection.isParsed:
          self.sections.append(thisSection)
        else:
          logging.error("Aborting parse due to section not being parseable.")
          return
        # Reset, new section
        thisSection = Section()
        thisSection.header = line
        logging.debug("Header is '{}'".format(thisSection.header))
        isTabLine = True
      # Else is has lines in order tabline->lyricline->repeat
      elif isTabLine:
        logging.debug("Adding Tabline is '{}'".format(line))
        thisSection.tablatures.append(line)
        isTabLine = False
      else:
        logging.debug("Adding Lyricline is '{}'".format(line))
        thisSection.lyrics.append(line)
        isTabLine = True
    # Add final section data
    thisSection.initSections()
    if thisSection.isParsed:
      self.sections.append(thisSection)
    else:
      logging.error("Aborting parse due to section not being parseable.")
      return
    self.isParsed = True
    
  """!@brief Parses self.rawData into Section objects and metadata
      @return None
  """
  def initSections(self):
    # Get raw data
    self.rawData = readSourceFile(self.inputFile)
    # Clean up input
    parseData = stripEmptyLines(self.rawData, self.keepEmptyLines)
    logging.debug("Clean data='{}'\n".format(parseData))
    # While not EOF: build sections until new section found.
    delimiterIndex = parseData.find("[")
    if delimiterIndex == -1:
      logging.error("Cannot parse input file, since it is not delimited by '[<sectionName>]' entries")
      return
    # Start with metadata
    self.metadata = parseData[:delimiterIndex]
    logging.debug("Set '{}' as metadata".format(self.metadata))
    parseData = parseData[delimiterIndex:]
    # We are now at the start of the first section, at the '[' character
    while parseData:
      # Init new Section object
      thisSection = Section()
      # Get header on the first line
      delimiterIndex = parseData.find("]\r\n")
      if delimiterIndex == -1:
        logging.error("Cannot parse input file, delimiter did not match '[<sectionName>]'")
        return
      # Skip the ']\r\n' characters
      thisSection.header = parseData[:delimiterIndex+3]
      parseData = parseData[delimiterIndex+3:]
      # Find next section
      delimiterIndex = parseData.find("[")
      # If EOF, current buffer is final section
      if delimiterIndex == -1:
        # Set thisSection's data to remaining buffer
        thisSection.rawData = parseData
        parseData = ""
      else:
        # Set thisSection's data and remove it from the buffer
        thisSection.rawData = parseData[:delimiterIndex]
        logging.debug("set rawData of '{}' to this section".format(thisSection.rawData))
        parseData = parseData[delimiterIndex:]
      # Finally parse section data
      thisSection.initSections()
      if thisSection.isParsed:
        self.sections.append(thisSection)
      else:
        logging.error("Aborting parse due to section not being parseable.")
        return
    self.isParsed = True
  
  
  
  
  
  
  
  
  
  
  
  
