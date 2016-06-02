#! /usr/bin/env python

import xml.etree.ElementTree as ET
import numpy
import matplotlib.pyplot as pylab

from scipy.ndimage.interpolation import shift

from matplotlib.collections import PolyCollection
from matplotlib.colors import colorConverter
from mpl_toolkits.mplot3d import Axes3D

import Tkinter
############################################
############################################
##Global variables

layersNames = []
refLayersNames = []
iRefLayer = 0

layerToPlot = [0,0,0,0,0,0,2,2,2,2,1,1,1,1,1,3,3,3]
layerToMeanDistPhiPlot = [0,1,0,1,0,1,2,2,2,2,3,3,3,3,3,4,4,4]
layerColors = ["b","g","r","c","m","y","b","g","r","c","m","b","g","r","c","b","g","r"]
addMeanDistPhi = False
plotTwoPt = False
############################################
############################################
def parsePatternsXML(fname):

    tree = ET.parse(fname)
    root = tree.getroot()

    goldenPatterns = root.findall("GP")
    ptCodes = getPtCodes(goldenPatterns)

    maxPtCode = ptCodes[len(ptCodes)-1]
    nCharges = 2
    nLayers = 18
    nRefLayers = 8
    nPdfBins = 128
    pdfArray = numpy.ndarray(shape=(maxPtCode+1, nCharges, nLayers, nRefLayers, nPdfBins), dtype=int)
    meanDistPhiArray = numpy.ndarray(shape=(maxPtCode+1, nCharges, nLayers, nRefLayers), dtype=int)

    pdfArray.fill(999)
    meanDistPhiArray.fill(999)

    for aGP in goldenPatterns:
        iCharge = (int(aGP.attrib["iCharge"])+1)/2        
        iLayer = 0
        for aLayer in aGP.findall("Layer"):
            #Parse mean dist phi
            iRefLayer = 0 
            for aRefLayer in aLayer.findall("RefLayer"):            
                for index in xrange(1,5):
                    iPtCode = int(aGP.attrib["iPt"+str(index)])
                    if iPtCode!=0:
                        meanDistPhiArray[iPtCode,iCharge,iLayer,iRefLayer] = int(aRefLayer.attrib["meanDistPhi"])
                iRefLayer+=1
            #Parse pdf values
            iBin = 0    
            for aPDF in aLayer.findall("PDF"):
                iRefLayer = iBin/128
                for index in xrange(1,5):
                    iPtCode = int(aGP.attrib["iPt"+str(index)])
                    if iPtCode!=0:
                        pdfArray[iPtCode,iCharge,iLayer,iRefLayer,iBin%128] = aPDF.attrib["value"+str(index)]
                iBin+=1
            iLayer+=1
    
    return ptCodes,meanDistPhiArray, pdfArray
############################################
############################################
def parseConnectionsXML(fname):

    tree = ET.parse(fname)
    root = tree.getroot()

    layers = root.findall("LayerMap")
    refLayers = root.findall("RefLayerMap")

    layersNames = []
    refLayersNames = []
    
    for aLayer in layers:
        layersNames.append(aLayer.attrib["hwName"])

    for aRefLayer in refLayers:
        refLayersNames.append(layersNames[int(aRefLayer.attrib["logicNumber"])])

    return layersNames, refLayersNames
############################################
############################################
def readEventFromXML(fname):

    tree = ET.parse(fname)
    root = tree.getroot()

    events = root.findall("Event")

    nProcessors = 6
    nLayers = 18
    nHitsInLayer = 2
    nCandidates = 3
    eventData =  numpy.ndarray(shape=(nProcessors, nLayers, nHitsInLayer), dtype=int)
    candidateData =  numpy.ndarray(shape=(nProcessors, nCandidates), dtype=int)
    eventData.fill(999)

    for aEvent in events:
        bx = aEvent.findall("bx")
        processors = bx[0].findall("Processor")
        for aProcessor in processors:
            iProcessor = int(aProcessor.attrib["iProcessor"])
            layers = aProcessor.findall("Layer")
            for aLayer in layers:
                iLayer = int(aLayer.attrib["iLayer"])
                hits = aLayer.findall("Hit")
                iHit = 0
                for aHit in hits:
                    iPhi = aHit.attrib["iPhi"]
                    eventData[iProcessor,iLayer,iHit] = iPhi
                    iHit+=1
            algoMuons = aProcessor.findall("AlgoMuon")
            iCandidate = 0
            for algoMuon in algoMuons:
                discriminator = algoMuon.attrib["disc"]
                candidateData[iProcessor,iCandidate] = discriminator
                
                    
        print eventData
        return

