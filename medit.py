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
# from sublime_plugin_lib.thread_progress_tracker import ThreadProgressTracker
from . import threadcheck


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

        if first_line is not None:
            temp_first_line = first_line.split(';')
            mynow = datetime.datetime.now().strftime("%m/%d/%y %H:%M")
            temp_first_line[2] = mynow
            clean_line = []
            for x in temp_first_line:
                clean_line.append(x.strip())

            new_first_line = clean_line[0] + ' ; ' + clean_line[1] + ' ; ' + clean_line[2]

            self.view.replace(edit, lines_num, new_first_line)
            print("first line")
            print(first_line)
            print("temp_first_line")
            print(temp_first_line)


class meditCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # self.view.insert(edit, 0, "Hello, World!")
        self.edit = edit
        try:
            pthcurrent = self.view.file_name()
        except:
            pass

        if (pthcurrent is None):
            prompt = 'ecptest.dallas:L:AGNRMSNG'
        else:
            prompt = "/".join(pthcurrent.split('/')[-1:])
            prompt = 'ecptest.dallas:S:' + "".join(prompt.split('.')[:1])

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
            '''
            print("argvs: ", meaction, rtn, host, context, brokerport,
                  accesscode, verifycode)
            print("python" + " " + meditrpc + " " + meaction + " " + rtn +
                  " " + host + " " + context + " " + brokerport + " " +
                  accesscode + " " + verifycode + " " + rtnpath)

            # test code end
            print('cmd: ')
            '''
            cmd = ["python" + " " + meditrpc + " " + meaction + " " + rtn +
                   " " + host + " " + context + " " + brokerport + " " +
                   accesscode + " " + verifycode + " " + rtnpath]
            print(cmd)

            win = self.view.window()
            maction = 'Saving....'
            maction_end = 'Saved!'
            thread = ThreadExecute(cmd, maction, win)
            thread.start()
            threadcheck.ThreadProgressTracker(thread, maction, maction_end)

        elif meaction == 'L':
            # load a routine from VistA
            print(' loading ---> ' + meditrpc)
            sublime.status_message("Loading... ^" + rtn + " from " + host)
            #
            print(" L : argvs: " + meditrpc, meaction, rtn, host, context,
                  brokerport, accesscode, verifycode)

            cmd = ["python" + " " + meditrpc + " " +
                   meaction + " " + rtn + " " + host + " " + context + " " +
                   brokerport + " " + accesscode + " " + verifycode + " " +
                   rtnpath]

            win = self.view.window()
            maction = 'Loading....'
            maction_end = 'Routine loaded!'
            thread = ThreadExecute(cmd, maction, win)
            thread.start()
            threadcheck.ThreadProgressTracker(thread, maction, maction_end)

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

