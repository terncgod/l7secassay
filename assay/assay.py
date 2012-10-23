"""
    Prog written to run a series of tests against a known
    vulnerable web app (DVWA). The goal would be to run this with
    no protective measures in place to display risk.
    Then another run with your Layer 7/Web App protective measure 
    in place to show the value and effectiveness of such a device
    when it is in place.

    Note:
    The DVWA version used when this prog was first written: 1.0.6
    http://www.dvwa.co.uk/download.php

    OWASP Top 10 areas covered by this prog:
        A1: Injection
        A2: Cross-Site Scripting (XSS)
        A3: Broken Authentication and Session Management
        A4: Insecure Direct Object References
        A5: Cross-Site Request Forgery (CSRF)
        A8: Failure to Restrict URL Access
        A10: Unvalidated Redirects and Forwards

    Obviously not every aspect of each one of these
    areas is covered. But enough is covered to show
    the value of the protective measure in place.

    Areas not covered:
        A6: Security Misconfiguration
        A7: Insecure Cryptographic Storage
        A9: Insufficient Transport Layer Protection
        
    License:
    assay
    Copyright (C) 2010 - 2012 Bayshore Networks, Inc.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import argparse
import sys
import funcs
import vars
import attacks
##################################################################
# vars
url = vars.getUrl()
# static vars
apppath = vars.apppath
loginpage = vars.loginpage
targetpath = vars.targetpath
slash = vars.slash
user = vars.user
# dynamic vars
targetloginpage = url+apppath+loginpage
successfulattacks = {}
##################################################################
# start prog
if __name__=='__main__':
    seclevel = 0
    parser = argparse.ArgumentParser(description='Bayshore Networks - assay')
    parser.add_argument('-s','--secure', help='level of security in front of DVWA instance (WAF present or not)', required=True)
    args = parser.parse_args()

    if funcs.checkArgs(args.secure):
        #vars.seclevel = int(args.secure)
        vars.setPrefix(val=int(args.secure))
    else:
        print "\nInvalid sec level\n"
        sys.exit(0)
    
    ##################################################################
    # print banner
    funcs.printBanner(targetloginpage, user)
    # do auth and get a Browser obj to work with
    try:
        fp = funcs.doLogin(targetloginpage)
    except Exception, e:
        funcs.attackOutPut(funcs.stepTwo, "info", e)
    # end of auth - session should be established from here on
    ##################################################################
    # perform attacks
    """
        if we made it here then auth is successful
        now go into the main loop based on attack
        types and work with the results, all the
        attack functions are in class "Attacks",
        filename: attacks.py
    """
    # create object
    attacks = attacks.DVWAAttacks(url, apppath)
    # establish a baseline if its possible
    attacks.setRedirBaseline(fp=fp, url=url)
    """
        kick off an initial browser instance
        with an authenticated session
    """
    #attacks.startUpBrowser()
    """
        dynamically construct the function names based on
        values from the types list/array
        the dynamic construction takes place in the class
    """
    for i in range(len(vars.typedesc)):
        for func in vars.typedesc:
            """
                do a match on index 3 (integer) to make
                sure an order is followed in terms of the
                chronology of attack events
            """
            if vars.typedesc[func][3] == i:
                #print typedesc[d]
                #print d
                # describe the step in stdout output
                funcs.attackOutPut(funcs.stepTwo, "step", "Processing - %s%s ..." % (vars.typedesc[func][0], vars.typedesc[func][1]))
                targeturl = url + apppath + targetpath + func + slash
                #print targeturl
                res = attacks.call(func, fp, targeturl)

                # a list is returned when attack vectors
                # were successfully injected
                if type(res) is list:
                    vars.successfulVectors += len(res)
                    successfulattacks[func] = res
    ##################################################################
    # output of results
    print
    wafdetect = attacks.detectWAF()
    if wafdetect:
        funcs.attackOutPut(funcs.stepOne, "discovered", "The following WAF was detected: %s" % wafdetect[0])

    funcs.printResults(successfulattacks=successfulattacks, url=url)
    funcs.printStats()
    attacks.saveHTML()
    ##################################################################