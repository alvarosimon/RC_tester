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
from subprocess import Popen, PIPE

time_format_definition = "%Y-%m-%dT%H:%M:%SZ"
log = logging.getLogger("RC_tester")
Log_OK_file = "RC_tester_installation_OK.log"
Log_ERROR_file = "RC_tester_installation_ERROR.log"
UMD = ''
PKGSTOINSTALL= ''
Logs_dir = 'log'
DEPENDENCIES = ['emi-wms', 'emi-voms-mysql', 'gfal2', 'emi-lfc_mysql', 'emi-lfc_oracle', 'emi-dpm_mysql', 'emi-dpm_oracle', 'emi-dpm_disk', 'gridsite', 'ige-meta-security-integration', 'ige-meta-globus-default-security', 'emi-cream-ce', 'emi-torque-server', 'emi-torque-client', 'emi-torque-utils', 'nordugrid-arc-client', 'nordugrid-arc-information-index', 'nordugrid-arc-compute-element', 'emi-mpi', 'ige-meta-gridway', 'ige-meta-globus-myproxy', 'ige-meta-globus-rls', 'emi.amga.amga-cli', 'emi.amga.amga-server', 'emi-emir', 'ige-meta-globus-gram5', 'ige-meta-saga', 'emi-lb', 'unicore-hila-unicore6', 'unicore-gateway6', 'unicore-registry6', 'unicore-tsi6', 'unicore-hila-gridftp', 'emi-wn', 'unicore-uvos-server', 'emi-px', 'emi-bdii-site', 'gfal', 'emi-trustmanager', 'emi-argus', 'apel-client', 'apel-parsers', 'emi-cluster', 'emi-voms-oracle', 'emi-ui', 'storm-backend-server', 'ige-meta-globus-gsissh', 'dcache-server', 'dcache-srmclient', 'glexec','unicore-unicorex6', 'ige-meta-globus-gridftp', 'emi-ge-utils','qcg-accounting', 'qcg-broker', 'qcg-comp', 'qcg-core', 'qcg-ntf']


def main(argv):
   global UMD
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
	 if arg != "all":
		DEPENDENCIES = arg

def install_cmd(cmd):
	p = Popen(cmd, shell=True, stdout=PIPE)
        output = p.communicate()[0]
        return p.returncode


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

