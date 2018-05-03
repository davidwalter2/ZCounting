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
from datetime import datetime
import pandas
import shutil
ROOT.gROOT.SetBatch(True)

ROOT.gStyle.SetCanvasPreferGL(1)

parser = argparse.ArgumentParser()



parser.add_argument("-c", "--cms", default="nothing", type=string, help="give the CMS csv as input")
parser.add_argument("-f", "--fill", default='6252', type=str, help="give fill numbers")
parser.add_argument("-s", "--saveDir", default='./', type=str, help="give fill numbers")
args = parser.parse_args()

if args.cms=="nothing":
	print "please provide cms input files"
	sys.exit()

print args.cms
#print args.atlas

data=pandas.read_csv(str(args.cms), sep=',',low_memory=False)#, skiprows=[1,2,3,4,5])
print data.axes
fills=data.drop_duplicates('fill')['fill'].tolist()
zcountlist=data.groupby('fill')['delZCount'].apply(list)
timelist=data.groupby('fill')['endTime'].apply(list)

fil=array('d')
zcountl=array('d')
timel=array('d')
fil=fills


#atlasfile=open(str(args.atlas))
cmsfile=open(str(args.cms))
fillsx=args.fill.split(",")
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
metaXsecCMS=array('d')
metaXsecATLAS=array('d')
metaZLumiRatio=array('d')
metaZLumiRatioEx=array('d')
metaZLumiRatioEy=array('d')

zcountsAccu=0
metazcountsAccu=array('d')

