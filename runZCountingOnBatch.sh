#!/bin/bash
runNum=$1
sizeChunk=$2
lumiChunk=$3

workdir="/afs/cern.ch/work/x/xniu/public/CMSSW_9_2_8/src/ZCountHarvest/CloneJob"
filedir="/afs/cern.ch/work/x/xniu/public/CMSSW_9_2_8/src/ZCountHarvest/CloneJob/TestResult/TestDec05"
subdir=${sizeChunk}-${lumiChunk}invpb

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

python testZCounting2.py -b $runNum -e $(($runNum + 1)) -s $sizeChunk -l $lumiChunk -m True -u True

cp -r $TOP/Run${runNum} ${filedir}/${subdir}
cp $TOP/csvfile${runNum}.csv ${filedir}/${subdir}
cp $TOP/effcsvfile${runNum}.csv ${filedir}/${subdir}
