# medit-sublime
This is attempt to create a plugin for Sublime Text 3

Current issues:
1. I am using Sublime Text 3 which uses python3. The RPCroker is is using 
   python2.7. I'll need to switch to new version of the RPCBroker in order 
   to seemlessly call connect from python3.

2. I am reading the sublime active window, so I'll need to change it to ask 
   for the file name without reading the sublime active window name.

Functionality:
1. Add a VistA menu option with Joel Ivy's Eclipse Editor RPCs and update medit configuration

2. There is a key binding provided
    { "keys": ["ctrl+m"], "command": "medit" },

3. A Sublime Event Listener for on_pre_save and on_modified was added in order 
   to update a modified '.m' routine date and time.
