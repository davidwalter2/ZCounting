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
#print args.atlas

#atlasfile=open(str(args.atlas))
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
metaXsecCMS=array('d')
metaXsecATLAS=array('d')
metaZLumiRatio=array('d')
metaZLumiRatioEx=array('d')
metaZLumiRatioEy=array('d')


for fill in fills:
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
		
		if elements[0]==fill:
			k=k+1
			rate=elements[3]
			cmsRates.append(float(rate))
			cmsRatesE.append(float(rate)*0.05)
			datestamp=elements[1].split(" ")
			date=ROOT.TDatime(2017,int(datestamp[0].split("/")[0]),int(datestamp[0].split("/")[1]),int(datestamp[1].split(":")[0]),int(datestamp[1].split(":")[1]),int(datestamp[1].split(":")[2]))
			print datestamp
			print date.Convert()
			cmsTimes.append(date.Convert())
			cmsTimesE.append(date.Convert()-date.Convert())
			cmsInstLum.append(float(elements[4]))
			cmsXsec.append(float(elements[3])/float(elements[4]))
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
	

	print i

	print fill


	def cmsFunc(x):
		return graph_cms.Eval(x)


	startTime=cmsTimes[0]
	endTime=cmsTimes[-1]
	
	cmsTimesZInt=array('d')
			
#	print "CMS Error: "+str(integrate.quad(atlasFunc,cmsTimes[0],cmsTimes[cmsTime])[1]/integrate.quad(atlasFunc,cmsTimes[0],cmsTimes[cmsTime])[0])	
	#print "ATLAS Error: "+str(integrate.quad(cmsFunc,cmsTimes[0],cmsTimes[cmsTime])[1]/integrate.quad(cmsFunc,cmsTimes[0],cmsTimes[cmsTime])[0])	

	#print ZintRatio
	
	
	

	c1=ROOT.TCanvas("c1","c1",1000,600)
	c1.Divide(1,2)
	c1.cd(1).SetPad(0.0,0.3,1.0,1.0)

	
	
	graph_cms.GetXaxis().SetTimeDisplay(1)
	graph_cms.SetTitle(suffix+" Z-Rates, Fill "+fill)
	graph_cms.GetYaxis().SetTitle("Z-Rate [Hz]")
	graph_cms.GetYaxis().SetTitleSize(0.07)
	graph_cms.GetYaxis().SetTitleOffset(0.5)
	graph_cms.GetXaxis().SetTitle("Time")
	graph_cms.GetXaxis().SetTitleSize(0.06)
	graph_cms.GetXaxis().SetTitleOffset(0.72)
	graph_cms.GetXaxis().SetLabelSize(0.05)
	graph_cms.GetYaxis().SetLabelSize(0.05)
	graph_cms.GetXaxis().SetRangeUser(startTime,endTime)

		
	c1.cd(1)
