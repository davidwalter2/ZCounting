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

parser = argparse.ArgumentParser()

parser.add_argument("-c", "--cms", default="/eos/home-d/dwalter/www/ZCounting/CMS-2018-ZRateData/csvFiles/Mergedcsvfile.csv", type=string, help="give the CMS csv as input")
parser.add_argument("-s", "--saveDir", default='/eos/home-d/dwalter/www/ZCounting/CMS-2018-ZRateData/ZCrossSectionMonitoring/', type=str, help="give output dir")
args = parser.parse_args()


ROOT.gStyle.SetCanvasPreferGL(1)
cmsfile=open(args.cms)
#cmsfile=open("/afs/cern.ch/user/l/lumipro/public/ZRatesFiles/2017Rates/ZCounting2017_CMS_Scaled_YYMMDD_v1.csv")
#cmsfile=open("Z_Counting_AllFillsAfter5400_Allplus.txt")
#cmsfile=open("/afs/cern.ch/user/l/lumipro/public/ZRatesFiles/2018Rates/ZCounting2018_CMS_Scaled_MMDDYY_v1.csv")
linescms=cmsfile.readlines()

cmsRates=array('d')
cmsL=array('d')
k=-1

for line in linescms:
	k=k+1
	if k<=1:
		continue
	elements=line.split(",")
	if float(elements[3])/float(elements[4])<500. or float(elements[3])/float(elements[4])>900.:
		continue
	cmsRates.append(float(elements[3])*1./float(elements[4]))
	cmsL.append(float(elements[4]))
	

graph_metaatlasXsec=ROOT.TGraph(len(cmsL),cmsL,cmsRates)
graph_metaatlasXsec.SetName("graph_metaXsecAtlas")
graph_metaatlasXsec.SetMarkerStyle(23)
graph_metaatlasXsec.SetMarkerColor(kAzure-4)
graph_metaatlasXsec.SetMarkerSize(1.5)
graph_metaatlasXsec.SetTitle("Z cross section VS Lumi")
graph_metaatlasXsec.GetXaxis().SetTitle("instantaneous luminosity [Hz/pb]")
graph_metaatlasXsec.GetYaxis().SetTitle("#sigma^{fid}_{Z} [pb]")

print "the simple average cross section is "+str(sum(cmsRates)/len(cmsRates))
#graph_metaatlasXsec.LeastSquareLinearFit(0,ROOT.Double(700.),ROOT.Double(0.),ROOT.Long(1),ROOT.Double(0.003),ROOT.Double(0.015))
graph_metaatlasXsec.Fit("pol1","","",0.0045,0.018)
c3=ROOT.TCanvas("c3","c3",1000,600)
c3.SetGrid()
graph_metaatlasXsec.Draw("AP")
c3.SaveAs(args.saveDir+"xL18v2.png")
#c3.SaveAs(args.saveDir+"xL18v2.root")
