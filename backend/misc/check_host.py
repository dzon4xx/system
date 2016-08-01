import os

if os.name == 'posix':
    is_RPI = True
else:
    is_RPI = False