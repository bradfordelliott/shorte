#!/usr/bin/env python
import os
import subprocess
import sys

# Cleanup any staged files
ph = subprocess.Popen(['git', 'reset', 'HEAD', '*'])
ph.wait()


count = 0
for root, dirs, paths in os.walk("."):
    for path in paths:
        fname = "%s/%s" % (root, path)
        phandle = subprocess.Popen(['git', 'diff', fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
        result = phandle.stdout.read()
        result += phandle.stderr.read()
        phandle.wait()
        rc = phandle.returncode
        phandle.stdout.close()
        phandle.stderr.close()

        if("diff" in result):

            if("old mode" in result):
                ph2 = subprocess.Popen(['git', 'checkout', '--', fname])
                ph2.wait()
                #print fname
                #print "RESULT:"
                #print result
                #print "RC:"
                #print rc

                count += 1

