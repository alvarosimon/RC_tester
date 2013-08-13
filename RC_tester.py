#!/usr/bin/python

import sys
import getopt

if sys.version_info < (2, 4):
    print "Your python interpreter is too old. Please consider upgrading."
    sys.exit(1)

import re
import os
import logging
import optparse
import hashlib
import datetime
import time
import commands
import platform


time_format_definition = "%Y-%m-%dT%H:%M:%SZ"
log = logging.getLogger("RC_tester")
UMD = ''
PRODUCT = ''
PKGSTOINSTALL= ''
LOGS_DIR = 'log'
DEPENDENCIES = ['emi-wms', 'emi-voms-mysql', 'gfal2', 'emi-lfc_mysql', 'emi-lfc_oracle', 'emi-dpm_mysql', 'emi-dpm_oracle', 'emi-dpm_disk', 'gridsite', 'ige-meta-security-integration', 'ige-meta-globus-default-security', 'emi-cream-ce', 'emi-torque-server', 'emi-torque-client', 'emi-torque-utils', 'nordugrid-arc-client', 'nordugrid-arc-information-index', 'nordugrid-arc-compute-element', 'emi-mpi', 'ige-meta-gridway', 'ige-meta-globus-myproxy', 'ige-meta-globus-rls', 'emi.amga.amga-cli', 'emi.amga.amga-server', 'emi-emir', 'ige-meta-globus-gram5', 'ige-meta-saga', 'emi-lb', 'unicore-hila-unicore6', 'unicore-gateway6', 'unicore-registry6', 'unicore-tsi6', 'unicore-hila-gridftp', 'emi-wn', 'unicore-uvos-server', 'emi-px', 'emi-bdii-site', 'gfal', 'emi-trustmanager', 'emi-argus', 'apel-client', 'apel-parsers', 'emi-cluster', 'emi-voms-oracle', 'emi-ui', 'ige-meta-globus-gsissh', 'dcache-server', 'dcache-srmclient', 'glexec']


def main(argv):
   global UMD
   global PRODUCT
   if not argv or len(sys.argv) < 1:
      print 'ERROR: unhandled option'
      print 'USAGE: RC_tester.py -u <UMD version> -p <product name>'
      print 'Example: RC_terter.py -u 3 -p umd-ui'
      sys.exit(2)
   try:
      opts, args = getopt.getopt(argv,'hu:p',['help','umd=','product='])
   except getopt.GetoptError:
      print 'RC_tester.py -u <UMD version> -p <product name>'
      sys.exit(2)
   for opt, arg in opts:
      if opt in ('-h','--help'):
         print 'RC_tester.py -u <UMD version> -p <product name>'
	 print 'OPTIONS:'
	 print '-h: help.'
         print '-u: UMD version to check. (1, 2 or 3).'
 	 print '-p: (optional) Product name to chek. "all" for all products.' 
         sys.exit()
      elif opt in ("-u", "--umd"):
         UMD = arg
      elif opt in ("-p", "--product"):
         PRODUCT = arg

def run_cmd(cmd):
        p = Popen(cmd, shell=True, stdout=PIPE)
        output = p.communicate()[0]
        return output


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":True,   "y":True,  "ye":True,
             "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")

if __name__ == "__main__":
	main(sys.argv[1:])


#for product in DEPENDENCIES:
#    print product

RELEASE = platform.dist()[0]


if RELEASE == 'redhat':
	print 'Scientific linux detected....'
        print 'Moving /var/log/yum.log to /var/log/yum.log.preUMD.'
	command = "/var/log/yum.log /var/log/yum.log.preUMD"
	log.info("Running: "+command)
	os.system(command)
        print 'Updating packages. Please wait...'
        command = "yum clean all;yum update -y"
        log.info("Running: "+command)
        os.system(command)


        print 'Installing RPM repo keys:'
        command = "rpm --import http://repository.egi.eu/sw/production/umd/UMD-RPM-PGP-KEY"
        log.info("Running: "+command)
        os.system(command)
        print 'Added UMD repo key.'

        command = "rpm --import http://emisoft.web.cern.ch/emisoft/dist/EMI/"+UMD+"/RPM-GPG-KEY-emi"
        log.info("Running: "+command)
        os.system(command)
        print 'Added EMI repo key.'

        command = "rpm --import http://repo-rpm.ige-project.eu/RPM-GPG-KEY-IGE"
        log.info("Running: "+command)
        os.system(command)
        print 'Added IGE repo key.'
	
        print 'Configuring /etc/yum/pluginconf.d/priorities.conf file...'
	prio_file = "/etc/yum/pluginconf.d/priorities.conf"
	with open(prio_file, "a") as myfile:
		myfile.write("\n")
    		myfile.write("check_obsoletes = 1\n")
		myfile.close()
        print 'Please make sure UMD repos are correctly installed into /etc/yum.repos.d directory and press enter and cross your fingers...'

elif RELEASE == 'debian':
        print 'Debian linux detected....'
        print 'Installing APT repo keys:'
        command = "wget -O umd.key http://repository.egi.eu/sw/production/umd/UMD-DEB-PGP-KEY; apt-key add umd.key"
        log.info("Running: "+command)
        os.system(command)
        print 'Added UMD repo key.'
	
        command = "wget -O ca.key http://repository.egi.eu/sw/production/cas/1/current/GPG-KEY-EUGridPMA-RPM-3; apt-key add ca.key"
        log.info("Running: "+command)
        os.system(command)
        print 'Added EUGridPMA repo key.'
	
       	command = "wget -O emi.key http://emisoft.web.cern.ch/emisoft/dist/EMI/2/RPM-GPG-KEY-emi ; apt-key add emi.key"
	log.info("Running: "+command)
        os.system(command)
        print 'Added EMI repo key.'

        command = "wget -O ige.key http://repo-rpm.ige-project.eu/RPM-GPG-KEY-IGE ; apt-key add ige.key"
	log.info("Running: "+command)
        os.system(command)

        print 'Added IGE repo key.'
        print 'Updating packages. Please wait...'
	command = "apt-get update;apt-get dist-upgrade -y"
	log.info("Running: "+command)
        os.system(command)

        print 'Please make sure UMD repos are correctly installed into /etc/apt/sources.list.d directory and press enter and cross your fingers...'

else:
	print ('ERROR: Unknown distro {0}... exiting'.format(RELEASE))
	log.info("ERROR: Unknown distro: "+RELEASE)
	sys.exit(2)



if query_yes_no("Do you want to coninue? ") == True:
	print "Ok, we will continue..."
	
else:
	print 'Exiting... Have a nice day.'