############################################
############################################
def getPtCodes(goldenPatterns):

    ptCodes = []
    for aGP in goldenPatterns:
        for iIndex in xrange(1,5):
            iPtCode = int(aGP.attrib["iPt"+str(iIndex)])
            iCharge = int(aGP.attrib["iCharge"])
            if iPtCode!=0 and iCharge==1:
                ptCodes.append(iPtCode)
    return ptCodes
############################################
############################################
def destroy(mainWindow):
    pylab.close("all")
    mainWindow.destroy()
############################################
############################################
def setRefLayer(index):
    global iRefLayer
    iRefLayer = index
############################################
############################################
def toggleAddMeanDistPhi():
    global addMeanDistPhi
    addMeanDistPhi = not addMeanDistPhi
############################################
############################################
def togglePlotTwoPt():
    global plotTwoPt
    plotTwoPt = not plotTwoPt
############################################
############################################
def plotMeanDistPhi(iRefLayer):

    title = "Ref layer: "+refLayersNames[iRefLayer]
    f, axarr = pylab.subplots(5,sharex=True,sharey=False,num=title,figsize=(8,12))

    iChargeIndex = 0
    iLayer = 1
    iSubPlot = 0

    for iLayer  in xrange(0,18):
        iSubPlot = layerToMeanDistPhiPlot[iLayer]
        for iCharge in xrange(-1,2,2):
            iChargeIndex = (iCharge+1)/2
            aArray = meanDistPhiArray[:,iChargeIndex,iLayer,iRefLayer]
            filteredIndexes = numpy.where(aArray!=999)
            aFilteredArray = aArray[filteredIndexes]
            axarr[iSubPlot].plot(aFilteredArray,linewidth=5,label=layersNames[iLayer]+" "+str(iCharge))        
        axarr[iSubPlot].legend(bbox_to_anchor=(1.05, 1), loc='upper left', shadow=False, fontsize='x-large')
    ##############################

    f.subplots_adjust(hspace=0,left=0.05, right=0.7, top=0.99, bottom=0.05)
    pylab.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)

    fname = "RefLayer_"+refLayersNames[iRefLayer].replace('/','.')+".png"
    pylab.savefig(fname)
    
    pylab.show()
############################################
############################################
def plotPtCode(iPt, iCharge, iRefLayer):

    if plotTwoPt:
         plotTwoPtCodes(iPt, iCharge, iRefLayer)
         return

    iChargeIndex = (iCharge+1)/2
    
    
    title = "PtCode = "+str(iPt)+" charge="+str(iCharge)+" ref layer: "+refLayersNames[iRefLayer]
    f, axarr = pylab.subplots(4,sharex=True,sharey=True,num=title,figsize=(8,12))

    for iLayer in xrange(0,18):
        if addMeanDistPhi:
            shiftedPdf = shift(pdfArray[iPt,iChargeIndex,iLayer,iRefLayer], meanDistPhiArray[iPt,iChargeIndex,iLayer,iRefLayer], cval=0)
        else:
            shiftedPdf = pdfArray[iPt,iChargeIndex,iLayer,iRefLayer]        
        axarr[layerToPlot[iLayer]].plot(shiftedPdf,linewidth=5,label=layersNames[iLayer],drawstyle='steps-mid')

    for iPlot in xrange(0,4):
        axarr[iPlot].legend(bbox_to_anchor=(1.05, 1),loc='upper left', shadow=False, fontsize='x-large')
    
    f.subplots_adjust(hspace=0,left=0.05, right=0.7, top=0.99, bottom=0.05)
    pylab.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)

    fname = "PtCode_"+str(iPt)+"_charge_"+str(iCharge)+"_RefLayer_"+refLayersNames[iRefLayer].replace('/','.')+".png"
    pylab.savefig(fname)
    pylab.xlabel('bin number')
    pylab.ylabel('digitized pdf value')
    pylab.show()
############################################
############################################
def plotTwoPtCodes(iPt, iCharge, iRefLayer):

    iChargeIndex = (iCharge+1)/2
    
    yValues = range(0,11)
    layerToYValue = [10, 0, 1, 11, 12, 2, 3, 13, 14, 4, 5]

    title = "PtCode = "+str(iPt)+" charge="+str(iCharge)+" ref layer: "+refLayersNames[iRefLayer]
    figure, axesArray = pylab.subplots(1,sharex=True,sharey=True,num=title,figsize=(8,12))
    
    for yValue in yValues:
        iLayer = layerToYValue[yValue]
        shiftedPdf = shift(pdfArray[iPt,iChargeIndex,iLayer,iRefLayer], meanDistPhiArray[iPt,iChargeIndex,iLayer,iRefLayer], cval=0)
        shiftedPdf+=yValue*63
        axesArray.plot(shiftedPdf,linewidth=5,color='red',label=layersNames[iLayer],drawstyle='steps-mid')
        iPtSecond = 5*2+1
        shiftedPdf = shift(pdfArray[iPtSecond,iChargeIndex,iLayer,iRefLayer], meanDistPhiArray[iPtSecond,iChargeIndex,iLayer,iRefLayer], cval=0)
        shiftedPdf+=yValue*63
        axesArray.plot(shiftedPdf,linewidth=5,color='blue',label=layersNames[iLayer],drawstyle='steps-mid')
        axesArray.text(141, yValue*63+30, layersNames[iLayer])
        
    pylab.setp([a.get_xticklabels() for a in figure.axes[:-1]], visible=False)
    pylab.xlabel('bin number')
    pylab.title('')

    pylab.show()
