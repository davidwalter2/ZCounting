# ZCounting

This code is to run over Z Counting histograms produced in DQM and produce a CSV file with Z rates. The output file format has been agreed upon with ATLAS in 2016.

A CMSSW environment needs to be set up to have the pandas library available.

The python file "testZCounting(versionnumber).py" is the file to be executed. Parameters such as the time granularity, DQM file location and the brilcalc CSV input file can be changed.

Many aspects in the code can be improved.

Notes: so far we keep mutiple versions, in order to use in various purpose:
testZCounting3.py: used for 2017 data, in a "semi-automatic" way
testZCounting4.py: the MAIN one, aim to be used with cron jobs for 2018 data, in a fully automatic way
testZCounting5.py: used for optimization purpose/tests, not with cron jobs, for 2018 data
