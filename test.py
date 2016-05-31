#! /usr/bin/env python

import xml.etree.ElementTree as ET
import numpy
import matplotlib.pyplot as pylab

from scipy.ndimage.interpolation import shift

import Tkinter
############################################
############################################
def readPdfFromXML(fname):

    tree = ET.parse(fname)
    root = tree.getroot()

    #aGP = root.findall(".//Layer/..[@iPt='"+str(iPt)+"']")[0]
    #aLayer = aGP.findall(".//*[@iLayer='0']")[0]
    #aPDF =  aGP.findall(".//PDF")

    aPDF =  root.findall(".//PDF")

    tmpList = []
    for child in aPDF:
        tmpList.append(int(child.attrib['value1']))
        
    pdfAllLayers = numpy.asarray(tmpList)
    pdf=numpy.reshape(pdfAllLayers,(nPtCodes,18,8,128))
    return pdf    
############################################
############################################
def readEventFromXML(fname):

    tree = ET.parse(fname)
    root = tree.getroot()

    #aGP = root.findall(".//Layer/..[@iPt='"+str(iPt)+"']")[0]
    #aLayer = aGP.findall(".//*[@iLayer='0']")[0]
    #aPDF =  aGP.findall(".//PDF")

    events = []
    eventData = {}

    aBX =  root.findall(".//bx")
    for aItem in aBX:
        aProc = list(aItem)
        if len(aProc):
            print "Event number: ",int(aItem.attrib["iBx"])/2
            eventData = {}
            for aItem1 in aProc:                
                aLayerData = list(aItem1)
                print "Processor number: ",aItem1.attrib["iProcessor"]
                for aItem2 in aLayerData:           
                    if  aItem2.tag=="Layer":
                        #print aItem2.tag, aItem2.attrib
                        aHitsData = list(aItem2)
                        for aItem3 in aHitsData:       
                            print "iLayer: ",aItem2.attrib["iLayer"], "iPhi ",aItem3.attrib["iPhi"]
                            eventData[aItem2.attrib["iLayer"]] = aItem3.attrib["iPhi"]
                    if  aItem2.tag=="AlgoMuon":
                        print aItem2.tag, aItem2.attrib
                        plotPtCode(int(aItem2.attrib["ptCode"]),
                                   int(aItem2.attrib["charge"]),
                                   int(aItem2.attrib["iRefLayer"]),
                                   eventData)                        
                        break
            events.append(eventData)     
############################################
############################################
def readMeanDistPhiFromXML(fname):

    tree = ET.parse(fname)
    root = tree.getroot()

    aMeanDistPhi =  root.findall(".//RefLayer")

    tmpList = []
    for child in aMeanDistPhi:
        tmpList.append(int(child.attrib['meanDistPhi']))
        
    allLayers = numpy.asarray(tmpList)
    meanDistPhi=numpy.reshape(allLayers,(nPtCodes,18,8))
    return meanDistPhi   
############################################
############################################


refLayers = ["MB1", "RE2", "MB2", "RE1/3", "RPCE2", "MB3", "RPC1in", "RPC1out"]
#refLayers = ["MB1", "MB2", "MB3", "MB4", "RPC1in", "RPC1out", "RPC2in", "RPC2out"]

refToLogicLayers = [0,7,2,6,16,4,10,11]


