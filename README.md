RC_tester
=========

_SA2 UMD Release Candidate tester. This script is used to verify UMD release candidates and UMD package dependencies._

* SA2.3 Verification wiki page -- https://wiki.egi.eu/wiki/EGI_Quality_Criteria_Verification
* EGI UMD repository -- http://repository.egi.eu/


Requirements
------------

* UMD repository configuration
* Python 2.5

### Examples
To test UMD 3 meta-packages:
~~~
RC_tester.py --umd 3
~~~

To test a specific meta-package:
~~~
RC_tester.py --umd 3 --product emi-ui
~~~
