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

inFile="/eos/cms/store/group/comm_luminosity/ZCounting/2017LumiByLS_trig.csv"
chunkSize=50
eosDir="/eos/cms/store/group/comm_luminosity/ZCounting/DQMFiles2017/cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/Run2017/SingleMuon/"

HLTeff=array('d')
SITeff=array('d')
Staeff=array('d')
crossX=array('d')


Zyield=array('d')
Zrate=array('d')
lumiDel=array('d')
instDel=array('d')
beginTime=[]
endTime=[]
fillarray=array('d')
windowarray=array('d')

ROOT.gROOT.Macro( os.path.expanduser( '~/.rootlogon.C' ) )
ROOT.gROOT.LoadMacro("calculateDataEfficiency_v2.C")
ROOT.gROOT.SetBatch(True)

#lumiFile=open("./run302031.csv")
#lumiLines=lumiFile.readlines()
#data=pandas.read_csv("./run302031.csv",sep=',',low_memory=False, skiprows=[0,len(lumiLines)-5,len(lumiLines)-4,len(lumiLines)-3,len(lumiLines)-2,len(lumiLines)-1,len(lumiLines)])

lumiFile=open(inFile)
lumiLines=lumiFile.readlines()
data=pandas.read_csv(inFile, sep=',',low_memory=False, skiprows=[0,len(lumiLines)-5,len(lumiLines)-4,len(lumiLines)-3,len(lumiLines)-2,len(lumiLines)-1,len(lumiLines)])

print data.axes

# TAKE INPUT CSV FILE AND STRUCTURE PER-RUN BASIS, THEN CREATE LIST OF LUMI AND LS`s PER RUN
LSlist=data.groupby('#run:fill')['ls'].apply(list)
recLumiList=data.groupby('#run:fill')['recorded(/pb)'].apply(list)
delLumiList=data.groupby('#run:fill')['delivered(/pb)'].apply(list)
timeList=data.groupby('#run:fill')['time'].apply(list)
for i in range(0,len(LSlist)):
	LSlist[i]=[int(x.split(':')[0]) for x in LSlist[i]]
fillRunlist=data.drop_duplicates('#run:fill')['#run:fill'].tolist()

print fillRunlist
print "length LS list: "+str(len(LSlist))
print "length Run list: "+str(len(fillRunlist))



for run_i in range(0,len(fillRunlist)):

    run=int(fillRunlist[run_i].split(':')[0])
    fill=int(fillRunlist[run_i].split(':')[1])
    print run
    print fill


    ## CHANGE THIS
    if run<303824: #or run>303062:
	continue
    if run<302030:
	era="C"
    if run>=302030 and run<303434:
	era="D"
    if run>=303434:
	era="E"
        
    LSchunks 	= [LSlist[run_i][x:x+chunkSize] for x in range(0, len(LSlist[run_i]), chunkSize)]

    Del_chunks  = [delLumiList[run_i][x:x+chunkSize] for x in range(0, len(delLumiList[run_i]), chunkSize)]

    Rec_chunks  = [recLumiList[run_i][x:x+chunkSize] for x in range(0, len(recLumiList[run_i]), chunkSize)]

    time_chunks = [timeList[run_i][x:x+chunkSize] for x in range(0, len(timeList[run_i]), chunkSize)]

    Zyield=array('d')  
    Zrate=array('d')
    lumiDel=array('d')
    instDel=array('d')
    beginTime=[]
    endTime=[]
    fillarray=array('d')
    windowarray=array('d')
    nMeasurements=0

    if not os.path.isfile(eosDir+"000"+str(run)[:-2]+"xx/DQM_V0001_R000"+str(run)+"__SingleMuon__Run2017"+era+"-PromptReco-v1__DQMIO.root"):
	print "hello"
	continue

    for chunk_i in range(0,len(LSchunks)):
	if float(LSchunks[chunk_i][-1]) > 2499.:
                continue 
   	nMeasurements=nMeasurements+1

	recLumi_i = sum(Rec_chunks[chunk_i])
	delLumi_i = sum(Del_chunks[chunk_i])	
	deadtime_i = recLumi_i/delLumi_i
	print time_chunks[chunk_i]

	datestamp_low=time_chunks[chunk_i][0].split(" ")
	date_low=ROOT.TDatime(2017,int(datestamp_low[0].split("/")[1]),int(datestamp_low[0].split("/")[2]),int(datestamp_low[1].split(":")[0]),int(datestamp_low[1].split(":")[1]),int(datestamp_low[1].split(":")[2]))

        datestamp_up=time_chunks[chunk_i][-1].split(" ")
	date_up=ROOT.TDatime(2017,int(datestamp_up[0].split("/")[1]),int(datestamp_up[0].split("/")[2]),int(datestamp_up[1].split(":")[0]),int(datestamp_up[1].split(":")[1]),int(datestamp_up[1].split(":")[2]))


	print time_chunks[chunk_i]
	print (date_up.Convert()-date_low.Convert())+23
    	print date_up.Convert()
	print date_low.Convert()
	print LSchunks[chunk_i]
	print recLumi_i
	print delLumi_i
