[0.9.0]
    [ ] template support
        [ ] create templates folder
            [ ] sched.json
            [ ] holidays.json
            [ ] config.json
        [ ] for each of the templates, where relevant if not found, copy out of templates folder
            [ ] sched
            [ ] holiday
            [ ] config
        [ ] .gitignore: ignore presense of template files in root dir
    [ ] add env variables as option for config.js
        [note] default -> json -> env vars -> argparse
    [ ] add config options
        [ ] drivers path
        [ ] browser path
    [ ] add edge support
        [ ] config option for browser version
            [ ] chrome (default)
                [ ] add config option to use chrome_auto_installer (default: True)
            [ ] edge
        [ ] add browser.py logic
    [ ] retain reason for failure, only count against retries on concurrent failures
    [ ] discord
        [ ] create separate discord webhook for mfa vs logging
        [ ] create a discord.py that functions the same as lumberjack
        [ ] add option to pass loggers[] to lumberjack to be called by _log_
        [ ] get rid of notify_user since new lumberjack will call discord
        [ ] in navigator, create _send_mfa_info_ to send mfa code to user with provided option
    [ ] redo logic between nav and Teams to initialize an instance of 'Today' which will contain a 'Day'
        property based on the actual day. this way we can generate the entire day's schedule up front
    [ ] create first release [v0.9.0]
        [note] reset history
[1.0.0]
    [ ] gen app
        [ ] unix
        [ ] osx
        [ ] windows
    [ ] Makefile
    [ ] Makefile.ps1
    [ ] Dockerfile
        [ ] unix
        [ ] windows
    [ ] create release [v1.0.0]
