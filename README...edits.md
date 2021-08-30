First Run Option 1:
  1. Run the teams-ka.exe, it will generate a 'teams-ka.ini' file and exit.
  2. Open the .ini file with a text editor and enter your username and password in the appropriate lines. Make sure to leave the 'key' field empty.
  3. Run the teams-ka.exe file again, this time it will encrypt your password in the .ini file and launch.

First Run Option 2:
  1. Using your shell console of choice (cmd/powershell/ConEmu), execute the teams-ka.exe file with the following arguments: ```-u [USERNAME] -p [PASSWORD]```
  2. The application will generate the .ini file then encrypt/store your password.

Once completing one of these steps you can continue to run teams-ka.exe without performing either option until the next time you change your password. To prevent accidental account locks, teams-ka will only attempt to submit a password once.