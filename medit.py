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
import subprocess
import datetime
import threading
from .threadcheck import ThreadProgressTracker


class PreInsertDateTime(sublime_plugin.EventListener):
    is_modified = False

    def on_pre_save_async(self, view):
        file_name = view.file_name()
        # print(view.file_name(), "is about to be saved")
        # should be .m
        mExt = file_name[-2:]
        #print(file_name[-2:])
        if (mExt == '.m' and self.is_modified):
            view.run_command('insert_date_timeb')

    def on_modified_async(self, view):
        self.is_modified = True


class InsertDateTimebCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        # add this to insert at current cursor position
        # http://www.sublimetext.com/forum/viewtopic.php?f=6&t=11509
        region = sublime.Region(0, 0)

        lines_num = self.view.line(region)

        first_line = self.view.substr(lines_num)

        if (first_line is not None):
            if (first_line.find(";") != -1):
                temp_first_line = first_line.split(';')
                mynow = datetime.datetime.now().strftime("%m/%d/%y %H:%M")
                temp_first_line[2] = mynow
                clean_line = []
                for x in temp_first_line:
                    clean_line.append(x.strip())

                new_first_line = clean_line[0] + ' ;' + clean_line[1] + ' ;' + clean_line[2]

                self.view.replace(edit, lines_num, new_first_line)
                '''
                print("first line")
                print(first_line)
                print("temp_first_line")
                print(temp_first_line)
                '''


