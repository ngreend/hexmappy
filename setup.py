from cx_Freeze import setup, Executable

base = None    

executables = [Executable("hexmappy.py", base=base)]

packages = ["idna","os","sys","platform","random","math","operator","pygame","threading","tkinter","utils","mapgen","hextile","button"]
options = {
    'build_exe': {    
        'packages':packages,
    },    
}

setup(
    name = "Hexmappy",
    options = options,
    version = "1.0",
    description = 'Hexmap editor',
    executables = executables
)
