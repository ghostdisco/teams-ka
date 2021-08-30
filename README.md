# Teams - Keep Alive!

<br>

# Windows Release
## Running

Pre-Requisites:
  * Mozilla Firefox
    * Firefox must be installed for all users and by default installs only for the user installing.
    * If you already have Firefox installed and would like to verify it's for all users, you can do so by verifying it is in either C:\Program Files\Mozilla Firefox or C:\Program Files (x86)\Mozilla Firefox. If not then you must uninstall then proceed to the next step to install for all users.
    * To install for all users:
      1. Visit the [download site](https://mozilla.org/en-US/firefox/all/#product-desktop-release)
      2. Select the following options:
          * Which browser would you like to download: Firefox
          * Select your preferred installer: Windows 64-bit MSI
      3. Download and run the .msi to install for all users

First Run Option 1:
  1. Extract the teams-ka.zip archive to the location you'd like it to run from.
  2. Run the run.bat file to launch the embedded python instance and the teams-ka module. The app will immediately close, having created a teams-ka.ini file in the teams-ka folder.
  3. Open the .ini file with a text editor and enter your username and password in the appropriate lines. Make sure to leave the 'key' field empty.
  4. Run the teams-ka.exe file again, this time it will encrypt your password in the .ini file and launch.

First Run Option 2:
  1. Using your shell console of choice (CMD/PowerShell/ConEmu), ignore the .bat file and instead go to the teams-ka folder and run: 
      * In CMD:  ```python.exe . -u [USERNAME] -p [PASSWORD]```
      * In PowerShell: ```./python.exe . -u [USERNAME] -p [PASSWORD]```
  2. The application will generate the .ini file then encrypt/store your password.

Once completing one of these steps you can continue to run teams-ka without providing your password. If you need to update your username or password in the future, you'll need to either:
  * Delete the teams-ka.ini file and perform the steps in 'First Run Option 1'.
  <br>or
  * Perform the steps in 'First Run Option 2' to overwrite the stored username/password.

<br>

# Mac OS/Linux Release (Coming Soon)
### Running

Pre-Requisites:
  * Mozilla Firefox

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

# Dev Workspace
I'm currently working on a Makefile to assist in setting up a workspace. At the moment you'll need to perform the following
  1. [Install python3](https://www.python.org/downloads/)
  2. Install Mozilla Firefox
      * If on Windows, ensure Firfox is installed in either C:\Program Files\Mozilla Firefox or C:\Program Files (x86)\Mozilla Firefox.
      <br>If Firefox is not installed in one of those locations, you'll want to download the .msi from their site and re-install.
      <br>Alternatively, you may [point geckodriver](https://selenium-python.readthedocs.io/api.html#module-selenium.webdriver.firefox.webdriver) to the binaries.
  3. [Download geckodriver](https://github.com/mozilla/geckodriver/releases) and add it to your system path.
  4. Install all dependencies at the root of the project: ```python3 -m pip install -r requirements.txt```

<br>

# Building
todo

<br>

# Packaging
All packaging is currently done manually.