#	graph_atlas.Draw("AP")
	graph_cms.Draw("AP")
	

	legend=ROOT.TLegend(0.65,0.65,0.9,0.9)
	legend.AddEntry(graph_cms,"CMS","p")
	legend.Draw()

	text1=ROOT.TText(0.1,0.93,"Work In Progress")
	text1.SetNDC()
	text1.Draw()

	c1.cd(2).SetPad(0.0,0.0,1.0,0.3)
	c1.cd(2)
	text2=ROOT.TText(0.8,0.73,"Int. Z-Luminosity Ratio ")
	text2.SetNDC()
	text2.Draw()
		
		
        text2=ROOT.TText(0.67,0.79,"Int. Z-Luminosity Ratio ")
	text2.SetNDC()
	text2.SetTextSize(0.1)
	text2.Draw()

	c1.cd(1)
	c1.Update()
	c1.SaveAs("zrates"+fill+suffix+".root")
	c1.SaveAs("zrates"+fill+suffix+".png")
	c1.Delete()

	
	metaXsecCMS.append(sum(cmsXsec)/len(cmsXsec))
	
	metaFills.append(float(fill))	

	
	
	
	


	cmsXsec2=array('d')
	for n in range(0,len(cmsXsec)):
		cmsXsec2.append(cmsXsec[n]/(sum(cmsXsec)/len(cmsXsec)))		
	
	print "CROSS SECTIONS"
	print cmsXsec
	graph_cmsXsec2=ROOT.TGraph(len(cmsXsec),cmsTimes,cmsXsec)
	graph_cmsXsec2.SetName("graph_cmsXsec")
	graph_cmsXsec2.SetTitle(suffix+" Z-Rates, Fill "+fill)
	graph_cmsXsec2.SetMarkerStyle(22)
	graph_cmsXsec2.SetMarkerColor(kOrange+8)
	graph_cmsXsec2.SetFillStyle(0)
	graph_cmsXsec2.SetMarkerSize(1.5)
	graph_cmsXsec2.GetXaxis().SetTimeDisplay(1)
	graph_cmsXsec2.GetYaxis().SetTitle("#sigma^{fid}_{Z}")#/<#sigma^{fid}_{Z}>")
	graph_cmsXsec2.GetYaxis().SetTitleSize(0.05)
	graph_cmsXsec2.GetYaxis().SetTitleOffset(0.95)
	graph_cmsXsec2.GetXaxis().SetTitle("Time")
	graph_cmsXsec2.GetXaxis().SetTitleSize(0.06)
	graph_cmsXsec2.GetXaxis().SetTitleOffset(0.72)
	graph_cmsXsec2.GetXaxis().SetLabelSize(0.05)
	graph_cmsXsec2.GetYaxis().SetLabelSize(0.05)	
	graph_cmsXsec2.GetYaxis().SetRangeUser(0.9*580,1.1*580)
	
	c4=ROOT.TCanvas("c4","c4",1000,600)
	c4.SetGrid()	
	graph_cmsXsec2.Draw("AP")	
	
	
	
	legend=ROOT.TLegend(0.75,0.75,0.9,0.9)
	legend.AddEntry(graph_cmsXsec2,"CMS","p")
	#legend.AddEntry(graph_atlasXsec2,"CMS new","p")
	legend.Draw()
	text=ROOT.TText(0.1,0.93,"Work In Progress")
	text.SetNDC()
	text.Draw()
	c4.SaveAs("ZStability"+fill+suffix+".root")
	c4.SaveAs("ZStability"+fill+suffix+".png")
	
	
	c4.Delete()
	
	
ROOT.gROOT.SetBatch(True)

#	metaXsecATLAS2.append(metaXsecATLAS[n]/(sum(metaXsecATLAS)/len(metaXsecATLAS)))	

metaXsecCMS2=array('d')
for n in range(0,len(metaXsecCMS)):
	metaXsecCMS2.append(metaXsecCMS[n]/(sum(metaXsecCMS)/len(metaXsecCMS)))	


graph_metacmsXsec=ROOT.TGraph(len(metaFills),metaFills,metaXsecCMS)
graph_metacmsXsec.SetName("graph_metaXsecCms")
graph_metacmsXsec.SetMarkerStyle(22)
graph_metacmsXsec.SetMarkerColor(kOrange+8)
graph_metacmsXsec.SetMarkerSize(1.5)
graph_metacmsXsec.SetTitle(suffix+" Z-Rates")

multMetaGraphXsec=ROOT.TMultiGraph("multMetaGraphXsec",suffix+" Z-Rates")
multMetaGraphXsec.SetName("multMetaGraphXsec")

graph_metacmsXsec.GetXaxis().SetTitle("Fill")
graph_metacmsXsec.GetYaxis().SetTitle("#sigma^{fid}_{Z}")#/<#sigma^{fid}_{Z}>")
graph_metacmsXsec.GetXaxis().SetTitleSize(0.05)
graph_metacmsXsec.GetYaxis().SetTitleSize(0.05)
graph_metacmsXsec.GetXaxis().SetTitleOffset(0.87)
graph_metacmsXsec.GetYaxis().SetTitleOffset(0.87)

multMetaGraphXsec.Add(graph_metacmsXsec)
#multMetaGraphXsec.Add(graph_metaatlasXsec)


c3=ROOT.TCanvas("c3","c3",1000,600)
c3.SetGrid()

graph_metacmsXsec.Draw("AP")

if suffix=="Barrel":
	graph_metacmsXsec.GetYaxis().SetRangeUser(0.9*580,1.1*580)
if suffix=="Inclusive":
	graph_metacmsXsec.GetYaxis().SetRangeUser(0.9*580,1.1*580)

legend=ROOT.TLegend(0.75,0.75,0.9,0.9)
legend.AddEntry(graph_metacmsXsec,"CMS","p")
#legend.AddEntry(graph_metaatlasXsec,"CMS new","p")
legend.Draw()

text=ROOT.TText(0.1,0.93,"Work In Progress")
text.SetNDC()
text.Draw()

c3.SaveAs("summaryZStability"+suffix+".root")
c3.SaveAs("summaryZStability"+suffix+".png")

