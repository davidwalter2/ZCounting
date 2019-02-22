#!/bin/bash
export PATH=$HOME/.local/bin:/afs/cern.ch/cms/lumi/brilconda-1.1.7/bin:$PATH
DATE=`date '+%m/%d/%y'`
DATE2=`date '+%m_%d_%y'`
TIME=`date '+%H:%M:%S'`
echo $DATE
echo $TIME

#2016
brilcalc lumi --begin 272786 --end 284044 -b "STABLE BEAMS" --byls -o /afs/cern.ch/work/d/dwalter/CMSSW_9_2_8/src/ZCounting/FillByLs_2016.csv --hltpath="HLT_IsoMu24_v*"

#2018:
brilcalc lumi --begin 315252 --end 325175 -b "STABLE BEAMS" --byls -o /afs/cern.ch/work/d/dwalter/CMSSW_9_2_8/src/ZCounting/FillByLs_2018.csv --hltpath="HLT_IsoMu24_v*" -normtag="hfoc18v5"
