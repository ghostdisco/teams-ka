import datetime, os, time
from datetime import datetime, timedelta
from teams_ka.helpers import centeredTitle, clear
from teams_ka.connection import Status

class Display:
  def __init__(self, connection) -> None:

    self.connection = connection
    self.username = connection.user.username
    self.running = False
    self.startTime = None

  
  def start(self):
    self.running = True
    self.startTime = datetime.now()
    self._run_()

  
  def _getRunningTime_(self) -> timedelta:
    return datetime.now() - self.startTime

  
  def _getRunningTimeFormatted_(self):
    delta = str(self._getRunningTime_())
    return f"{':'.join(delta.split(':')[:2])}:{str(int(delta.split(':')[2].split('.')[0]) + 1).rjust(2, '0')}".rjust(8, '0')


  def _print_(self):
    running = self._getRunningTimeFormatted_()
    consoleWidth = os.get_terminal_size().columns
    action = self.connection.action

    # build exit 'button'
    button = f'| press enter to exit ({running}) |'
    buttonWidth = button.__len__()

    # build display
    display = centeredTitle(consoleWidth)
    display +=  '\n'
    display += f'{self.username} - {self.connection.status.value} - {action}'.center(consoleWidth)
    display +=  '\n\n'
    display += f' {(buttonWidth - 2) * "_"} '.center(consoleWidth)
    display += button.center(consoleWidth)
    display += f' {(buttonWidth - 2) * "‾"} '.center(consoleWidth)
    display +=  '\n'

    # print
    clear()
    print(display)


  def _run_(self):
    # main loop
    while (self.running and self.connection.status != Status.TERMINATED):

      # get current status
      status = self.connection.status.value
      action = self.connection.action

      # print display
      self._print_()

      # watch for status or action change
      while (status == self.connection.status.value and action == self.connection.action):
        time.sleep(1)
        self._print_()


    # handle exits
    self._print_()
    self.exit()

  def exit(self):
    self.running = False