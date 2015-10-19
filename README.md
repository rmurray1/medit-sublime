# medit-sublime
This is an attempt to create a plugin for Sublime Text 3

Current issues:
1. I am using Sublime Text 3 which uses python3. The RPCroker is using 
   python2.7. I'll need to switch to a new version of the RPCBroker in order 
   to seemlessly call connect from python3.

2. I am reading the sublime active window, so I'll need to change it to ask 
   for the file name.


Functionality:
1. Add a VistA menu option with Joel Ivy's Eclipse Editor RPCs and update medit or
   install the new .KIDs build

2. There is a key binding example: { "keys": ["ctrl+m"], "command": "medit" }

3. Added updating the .m modified date. Functionality uses Sublime Event  
   Listeners "on_pre_save" and "on_modified" insert current date and time.

