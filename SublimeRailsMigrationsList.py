import sublime
import sublime_plugin
import os
import re

class RailsMigrationsListCommand(sublime_plugin.WindowCommand):
  migrations = []
  migrations_dir = ''
  def run(self):
    try:
      cur_path = self.window.active_view().file_name()
    except AttributeError:
      if self.window.folders():
        cur_path = self.window.folders()[0]

    if cur_path:
      if os.path.isfile(cur_path):
        cur_path = os.path.dirname(cur_path)
      root = self.find_ror_root(cur_path)
    else:
      raise NothingOpen("Please open a file or folder to search migrations")

    if root:
      self.ror_root = root
      self.migrations_dir = os.path.join(root, 'db', 'migrate')
      migrations = os.listdir(self.migrations_dir)

      pattern = re.compile('^\d+_\w+.rb$')
      self.fileList = sorted([m for m in migrations if pattern.match(m)], reverse=True)

      self.window.show_quick_panel(self.fileList, self.get_file)


  def get_file(self, index):
    if index >= 0:
      url = os.path.join(self.migrations_dir, self.fileList[index])
      self.window.open_file(url)

  # Recursively searches each up a directory structure for the
  # expected items that are common to a Rails application.
  def find_ror_root(self, path):
    expected_items = ['Gemfile', 'app', 'config', 'db']
    files = os.listdir(path)

    # The recursive search has gone too far and we've reached the system's
    # root directory! At this stage it's safe to assume that we won't come
    # across a familiar directory structure for a Rails app.
    if path == '/':
      raise NotRailsApp("Please, open a rails application")

    if len([x for x in expected_items if x in files]) == len(expected_items):
      return path
    else:
      return self.find_ror_root(self.parent_path(path))

  # Returns the parent path of the path passed to it.
  def parent_path(self, path):
    return os.path.abspath(os.path.join(path, '..'))

class Error(Exception):
  def __init__(self, msg):
    self.msg = msg
    sublime.error_message(self.msg)

class NotRailsApp(Error):
  pass
class NothingOpen(Error):
  pass