import ROOT
import os,sys
from ROOT import TGraphAsymmErrors
from ROOT import TGraphErrors
from ROOT import TColor
from array import array
from ROOT import *
from operator import truediv
import random
import math
import pandas
import os.path
import glob
import logging as log
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-b","--beginRun",help="first run to analyze [%default]",default=299918)
parser.add_argument("-e","--endRun",help="analyze stops when comes to this run [%default]",default=1000000)
parser.add_argument("-m","--mergeStat",help="option to switch on merging: measurement less than lumiChunk to be merged with next measurement [%default]",default=True)
parser.add_argument("-l","--lumiChunk",help="define statistics: measurement less than this to be merged with next measurement [%default]",default=10.)
parser.add_argument("-p","--parametrizeType",help="define parametrization: 1 is for extrapolation, 2 is for piece-wise function",default=1)
parser.add_argument("-s","--sizeChunk",help="define granularity: numbers of LS to be merged for one measurement [%default]",default=50)
parser.add_argument("-u","--microBarn",help="luminosity in input csv file is in microbarn",default=False)
parser.add_argument("-v","--verbose",help="increase logging level from INFO to DEBUG",default=False,action="store_true")
parser.add_argument("-c","--writeSummaryCSV",help="produce merged CSV with all runs",default=True)
parser.add_argument("-a","--dirCSV",help="where to write/store the CSV files",default="/eos/cms/store/group/comm_luminosity/ZCounting/csvFiles2018/")
parser.add_argument("-x","--dirEff",help="where to write/store efficiency Plots",default="/afs/cern.ch/user/j/jsalfeld/www/CMS-2018-ZRateData/ZAndMuonEfficiencies/RunsAndFits/")

args = parser.parse_args()
if args.verbose:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
else:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)

#ByLS csv inputs
#inFile="/afs/cern.ch/work/x/xniu/public/CMSSW_9_2_8/src/ZCountHarvest/CloneJob/2017LumiByLS_hfet_trig_PU.csv"
inFileList=glob.glob('/eos/cms/store/group/comm_luminosity/ZCounting/brilcalcFile2018/*csv')
inFileList.sort(key=os.path.getmtime)
inFile=inFileList[-1]
print "The brilcalc csv file: "+str(inFile)

#Data inputs
eosDir="/eos/cms/store/group/comm_luminosity/ZCounting/DQMFiles2018/cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/Run2018/SingleMuon/"

#MC inputs: to build MC*Gaussian template for efficiency fitting
mcDir="/afs/cern.ch/work/x/xniu/public/CMSSW_9_2_8/src/ZCountHarvest/LookupTable/"
mcShapeSubDir="MCFiles/92X_norw_IsoMu27_noIso/"

#Constant settings
secPerLS=float(23.3)
currentYear=2018
maximumLS=2500
chunkSize=int(args.sizeChunk)
lumiChunk=float(args.lumiChunk)
paraType=int(args.parametrizeType)
staFitChi2Th=2.     #threshold on chi2 to trigger protection mechanism
staFitEffThHi=0.999 #threshold on eff. to trigger protection mechanism
staFitEffThLo=0.95 #threshold on eff. to trigger protection mechanism

if args.microBarn:
    lumiChunk = lumiChunk*1000000.

log.info("Loading C marco...")
ROOT.gROOT.Macro( os.path.expanduser( '/afs/cern.ch/work/j/jsalfeld/Princeton/forZCounting2018/.rootlogon.C' ) )
ROOT.gROOT.LoadMacro("/afs/cern.ch/work/j/jsalfeld/Princeton/forZCounting2018/CMSSW_9_4_4/src/ZCounting/calculateDataEfficiency.C")
ROOT.gROOT.SetBatch(True)

