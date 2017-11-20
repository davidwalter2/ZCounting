import os,sys
#sys.argv.append( '-b-' )
#from scipy.interpolate import UnivariateSpline
import ROOT
from ROOT import TGraph
from ROOT import TGraphErrors
from array import array
from ROOT import *
from operator import truediv
import random
import argparse
import scipy.integrate as integrate
ROOT.gROOT.SetBatch(True)

ROOT.gStyle.SetCanvasPreferGL(1)

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--cms", default="nothing", type=string, help="give the CMS csv as input")
parser.add_argument("-f", "--fill", default='6252', type=str, help="give fill numbers")
args = parser.parse_args()
if args.cms=="nothing":
	print "please provide cms input files"
	sys.exit()
print args.cms

def plotPerFillEff(nMeas,nFill,effArray,times,suffixN, isInterFill):
	graph_cms=ROOT.TGraph(nMeas,times,effArray)
	graph_cms.SetName("graph_cms"+suffixN)
	graph_cms.SetMarkerStyle(22)
	graph_cms.SetMarkerColor(kOrange+8)
	graph_cms.SetMarkerSize(2)

	c1=ROOT.TCanvas("c1"+suffixN,"c1"+suffixN,1000,600)
	if isInterFill:
 		graph_cms.GetXaxis().SetTimeDisplay(1)
	graph_cms.SetTitle(suffixN+", Fill "+nFill)
	graph_cms.GetYaxis().SetTitle("Efficiency")
	graph_cms.GetYaxis().SetTitleSize(0.07)
	graph_cms.GetYaxis().SetTitleOffset(0.7)
	graph_cms.GetXaxis().SetTitle("Time")
	graph_cms.GetXaxis().SetTitleSize(0.06)
	graph_cms.GetXaxis().SetTitleOffset(0.72)
	graph_cms.GetXaxis().SetLabelSize(0.05)
	graph_cms.GetYaxis().SetLabelSize(0.05)
	graph_cms.GetXaxis().SetRangeUser(times[0],times[-1])
	#graph_cms.GetYaxis().SetRangeUser(0.75,1.0)
	graph_cms.Draw("AP")
	legend=ROOT.TLegend(0.72,0.72,0.9,0.9)
	legend.AddEntry(graph_cms,suffixN,"p")
	#legend.Draw()

	text1=ROOT.TText(0.1,0.91,"Work In Progress")
	text1.SetNDC()
	text1.Draw()
	c1.Update()
	c1.SaveAs(nFill+suffixN+".root")
	c1.SaveAs(nFill+suffixN+".png")
	c1.Delete()

	
	avrgEff=sum(effArray)/nMeas
	return avrgEff

cmsfile=open(str(args.cms))
fills=args.fill.split(",")
suffix=""

print "Fills being processed: "+str(fills)
if "Central" in str(args.cms):
	suffix="Barrel"
else:
	suffix="Inclusive"

print suffix

linescms=cmsfile.readlines()
#linesatlas=atlasfile.readlines()


metaFills=array('d')

avrgHLTBEff=array('d')
avrgHLTEEff=array('d')
avrgSITBEff=array('d')
avrgSITEEff=array('d')
avrgStaBEff=array('d')
avrgStaEEff=array('d')
avrgZBBEff=array('d')
avrgZBEEff=array('d')
avrgZEEEff=array('d')

for fill in fills:
	
	cmsTimes=array('d')
	cmsTimesE=array('d')
	
	HLTBeff=array('d')
	HLTEeff=array('d')
	SITBeff=array('d')
	SITEeff=array('d')
	StaBeff=array('d')
	StaEeff=array('d')
	ZBBeff =array('d')
	ZBEeff =array('d')
	ZEEeff =array('d')

	k=0

	for linecms in range(0,len(linescms)):
		elements=linescms[linecms].split(",")
		
		if elements[0]==fill:
			k=k+1
			rate=elements[3]
			#print elements[11]
			
			HLTBeff.append(float(elements[11]))
			HLTEeff.append(float(elements[12]))
			SITBeff.append(float(elements[13]))
			SITEeff.append(float(elements[14]))
			StaBeff.append(float(elements[15]))
			StaEeff.append(float(elements[16]))
			ZBBeff.append(float(elements[17]))
			ZBEeff.append(float(elements[18]))
			ZEEeff.append(float(elements[19]))

			datestamp=elements[1].split(" ")
			date=ROOT.TDatime(2017,int(datestamp[0].split("/")[0]),int(datestamp[0].split("/")[1]),int(datestamp[1].split(":")[0]),int(datestamp[1].split(":")[1]),int(datestamp[1].split(":")[2]))
			cmsTimes.append(date.Convert())
				


#	plotPerFillEff(nMeas,nFill,effArray,times,suffixN)
	avrgHLTBEff.append(plotPerFillEff(k,fill,HLTBeff,cmsTimes,"HLT_Barrel_Efficiency",True))
	avrgHLTEEff.append(plotPerFillEff(k,fill,HLTEeff,cmsTimes,"HLT_Endcap_Efficiency",True))
	avrgSITBEff.append(plotPerFillEff(k,fill,SITBeff,cmsTimes,"SelAndTracking_Barrel_Efficiency",True))
	avrgSITEEff.append(plotPerFillEff(k,fill,SITEeff,cmsTimes,"SelAndTracking_Endcap_Efficiency",True))
	avrgStaBEff.append(plotPerFillEff(k,fill,StaBeff,cmsTimes,"Standalone_Barrel_Efficiency",True))
	avrgStaEEff.append(plotPerFillEff(k,fill,StaEeff,cmsTimes,"Standalone_Endcap_Efficiency",True))
	avrgZBBEff.append(plotPerFillEff(k,fill,ZBBeff,cmsTimes,"Z_BarrelBarrel_Efficiency",True))
	avrgZEEEff.append(plotPerFillEff(k,fill,ZEEeff,cmsTimes,"Z_EndcapEndcap_Efficiency",True))
	avrgZBEEff.append(plotPerFillEff(k,fill,ZBEeff,cmsTimes,"Z_BarrelEndcap_Efficiency",True))

	metaFills.append(float(fill))

plotPerFillEff(len(avrgHLTBEff),"all",avrgHLTBEff,metaFills,"SummaryHLT_Barrel_Efficiency",False)
plotPerFillEff(len(avrgHLTEEff),"all",avrgHLTEEff,metaFills,"SummaryHLT_Endcap_Efficiency",False)
plotPerFillEff(len(avrgSITBEff),"all",avrgSITBEff,metaFills,"SummarySelAndTracking_Barrel_Efficiency",False)
plotPerFillEff(len(avrgSITEEff),"all",avrgSITEEff,metaFills,"SummarySelAndTracking_Endcap_Efficiency",False)
plotPerFillEff(len(avrgStaBEff),"all",avrgStaBEff,metaFills,"SummaryStandalone_Barrel_Efficiency",False)
plotPerFillEff(len(avrgStaEEff),"all",avrgStaEEff,metaFills,"SummaryStandalone_Endcap_Efficiency",False)
plotPerFillEff(len(avrgZBBEff),"all",avrgZBBEff,metaFills,"Summary_Z_BarrelBarrel_Efficiency",False)
plotPerFillEff(len(avrgZBEEff),"all",avrgZBEEff,metaFills,"Summary_Z_BarrelEndcap_Efficiency",False)
plotPerFillEff(len(avrgZEEEff),"all",avrgZEEEff,metaFills,"Summary_Z_EndcapEndcap_Efficiency",False)
	