class meditCommand(sublime_plugin.TextCommand):
    pthcurrent = None
    servers = None
    selserver = None
    selaction = None
    actions = None

    @staticmethod
    def readjson():
        # read json file
        import json
        # cfpath = os.getcwd()
        pkpath = sublime.packages_path()
        brokersettings = pkpath + "/medit/medit.default-config.json"
        # test print code
        hostnames = []
        '''
        print('broker:' + brokersettings)
        print("pkpath: " + pkpath)
        '''
        mydata = '0'
        if os.path.exists(pkpath):
            # Grab the data
            # print('before the try')
            my_data = json.loads(open(brokersettings).read())
            # print(my_data)
            for key in my_data.keys():
                #print(key)
                hostnames.append(key)
        return hostnames

    def run(self, edit):
        # self.view.insert(edit, 0, "Hello, World!")
        self.edit = edit
        self.actions = ['Load', 'Save']
        try:
            self.pthcurrent = self.view.file_name()
        except:
            pass

        self.servers = self.readjson()
        '''
        print("servers")
        print(self.servers)
        '''

        if self.servers is None:
            return
        self.getserver()

    def getserver(self):
        win = self.view.window()
        win.show_quick_panel(self.servers, self.actserver)

    def actserver(self, idx):
        self.selserver = self.servers[idx]
        '''
        print('self.selserver')
        print(self.selserver)
        '''
        self.getaction()

    def getaction(self):

        win = self.view.window()
        win.show_quick_panel(self.actions, self.actaction)

    def actaction(self, idx):
        self.selaction = self.actions[idx][0]
        '''
        print('self.selaction')
        print(self.selaction)
        '''
        if (self.selaction is None) or (self.selserver is None):
            return

        prompt =  self.selserver + ':' + self.selaction
        '''
        print('my prompt:')
        print(prompt)
        '''
        if (self.pthcurrent is None):
            prompt = prompt + ':ROUTINE'

        if (self.pthcurrent is not None):
            #filenmpt = "/".join(self.pthcurrent.split('/')[-1:])
            #filenm =  "".join(filenmpt.split('.')[:1])
            fileName,fileExtension = os.path.splitext(self.pthcurrent)
            filenm = "/".join(fileName.split('/')[-1:])

            '''
            print('filenm')
            print(filenm)
            print("fileName",fileName)
            print("fileExtension",fileExtension)
            '''
            if (fileExtension != ".m"):
                sublime.status_message(filenm + fileExtension + ' is not a Mumps *.m file')
                return
            prompt = prompt +":" + filenm
            '''
            print("prmpt")
            print(prompt)
            '''
        win = self.view.window()
        win.show_input_panel("Enter <site:action:routine name> ",
                             prompt, self.on_done, None, None)

    def on_done(self, user_input):
        # this is displayed in status bar at bottom

        def Window():
            return sublime.active_window()

        # when closing a project, project_data returns "None"
        def get_project_data(window):
            project_data = window.project_data()
            if project_data is None or 'folders' not in project_data:
                project_data = {}
                project_data['folders'] = []
            return project_data

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
        try:
            folder = self.view.window().folders()[0]
            pthcurrent = self.view.file_name()
        except:
            pass

        # /Users/vhantxmurrar/Documents..
        # /Raleigh/Assignments/VistA_projects/Radnuc/R1RARNU5.m
        print("folder  --")
        print(folder)
        print("pthcurrent  --")
        print(pthcurrent)

        if pthcurrent is None:
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
            #
            # <=============  save routine to VistA =================>
            sublime.status_message("Saving... ^" + rtn + " to VistA")
            # test code to print out

            cmd = ["python" + " " + meditrpc + " " + meaction + " " + rtn +
                   " " + host + " " + context + " " + brokerport + " " +
                   accesscode + " " + verifycode + " " + rtnpath]
            print(cmd)

            win = self.view.window()
            maction = host + ': ' + rtn + ' -> Saving.... '
            maction_end = host + ': ' + rtn + ' -> Saved!'
            thread = ThreadExecute(cmd, maction, win)
            thread.start()
            ThreadProgressTracker(thread, maction, maction_end)

        elif meaction == 'L':
            # load a routine from VistA
            print(' loading ---> ' + meditrpc)
            sublime.status_message("Loading... ^" + rtn + " from " + host)
            #
            # print(" L : argvs: " + meditrpc, meaction, rtn, host, context,
            #      brokerport, accesscode, verifycode)

            cmd = ["python" + " " + meditrpc + " " +
                   meaction + " " + rtn + " " + host + " " + context + " " +
                   brokerport + " " + accesscode + " " + verifycode + " " +
                   rtnpath]

            print("load cmd: ", cmd)
            win = self.view.window()
            maction = host + ': ' + rtn + ' -> Loading....'
            maction_end = host + ': ' + rtn + ' -> Routine loaded!'
            thread = ThreadExecute(cmd, maction, win)
            thread.start()
            ThreadProgressTracker(thread, maction, maction_end)

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


    def getnodedata(self, node, configjs):
        server_config = '0'
        if configjs is not None:
            #
            # load the right configuration from the passed in node
            #
            server_config = {
                "context": configjs["context"]["menuoption"],
                "host": configjs[node]["host"],
                "brokerport": configjs[node]["brokerport"],
                "accesscode": configjs[node]["accesscode"],
                "verifycode": configjs[node]["verifycode"]
            }
        return server_config

class ThreadExecute(threading.Thread):
    def __init__(self, cmd, action, win):
        self.cmd = cmd
        self.action = action
        self.result = None
        self.error = None
        self.win = win
        threading.Thread.__init__(self)

    def run(self):
        # print_to_panel

        # call python verion 2.7.9 to connect to VistA broker
        try:
            mypipe = subprocess.Popen(self.cmd, shell=True,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)

            (self.result, self.error) = mypipe.communicate()
            print("self.result ===>")
            print(self.result)
            self.print_to_panel(self.result, self.win)
        except Exception as e:
            print(str(e))
            self.print_to_panel(e, self.win)

    def print_to_panel(self, output_lines, win):
            # strtxt = u"".join(line.decode("utf-8") for line in output_lines)
            strlist = bytes(output_lines).decode('utf-8')

            # strlist = str(output_lines).split('\r\n')
            #win = self.view.window()
            if(len(strlist)):
                outputview = win.create_output_panel('vrpc_out')
                outputview.run_command('erase_view')
                win.run_command("show_panel", {"panel": "output.vrpc_out"})
                outputview.run_command('insert', {'characters': strlist})
                print(strlist)