log.info("Loading input byls csv...")
lumiFile=open(str(inFile))
lumiLines=lumiFile.readlines()
data=pandas.read_csv(inFile, sep=',',low_memory=False, skiprows=[0,len(lumiLines)-11,len(lumiLines)-10,len(lumiLines)-9,len(lumiLines)-8,len(lumiLines)-7,len(lumiLines)-6,len(lumiLines)-5,len(lumiLines)-4,len(lumiLines)-3,len(lumiLines)-2,len(lumiLines)-1,len(lumiLines)])
log.debug("%s",data.axes)
log.info("Loading input byls csv DONE...")

# TAKE INPUT CSV FILE AND STRUCTURE PER-RUN BASIS, THEN CREATE LIST OF LUMI AND LS`s PER RUN
LSlist=data.groupby('#run:fill')['ls'].apply(list)
if args.microBarn:
    recLumiList=data.groupby('#run:fill')['recorded(/ub)'].apply(list)
    delLumiList=data.groupby('#run:fill')['delivered(/ub)'].apply(list)
else:
    recLumiList=data.groupby('#run:fill')['recorded(/pb)'].apply(list)
    delLumiList=data.groupby('#run:fill')['delivered(/pb)'].apply(list)
avgpuList=data.groupby('#run:fill')['avgpu'].apply(list)
timeList=data.groupby('#run:fill')['time'].apply(list)

for i in range(0,len(LSlist)):	
	#print LSlist
	LSlist[i]=[int(x.split(':')[0]) for x in LSlist[i]]
fillRunlist=data.drop_duplicates('#run:fill')['#run:fill'].tolist()

log.debug("%s",fillRunlist)
log.debug("length LS list: %i",len(LSlist))
log.debug("length Run list: %i",len(fillRunlist))

