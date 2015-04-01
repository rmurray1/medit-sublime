'''
------------------------------
    Author:  Raleigh Murray
    Date: 2/11/2015
    FileName: medit.py

    Description:
        plugin to access a remote VistA System
        uses vistarpc which is installed in python 2.7
        from Sublime Text 3  a helper script 'meditrpcex.py is called
------------------------------

'''
import sublime
import sublime_plugin
import os
import sys


class meditCommand(sublime_plugin.TextCommand):
    def run(self, view):
        # self.view.insert(edit, 0, "Hello, World!")
        pthcurrent = self.view.file_name()
        if (len(pthcurrent) == 0):
            prompt = 'ecptest.dallas:L:AGNRMSNG'
        else:
            prompt = "/".join(pthcurrent.split('/')[-1:])
            prompt = 'ecptest.dallas:S:' + "".join(prompt.split('.')[:1])
        self.view.window().show_input_panel(
            "Enter <site:action:routine name> ",
            prompt, self.on_done, None, None)

    def on_done(self, user_input):
        import subprocess
        # this is displayed in status bar at bottom

        def print_to_panel(output_lines):
            # strtxt = u"".join(line.decode("utf-8") for line in output_lines)
            strlist = output_lines.decode("utf-8")
            # strlist = str(output_lines).split('\r\n')
            win = self.view.window()
            if(len(strlist)):
                outputview = win.create_output_panel('vrpc_out')
                outputview.run_command('erase_view')
                win.run_command("show_panel", {"panel": "output.vrpc_out"})
                outputview.run_command('insert', {'characters': strlist})
                print(strlist)

        valid = ['S', 'L']
        data = str(user_input).split(':')
        #
        # ex site:meaction:routinename
        # ecptest.dallas:S:AGNRMSNG
        #
        site = data[0]
        meaction = data[1].upper()
        rtn = data[2].upper()
        #
        print(meaction, rtn)
        #
        # retreive config data
        myconfig = self.readconfigjs(site)
        context = "'{}'".format(myconfig["context"])
        host = "'{}'".format(myconfig["host"])
        brokerport = "'{}'".format(myconfig["brokerport"])
        accesscode = "'{}'".format(myconfig["accesscode"])
        verifycode = "'{}'".format(myconfig["verifycode"])
        # print(myconfig)
        #
        folder = self.view.window().folders()[0]
        #
        pthcurrent = self.view.file_name()
        if len(pthcurrent) is None:
            pthcurrent = folder
        else:
            pthcurrent = "/".join(pthcurrent.split('/')[:-1])

        pkpath = sublime.packages_path()
        rtnpath = "'" + pthcurrent + "'"
        meditrpc = "'" + pkpath + "/medit/meditrpcex.py'"
        print("rtnpath: " + rtnpath)
        if meaction not in valid:
            sys.exit(1)
        elif meaction == 'S':
            # save routine to VistA
            sublime.status_message("Saving... ^" + rtn + " to VistA")
            # test code to print out
            print("argvs: ", meaction, rtn, host, context, brokerport,
                  accesscode, verifycode)
            print("python" + " " + meditrpc + " " + meaction + " " + rtn +
                  " " + host + " " + context + " " + brokerport + " " +
                  accesscode + " " + verifycode + " " + rtnpath)
            # test code end
            #
            print(self.view.file_name())
            process = subprocess.Popen(
                ["python" + " " + meditrpc + " " + meaction + " " + rtn + " " +
                    host + " " + context + " " + brokerport + " " +
                    accesscode + " " + verifycode + " " + rtnpath],
                shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # check output from process communication
            output, error = process.communicate()
            if error:
                print(error)
            else:
                sublime.status_message("^" + rtn + " saved")
                # list_output = str(output).split('\r\n')
                print_to_panel(output)

        elif meaction == 'L':
            # load a routine from VistA
            print(' loading ---> ' + meditrpc)
            sublime.status_message("Loading... ^" + rtn + " from " + host)
            #
            print(" L : argvs: " + meditrpc, meaction, rtn, host, context,
                  brokerport, accesscode, verifycode)

            process = subprocess.Popen(
                ["python" + " " + meditrpc + " " +
                    meaction + " " + rtn + " " + host + " " + context + " " +
                    brokerport + " " + accesscode + " " + verifycode + " " +
                    rtnpath],
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            # process.wait()
            output, error = process.communicate()
            if error:
                print(error)
            else:
                sublime.status_message("^" + rtn + " loaded")
                print_to_panel(output)

    def readconfigjs(self, node):
        # read json file
        import json
        # cfpath = os.getcwd()
        pkpath = sublime.packages_path()
        brokersettings = pkpath + "/medit/medit.default-config.json"
        # test print code
        '''
        print('broker:' + brokersettings)
        print("pkpath: " + pkpath)
        '''
        # brokersettings = "meditrpc-config.json"
        server_config = '0'
        if os.path.exists(pkpath):
            # Grab the data
            print('before the try')
            my_data = json.loads(open(brokersettings).read())
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

