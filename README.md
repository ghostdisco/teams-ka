# Teams - Keep Alive!

<br>

# Windows Release
## Running
INFO: Download and run the release executable. You may be prompted by Windows that the publisher is untrutsted, this is because I haven't spent $300 on an EV cert yet :/

First Run Option 1:
  1. Run the teams-ka.exe, it will generate a 'teams-ka.ini' file and exit.
  2. Open the .ini file with a text editor and enter your username and password in the appropriate lines. Make sure to leave the 'key' field empty.
  3. Run the teams-ka.exe file again, this time it will encrypt your password in the .ini file and launch.

First Run Option 2:
  1. Using your shell console of choice (cmd/powershell/ConEmu), execute the teams-ka.exe file with the following arguments: ```-u [USERNAME] -p [PASSWORD]```
  2. The application will generate the .ini file then encrypt/store your password.

Once completing one of these steps you can continue to run teams-ka.exe without performing either option until the next time you change your password. To prevent accidental account locks, teams-ka will only attempt to submit a password once.

<br>

## Packaging
Packaging for Windows is currently done manually by creating an sfx of all dependencies (including Mozilla Firefox binaries) and launches a cmd bootstrap.

<br>

# Mac OS/Linux Release
### Running

First Run Option 1:
  1. In Terminal, update the permissions of the file to be executable: ```chmod u+x teams-ka.app```
  2. Execute the app to generate a .ini file: ```./teams-ka.app```
  3. Open the resulting teams-ka.ini file with a text editor and enter your username and password in the appropriate lines. Make sure to leave the 'key' field empty.
  4. Execute the app again and it should run.

First Run Option 2:
  1. In Terminal, update the permissions of the file to be executable: ```chmod u+x teams-ka.app```
  2. Execute the app with arguments to add your username and password to the resulting .ini file: ```./teams-ka.app -u [USERNAME] -p [PASSWORD]```

Once completing one of these steps you can continue to run teams-ka.exe without performing either option until the next time you change your password. To prevent accidental account locks, teams-ka will only attempt to submit a password once.

I recommend using [screen](https://kapeli.com/cheat_sheets/screen.docset/Contents/Resources/Documents/index) to free up your terminal after executing the app.

<br>

# Workspace
I'm currently working on a Makefile to assist in setting up a workspace. At the moment you'll need to perform the following
  1. [Install python3](https://www.python.org/downloads/)
  2. Install Mozilla Firefox
      * Unless you want to point geckodriver to the binaries in code, this must be a system install.
      <br>If on Windows, ensure Firfox is installed in either C:\Program Files\Mozilla Firefox or C:\Program Files (x86)\Mozilla Firefox.
      <br>If Firefox is not installed in one of those locations, you'll want to download the .msi from their site and re-install.
  3. [Download geckodriver](https://github.com/mozilla/geckodriver/releases) and add it to your system path.
  4. Install all dependencies at the root of the project: ```python3 -m pip install -r requirements.txt```

<br>

# Building
todo