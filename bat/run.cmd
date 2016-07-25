@echo off
cd C:\Users\dzony\Documents\projects\system\env\system\Scripts

start cmd /k "activate && cd C:\Users\dzony\Documents\projects\system\server__client\ && python start.py"
sleep 0.1
start cmd /k "activate && cd C:\Users\dzony\Documents\projects\system\backend\ && python start.py"



