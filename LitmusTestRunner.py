import sys
import os
import unittest
import httplib
import urllib
import time
import platform
import StringIO
from sikuli.Sikuli import *

import sg8_miroguide
import sg2_search
import sg6_feeds


   
def get_os_name():
    """Returns the os string for the SUT
    """
    if "MAC" in str(Env.getOS()):
        return "osx"
    elif "WINDOWS" in str(Env.getOS()):
        return "win"
    elif "LINUX" in str(Env.getOS()):
        return "lin"
    else:
        print ("I don't know how to handle platform '%s'", Env.getOS())

HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<litmusresults action="submit" useragent="UberSikuliAgent/1.0 (machine foobar)" machinename="sikuli_machine">
   <testresults
   username="pcf.subwriter@gmail.com"
   authtoken="autotester"
   product="Miro"
   platform="%(opsys)s"
   opsys="%(platform)s"  
   branch="git-Master"
   buildid="%(buildid)s"
   locale="en-US"
   >
   """

STORY = """
    <result testid="%(testid)s"
    is_automated_result="0"
    resultstatus="%(status)s"
    exitstatus="0"
    timestamp="%(timestamp)s"
    >
    
        <comment><![CDATA[ %(error_msg)s]]>
        </comment>
    </result>
"""

FOOTER = """
    </testresults>
</litmusresults>
"""

def set_test_id(test_id):
    tid = test_id.split()
    s = str(tid[0]).strip(">,<,[,]")
    L = s.split('_')
    testid = L.pop()
    return testid


def set_status(stat):
    print stat
    if stat == ".":
        status = "pass"
    else:
        status = "fail"
    return status

def get_linux_os():
    UBUNTU_DICT = {"10.04":"Ubuntu (Lucid)",
                   "10.10":"Ubuntu (Maverick)",
                   "11.04":"Ubuntu (Natty)"}

    f = open("/etc/issue",'r')
    info = f.read()
    f.close()
    v,r,_,_ = info.split()
    if v == "Ubuntu":
        plat = UBUNTU_DICT[r]
    else:
        plat = "generic"
    return plat

def set_litmus_os():
    """Returns the os string for the SUT using the Sikuli way)

    """
    test_os = get_os_name()
    if str(test_os) == "osx":
        v, _, _ = platform.mac_ver()
        v = str('.'.join(v.split('.')[:2]))
        lit_os = ["OS X", v]
        return lit_os
    elif str(test_os) == "win":
        v = platform.release()
        lit_os = ["Windows", v]
        return lit_os
    elif str(test_os) == "lin":
        plat = get_linux_os()
        lit_os = ["Linux",plat]
        return lit_os
        
    else:
        print ("I don't know how to handle platform '%s'", test_os)      


def write_log(log,testid,stat,error_info=""):
    f = open(log, 'a')
 
    
    f.write(STORY % {"testid": set_test_id(testid),
                     "status": set_status(stat),
                     "timestamp": time.strftime("%Y%m%d%H%M%S", time.gmtime()),
                     "error_msg": error_info.lstrip('.')
                         })
    f.close

def write_footer(log):
    f = open(log, 'a')
    f.write(FOOTER)
    f.close


def send_result(log):
    f = open(log)
    log_data = f.read()
    params = urllib.urlencode({'data':log_data,                               
                                })
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    conn = httplib.HTTPConnection("litmus.pculture.org")

    print "sending test result..."
    conn.request("POST", "/process_test.cgi", params, headers)
    response = conn.getresponse()
    data = response.read()
    print data
    conn.close()
    f.close()


def set_build_id():
#    build_id = "2010112900" #set custom build id here.
    build_id = time.strftime("%Y%m%d", time.gmtime()) + "99"
    return build_id

def write_header(log):
    (r,v) = set_litmus_os()
    f = open(log,'w')
    f.write(HEADER % {"buildid": set_build_id(),
                      "opsys": r,
                      "platform": v
                      })
    f.close



class LitmusRunner(unittest.TestCase):
    def __init__(self,suite,litmus):
        params = []
        self.litmus = litmus
        if "Miro_Suite" in str(suite):
            self.suite = unittest.TestLoader().loadTestsFromTestCase(suite)
        else:
            params = list(suite)
            subgroup = params[0]
            sg = subgroup.split('.sikuli')
            self.suite = unittest.TestSuite()
            for tc in params:
                if "test" in tc:
                    self.suite.addTests([unittest.defaultTestLoader.loadTestsFromName(sg[0]+'.Miro_Suite.'+tc)],)
                    
    def litmus_test_run(self):   
        logfile = os.path.join(os.getcwd(),"log.xml")
        buf = StringIO.StringIO()
        runner = unittest.TextTestRunner(stream=buf)
        write_header(logfile)
        
        for x in self.suite:
            runner.run(x)
            # check out the output
            byte_output = buf.getvalue()
            id_string = str(x)
            stat = byte_output[0]
            print byte_output
            write_log(logfile,id_string,stat,byte_output)
            buf.truncate(0)

        write_footer(logfile)
#        send_result(logfile)