log.info("Looping over runs...")
for run_i in range(0,len(fillRunlist)):

    run=int(fillRunlist[run_i].split(':')[0])
    fill=int(fillRunlist[run_i].split(':')[1])

    if run<int(args.beginRun) or run>=int(args.endRun):
        continue
    if run<299918:#Z Coungig module is enabled since this run 
	continue

    #check if run was processed already
    processedRun = glob.glob(args.dirEff+'Run'+str(run))
    if len(processedRun)>0:
        print "Run "+str(run)+" was already processed, skipping and going to next run"
        continue
    

    #era split follows here:https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmV2017Analysis#DATA

    log.info("===Running Run %i",run)
    log.info("===Running Fill %i",fill)
        
    LSchunks 	= [LSlist[run_i][x:x+chunkSize] for x in range(0, len(LSlist[run_i]), chunkSize)]
    Del_chunks  = [delLumiList[run_i][x:x+chunkSize] for x in range(0, len(delLumiList[run_i]), chunkSize)]
    Rec_chunks  = [recLumiList[run_i][x:x+chunkSize] for x in range(0, len(recLumiList[run_i]), chunkSize)]
    Avgpu_chunks = [avgpuList[run_i][x:x+chunkSize] for x in range(0, len(avgpuList[run_i]), chunkSize)]
    time_chunks = [timeList[run_i][x:x+chunkSize] for x in range(0, len(timeList[run_i]), chunkSize)]

    log.debug("===Pre-looping over LSchunks to fit current 2500 LS budget...")
    log.debug("===LSchunk lists before truncate: %s",LSchunks)
    for chunk_j in range(0,len(LSchunks)):
        if float(LSchunks[chunk_j][-1]) > maximumLS:
            log.warning("======Losing data after LS %i for Run%i",maximumLS,run)
            while LSchunks[chunk_j][-1] > maximumLS:
                del LSchunks[chunk_j][-1]
                del Del_chunks[chunk_j][-1]
                del Rec_chunks[chunk_j][-1]
                del Avgpu_chunks[chunk_j][-1]
                del time_chunks[chunk_j][-1]
            for chunk_k in range(chunk_j+1, len(LSchunks)):
                del LSchunks[-1] 
                del Del_chunks[-1]
                del Rec_chunks[-1]
                del Avgpu_chunks[-1]
                del time_chunks[-1]
            break
    log.debug("===LSchunk lists after truncate: %s",LSchunks)

    if args.mergeStat:
        log.debug("===Pre-looping over LSchunks to merge stat...")
        log.debug("===LSchunk lists before merge: %s",LSchunks)

  
        for chunk_i in range(0,len(LSchunks)):
            log.debug("======current ivalue = %i",chunk_i)
            log.debug("======current length = %i",len(LSchunks))

            if chunk_i == len(LSchunks):
                break

            log.debug("======current lumi   = %f",sum(Rec_chunks[chunk_i]))

            chunk_j = chunk_i
            currentLumi = sum(Rec_chunks[chunk_j])
            if currentLumi < lumiChunk:
                while currentLumi < lumiChunk and chunk_j < len(LSchunks)-1:
                    log.debug("========= current jvalue = %i",chunk_j)
                    log.debug("========= index to merge = %i",chunk_j+1)
                    log.debug("========= lumi  to merge = %f",sum(Rec_chunks[chunk_j+1]))
                    log.debug("========= lumi  total    = %f",currentLumi + sum(Rec_chunks[chunk_j+1]))

                    currentLumi += sum(Rec_chunks[chunk_j+1])
		    LSchunks[chunk_j]     = LSchunks[chunk_j]     + LSchunks[chunk_j+1]
                    Del_chunks[chunk_j]   = Del_chunks[chunk_j]   + Del_chunks[chunk_j+1]
                    Rec_chunks[chunk_j]   = Rec_chunks[chunk_j]   + Rec_chunks[chunk_j+1]
                    Avgpu_chunks[chunk_j] = Avgpu_chunks[chunk_j] + Avgpu_chunks[chunk_j+1]
                    time_chunks[chunk_j]  = time_chunks[chunk_j]  + time_chunks[chunk_j+1]

                    log.debug("========= merged LSchunk =%s",LSchunks[chunk_j])

                    del LSchunks[chunk_j+1]
                    del Del_chunks[chunk_j+1]
                    del Rec_chunks[chunk_j+1]
                    del Avgpu_chunks[chunk_j+1]
                    del time_chunks[chunk_j+1]
            else:
                log.debug("====== not merging index "),str(chunk_i)

    if args.mergeStat:
        log.debug("===LSchunk lists after merge: %s",LSchunks)

    log.debug("===Setting up arrays for output csv...")
    fillarray=array('d')
    beginTime=[]
    endTime=[]
    Zrate=array('d')
    instDel=array('d')
    lumiDel=array('d')
    pileUp=array('d')
    ZyieldDel=array('d')

    ZyieldRec=array('d')
    lumiRec=array('d')
    windowarray=array('d')
    deadTime=array('d')
    beginLS=array('i')
    endLS=array('i')

    HLTeffB=array('d')
    HLTeffE=array('d')
    SITeffB=array('d')
    SITeffE=array('d')
    StaeffB=array('d')
    StaeffE=array('d')

    ZMCeff=array('d')
    ZMCeffBB=array('d')
    ZMCeffBE=array('d')
    ZMCeffEE=array('d')

    ZBBeff=array('d')
    ZBEeff=array('d')
    ZEEeff=array('d')

    nMeasurements=0
    prevStaEffB=0.98
    prevStaEffE=0.98

    log.info("===Loading input DQMIO.root file...")
    eosFileList = glob.glob('/eos/cms/store/group/comm_luminosity/ZCounting/DQMFiles2018/cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/Run2018/SingleMuon/*/*'+str(run)+'*root')

    if not len(eosFileList)>0:
	print "The file does not yet exist for run: "+str(run)
	continue

    else:
	eosFile=eosFileList[0]

    print "The file exists: "+str(eosFile)+" for run  "+str(run)
    log.info("===Looping over LSchunks...")

    for chunk_i in range(0,len(LSchunks)):
        nMeasurements=nMeasurements+1

        log.info("======Running LSchunk No.%i",chunk_i)
        log.debug("======LS list: %s",LSchunks[chunk_i])

	recLumi_i = sum(Rec_chunks[chunk_i])
	delLumi_i = sum(Del_chunks[chunk_i])	
        deadtime_i = recLumi_i/delLumi_i

        if args.microBarn:
            recLumi_i = recLumi_i/1000000.
            delLumi_i = delLumi_i/1000000.

        log.debug("======RecLumi: %f",recLumi_i)
        log.debug("======DelLumi: %f",delLumi_i)
        log.debug("======DeadTime: %f",deadtime_i)


	avgPileup_i = sum(Avgpu_chunks[chunk_i])
	avgPileup_i = avgPileup_i/len(Avgpu_chunks[chunk_i])
        log.debug("======avgPU: %f",avgPileup_i)

	datestamp_low=time_chunks[chunk_i][0].split(" ")
	date_low=ROOT.TDatime(currentYear,int(datestamp_low[0].split("/")[0]),int(datestamp_low[0].split("/")[1]),int(datestamp_low[1].split(":")[0]),int(datestamp_low[1].split(":")[1]),int(datestamp_low[1].split(":")[2]))
        datestamp_up=time_chunks[chunk_i][-1].split(" ")
	date_up=ROOT.TDatime(currentYear,int(datestamp_up[0].split("/")[0]),int(datestamp_up[0].split("/")[1]),int(datestamp_up[1].split(":")[0]),int(datestamp_up[1].split(":")[1]),int(datestamp_up[1].split(":")[2]))
        timeWindow_i=(date_up.Convert()-date_low.Convert())+secPerLS
        log.debug("======time_chunks: %s",time_chunks[chunk_i])
        log.debug("======beginTime: %s",date_low.Convert())
        log.debug("======endTime: %s",date_up.Convert())
        log.debug("======timeWindow: %f",timeWindow_i)

        log.debug("Openning DQMIO.root file: %s", eosFile)
        HLTeffresB_i=ROOT.calculateDataEfficiency(0,str(eosFile),args.dirEff,str(run),chunk_i,LSchunks[chunk_i][0],LSchunks[chunk_i][-1],avgPileup_i,"HLT",0,0,0,0,0,recLumi_i)
        HLTeffresE_i=ROOT.calculateDataEfficiency(0,str(eosFile),args.dirEff,str(run),chunk_i,LSchunks[chunk_i][0],LSchunks[chunk_i][-1],avgPileup_i,"HLT",1,0,0,0,0,recLumi_i)
        SITeffresB_i=ROOT.calculateDataEfficiency(0,str(eosFile),args.dirEff,str(run),chunk_i,LSchunks[chunk_i][0],LSchunks[chunk_i][-1],avgPileup_i,"SIT",0,1,1,1,1,recLumi_i)#,mcDir+mcShapeSubDir+"MuStaEff/MC/probes.root",mcDir)
        SITeffresE_i=ROOT.calculateDataEfficiency(0,str(eosFile),args.dirEff,str(run),chunk_i,LSchunks[chunk_i][0],LSchunks[chunk_i][-1],avgPileup_i,"SIT",1,1,1,1,1,recLumi_i)#,mcDir+mcShapeSubDir+"MuStaEff/MC/probes.root",mcDir)
        StaeffresB_i=ROOT.calculateDataEfficiency(0,str(eosFile),args.dirEff,str(run),chunk_i,LSchunks[chunk_i][0],LSchunks[chunk_i][-1],avgPileup_i,"Sta",0,2,2,2,2,recLumi_i,mcDir+mcShapeSubDir+"MuStaEff/MC/probes.root",mcDir)
        StaeffresE_i=ROOT.calculateDataEfficiency(0,str(eosFile),args.dirEff,str(run),chunk_i,LSchunks[chunk_i][0],LSchunks[chunk_i][-1],avgPileup_i,"Sta",1,2,2,2,2,recLumi_i,mcDir+mcShapeSubDir+"MuStaEff/MC/probes.root",mcDir)
        Zyieldres_i=ROOT.calculateDataEfficiency(1,str(eosFile),args.dirEff,str(run),chunk_i,LSchunks[chunk_i][0],LSchunks[chunk_i][-1],avgPileup_i,"HLT",0,0,0,0,0)

        HLTeffB_i = HLTeffresB_i[0]
        HLTeffE_i = HLTeffresE_i[0]
        SITeffB_i = SITeffresB_i[0]
        SITeffE_i = SITeffresE_i[0]
        StaeffB_i = StaeffresB_i[0]
        StaeffE_i = StaeffresE_i[0]
        Zyield_i  = Zyieldres_i[0]

        if StaeffresB_i[3] > staFitChi2Th or StaeffresB_i[4] > staFitChi2Th or StaeffB_i >= staFitEffThHi or StaeffB_i <= staFitEffThLo:
            StaeffB_i = prevStaEffB
            log.warning("======Bad fit might happen, origin eff = %f, with chi2 = %f, %f",StaeffresB_i[0],StaeffresB_i[3],StaeffresB_i[4])
        else:
            prevStaEffB = StaeffB_i

        if StaeffresE_i[3] > staFitChi2Th or StaeffresE_i[4] > staFitChi2Th or StaeffE_i >= staFitEffThHi or StaeffE_i <= staFitEffThLo:
            StaeffE_i = prevStaEffE
            log.warning("======Bad fit might happen, origin eff = %f, with chi2 = %f, %f",StaeffresE_i[0],StaeffresE_i[3],StaeffresE_i[4])
        else:
            prevStaEffE = StaeffE_i


        log.debug("======perMuonEff: %f, %f ,%f, %f, %f, %f",HLTeffB_i,HLTeffE_i,SITeffB_i,SITeffE_i,StaeffB_i,StaeffE_i)
        log.debug("======ZRawYield: %f",Zyield_i)

	#ZtoMuMu efficiency purely from data
        ZBBEff=(StaeffB_i*StaeffB_i * SITeffB_i*StaeffB_i * (1-(1-HLTeffB_i)*(1-HLTeffB_i)))
        ZBEEff=(StaeffB_i*StaeffE_i * SITeffB_i*SITeffE_i * (1-(1-HLTeffB_i)*(1-HLTeffE_i)))
        ZEEEff=(StaeffE_i*StaeffE_i * SITeffE_i*StaeffE_i * (1-(1-HLTeffE_i)*(1-HLTeffE_i)))

	#ZtoMuMu efficiency correction as a parametrized function of pile-up
	#ZBBEffCorr = 0.00305155 + 0.000519427 * avgPileup_i
	#ZBEEffCorr = 0.00585766 + 0.000532229 * avgPileup_i
	#ZEEEffCorr = 0.0114659  + 0.00048351  * avgPileup_i

        ZBBEffCorr = 0
	ZBEEffCorr = 0
	ZEEEffCorr = 0

	if paraType == 1:
	    ZBBEffCorr = 0.00305155 + 0.000519427 * avgPileup_i
	    ZBEEffCorr = 0.00585766 + 0.000532229 * avgPileup_i
	    ZEEEffCorr = 0.0114659  + 0.00048351  * avgPileup_i
            #ZBBEffCorr = 0.0123732 + 0.000161345 * avgPileup_i
            #ZBEEffCorr = 0.00875762 + 0.000493846 * avgPileup_i
            #ZEEEffCorr = 0.0160629 + 0.000296308 * avgPileup_i

	if paraType == 2:
    	    if avgPileup_i < 50:
                ZBBEffCorr = 0.0123732 + 0.000161345 * avgPileup_i 
            else:
                ZBBEffCorr = -0.0878557 + 0.00218727 * avgPileup_i
     
            if avgPileup_i < 55:
                ZBEEffCorr = 0.00875762 + 0.000493846 * avgPileup_i
            else:
                ZBEEffCorr = -0.0600895 + 0.00179 * avgPileup_i
    
            if avgPileup_i < 40:
                ZEEEffCorr = 0.0160629 + 0.000296308 * avgPileup_i
            else:
                ZEEEffCorr = 0.00132398 + 0.000743008 * avgPileup_i

	#ZtoMuMu efficiency after correction 
	ZMCEffBB = ZBBEff - ZBBEffCorr 
	ZMCEffBE = ZBEEff - ZBEEffCorr
	ZMCEffEE = ZEEEff - ZEEEffCorr
	ZMCEff = (ZMCEffBB * 0.077904 + ZMCEffBE * 0.117200 + ZMCEffEE * 0.105541)/0.300644 
        log.debug("======ZToMuMuEff: %f",ZMCEff)
        log.debug("======ZToMuMuEff: %f, %f ,%f, %f, %f, %f",ZMCEffBB, ZMCEffBE, ZMCEffEE, ZBBEff, ZBEEff, ZEEEff)

	#End products
        ZXSec  = Zyield_i*(1-0.01)/(ZMCEff*recLumi_i)
        ZRate  = Zyield_i*(1-0.01)/(ZMCEff*timeWindow_i*deadtime_i)
        log.debug("======ZXSec: %f",ZXSec)
        log.debug("======ZRate: %f",ZRate)

	#Variables to write in csv file
        fillarray.append(fill)

	#datestamp_low=time_chunks[chunk_i][0].split(" ")
	#date_low=ROOT.TDatime(currentYear,int(datestamp_low[0].split("/")[0]),int(datestamp_low[0].split("/")[1]),int(datestamp_low[1].split(":")[0]),int(datestamp_low[1].split(":")[1]),int(datestamp_low[1].split(":")[2]))
        #datestamp_up=time_chunks[chunk_i][-1].split(" ")
	#date_up=ROOT.TDatime(currentYear,int(datestamp_up[0].split("/")[0]),int(datestamp_up[0].split("/")[1]),int(datestamp_up[1].split(":")[0]),int(datestamp_up[1].split(":")[1]),int(datestamp_up[1].split(":")[2]))


        beginTime.append(time_chunks[chunk_i][0])
        endTime.append(time_chunks[chunk_i][-1])
        Zrate.append(ZRate)
        instDel.append(delLumi_i/timeWindow_i)
        lumiDel.append(delLumi_i)
	pileUp.append(avgPileup_i)
        ZyieldDel.append(Zyield_i*(1-0.01)/(ZMCEff*deadtime_i))

	#Additional variables to write in efficiency csv file
        ZyieldRec.append(Zyield_i*(1-0.01))
        lumiRec.append(recLumi_i)
        windowarray.append(timeWindow_i)
        deadTime.append(deadtime_i)
        beginLS.append(LSchunks[chunk_i][0])
        endLS.append(LSchunks[chunk_i][-1])
	#Efficiency related
    	HLTeffB.append(HLTeffB_i)
    	HLTeffE.append(HLTeffE_i)
        SITeffB.append(SITeffB_i)
        SITeffE.append(SITeffE_i)
        StaeffB.append(StaeffB_i)
        StaeffE.append(StaeffE_i)

        ZMCeff.append(ZMCEff)
        ZMCeffBB.append(ZMCEffBB)
        ZMCeffBE.append(ZMCEffBE)
        ZMCeffEE.append(ZMCEffEE)

        ZBBeff.append(ZBBEff)
        ZBEeff.append(ZBEEff)
        ZEEeff.append(ZEEEff)

    ## Write Per Run CSV Files 
    print "Writing per Run CSV file"
    with open(args.dirCSV+'csvfile'+str(run)+'.csv','wb') as file:
        for c in range(0,nMeasurements):
		print str(int(fillarray[c]))+","+str(beginTime[c])+","+str(endTime[c])+","+str(Zrate[c])+","+str(instDel[c])+","+str(lumiDel[c])+","+str(ZyieldDel[c]) 
                file.write(str(int(fillarray[c]))+","+str(beginTime[c])+","+str(endTime[c])+","+str(Zrate[c])+","+str(instDel[c])+","+str(lumiDel[c])+","+str(ZyieldDel[c]))
		file.write('\n')

    with open(args.dirCSV+'effcsvfile'+str(run)+'.csv','wb') as file:
        for c in range(0,nMeasurements):
		print str(int(fillarray[c]))+","+str(beginTime[c])+","+str(endTime[c])+","+str(Zrate[c])+","+str(instDel[c])+","+str(lumiDel[c])+","+str(ZyieldDel[c]) 
                file.write(str(int(fillarray[c]))+","+str(beginTime[c])+","+str(endTime[c])+","+str(Zrate[c])+","+str(instDel[c])+","+str(lumiDel[c])+","+str(ZyieldDel[c])+","+str(beginLS[c])+","+str(endLS[c])+","+str(lumiRec[c])+","+str(windowarray[c])+","+str(HLTeffB[c])+","+str(HLTeffE[c])+","+str(SITeffB[c])+","+str(SITeffE[c])+","+str(StaeffB[c])+","+str(StaeffE[c])+","+str(ZMCeff[c])+","+str(ZMCeffBB[c])+","+str(ZMCeffBE[c])+","+str(ZMCeffEE[c])+","+str(ZBBeff[c])+","+str(ZBEeff[c])+","+str(ZEEeff[c])+","+str(pileUp[c]))
                file.write('\n')