############################################
############################################
def createButtons(mainWindow):
    
    buttons = []

    nPtCodes = len(ptCodes)

    ##Columns labels 
    text = Tkinter.Text(mainWindow, height=1, width=40)
    text.insert(Tkinter.INSERT, "Pt [GeV]")
    text.insert(Tkinter.END, "                ")
    text.insert(Tkinter.END, "Ref. layer")
    text.tag_add("ptLabel", "1.0", "1.8")
    text.tag_add("refLayerLabel", "1.24", "1.42")
    text.tag_config("ptLabel", background="sky blue")
    text.tag_config("refLayerLabel", background="yellow")    
    text.pack()
    
    #Buttons selecting pt code to be drawn
    index = 0
    for aPtCode in ptCodes:
        button = Tkinter.Button(mainWindow, text=str((aPtCode-1)/2.0)+"+", bg="sky blue",command = lambda ptCode=aPtCode: plotPtCode(ptCode,1,iRefLayer))
        button.pack()
        button.place(relx=0.03,rely=0.05+index*(0.95/nPtCodes), relwidth=0.33)   
        buttons.append(button)
        button = Tkinter.Button(mainWindow, text=str((aPtCode-1)/2.0)+"-", bg="sky blue",command =  lambda ptCode=aPtCode: plotPtCode(ptCode,-1,iRefLayer))
        button.pack()
        button.place(relx=0.37,rely=0.05+index*(0.95/nPtCodes), relwidth=0.33)   
        buttons.append(button)
        index+=1

    #Buttons selecting reference layer to be drawn
    for index in xrange(0,8):                    
        button = Tkinter.Button(mainWindow, text=refLayersNames[index],bg="yellow",command = lambda iRefLayer = index: setRefLayer(iRefLayer))
        button.pack()
        button.place(relx=0.7, rely=0.05+index*(0.95/nPtCodes), relwidth=0.35)

    button= Tkinter.Button(mainWindow, wraplength=80, text="Toggle add mean dist. phi",bg="pale green",command=lambda :toggleAddMeanDistPhi())
    button.pack()
    button.place(relx=0.7, rely=0.05+10*(0.95/nPtCodes), relwidth=0.3)
        
    button= Tkinter.Button(mainWindow,wraplength=80, text="Plot mean dist. phi",bg="pale green",command=lambda :plotMeanDistPhi(iRefLayer))
    button.pack()
    button.place(relx=0.7, rely=0.05+12*(0.95/nPtCodes), relwidth=0.3)

    button= Tkinter.Button(mainWindow, wraplength=80, text="Toggle plot two pt",bg="green",command=lambda :togglePlotTwoPt())
    button.pack()
    button.place(relx=0.7, rely=0.05+14*(0.95/nPtCodes), relwidth=0.3)
        
    button= Tkinter.Button(mainWindow,text="EXIT",bg="red",command=lambda: destroy(mainWindow))
    button.pack()
    button.place(relx=0.7, rely=0.05+10*(2.0/nPtCodes), relwidth=0.3)
############################################
############################################
def main():

    #Load data from XML and saveto picled txt file
    patternsXMLFileName = "Patterns_0x0003.xml"
    connectionsXMLFileName = "hwToLogicLayer_0x0003.xml"
    eventDataFileName = "TestData.xml"
    
    #readEventFromXML(eventDataFileName)
    #return

    global layersNames
    global refLayersNames
    global ptCodes
    global meanDistPhiArray
    global pdfArray
    
    ptCodes, meanDistPhiArray, pdfArray = parsePatternsXML(patternsXMLFileName)
    layersNames, refLayersNames = parseConnectionsXML(connectionsXMLFileName)
    numpy.savez('GPs',ptCodes, meanDistPhiArray, pdfArray)

    #ptCodes = numpy.load('GPs.npz')['arr_1']
    #meanDistPhiArray = numpy.load('GPs.npz')['arr_1']
    #pdfArray = numpy.load('GPs.npz')['arr_2']

    mainWindow = Tkinter.Tk()
    mainWindow.geometry("250x900")
    createButtons(mainWindow)
    mainWindow.mainloop()

################################################
################################################
if __name__ == "__main__":
    main()
