import logging, os, sys, time
from teams_ka.models import User
from threading import Thread
from teams_ka import helpers
from teams_ka.config import Config
from teams_ka.connection import Connection
from teams_ka.display import Display


if __name__ == '__main__':

  # config
  config = Config()
  if not config.allReqsMet:
    print('\nRun with -h for help.')
    sys.exit()


  # print title
  print(helpers.centeredTitle(os.get_terminal_size().columns))


  # app logging
  logging.Formatter.converter = time.localtime if helpers.amDebugging else time.gmtime
  logging.basicConfig(filename='teams-ka.log', level=logging.DEBUG if config.verbose else logging.INFO, format='%(asctime)s %(name)s %(levelname)s: %(message)s')
  logger = logging.getLogger(__name__)
  logger.info('MS Teams - Always Available!')


  # library logging
  logging.getLogger("requests").setLevel(logging.ERROR)
  logging.getLogger("urllib3").setLevel(logging.ERROR)


  # connection
  connection = Connection(config)
  connection_process = Thread(name='teams', target=connection.start)


  # display
  display = Display(connection)
  display_process = Thread(name='display', target=display.start)


  # start
  connection_process.start()
  display_process.start()


  # exit
  input()
  connection.exit()
  display.exit()

  connection_process.join()
  display_process.join()

  sys.exit(0)