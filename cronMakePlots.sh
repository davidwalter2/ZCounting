#!/bin/bash
cmsswRel=/afs/cern.ch/work/j/jsalfeld/Princeton/forZCounting2018/CMSSW_9_4_4/src
cd $cmsswRel
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
cd ZCounting
python plot_Zrate_DataCMS.py --fill 6616,6617,6618 --cms /eos/cms/store/group/comm_luminosity/ZCounting/csvFiles2018/Mergedeffcsvfile.csv --saveDir ~/www/CMS-2018-ZRateData/ZCrossSectionMonitoring/

python plot_ZEfficiency_DataCMS.py --fill 6616,6617,6618 --cms /eos/cms/store/group/comm_luminosity/ZCounting/csvFiles2018/Mergedeffcsvfile.csv --saveDir ~/www/CMS-2018-ZRateData/ZAndMuonEfficiencies/

cd ../ZRates/plottingTools
python plot_Zrate_Data.py --cms /eos/cms/store/group/comm_luminosity/ZCounting/csvFiles2018/Mergedcsvfile.csv --atlas /afs/cern.ch/user/p/ponyisi/public/zlumi/atlas_2018.csv