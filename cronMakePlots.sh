#!/bin/bash
#cmsswRel=/afs/cern.ch/work/j/jsalfeld/Princeton/forZCounting2018/CMSSW_9_4_4/src
cmsswRel=/afs/cern.ch/work/d/dwalter/CMSSW_9_2_8/src
cd $cmsswRel
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
cd ZCounting

cmsCSV = "/eos/home-d/dwalter/www/ZCounting/CMS-2018-ZRateData/csvFiles/Mergedcsvfile.csv"

python plot_Zrate_DataCMS.py --cms cmsCSV --saveDir /eos/home-d/dwalter/www/ZCounting/CMS-2018-ZRateData/ZCrossSectionMonitoring/

python plot_ZEfficiency_DataCMS.py --cms cmsCSV --saveDir /eos/home-d/dwalter/www/ZCounting/CMS-2018-ZRateData/ZAndMuonEfficiencies/

python makeZvsL.py --cms cmsCSV --saveDir /eos/home-d/dwalter/www/ZCounting/CMS-2018-ZRateData/ZCrossSectionMonitoring/

python ../ZRates/plottingTools/plot_Zrate_Data.py --cms cmsCSV --atlas /afs/cern.ch/user/p/ponyisi/public/zlumi/atlas_2018.csv -s /eos/home-d/dwalter/www/ZCounting/CMS-2018-ZRateData/ZCrossSectionMonitoring/