layerToPlot = [0,0,0,0,0,0,2,2,2,2,1,1,1,1,1,3,3,3]
layerColors = ["b","g","r","c","m","y","b","g","r","c","m","b","g","r","c","b","g","r"]
layersLabels = ["MB1", "MB1 bend.", "MB2", "MB2 bend.", "MB3", "MB3 bend.", "RPC1in", "RPC1out", "RPC2in", "RPC2out", "RPC3", "CSC ME1.3", "CSC ME2", "CSC ME3", "CSC ME1.2", "RPC E1", "RPC E2", "RPC E3"]
############################################
############################################
def plotPtCode(iPt, iCharge, iRefLayer, eventData={}):

    iPt = (31-iPt)*2+(iCharge==1)
    
    title = "PtCode = "+str(iPt)+" charge="+str(iCharge)+" ref layer: "+refLayers[iRefLayer]
    print title
 
    f, axarr = pylab.subplots(4,sharex=True,sharey=True,num=title,figsize=(8,12))

    ##DT layers
    for iLayer in xrange(0,6):
        shiftedPdf = shift(pdf[iPt,iLayer,iRefLayer], meanDistPhi[iPt,iLayer,iRefLayer], cval=0)
        axarr[0].plot(shiftedPdf,linewidth=5,label=layersLabels[iLayer])
    axarr[0].legend(loc='upper right', shadow=False, fontsize='x-large')

    #Barrel RPC layers
    for iLayer in xrange(6,11):
        shiftedPdf = shift(pdf[iPt,iLayer,iRefLayer], meanDistPhi[iPt,iLayer,iRefLayer], cval=0)
        axarr[1].plot(shiftedPdf,linewidth=5,label=layersLabels[iLayer])
    axarr[1].legend(loc='upper right', shadow=False, fontsize='x-large') 

    #CSC layers
    for iLayer in xrange(11,15):
        shiftedPdf = shift(pdf[iPt,iLayer,iRefLayer], meanDistPhi[iPt,iLayer,iRefLayer], cval=0)
        axarr[2].plot(shiftedPdf,linewidth=5,label=layersLabels[iLayer])
    axarr[2].legend(loc='upper right', shadow=False, fontsize='x-large') 
    
    #Endcap RPC layers
    for iLayer in xrange(15,18):
        shiftedPdf = shift(pdf[iPt,iLayer,iRefLayer], meanDistPhi[iPt,iLayer,iRefLayer], cval=0)
        axarr[3].plot(shiftedPdf,linewidth=5,label=layersLabels[iLayer])
    axarr[3].legend(loc='upper right', shadow=False, fontsize='x-large') 
    

    llh = 0
    if(len(eventData)):
        for iLayer,aHit in eventData.iteritems():
            refPhi = eventData[str(refToLogicLayers[iRefLayer])]
            phiMean = meanDistPhi[index,int(iLayer),iRefLayer]
            if(int(iLayer)==1 or int(iLayer)==3 or int(iLayer)==5):
                refPhi = "0"
            phi = int(aHit) - int(refPhi) - int(phiMean) + 64
            print "iLayer: ",iLayer,"phiHit: ",aHit," refPhi: ",refPhi," phiMean: ",phiMean," pdf index: ",phi," llh: ",pdf[index,int(iLayer),iRefLayer,phi]
            axarr[layerToPlot[int(iLayer)]].plot(phi,40,marker="o",markersize=10,color=layerColors[int(iLayer)],label="Hit")
            if(phi>=0 and phi<128):
                llh+=pdf[index,int(iLayer),iRefLayer,phi]       
        print "llh: ",llh
    
    f.subplots_adjust(hspace=0,left=0.05, right=0.99, top=0.99, bottom=0.05)
    pylab.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)

    fname = "PtCode_"+str(iPt)+"_charge_"+str(iCharge)+"_RefLayer_"+refLayers[iRefLayer]+".png"
    pylab.savefig(fname)
    pylab.xlabel('bin number')
    pylab.ylabel('digitized pdf value')

    pylab.show() 
