import Image, ImageDraw, ImageFont
import os
import re
import datetime
import settings





class AbortProcessing(Exception):
    pass





class Screenshot:
    def __init__(self, filename, timestamp):
        self.filename = filename
        self.extractedTimestamp = timestamp
        self.croppedImage = None
        self.scrollPos = None
        self.thumbSize = None





class Cluster:
    def __init__(self):
        self.screenshots = []
        self.messages = []
        self.warnings = 0
        self.mergedImage = None
        self.timestamp = None
        self.clusters = None
        self.firstImageFilename = None
        self.screenshotsProcessed = 0
        self.screenshotsUsed = 0
        
    def addScreenshot(self, screenshot):
        if(self.screenshotsProcessed == 0):
            self.timestamp = screenshot.extractedTimestamp
            self.firstImageFilename = screenshot.filename
        self.screenshots.append(screenshot)
        self.screenshotsProcessed += 1
        
    def getTimestampString(self):
        return("%04i-%02i-%02i, %02i:%02ih" % (self.timestamp.year, self.timestamp.month, self.timestamp.day, self.timestamp.hour, self.timestamp.minute))
        
    def getTitle(self):
        stringBuilder = self.getTimestampString()
        if(self.screenshotsUsed > 1):
            stringBuilder += " (%i used screenshots / %i in cluster)" % (self.screenshotsUsed, self.screenshotsProcessed)
        elif(self.screenshotsUsed == 1):
            stringBuilder += " (%i used screenshot / %i in cluster)" % (self.screenshotsUsed, self.screenshotsProcessed)
        else:
            stringBuilder += " (no valid screenshots found / %i in cluster) [FAILED]" % (self.screenshotsProcessed)
        if(self.warnings == 1):
            stringBuilder += " [1 WARNING]"
        elif(self.warnings > 1):
            stringBuilder += " [%i WARNINGS]" % (self.warnings)
        return(stringBuilder)
        
    def getFilenameSuggestion(self):
        return("Allegiance_Game_Statistics_%04i-%02i-%02i_%02i-%02i.png" % (self.timestamp.year, self.timestamp.month, self.timestamp.day, self.timestamp.hour, self.timestamp.minute))
        
    
        




