#! /usr/bin/python
#
'''
Project     :       Apache Solr Health Check
Version     :       0.4
Author      :       Ashok Raja R <ashokraja.linux@gmail.com>
Summary     :       This program is a nagios plugin that checks Apache Solr Health
Dependency  :       Linux/nagios/Python-2.6

Usage :
```````
shell> python check_solr.py
'''

#-----------------------|
# Import Python Modules |
#-----------------------|
import os, sys, urllib
import xml.etree.ElementTree as ET
from optparse import OptionParser

#--------------------------|
# Main Program Starts Here |
#--------------------------|
# Command Line Arguments Parser
cmd_parser = OptionParser(version = "%prog 0.2")
cmd_parser.add_option("-q", "--qps", action = "store_true", dest = "qps", help = "Get QPS information of the SOLR Server")
cmd_parser.add_option("-r", "--requesttime", action = "store_true", dest = "tpr", help = "Get Average Time Per Requests")
cmd_parser.add_option("-d", "--doc", action = "store_true", dest = "doc", help = "Get Docs information of the SOLR Server", default = True)
cmd_parser.add_option("-u", "--solrurl", type = "string", action = "store", dest = "solr_url", help = "SOLR Admin Stats URL.", metavar = "http://localhost:8090/solr")
cmd_parser.add_option("-w", "--warning", type = "float", action = "store", dest = "warning_per", help = "Exit with WARNING status if higher than the percentage", metavar = "70")
cmd_parser.add_option("-c", "--critical", type = "float", action = "store", dest = "critical_per", help = "Exit with CRITICAL status if higher than the percentage", metavar = "99")
(cmd_options, cmd_args) = cmd_parser.parse_args()
# Check the Command syntax
if not (cmd_options.warning_per and cmd_options.critical_per and cmd_options.solr_url):
    cmd_parser.print_help()
    sys.exit(3)

# Collect Solr Statistics Object
class CollectStat:
    ''' Object to Collect the Statistics from the specified Element of the XML Data'''
    def __init__(self, groupname, entryname):
        self.stats = {}

        doc = ET.fromstring(urllib.urlopen(cmd_options.solr_url + "/admin/stats.jsp").read())

        tags = doc.findall(".//solr-info/" + groupname + "/entry")
        for b in tags:
            if b.find('name').text.strip() == entryname:
                stats = b.findall("stats/*")
                for stat in stats:
                    self.stats[stat.get('name')] = stat.text.strip()
# Check QPS
if cmd_options.qps :
    # Get the QPS Statistics
    solr_qps_stats = CollectStat('QUERYHANDLER', 'search')
    if float(solr_qps_stats.stats['avgRequestsPerSecond']) >= cmd_options.critical_per:
        print "SOLR QPS CRITICAL : %.2f requests per second | ReqPerSec=%.2freqs" % (float(solr_qps_stats.stats['avgRequestsPerSecond']), float(solr_qps_stats.stats['avgRequestsPerSecond']))
        sys.exit(2)
    elif float(solr_qps_stats.stats['avgRequestsPerSecond']) >= cmd_options.warning_per:
        print "SOLR QPS WARNING : %.2f requests per second | ReqPerSec=%.2freqs" % (float(solr_qps_stats.stats['avgRequestsPerSecond']), float(solr_qps_stats.stats['avgRequestsPerSecond']))
        sys.exit(1)
    else:
        print "SOLR QPS OK : %.2f requests per second | ReqPerSec=%.2freqs" % (float(solr_qps_stats.stats['avgRequestsPerSecond']), float(solr_qps_stats.stats['avgRequestsPerSecond']))
        sys.exit(0)
# Check Average Response Time
elif cmd_options.tpr :
    solr_tpr_stats = CollectStat('QUERYHANDLER', 'search')
    if float(solr_tpr_stats.stats['avgTimePerRequest']) >= float(cmd_options.critical_per):
        print "SOLR AvgRes CRITICAL : %.2f msecond response time | AvgRes=%.2f" % (float(solr_tpr_stats.stats['avgTimePerRequest']), float(solr_tpr_stats.stats['avgTimePerRequest']))
        sys.exit(2)
    elif float(solr_tpr_stats.stats['avgTimePerRequest']) >= float(cmd_options.warning_per):
        print "SOLR AvgRes WARNING : %.2f msecond response time | AvgRes=%.2f" % (float(solr_tpr_stats.stats['avgTimePerRequest']), float(solr_tpr_stats.stats['avgTimePerRequest']))
        sys.exit(1)
    else:
        print "SOLR AvgRes OK : %.2f msecond response time | AvgRes=%.2f" % (float(solr_tpr_stats.stats['avgTimePerRequest']), float(solr_tpr_stats.stats['avgTimePerRequest']))
        sys.exit(0)
# Check Docs
elif cmd_options.doc :
    # Get the Documents Statistics
    solr_doc_stats = CollectStat('CORE', 'searcher')
    if int(solr_doc_stats.stats['numDocs']) >= int(cmd_options.critical_per):
        print "SOLR DOCS CRITICAL : %d Total Documents | numDocs=%d" % (int(solr_doc_stats.stats['numDocs']), int(solr_doc_stats.stats['numDocs']))
        sys.exit(2)
    elif int(solr_doc_stats.stats['numDocs']) >= int(cmd_options.warning_per):
        print "SOLR DOCS WARNING : %d Total Documents | numDocs=%d" % (int(solr_doc_stats.stats['numDocs']), int(solr_doc_stats.stats['numDocs']))
        sys.exit(1)
    else:
        print "SOLR DOCS OK : %d Total Documents | numDocs=%d" % (int(solr_doc_stats.stats['numDocs']), int(solr_doc_stats.stats['numDocs']))
        sys.exit(0)
else:
    sys.exit(3)