############################################
iRefLayer = 0
############################################
def plotMeanDistPhi(iRefLayer):

    title = "Ref layer: "+refLayers[iRefLayer]
    f, axarr = pylab.subplots(5,sharex=True,sharey=False,num=title,figsize=(8,12))

    print title
    
    axarr[0].plot(meanDistPhi[:,0,iRefLayer],linewidth=5,label="MB1")
    axarr[0].plot(meanDistPhi[:,2,iRefLayer],linewidth=5,label="MB2")
    axarr[0].plot(meanDistPhi[:,4,iRefLayer],linewidth=5,label="MB3")
    axarr[0].legend(loc='upper right', shadow=False, fontsize='x-large') 

    axarr[1].plot(meanDistPhi[:,1,iRefLayer],linewidth=5,label="MB1 dev")
    axarr[1].plot(meanDistPhi[:,3,iRefLayer],linewidth=5,label="MB2 dev")
    axarr[1].plot(meanDistPhi[:,5,iRefLayer],linewidth=5,label="MB3 dev")
    axarr[1].legend(loc='upper right', shadow=False, fontsize='x-large') 
    
    axarr[2].plot(meanDistPhi[:,6,iRefLayer],linewidth=5,label="ME1/3")
    axarr[2].plot(meanDistPhi[:,7,iRefLayer],linewidth=5,label="ME2")
    axarr[2].plot(meanDistPhi[:,8,iRefLayer],linewidth=5,label="ME3")
    axarr[2].plot(meanDistPhi[:,9,iRefLayer],linewidth=5,label="ME1/2")
    axarr[2].legend(loc='upper right', shadow=False, fontsize='x-large') 

    axarr[3].plot(meanDistPhi[:,10,iRefLayer],linewidth=5,label="RPC1in")
    axarr[3].plot(meanDistPhi[:,11,iRefLayer],linewidth=5,label="RPC1out")
    axarr[3].plot(meanDistPhi[:,12,iRefLayer],linewidth=5,label="RPC2in")
    axarr[3].plot(meanDistPhi[:,13,iRefLayer],linewidth=5,label="RPC2out")
    axarr[3].plot(meanDistPhi[:,14,iRefLayer],linewidth=5,label="RPC3")
    axarr[3].legend(loc='upper right', shadow=False, fontsize='x-large') 

    axarr[4].plot(meanDistPhi[:,15,iRefLayer],linewidth=5,label="RPC E1")
    axarr[4].plot(meanDistPhi[:,16,iRefLayer],linewidth=5,label="RPC E2")
    axarr[4].plot(meanDistPhi[:,17,iRefLayer],linewidth=5,label="RPC E3")
    axarr[4].legend(loc='upper right', shadow=False, fontsize='x-large')  


    print iRefLayer,meanDistPhi[:,15,iRefLayer]
    iRefLayer = 5
    print iRefLayer,meanDistPhi[:,15,iRefLayer]
    iRefLayer = 3
    print iRefLayer,meanDistPhi[:,15,iRefLayer]

    f.subplots_adjust(hspace=0,left=0.05, right=0.99, top=0.99, bottom=0.05)
    pylab.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)

    #fname = "RefLayer_"+refLayers[iRefLayer]+".png"
    #pylab.savefig(fname)
    pylab.draw()
    pylab.show()
############################################
############################################
def setRefLayer(iTmp):
    global iRefLayer
    iRefLayer = iTmp
############################################
############################################
def destroy(top):
    pylab.close("all")
    top.destroy()
############################################
############################################
def addButtons():
    buttons = []
    ptCode = [0]
    for index in xrange(0,nPtCodes/2):
        ptCode = (31-index)
        button = Tkinter.Button(top, text =str(ptCode)+"+", command = lambda ptCode=ptCode: plotPtCode(ptCode,1,iRefLayer))
        button.pack()
        button.place(relx=0.03,rely=0.05+index*(0.95*2.0/nPtCodes), relwidth=0.3)   
        buttons.append(button)
        button = Tkinter.Button(top, text =str(ptCode)+"-", command =  lambda ptCode=ptCode: plotPtCode(ptCode,-1,iRefLayer))
        button.pack()
        button.place(relx=0.37,rely=0.05+index*(0.95*2.0/nPtCodes), relwidth=0.3)   
        buttons.append(button)

        
    for index in xrange(0,8):                    
        button = Tkinter.Button(top, text=refLayers[index],command = lambda iRefLayer = index: setRefLayer(iRefLayer))
        button.pack()
        button.place(relx=0.7, rely=0.05+index*(2.0/nPtCodes), relwidth=0.3)

    button= Tkinter.Button(top,text="MeanDist",command=lambda :plotMeanDistPhi(iRefLayer))
    button.pack()
    button.place(relx=0.7, rely=0.05+8*(2.0/nPtCodes), relwidth=0.3)
        
    button= Tkinter.Button(top,text="Exit",command=lambda: destroy(top))
    button.pack()
    button.place(relx=0.7, rely=0.05+10*(2.0/nPtCodes), relwidth=0.3)
        
############################################
############################################ 
  
#Load data from XML and saveto picled txt file
fname = "Patterns.xml"

nPtCodes = 52

###Comment this when loading the data from numpy file
#pdf = readPdfFromXML(fname)
#meanDistPhi = readMeanDistPhiFromXML(fname)
#numpy.savez('GPs',pdf,meanDistPhi)
##############################################

##Uncomment this when loading data from numpy file
pdf = numpy.load('GPs.npz')['arr_0']
meanDistPhi = numpy.load('GPs.npz')['arr_1']
###############################################

##Uncommnet this is you want to plot reconstructed events on top of the pdf
#fname = "TestData.xml"
#readEventFromXML(fname)
###############################################

top = Tkinter.Tk()
top.geometry("150x900")
addButtons()

top.mainloop()