#	if float(LSchunks[chunk_i][-1]) > 1250.:
#		continue

	print "opening file: "+eosDir+"000"+str(run)[:-2]+"xx/DQM_V0001_R000"+str(run)+"__SingleMuon__Run2017"+era+"-PromptReco-v1__DQMIO.root"


    	HLTeff_i=ROOT.calculateDataEfficiency_v2(0,eosDir+"000"+str(run)[:-2]+"xx/DQM_V0001_R000"+str(run)+"__SingleMuon__Run2017"+era+"-PromptReco-v1__DQMIO.root",".",str(run),chunk_i,LSchunks[chunk_i][0],LSchunks[chunk_i][-1],30,"HLT",0,0,0,0)
	SITeff_i=ROOT.calculateDataEfficiency_v2(0,eosDir+"000"+str(run)[:-2]+"xx/DQM_V0001_R000"+str(run)+"__SingleMuon__Run2017"+era+"-PromptReco-v1__DQMIO.root",".",str(run),chunk_i,LSchunks[chunk_i][0],LSchunks[chunk_i][-1],30,"SIT",1,1,1,1)
#	Staeff_i=ROOT.calculateDataEfficiency_v2(0,eosDir+"000"+str(run)[:-2]+"xx/DQM_V0001_R000"+str(run)+"__SingleMuon__Run2017"+era+"-PromptReco-v1__DQMIO.root",".",str(run),chunk_i,LSchunks[chunk_i][0],LSchunks[chunk_i][-1],30,"Sta",1,2,1,2)
	Staeff_i=0.99


	Zyield_i=ROOT.calculateDataEfficiency_v2(1,eosDir+"000"+str(run)[:-2]+"xx/DQM_V0001_R000"+str(run)+"__SingleMuon__Run2017"+era+"-PromptReco-v1__DQMIO.root",".",str(run),chunk_i,LSchunks[chunk_i][0],LSchunks[chunk_i][-1],30,"HLT",0,0,0,0)


	crossX.append(Zyield_i/(Staeff_i**2 * SITeff_i**2 * (1-(1-HLTeff_i)*(1-HLTeff_i))*recLumi_i))
	effTot_i=(Staeff_i**2 * SITeff_i**2 * (1-(1-HLTeff_i)*(1-HLTeff_i)))
	timeWindow_i=(date_up.Convert()-date_low.Convert())+23 #in seconds
	zRate_i = Zyield_i/(effTot_i*deadtime_i*timeWindow_i)
	
	print Zyield
	print effTot_i
	print deadtime_i
	print timeWindow_i
	print zRate_i
	#Fill output Arrays

	lumiDel.append(delLumi_i)
	Zrate.append(zRate_i)
	Zyield.append(Zyield_i)
	Staeff.append(Staeff_i)
	#Staeff.append(0.99)

	SITeff.append(SITeff_i)
    	HLTeff.append(HLTeff_i)
	beginTime.append(time_chunks[chunk_i][0])
	endTime.append(time_chunks[chunk_i][-1])
	fillarray.append(fill)
	lumiDel.append(delLumi_i)
	instDel.append(delLumi_i/timeWindow_i)
	windowarray.append(timeWindow_i)
		#5427, 16/10/19 07:06:35, 16/10/19 07:22:54, 6.80618, 0.0105032, 10.024, 6495.66
	
	

    with open('csvfile'+str(run)+'.csv','wb') as file:
        for c in range(0,nMeasurements):
                file.write(str(int(fillarray[c]))+","+str(beginTime[c])+","+str(endTime[c])+","+str(Zrate[c])+","+str(instDel[c])+","+str(lumiDel[c])+","+str(Zyield[c]))
		file.write('\n')




#with open('csvfile.csv','wb') as file:
#	for c in range(0,nMeasurements):
#		file.write(str(int(fillarray[c]))+","+str(beginTime[c])+","+str(endTime[c])+","+str(Zrate[c])+","+str(instDel[c])+","+str(lumiDel[c])+","+str(Zyield[c]))
#        	file.write('\n')

print "crossX: "+str(crossX)
print "Zyield: "+str(Zyield)
print "Zrate: "+str(Zrate)
print "lumiDel: "+str(lumiDel)
print "instDel: "+str(instDel)
print "fill: "+str(fillarray)
print "beginTime: "+str(beginTime)
print "endTime: "+str(endTime)
print "HLTeff: "+str(HLTeff)
print "SITeff: "+str(SITeff)
print "Staeff: "+str(Staeff)
print "timeWindow: "+str(windowarray)
