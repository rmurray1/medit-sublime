#!/usr/bin/env python
'''
------------------------------
    Author:  Raleigh Murray
    Date: 2/11/2015
    FileName: meditrpcex.py

   Description:
        plugin to access a remote VistA System
        uses vistarpc which is installed in python 2.7
        from Sublime Text 3  a helper script 'meditrpcex.py is called
 -----------------------------
Create a Menu optioin called 'R2 MEDIT RPC' with the following RPC

Used the eclipse plugin and routine ^XTECLIPS as a guide
RPC(XTECRES,XTECFUNC,XTECLINE,XTECFROM,XTECTO,XTECOPT) --

XTECRES = this is the return value from the RPC call, will contain a
                  global reference
XTECFUNC = this is the type of function that is being done.
       ;       = RD Routine directory passed back in ARRAY
       ;       = RL Routine Load into ARRAY
       ;       = RS Routine Save Save the routine from XTECLINE
       ;       = GD Global directory Passed Back in ARRAY
       ;       = GL Global List in ARRAY
XTECLINE = This is the total number of line that are requested at a time
XTECFROM = This is the starting point or the one to be listed
XTECTO =  this is the ending point

rpc: XT ECLIPSE M EDITOR
NUMBER: 3124                            NAME: XT ECLIPSE M EDITOR
TAG: RPC                              ROUTINE: XTECLIPS
RETURN VALUE TYPE: GLOBAL ARRAY       WORD WRAP ON: TRUE

'''
import os
import json
import sys

from vavista.rpc import connect, PLiteral, PList, PReference


def readconfigjs(node):
    # read json file

    # cfpath = os.getcwd()
    brokersettings = "meditrpc-config.json"
    if os.path.exists(brokersettings):
        # Grab the data
        try:
            my_data = json.loads(open(brokersettings).read())
        except:
            sys.exit(1)

        # load the right configuration from the passed in node
        server_config = {
            "context": my_data["context"]["menuoption"],
            "host": my_data[node]["host"],
            "brokerport": my_data[node]["brokerport"],
            "accesscode": my_data[node]["accesscode"],
            "verifycode": my_data[node]["verifycode"]
        }
        # print(server_config)
    return server_config

# String rpcResult = vistaConnection.rpc("XT ECLIPSE M EDITOR", "RS", contents, routineName, "0^^0"


def routinesaveto_VistA(c, routinename, rtndir):
    # ----- Call to save routine to VistA ----------
    # routinename = "XUP"
    #
    rtnfile = rtndir + '/' + routinename + '.m'
    if not os.path.exists(rtnfile):
        print("Error: no such file or directory " + "'" + rtnfile + "'")
        sys.exit(1)

    try:
        f = open(rtndir + "/" + routinename + '.m', 'r')
    except:
        print('Error: reading ' + routinename + '.m')
        sys.exit(1)
    rtn_data = f.readlines()
    f.close()
    contents = {}
    print(rtn_data[0])
    i = 0
    for i in range(len(rtn_data)):
        # remove the \r\n at the end of the line
        rtn_data[i] = rtn_data[i].rstrip('\r\n')
        # remove the \t at the beginning of a line
        first_tab_init_pos = rtn_data[i].find('\t')
        # print('first: ' + str(i) + " -->" + str(first_tab_init_pos))
        if first_tab_init_pos == 0:
            # replace  '\t' if at the start of line a space'
            rtn_data[i] = rtn_data[i].replace('\t', ' ')
            contents[i+1] = rtn_data[i]
        else:
            contents[i+1] = rtn_data[i]

    #  call VistA rpc to save the routine
    # print(contents)
    rpcresult = "1"
    '''
    test code below
    python meditrpcex.py 'S' 'XUP' '127.0.0.1' 'R2 MEDIT RPC' 9430 'SM1234' 'SM1234!!'
    '''
    rpcresult = c.invoke("XT ECLIPSE M EDITOR", "RS", PList(contents), routinename, "0^^1")
    '''
    if (rpcresult.split("^") == 1):
        rpcresult = ""
    '''
    # rpcresult = rpcresult[rpcresult.find('\n')+1:]
    #
    print(rpcresult)
    return rpcresult

#Routine Load from VistA


def routineloadfrmVistA(c, routinename, savedir):
    # routinename = "AGNRMSNG"
    rpcresult = c.invoke("XT ECLIPSE M EDITOR", "RL", "notused", routinename)
    if not rpcresult.startswith("-1^Error Processing load request"):
        try:
            f = open(savedir + "/" + routinename + '.m', 'w')
        except:
            # invalid json
            sys.exit(1)

        # suppose to skip the first line "1^routinename\n"
        rpcresult = rpcresult[rpcresult.find('\n')+1:]
        for rtnline in rpcresult:
                f.write(rtnline)
        f.close()
    return rpcresult


# main()
def main():
    import sys
    import getopt
   #  from vavista.rpc import connect, PLiteral, PList, PReference

    opts, args = getopt.getopt(sys.argv[1:], "")

    if len(args) < 4:
        print(args)
        sys.stderr.write("meditrpcex.py maybe missing \n")
        sys.exit(1)

    maction = sys.argv[1]
    rtnfile = sys.argv[2]
    host = sys.argv[3]
    context = sys.argv[4]
    brokerport = sys.argv[5]
    access = sys.argv[6]
    verify = sys.argv[7]
    rtnpath = sys.argv[8]
    #
    #
    # print("action: " + maction + " : rtn " + rtnfile + " : host " + host +" ... port " + brokerport + "  ... access " + access + "  ... verify  " + verify + "  ... context " + context + " :  " + rtnpath + "\n" )
    try:
        c = connect(host, int(brokerport), access, verify, context)
        # c = connect('127.0.0.1', 9430, 'SM1234', 'xxxxxxxx', 'R2 MEDIT RPC')
    except:
        print("can't connect to " + host)
        sys.exit(1)

    """
       ;       = RD Routine directory passed back in ARRAY
       ;   L  = RL Routine Load into ARRAY
       ;   S  = RS Routine Save Save the routine from XTECLINE
       ;       = GD Global directory Passed Back in ARRAY
       ;       = GL Global List in ARRAY

    """
    if maction == 'L':
        # print('Loading --->' + rtnfile)
        routineloadfrmVistA(c, rtnfile, rtnpath)
        sys.exit(1)
    elif maction == 'S':
        # print('Saving --> ' + rtnfile)
        routinesaveto_VistA(c, rtnfile, rtnpath)

    # routineloadfrmVistA

if __name__ == '__main__':
    main()
