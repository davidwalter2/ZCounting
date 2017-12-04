#!/bin/bash
runNum=$1

workdir="/afs/cern.ch/work/x/xniu/public/CMSSW_9_2_8/src/ZCountHarvest/CloneJob"
filedir="/afs/cern.ch/work/x/xniu/public/CMSSW_9_2_8/src/ZCountHarvest/CloneJob/TestResult/TestNov09"

CMSSW_BASE="/afs/cern.ch/work/x/xniu/public/CMSSW_9_2_8/src/"
TOP="$PWD"

cd $CMSSW_BASE
eval `scramv1 runtime -sh`
cd $TOP

cp -r ${workdir}/Utils $TOP
cp -r ${workdir}/.rootlogon.C $TOP
cp ${workdir}/calculateDataEfficiency_v3.C $TOP
cp ${workdir}/calculateZEfficiency.C $TOP
cp ${workdir}/testZCounting2.py $TOP

python testZCounting2.py -b $runNum -e $(($runNum + 1))

cp -r $TOP/Run${runNum} ${filedir}
cp $TOP/csvfile${runNum}.csv ${filedir}
cp $TOP/effcsvfile${runNum}.csv ${filedir}