def try_my_software(RELEASE,DEPENDENCIES):
	global Logs_dir
	global Log_OK_file
	global Log_ERROR_file
	# Generate a logs dir first
	path = os.getcwd()
	Logs_dir = os.path.join(path, Logs_dir)
	if not os.path.isdir(Logs_dir):
		try:
    			os.makedirs(Logs_dir)
		except:
			print 'Error creating Logs dir... Exiting.'
			sys.exit(2)

	Log_OK_file = os.path.join(Logs_dir, Log_OK_file) 
	Log_ERROR_file = os.path.join(Logs_dir, Log_ERROR_file)
		
	if RELEASE == 'debian':
		print "OK, we will contine... Testing debian release."
		for package in DEPENDENCIES:
			print ('Installing {0} meta-package...'.format(package))
			command = "apt-get install -y "+ package +" > "+ Logs_dir +"/"+ package +"_apt_OUTPUT.log 2>&1"
			exit_code = install_cmd(command)
			# If installation was successful
			if exit_code == 0:
				with open(Log_OK_file, "a") as myfile:
                			myfile.write(package +": [OK] All dependencies are satisfied.\n")
                			myfile.close()
				command = "apt-get update;apt-get dist-upgrade -y -qq > "+ Logs_dir +"/"+ package +"_apt_postupdate.log 2>&1"
				os.system(command)
                	# If not something is wrong, write a log
                	else:
				print ('ERROR found installing {0} meta-package! Please check RC_tester logs.'.format(package))
	                        with open(Log_ERROR_file, "a") as myfile:
                                	myfile.write(package +": [ERROR] impossible to install some missing dependencies. Please, install it manually and read "+ package +"_apt_OUTPUT.log\n")
                                        myfile.close()

	if RELEASE == 'redhat':
		print "OK, we will contine... Testing redhat release."
		# remove VM yum log history 
		os.remove("/var/log/yum.log")
		for package in DEPENDENCIES:
			print ('Installing {0} meta-package...'.format(package))
			command = "yum install -y "+ package +" > "+ Logs_dir +"/"+ package +"_yum_OUTPUT.log 2>&1"
			exit_code = install_cmd(command)
                        # If installation was successful
                        if exit_code == 0:
                                with open(Log_OK_file, "a") as myfile:
                                        myfile.write(package +": [OK] All dependencies are satisfied.\n")
                                        myfile.close()


				# Create Uninstallation list
				command = "awk '{print $5}' /var/log/yum.log > uninstall.list"
				os.system(command)
				command = "yum update -y > "+  Logs_dir +"/"+ package +"_yum_postupdate.log 2>&1"
				os.system(command)
				
				# Uninstall UMD software
				uninstall_list = "uninstall.list"
				UNINSTALL = []

				# Read uninstall pakages list from the file 
				with open(uninstall_list) as my_file:
					for line in my_file:
						UNINSTALL.append(line.strip())

					my_file.close()

				UNINSTALL_LIST = ' '.join(UNINSTALL)

				print ('UNINSTALL list: {0}'.format(UNINSTALL_LIST))
				command = "yum remove -y "+ UNINSTALL_LIST +" > "+ Logs_dir +"/"+ package +"_yum_uninstall.log 2>&1"
				os.system(command)
				os.remove("/var/log/yum.log")
			else:
				print ('ERROR found installing {0} meta-package! Please check RC_tester logs.'.format(package))
                                with open(Log_ERROR_file, "a") as myfile:
                                	myfile.write(package +": [ERROR] impossible to install some missing dependencies. Please, install it manually and read "+ package +"_yum_OUTPUT.log\n")
                                        myfile.close()


if __name__ == "__main__":
	main(sys.argv[1:])
	euid = os.geteuid()
	if euid != 0:
    		print "Script not started as root. Exiting.."
		sys.exit(2)

#for product in DEPENDENCIES:
#    print product

RELEASE = platform.dist()[0]


if RELEASE == 'redhat':
	print 'Scientific linux detected....'
        print 'Moving /var/log/yum.log to /var/log/yum.log.preUMD.'
	command = "mv /var/log/yum.log /var/log/yum.log.preUMD"
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

        command = "rpm --import http://www.qoscosgrid.org/qcg-packages/sl5/RPM-GPG-KEY-QCG"
        log.info("Running: "+command)
        os.system(command)
        print 'Added QCG repo key.'

	command = "rpm --import http://download.nordugrid.org/RPM-GPG-KEY-nordugrid"
        log.info("Running: "+command)
        os.system(command)
        print 'Added NORDUGRID repo key.'

        command = "rpm --import http://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-6"
        log.info("Running: "+command)
        os.system(command)
        print 'Added EPEL 6 repo key.'
	
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

	command = "wget -O qcg.key http://www.qoscosgrid.org/qcg-packages/sl5/RPM-GPG-KEY-QCG ; apt-key add qcg.key"
        log.info("Running: "+command)
        os.system(command)

        print 'Added IGE repo key.'

        command = "wget -O arc.key http://download.nordugrid.org/RPM-GPG-KEY-nordugrid ; apt-key add arc.key"
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



if query_yes_no("Do you want to continue?: ") == True:
	try_my_software(RELEASE,DEPENDENCIES)
	print "DONE. Please read installator_OK.log and intallator_ERROR.log files for a complete report."
	print "Have a nice day!!!"
	
else:
	print 'Exiting... Have a nice day!!!.'
	sys.exit(0)