class StatsMerger:
    reScreenshotFile = re.compile(r"(?P<filename>(\d{4})-(\d{1,2})-(\d{1,2})_(\d{1,2})\.(\d{1,2})\.(\d{1,2})\.\d{1,3}\.bmp)")
    MIN_SYNC_LINES = 3
    FINAL_IMAGE_WIDTH = 600
    SCROLLBAR_X_POS = 580


    
    def __init__(self, path, clusterThreshold, stateInitFunc, stateUpdateFunc):
        self.path = path
        self.clusterThreshold = clusterThreshold
        self.stateInitFunc = stateInitFunc
        self.stateUpdateFunc = stateUpdateFunc
        self.currentState = None
        self.abortProcessing = False
        self.clusters = []
        self.statsScreenDetectionTemplateR3 = Image.open("StatsScreenDetectionTemplateR3.png")
        self.statsScreenDetectionTemplateR4 = Image.open("StatsScreenDetectionTemplateR4.png")
        self.statsScreenTopBorder = Image.open("StatsScreenTopBorder.png")
        self.statsScreenRightBorder = Image.open("StatsScreenRightBorder.png")
        self.statsScreenBottomBorder = Image.open("StatsScreenBottomBorder.png")
        self.statsScreenLeftBorder = Image.open("StatsScreenLeftBorder.png")
        self.scrollbarPointerUp = Image.open("ScrollbarPointerUp.png")
        self.scrollbarPointerDown = Image.open("ScrollbarPointerDown.png")



    def initState(self, totalNumberOfOperations):
        self.currentState = 0
        if(self.stateUpdateFunc):
            self.stateInitFunc(totalNumberOfOperations)
            self.stateUpdateFunc(self.currentState)
        


    def increaseState(self):
        self.currentState += 1
        if(self.stateUpdateFunc):
            self.stateUpdateFunc(self.currentState)
        
        

    def getListOfScreenshots(self):
        screenshots = []
        filelist = os.listdir(self.path)
        for filename in filelist:
            reResult = StatsMerger.reScreenshotFile.match(filename)
            if(reResult):
                # build a timestamp from the data we recovered
                thisTimestamp = datetime.datetime(int(reResult.group(2)), int(reResult.group(3)), int(reResult.group(4)), int(reResult.group(5)), int(reResult.group(6)), int(reResult.group(7)))
                
                # create a new Screenshot object for this and store it
                screenshots.append(Screenshot(reResult.group("filename"), thisTimestamp))
        screenshots = sorted(screenshots, cmp=lambda x,y: cmp(x.extractedTimestamp, y.extractedTimestamp))
        return(screenshots)
    
    
    
    def getClusters(self, screenshots):
        clusters = []
        lastTimestamp = None
        currentCluster = None
        
        for screenshot in screenshots:
            thisTimestamp = screenshot.extractedTimestamp
            
            # this should never happen, because we're parsing the files in sorted order, but just in case we check
            if(lastTimestamp and lastTimestamp > thisTimestamp):
                raise "Error: files aren't properly sorted by date."
            
            # determine if we have to start a new cluster -- that's the case if this is the first file or the time difference is big enough
            if(not lastTimestamp):
                startNewCluster = True
            else:
                differenceInSeconds = (thisTimestamp - lastTimestamp).days*24*60*60 + (thisTimestamp - lastTimestamp).seconds
                startNewCluster = (differenceInSeconds > self.clusterThreshold)
            lastTimestamp = thisTimestamp

            # if we are starting a new cluster, we have to finish the last and open a new one      
            if(startNewCluster):
                if(currentCluster):
                    clusters.append(currentCluster)
                currentCluster = Cluster()

            # either way, we need to add this file to the cluster now
            currentCluster.addScreenshot(screenshot)
        
        # if we found at least one, the last cluster needs to be finished now
        if(currentCluster):
            clusters.append(currentCluster)
        
        # and we return the list of clusters
        return(clusters)
            
            
            
    def areImagesEqual(self, imageData, templateData, imageWidth, templateWidth, templateHeight):
        for x in xrange(0, templateWidth):
            for y in xrange(0, templateHeight):
                if(imageData[(50+y)*imageWidth+(88+x)] != templateData[y*templateWidth+x]):
                    return(False)
        return(True)



    def isStatsScreenshot(self, image):
        # shortcut if this can't be a stats screenshot
        if(image.size[0] != 800 or image.size[1] != 600):
            return(False)
        
        # prepare some variables
        imageData = image.getdata()
        templateDataR3 = self.statsScreenDetectionTemplateR3.getdata()
        templateDataR4 = self.statsScreenDetectionTemplateR4.getdata()
        imageWidth = image.size[0]
        templateWidth = self.statsScreenDetectionTemplateR3.size[0]
        templateHeight = self.statsScreenDetectionTemplateR3.size[1]
        
        # check if the image contains the stats top border
        if(self.areImagesEqual(imageData, templateDataR3, imageWidth, templateWidth, templateHeight)):
            return(True)
        else:
            return(self.areImagesEqual(imageData, templateDataR4, imageWidth, templateWidth, templateHeight))
    
    
    
    def getScrollbarPosition(self, image):
        startingY = None
        for y in xrange(88, 245+1):
            if(not startingY and image.getpixel((676, y)) == (255, 255, 255)):
                startingY = y
            elif(startingY and image.getpixel((676, y)) != (255, 255, 255)):
                return((startingY-88, y-startingY))
        if(startingY):
            return((startingY-88, y-startingY))
        else:
            raise "Error: Couldn't detect scrollbar position!"
        
    
    
    def filterNonStatsImagesAndCrop(self, cluster):
        newList = []
        for screenshot in cluster.screenshots:
            image = Image.open(os.path.join(self.path, screenshot.filename))
            if(self.isStatsScreenshot(image)):
                box = (91, 83, 663, 251)
                (screenshot.scrollPos, screenshot.thumbSize) = self.getScrollbarPosition(image)
                screenshot.croppedImage = image.crop(box)
                cluster.messages.append("File %s has been added to cluster. (Scrollbar pos: %i, Thumb size: %i)" % (screenshot.filename, screenshot.scrollPos, screenshot.thumbSize))
                newList.append(screenshot)
            else:
                #print cluster.screenshots
                #print screenshot
                #cluster.screenshots.remove(screenshot)
                #print cluster.screenshots
                #print "--------------------"
                self.increaseState()
                cluster.messages.append("File %s has been discarded, doesn't seem to be a stats screenshot." % (screenshot.filename))
        cluster.screenshots = newList
        for screenshot in cluster.screenshots:
            if(not screenshot.croppedImage):
                print "ERROR: %s" % (screenshot.filename)



    def getNextLine(self, lastY, dataSequence, width, steps):
        currentRow = lastY
        while(True):
            # calculate the new current row
            currentRow += steps
            
            # check whether all pixels in this row are either white or black
            allWhiteOrBlack = True
            for i in xrange(currentRow*width, (currentRow+1)*width):
                if(dataSequence[i] != (8, 8, 8) and dataSequence[i] != (255, 255, 255)):
                    allWhiteOrBlack = False
                    break
            
            # 
            if(not allWhiteOrBlack):
                currentLine = []
                for i in xrange(currentRow*width, (currentRow+1)*width):
                    currentLine.append(dataSequence[i])
                return((currentRow, tuple(currentLine)))
            


    def detectOverlap(self, topScreenshot, topHeight, bottomScreenshot):
        topData = topScreenshot.getdata()
        bottomData = bottomScreenshot.getdata()
        width = topScreenshot.size[0]
        height = topScreenshot.size[1]
        
        try:
            # find the first non-empty line in the top image that matches the one in the bottom image
            topSyncY = topHeight
            while(True):
                try:
                    (topSyncY, topLine) = self.getNextLine(lastY=topSyncY, dataSequence=topData, width=width, steps=-1)
                    #print "testing line %i in top image" % (topSyncY)

                    # find the first non-empty line in the bottom image from the bottom
                    bottomSyncY = -1
                    while(True):
                        (bottomSyncY, bottomLine) = self.getNextLine(lastY=bottomSyncY, dataSequence=bottomData, width=width, steps=+1)
                
                        # if they match...
                        if(topLine == bottomLine):
                            
                            # check that MIN_SYNC_LINES many lines match
                            #print "  seems to match with %i in bottom image, testing following lines (upwards)" % (bottomSyncY)
                            lastTopMatchY = topSyncY
                            lastBottomMatchY = bottomSyncY
                            allLinesMatch = True
                            for i in range(0, StatsMerger.MIN_SYNC_LINES):
                                (topMatchY, topLine) = self.getNextLine(lastY=lastTopMatchY, dataSequence=topData, width=width, steps=-1)
                                (bottomMatchY, bottomLine) = self.getNextLine(lastY=lastBottomMatchY, dataSequence=bottomData, width=width, steps=-1)
                                
                                # both the line content *and* the offset from the last line have to match!
                                if((topLine != bottomLine) or (topMatchY-lastTopMatchY != bottomMatchY-lastBottomMatchY)):
                                    allLinesMatch = False
                                    break
                                else:
                                    lastTopMatchY = topMatchY
                                    lastBottomMatchY = bottomMatchY

                            if(allLinesMatch):
                                #print "  successful!"
                                placementOffset = -(topHeight-topSyncY)     # negative offset = upwards movement!
                                return(placementOffset, bottomSyncY)

                except IndexError:
                    break

        # if this exception occurs, synching failed!
        except IndexError:
            return(None)
        
        
    
    def mergeScreenshots(self, cluster):
        # prepare a temporary image for storing the image parts in
        screenshots = cluster.screenshots
        partWidth = screenshots[0].croppedImage.size[0]
        partHeight = screenshots[0].croppedImage.size[1]
        innerImage = Image.new('RGB', (partWidth, partHeight*len(screenshots)))