for fill in fills:
	print zcountlist[fill]
	zcountl.append(sum(zcountlist[fill]))
	zcountsAccu=zcountsAccu+sum(zcountlist[fill])
	metazcountsAccu.append(zcountsAccu)
	dateZ=timelist[fill][-1].split(" ")
	dateZ2=ROOT.TDatime(2018,int(dateZ[0].split("/")[0]),int(dateZ[0].split("/")[1]),int(dateZ[1].split(":")[0]),int(dateZ[1].split(":")[1]),int(dateZ[1].split(":")[2]))
	timel.append(dateZ2.Convert())
	cmsRates=array('d')
	cmsRatesE=array('d')
	cmsTimes=array('d')
	cmsTimesE=array('d')
	cmsInstLum=array('d')
	cmsXsec=array('d')
	cmsXsecEx=array('d')
	cmsXsecEy=array('d')

	atlasRates=array('d')
	atlasRatesE=array('d')
	atlasTimes=array('d')
	atlasTimesE=array('d')
	atlasInstLum=array('d')
	atlasXsec=array('d')
	atlasXsecEx=array('d')
	atlasXsecEy=array('d')

	#ZintRatio=array('d')

	atlascmsratio=array('d')
	atlascmsratioerrorX=array('d')
	atlascmsratioerrorXE=array('d')
	atlascmsratioerrorY=array('d')
	atlascmsratioerrorYE=array('d')
	
	k=0
	for linecms in range(0,len(linescms)):
		elements=linescms[linecms].split(",")
		#print fill
		#print elements[0]
		if elements[0]==str(fill):
			
			rate=elements[3]
			if rate=="nan":
				continue
			k=k+1
			cmsRates.append(float(rate))
			cmsRatesE.append(float(rate)*0.05)
			datestamp=elements[1].split(" ")
			date=ROOT.TDatime(2018,int(datestamp[0].split("/")[0]),int(datestamp[0].split("/")[1]),int(datestamp[1].split(":")[0]),int(datestamp[1].split(":")[1]),int(datestamp[1].split(":")[2]))
			#print datestamp
			#print date.Convert()
			cmsTimes.append(date.Convert())
			cmsTimesE.append(date.Convert()-date.Convert())
			cmsInstLum.append(float(elements[4]))
			cmsXsec.append(float(elements[6])/float(elements[5]))
			cmsXsecEy.append((float(elements[3])/float(elements[4]))*0.02)


	#print "here1"

	graph_cms=ROOT.TGraphErrors(k,cmsTimes,cmsRates,cmsTimesE,cmsRatesE)
	graph_cms.SetName("graph_cms")
	graph_cms.SetMarkerStyle(22)
	graph_cms.SetMarkerColor(kOrange+8)
	graph_cms.SetFillStyle(0)
	graph_cms.SetMarkerSize(1.5)

	graph_cmsinstLum=ROOT.TGraph(k,cmsTimes,cmsInstLum)
	graph_cmsinstLum.SetName("graph_cmsinstLum")
	graph_cmsinstLum.SetMarkerStyle(34)
	graph_cmsinstLum.SetMarkerColor(kRed)
	graph_cmsinstLum.SetMarkerSize(2)

	graph_cmsXsec=ROOT.TGraph(k,cmsTimes,cmsXsec)
	graph_cmsXsec.SetName("graph_cmsXsec")
	graph_cmsXsec.SetMarkerStyle(22)
	graph_cmsXsec.SetMarkerColor(kOrange+8)
	graph_cmsXsec.SetFillStyle(0)
	graph_cmsXsec.SetMarkerSize(1.5)

	i=0
	
	def cmsFunc(x):
		return graph_cms.Eval(x)


	startTime=cmsTimes[0]
	endTime=cmsTimes[-1]
	
	cmsTimesZInt=array('d')
	
	shutil.rmtree(args.saveDir+"PlotsFill_"+str(fill), ignore_errors=True)
	os.makedirs(args.saveDir+"PlotsFill_"+str(fill))
	

	c1=ROOT.TCanvas("c1","c1",1000,600)	
	graph_cms.GetXaxis().SetTimeDisplay(1)
	graph_cms.SetTitle(suffix+" Z-Rates, Fill "+str(fill))
	graph_cms.GetYaxis().SetTitle("Z-Rate [Hz]")
	graph_cms.GetYaxis().SetTitleSize(0.07)
	graph_cms.GetYaxis().SetTitleOffset(0.7)
	graph_cms.GetXaxis().SetTitle("Time")
	graph_cms.GetXaxis().SetTitleSize(0.06)
	graph_cms.GetXaxis().SetTitleOffset(0.75)
	graph_cms.GetXaxis().SetLabelSize(0.05)
	graph_cms.GetYaxis().SetLabelSize(0.05)
	graph_cms.GetXaxis().SetRangeUser(startTime,endTime)

		
	c1.cd(1)
	graph_cms.Draw("AP")

	legend=ROOT.TLegend(0.65,0.65,0.9,0.9)
	legend.AddEntry(graph_cms,"CMS","p")

	text1=ROOT.TText(0.3,0.83,"CMS Automatic, produced: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	text1.SetNDC()
	text1.Draw()
	c1.cd(1)
	c1.Update()
	#c1.SaveAs("zrates"+str(fill)+suffix+".root")
	c1.SaveAs(args.saveDir+"PlotsFill_"+str(fill)+"/zrates"+str(fill)+suffix+".png")
	c1.Delete()
	
	metaXsecCMS.append(sum(cmsXsec)/len(cmsXsec))	
	metaFills.append(float(fill))	

	cmsXsec2=array('d')
	for n in range(0,len(cmsXsec)):
		cmsXsec2.append(cmsXsec[n]/(sum(cmsXsec)/len(cmsXsec)))		
	
	#print "CROSS SECTIONS"
	#print cmsXsec
	graph_cmsXsec2=ROOT.TGraph(len(cmsXsec),cmsTimes,cmsXsec)
	graph_cmsXsec2.SetName("graph_cmsXsec")
	graph_cmsXsec2.SetTitle(suffix+" Z-Rates, Fill "+str(fill))
	graph_cmsXsec2.SetMarkerStyle(22)
	graph_cmsXsec2.SetMarkerColor(kOrange+8)
	graph_cmsXsec2.SetFillStyle(0)
	graph_cmsXsec2.SetMarkerSize(1.5)
	graph_cmsXsec2.GetXaxis().SetTimeDisplay(1)
	graph_cmsXsec2.GetYaxis().SetTitle("#sigma^{fid}_{Z} [pb]")#/<#sigma^{fid}_{Z}>")
	graph_cmsXsec2.GetYaxis().SetTitleSize(0.06)
	graph_cmsXsec2.GetYaxis().SetTitleOffset(0.80)
	graph_cmsXsec2.GetXaxis().SetTitle("Time")
	graph_cmsXsec2.GetXaxis().SetTitleSize(0.06)
	graph_cmsXsec2.GetXaxis().SetTitleOffset(0.72)
	graph_cmsXsec2.GetXaxis().SetLabelSize(0.05)
	graph_cmsXsec2.GetYaxis().SetLabelSize(0.05)	
	graph_cmsXsec2.GetYaxis().SetRangeUser(0.9*600,1.1*600)

	c4=ROOT.TCanvas("c4","c4",1000,600)
	c4.SetGrid()	
	graph_cmsXsec2.Draw("AP")		
	
	legend=ROOT.TLegend(0.75,0.75,0.9,0.9)
	legend.AddEntry(graph_cmsXsec2,"CMS","p")
	#legend.Draw()
	text=ROOT.TText(0.3,0.83,"CMS Automatic, produced: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	text.SetNDC()
	text.Draw()
	text2=ROOT.TLatex(0.6,0.23,"#splitline{66 GeV<M(#mu#mu) < 116 GeV}{p_{T}(#mu)>30 GeV, |#eta(#mu)|<2.4}")
	text2.SetNDC()
	text2.SetTextSize(0.04)
	text2.Draw()
	c4.SaveAs(args.saveDir+"PlotsFill_"+str(fill)+"/ZStability"+str(fill)+suffix+".png")
	
	
	c4.Delete()
	
	
ROOT.gROOT.SetBatch(True)
metaXsecCMS2=array('d')
for n in range(0,len(metaXsecCMS)):
	metaXsecCMS2.append(metaXsecCMS[n]/(sum(metaXsecCMS)/len(metaXsecCMS)))	


graph_metacmsXsec=ROOT.TGraph(len(metaFills),metaFills,metaXsecCMS)
graph_metacmsXsec.SetName("graph_metaXsecCms")
graph_metacmsXsec.SetMarkerStyle(22)
graph_metacmsXsec.SetMarkerColor(kOrange+8)
graph_metacmsXsec.SetMarkerSize(2.5)
graph_metacmsXsec.SetTitle("Cross Section Summary, "+suffix+" Z-Rates")

multMetaGraphXsec=ROOT.TMultiGraph("multMetaGraphXsec",suffix+" Z-Rates")
multMetaGraphXsec.SetName("multMetaGraphXsec")
graph_metacmsXsec.GetXaxis().SetTitle("Fill")
graph_metacmsXsec.GetYaxis().SetTitle("#sigma^{fid}_{Z} [pb]")#/<#sigma^{fid}_{Z}>")
graph_metacmsXsec.GetXaxis().SetTitleSize(0.06)
graph_metacmsXsec.GetYaxis().SetTitleSize(0.06)
graph_metacmsXsec.GetXaxis().SetTitleOffset(0.72)
graph_metacmsXsec.GetYaxis().SetTitleOffset(0.8)
graph_metacmsXsec.GetXaxis().SetLabelSize(0.05)
graph_metacmsXsec.GetYaxis().SetLabelSize(0.05)

multMetaGraphXsec.Add(graph_metacmsXsec)

c3=ROOT.TCanvas("c3","c3",1000,600)
c3.SetGrid()

graph_metacmsXsec.Draw("AP")

if suffix=="Barrel":
	graph_metacmsXsec.GetYaxis().SetRangeUser(0.9*600,1.1*600)
if suffix=="Inclusive":
	graph_metacmsXsec.GetYaxis().SetRangeUser(0.9*600,1.1*600)


text=ROOT.TLatex(0.3,0.83,"CMS Automatic, produced: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
text.SetNDC()
text.Draw()
text2=ROOT.TLatex(0.6,0.23,"#splitline{66 GeV<M(#mu#mu) < 116 GeV}{p_{T}(#mu)>30 GeV, |#eta(#mu)|<2.4}")
text2.SetNDC()
text2.SetTextSize(0.04)
text2.Draw()
c3.SaveAs(args.saveDir+"summaryZStability"+suffix+".png")
graph_zcount=ROOT.TGraph(len(metaFills),metaFills,zcountl)
#print zcountl
graph_zcount.SetName("graph_zcount")
graph_zcount.SetMarkerStyle(22)
graph_zcount.SetMarkerColor(kOrange+8)
graph_zcount.SetMarkerSize(2.5)
graph_zcount.SetTitle("Z Counts Per Fill")
graph_zcount.GetXaxis().SetTitle("Fill")
graph_zcount.GetYaxis().SetTitle("Z Count")#/<#sigma^{fid}_{Z}>")
graph_zcount.GetXaxis().SetTitleSize(0.06)
graph_zcount.GetYaxis().SetTitleSize(0.06)
graph_zcount.GetXaxis().SetTitleOffset(0.72)
graph_zcount.GetYaxis().SetTitleOffset(0.8)
graph_zcount.GetXaxis().SetLabelSize(0.05)
graph_zcount.GetYaxis().SetLabelSize(0.05)
graph_zcount.GetXaxis().SetLabelSize(0.05)
graph_zcount.GetYaxis().SetLabelSize(0.05)
c5=ROOT.TCanvas("c3","c3",1000,600)
c5.SetGrid()
graph_zcount.Draw("AP")
text=ROOT.TLatex(0.3,0.83,"CMS Automatic, produced: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
text.SetNDC()
text.Draw()
text2=ROOT.TLatex(0.6,0.23,"#splitline{66 GeV<M(#mu#mu) < 116 GeV}{p_{T}(#mu)>30 GeV, |#eta(#mu)|<2.4}")
text2.SetNDC()
text2.SetTextSize(0.04)
text2.Draw()
text3=ROOT.TLatex(0.7,0.33,"#color[4]{HLT_IsoMu27_v*}")
text3.SetNDC()
text3.SetTextSize(0.04)
text3.Draw()
c5.SaveAs(args.saveDir+"ZCountPerFill"+suffix+".png")


graph_zcountA=ROOT.TGraph(len(metaFills),timel,metazcountsAccu)
#print zcountl
graph_zcountA.SetName("graph_zcountAccu")
graph_zcountA.SetMarkerStyle(22)
graph_zcountA.SetMarkerColor(kOrange+8)
graph_zcountA.SetMarkerSize(2.5)
graph_zcountA.SetTitle("Accumulated Z Bosons over Time")
graph_zcountA.GetXaxis().SetTitle("Time")
graph_zcountA.GetXaxis().SetTimeDisplay(1)
graph_zcountA.GetYaxis().SetTitle("Z Count")#/<#sigma^{fid}_{Z}>")
graph_zcountA.GetXaxis().SetTitleSize(0.06)
graph_zcountA.GetYaxis().SetTitleSize(0.06)
graph_zcountA.GetXaxis().SetTitleOffset(0.72)
graph_zcountA.GetYaxis().SetTitleOffset(0.8)
graph_zcountA.GetXaxis().SetLabelSize(0.05)
graph_zcountA.GetYaxis().SetLabelSize(0.05)
graph_zcountA.GetXaxis().SetLabelSize(0.05)
graph_zcountA.GetYaxis().SetLabelSize(0.05)
c6=ROOT.TCanvas("c3","c3",1000,600)
c6.SetGrid()
graph_zcountA.Draw("AP")
text=ROOT.TLatex(0.3,0.83,"CMS Automatic, produced: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
text.SetNDC()
text.Draw()
text2=ROOT.TLatex(0.6,0.23,"#splitline{66 GeV<M(#mu#mu) < 116 GeV}{p_{T}(#mu)>30 GeV, |#eta(#mu)|<2.4}")
text2.SetNDC()
text2.SetTextSize(0.04)
text2.Draw()
text3=ROOT.TLatex(0.7,0.33,"#color[4]{HLT_IsoMu27_v*}")
text3.SetNDC()
text3.SetTextSize(0.04)
text3.Draw()
c6.SaveAs(args.saveDir+"ZCountAccumulated"+suffix+".png")