## Write Big CSV File
print "Writing overall CSV file"
if args.writeSummaryCSV:
	rateFileList=sorted(glob.glob(args.dirCSV+'csvfile*.csv'))	
	with open(args.dirCSV+'Mergedcsvfile.csv','w') as file:
		file.write("fill,beginTime,endTime,ZRate,instDelLumi,delLumi,delZCount")
		file.write('\n')
		print "There are "+str(len(rateFileList))+" runs in the directory"
		for m in range(0,len(rateFileList)):						
			print "producing now csv file: "+rateFileList[m]
			try:
				iterF=open(rateFileList[m])
				lines=iterF.readlines()
				for line in lines:
					element=line.split(',')
					if element[3]=="nan" or element[3]=="0.0" or element[3]=="-0.0" or element[3]=="inf":
						continue
					file.write(line)
			except IOError as err:
    				print err.errno 
                                print err.strerror
				continue

        effFileList=sorted(glob.glob(args.dirCSV+'effcsvfile*.csv'))
	print "Starting to write efficiency files."	
        with open(args.dirCSV+'Mergedeffcsvfile.csv','wb') as fileTwo:
		fileTwo.write("fill,beginTime,endTime,ZRate,instDelLumi,delLumi,delZCount,beginLS,endLS,lumiRec,windowarray,HLTeffB,HLTeffE,SITeffB,SITeffE,,StaeffB,StaeffE,ZMCeff,ZMCeffBB,ZMCeffBE,ZMCeffEE,ZBBeff,ZBEeff,ZEEeff,pileUp")
		fileTwo.write('\n')
		for m in range(0,len(effFileList)):

			print "producing now eff csv file: "+rateFileList[m]
			try:
				iterF=open(effFileList[m])
				lines=iterF.readlines()
				for line in lines:
					element=line.split(',')
					if element[3]=="nan" or element[3]=="0.0" or element[3]=="-0.0" or element[3]=="inf":
						continue
					fileTwo.write(line)
                        except IOError as err:
				print err.errno 
                                print err.strerror
                                continue