#        DEBUGcounter = 0
        
        # iterate over all images in the cluster, determine their offset and paste them into the temporary image
        currentYPos = 0
        lastScreenshot = None
        for screenshot in screenshots:
            placementOffset = 0
            bottomOffset = 0

            # prepare the log message
            baseMessage = "Adding %s to the board... " % (screenshot.filename)
            
            # if this is the first image, it will get an offset of 0
            if(currentYPos == 0):
                cluster.messages.append(baseMessage + "first image.")
            
            # otherwise, we need to determine the offset by determining the overlap
            else:
                # we have a couple of different cases here, depending on the movement of the scrollbar:
                deltaBetweenScrollposAndExpectedScrollposOnPageScroll = screenshot.scrollPos - (lastScreenshot.scrollPos + lastScreenshot.thumbSize)
                baseMessage += "[scrollbar delta=%i] " % (deltaBetweenScrollposAndExpectedScrollposOnPageScroll)
                
                # a) the scrollbar moved more than one thumb size (+1 pixel, Alleg sometimes jumps a pixel),
                #    that usually means some lines are missing
                if(deltaBetweenScrollposAndExpectedScrollposOnPageScroll > 1):
                    cluster.messages.append(baseMessage + "scrollbars indicate that lines are missing, appending nevertheless, please verify final image!")
                    cluster.warnings += 1

                # b) the scrollbar moved one thumb size (+0/1 pixel, that's fine), that means we have page scrolling 
                elif(deltaBetweenScrollposAndExpectedScrollposOnPageScroll in range(0, 1+1)):
                    cluster.messages.append(baseMessage + "scrollbars look like page scrolling, appending without merging.")

                # c) 
                else:
                    offsets = self.detectOverlap(innerImage, currentYPos, screenshot.croppedImage)
                    if(offsets):
                        (placementOffset, bottomOffset) = offsets
                        cluster.messages.append(baseMessage + "scrollbars show overlap, merged successfully (overwriting last %i, offset of %i in bottom image)." % (placementOffset, bottomOffset))
                    else:
                        (placementOffset, bottomOffset) = (None, None)
                        cluster.messages.append(baseMessage + "scrollbars show overlap, merging failed, discarding this image!")
                        cluster.warnings += 1

            # now merge (the determined part of) the bottom image into the complete image
            # (this part is executed in all cases *except* a failed merge (i.e. in the cases of missing lines / page scrolling / detected overlap)!)
            if(bottomOffset != None):
                cluster.screenshotsUsed += 1
                cropBox = (0, bottomOffset, partWidth, partHeight)
                innerImage.paste(screenshot.croppedImage.crop(cropBox), (0, currentYPos+placementOffset))
#                innerImage.save("result%02i.png" % (DEBUGcounter))
#                DEBUGcounter += 1
                currentYPos += (partHeight + placementOffset - bottomOffset)
                lastScreenshot = screenshot
                
            # one step ahead
            self.increaseState()
            if(self.abortProcessing):
                raise AbortProcessing()
            
        # we're done, crop off the unused part and return
        cropBox = (0, 0, partWidth, currentYPos)
        return(innerImage.crop(cropBox))



    def getTableHeader(self, filename):
        image = Image.open(os.path.join(self.path, filename))
        box = (88, 63, 700, 82)
        return(image.crop(box))



    def getTeamStats(self, filename):
        image = Image.open(os.path.join(self.path, filename))
        box = (88, 276, 700, 409)
        teamStats = image.crop(box)
        rightBorder = teamStats.crop((591, 0, 612, teamStats.size[1]))
        teamStats.paste(rightBorder, (StatsMerger.FINAL_IMAGE_WIDTH - rightBorder.size[0], 0))
        return(teamStats.crop((0, 0, StatsMerger.FINAL_IMAGE_WIDTH, teamStats.size[1])))
    
    
    
    def createFinalImage(self, tableHeader, innerImage, teamStats, text):
        # determine some values
        innerWidth = innerImage.size[0]
        innerHeight = innerImage.size[1]
        totalWidth = self.statsScreenTopBorder.size[0]
        fontHeight = 20
        totalHeight = self.statsScreenTopBorder.size[1] + tableHeader.size[1] + innerHeight + self.statsScreenBottomBorder.size[1] + teamStats.size[1] + fontHeight
        
        # determine the Y positions of the image elements
        topBorderY = 0
        tableHeaderY = topBorderY + self.statsScreenTopBorder.size[1]
        playerStatsY = tableHeaderY + tableHeader.size[1]
        bottomBorderY = playerStatsY + innerImage.size[1]
        teamStatsY = bottomBorderY + self.statsScreenBottomBorder.size[1]
        textY = teamStatsY + teamStats.size[1]
        
        # create new image
        finalImage = Image.new('RGB', (totalWidth, totalHeight), color=(8, 8, 8))
        drawer = ImageDraw.Draw(finalImage)
        
        # add the top border
        finalImage.paste(self.statsScreenTopBorder, (0, topBorderY))
        
        # add the table header
        finalImage.paste(tableHeader, (0, tableHeaderY))
        
        # add the actual merged stats
        finalImage.paste(innerImage, (self.statsScreenLeftBorder.size[0], playerStatsY))

        # add the borders at the left and right side (WARNING: writes more than necessary to the bottom!)
        for i in xrange(0, (innerHeight / self.statsScreenLeftBorder.size[1])+1):
            thisSideBorderY = tableHeaderY + i * self.statsScreenLeftBorder.size[1]
            finalImage.paste(self.statsScreenLeftBorder, (0, thisSideBorderY))
            finalImage.paste(self.statsScreenRightBorder, (totalWidth - self.statsScreenRightBorder.size[0], thisSideBorderY))
            
        # add the bottom border
        finalImage.paste(self.statsScreenBottomBorder, (0, bottomBorderY))
        
        # draw the scrollbar
        finalImage.paste(self.scrollbarPointerUp, (StatsMerger.SCROLLBAR_X_POS, 32))
        artificialScrollbarHeight = innerHeight-12
        drawer.rectangle((StatsMerger.SCROLLBAR_X_POS+3, 38, StatsMerger.SCROLLBAR_X_POS+8, 38+artificialScrollbarHeight), outline=(255,255,255), fill=(255,255,255))
        finalImage.paste(self.scrollbarPointerDown, (StatsMerger.SCROLLBAR_X_POS, 38+artificialScrollbarHeight))

        # add the team stats
        finalImage.paste(teamStats, (0, teamStatsY))
        
        # print the info on the image
        font = ImageFont.truetype("arial.ttf", 10)
        textWidth = drawer.textsize(text, font=font)[0]
        drawer.text((totalWidth - textWidth - 10, textY + 2), text, fill=(255, 255, 255), font=font)
        
        # return the final image
        return(finalImage)



    def process(self):
        self.abortProcessing = False

        # step 1: get a sorted list of all screenshots in the given path
        screenshots = self.getListOfScreenshots()
        
        # step 2: determine screenshot clusters
        clusters = self.getClusters(screenshots)
        
        # determine the number of total operations (cutting and merging a screenshot is considered one operation each, so is creating a cluster (sorting, etc.) and merging the final image of each cluster
        self.initState(len(screenshots) + 2 * len(clusters))
        
        # early abort if requested
        if(self.abortProcessing):
            self.clusters = []
            return
        
        # step 3: analyse all the clusters now
        currentClusterIndex = 0
        try:
            for cluster in clusters:
                
                # step 3.1: filter non-stats images
                self.filterNonStatsImagesAndCrop(cluster)
                if(len(cluster.screenshots) == 0):
                    cluster.messages.append("Cluster discarded, no stats images remaining.")
                    self.increaseState()
                    self.increaseState()
                    continue
                
                # step 3.2: check that all scrollbars have the same thumbSize
                firstThumbSize = cluster.screenshots[0].thumbSize
                for screenshot in cluster.screenshots:
                    if(screenshot.thumbSize != firstThumbSize):
                        cluster.messages.append("Warning, not all screenshots in this cluster have the same scrollbar thumb size! Generating nevertheless, but the result is most likely incorrect!")
                        cluster.warnings += 1
                
                # step 3.3: sort by scrollbar position
                cluster.screenshots = sorted(cluster.screenshots, cmp=lambda x,y: cmp(x.scrollPos, y.scrollPos))
                self.increaseState()
                
                # DEBUG
                #counter = 0
                #for screenshot in cluster.screenshots:
                #    screenshot.croppedImage.save("image%i.png" % (counter))
                #    counter += 1
    
                # step 3.4: detect overlaps, determine offsets and merge images
                innerImage = self.mergeScreenshots(cluster)
                
                # we can delete the actual screenshot images now
                cluster.screenshots = None
                
                # step 3.5: get the table header and the team stats
                tableHeader = self.getTableHeader(cluster.firstImageFilename)
                teamStats = self.getTeamStats(cluster.firstImageFilename)
                
                # step 3.6: merge the images
                text = "created by %s v%s, game ended %s (local time)" % (settings.name, settings.versionNumber, cluster.getTimestampString())  
                cluster.mergedImage = self.createFinalImage(tableHeader, innerImage, teamStats, text)
                self.increaseState()
                
                # we need the current index in the cluster to abort properly
                currentClusterIndex += 1

                # abort if requested
                if(self.abortProcessing):
                    raise AbortProcessing()
                
                #cluster.mergedImage.save("result.png")
                #print "\n".join(cluster.messages)
                
            # if it wasn't aborted, all clusters are final now
            self.clusters = clusters
                
        except AbortProcessing:
            # if it was aborted, we need to cut off the unprocessed part
            self.clusters = clusters[:currentClusterIndex]


    
    def triggerAbort(self):
        self.abortProcessing = True


    
    def getResults(self):
        return(self.clusters)



    
if(__name__ == "__main__"):
    sm = StatsMerger("e:\\[Spiele]\\Allegiance", 60, None, None)
    clusters = sm.getResults()
    for cluster in clusters:
        print "\n".join(cluster.messages)
        print "----------------------------------"
        #cluster.mergedImage.save(cluster.getTitle() + ".png")
        print "saved as %s" % (cluster.getTitle() + ".png") 
        print "=================================="
