# -*- coding: utf-8 -*-
#
# Copyright © 2009 Pierre Raybaut
# Licensed under the terms of the MIT License
# (see spyderlib/__init__.py for details)

"""External Console plugin"""

# pylint: disable-msg=C0103
# pylint: disable-msg=R0903
# pylint: disable-msg=R0911
# pylint: disable-msg=R0201

from PyQt4.QtGui import (QVBoxLayout, QFileDialog, QFontDialog, QMessageBox,
                         QInputDialog, QLineEdit)
from PyQt4.QtCore import SIGNAL, QString, Qt

import sys, os
import os.path as osp

# For debugging purpose:
STDOUT = sys.stdout

# Local imports
from spyderlib.config import CONF, get_font, get_icon, set_font
from spyderlib.utils.qthelpers import create_action, mimedata2url
from spyderlib.utils.programs import is_module_installed
from spyderlib.widgets.tabs import Tabs
from spyderlib.widgets.externalshell.pythonshell import ExternalPythonShell
from spyderlib.widgets.externalshell.systemshell import ExternalSystemShell
from spyderlib.widgets.shellhelpers import get_error_match
from spyderlib.widgets.findreplace import FindReplace
from spyderlib.plugins import SpyderPluginWidget


class ExternalConsole(SpyderPluginWidget):
    """
    Console widget
    """
    ID = 'external_shell'
    def __init__(self, parent, commands=None):
        self.commands = commands
        self.tabwidget = None
        self.menu_actions = None
        self.inspector = None
        self.historylog = None
        
        self.ipython_count = 0
        self.python_count = 0
        self.terminal_count = 0
        
        if CONF.get(self.ID, 'ipython_options', None) is None:
            default_options = ["-q4thread"]
            if is_module_installed('matplotlib'):
                default_options.append("-pylab")
            default_options.append("-colors LightBG")
            CONF.set(self.ID, 'ipython_options', " ".join(default_options))
        
        self.shells = []
        self.filenames = []
        self.icons = []
        
        SpyderPluginWidget.__init__(self, parent)
        
        layout = QVBoxLayout()
        self.tabwidget = Tabs(self, self.menu_actions)
        self.connect(self.tabwidget, SIGNAL('currentChanged(int)'),
                     self.refresh_plugin)
        self.connect(self.tabwidget, SIGNAL('move_data(int,int)'),
                     self.move_tab)
                     
        self.tabwidget.set_close_function(self.close_console)

        layout.addWidget(self.tabwidget)
        
        # Find/replace widget
        self.find_widget = FindReplace(self)
        self.find_widget.hide()
        layout.addWidget(self.find_widget)
        
        self.setLayout(layout)
            
        # Accepting drops
        self.setAcceptDrops(True)
        
    def move_tab(self, index_from, index_to):
        """
        Move tab (tabs themselves have already been moved by the tabwidget)
        """
        filename = self.filenames.pop(index_from)
        shell = self.shells.pop(index_from)
        icon = self.icons.pop(index_from)
        
        self.filenames.insert(index_to, filename)
        self.shells.insert(index_to, shell)
        self.icons.insert(index_to, icon)

    def close_console(self, index=None):
        if not self.tabwidget.count():
            return
        if index is None:
            index = self.tabwidget.currentIndex()
        self.tabwidget.widget(index).close()
        self.tabwidget.removeTab(index)
        self.filenames.pop(index)
        self.shells.pop(index)
        self.icons.pop(index)
        
    def set_historylog(self, historylog):
        """Bind historylog instance to this console"""
        self.historylog = historylog
        
    def set_inspector(self, inspector):
        """Bind inspector instance to this console"""
        self.inspector = inspector
        
    def __find_python_shell(self):
        current_index = self.tabwidget.currentIndex()
        if current_index == -1:
            return
        from spyderlib.widgets.externalshell import pythonshell
        for index in [current_index]+range(self.tabwidget.count()):
            shellwidget = self.tabwidget.widget(index)
            if isinstance(shellwidget, pythonshell.ExternalPythonShell):
                self.tabwidget.setCurrentIndex(index)
                return shellwidget
        
    def run_script_in_current_shell(self, filename):
        """Run script in current shell, if any"""
        shellwidget = self.__find_python_shell()
        if shellwidget is not None:
            if shellwidget.ipython:
                line = "run '%s'" % unicode(filename)
            else:
                line = "execfile('%s')" % unicode(filename)
            shellwidget.shell.execute_lines(line)
            shellwidget.shell.setFocus()
        
    def execute_python_code(self, lines):
        """Execute Python code in an already opened Python interpreter"""
        shellwidget = self.__find_python_shell()
        if shellwidget is not None:
            shellwidget.shell.execute_lines(unicode(lines))
            shellwidget.shell.setFocus()
        
    def start(self, fname, wdir=None, ask_for_arguments=False,
              interact=False, debug=False, python=True,
              ipython=False, arguments=None, current=False):
        """Start new console"""
        # Note: fname is None <=> Python interpreter
        fname = unicode(fname) if isinstance(fname, QString) else fname
        wdir = unicode(wdir) if isinstance(wdir, QString) else wdir

        if fname is not None and fname in self.filenames:
            index = self.filenames.index(fname)
            if CONF.get(self.ID, 'single_tab'):
                old_shell = self.shells[index]
                if old_shell.is_running():
                    answer = QMessageBox.question(self, self.get_plugin_title(),
                        self.tr("%1 is already running in a separate process.\n"
                                "Do you want to kill the process before starting "
                                "a new one?").arg(osp.basename(fname)),
                        QMessageBox.Yes | QMessageBox.Cancel)
                    if answer == QMessageBox.Yes:
                        old_shell.process.kill()
                        old_shell.process.waitForFinished()
                    else:
                        return
                self.close_console(index)
        else:
            index = 0

        # Creating a new external shell
        pythonpath = self.main.get_spyder_pythonpath()
        if python:
            shell_widget = ExternalPythonShell(self, fname, wdir, self.commands,
                                               interact, debug, path=pythonpath,
                                               ipython=ipython,
                                               arguments=arguments)
        else:
            shell_widget = ExternalSystemShell(self, wdir, path=pythonpath)
        
        # Code completion / calltips
        case_sensitive = CONF.get(self.ID, 'codecompletion/case-sensitivity')
        show_single = CONF.get(self.ID, 'codecompletion/select-single')
        from_document = CONF.get(self.ID, 'codecompletion/from-document')
        shell_widget.shell.setup_code_completion(case_sensitive, show_single,
                                                 from_document)
        
        shell_widget.shell.setMaximumBlockCount( CONF.get(self.ID,
                                                          'max_line_count') )
        shell_widget.shell.set_font( get_font(self.ID) )
        shell_widget.shell.toggle_wrap_mode( CONF.get(self.ID, 'wrap') )
        shell_widget.shell.set_calltips( CONF.get(self.ID, 'calltips') )
        shell_widget.shell.set_codecompletion_auto( CONF.get(self.ID,
                                                 'codecompletion/auto') )
        shell_widget.shell.set_codecompletion_enter(CONF.get(self.ID,
                                                 'codecompletion/enter-key'))
        if python and self.inspector is not None:
            shell_widget.shell.set_inspector(self.inspector)
        if self.historylog is not None:
            self.historylog.add_history(shell_widget.shell.history_filename)
            self.connect(shell_widget.shell,
                         SIGNAL('append_to_history(QString,QString)'),
                         self.historylog.append_to_history)
        self.connect(shell_widget.shell, SIGNAL("go_to_error(QString)"),
                     self.go_to_error)
        self.connect(shell_widget.shell, SIGNAL("focus_changed()"),
                     lambda: self.emit(SIGNAL("focus_changed()")))
        if python:
            if fname is None:
                if ipython:
                    self.ipython_count += 1
                    tab_name = "IPython %d" % self.ipython_count
                    tab_icon = get_icon('ipython.png')
                else:
                    self.python_count += 1
                    tab_name = "Python %d" % self.python_count
                    tab_icon = get_icon('python.png')
            else:
                tab_name = osp.basename(fname)
                tab_icon = get_icon('run.png')
        else:
            fname = id(shell_widget)
            if os.name == 'nt':
                tab_name = self.tr("Command Window")
            else:
                tab_name = self.tr("Terminal")
            self.terminal_count += 1
            tab_name += (" %d" % self.terminal_count)
            tab_icon = get_icon('cmdprompt.png')
        self.shells.insert(index, shell_widget)
        self.filenames.insert(index, fname)
        self.icons.insert(index, tab_icon)
        if index is None:
            index = self.tabwidget.addTab(shell_widget, tab_name)
        else:
            self.tabwidget.insertTab(index, shell_widget, tab_name)
        
        self.connect(shell_widget, SIGNAL("started()"),
                     lambda sid=id(shell_widget): self.process_started(sid))
        self.connect(shell_widget, SIGNAL("finished()"),
                     lambda sid=id(shell_widget): self.process_finished(sid))
        self.find_widget.set_editor(shell_widget.shell)
        self.tabwidget.setTabToolTip(index, fname if wdir is None else wdir)
        self.tabwidget.setCurrentIndex(index)
        if self.dockwidget and not self.ismaximized:
            self.dockwidget.setVisible(True)
            self.dockwidget.raise_()
        
        self.toggle_icontext(CONF.get(self.ID, 'show_icontext'))
        
        # Start process and give focus to console
        shell_widget.start(ask_for_arguments)
        shell_widget.shell.setFocus()
        
    #------ Private API --------------------------------------------------------
    def process_started(self, shell_id):
        for index, shell in enumerate(self.shells):
            if id(shell) == shell_id:
                self.tabwidget.setTabIcon(index, self.icons[index])
                if self.inspector is not None:
                    self.inspector.set_shell(shell.shell)
        
    def process_finished(self, shell_id):
        for index, shell in enumerate(self.shells):
            if id(shell) == shell_id:
                self.tabwidget.setTabIcon(index, get_icon('terminated.png'))
                if self.inspector is not None:
                    if self.inspector.get_shell() is shell.shell:
                        # Switch back to interactive shell:
                        self.inspector.set_shell(self.main.console.shell)
        
    #------ SpyderPluginWidget API ---------------------------------------------    
    def get_plugin_title(self):
        """Return widget title"""
        return self.tr('External console')
    
    def get_focus_widget(self):
        """
        Return the widget to give focus to when
        this plugin's dockwidget is raised on top-level
        """
        return self.tabwidget.currentWidget()
        
    def get_plugin_actions(self):
        """Setup actions"""
        interpreter_action = create_action(self,
                            self.tr("Open &interpreter"), None,
                            'python.png', self.tr("Open a Python interpreter"),
                            triggered=self.open_interpreter)
        if os.name == 'nt':
            text = self.tr("Open &command prompt")
            tip = self.tr("Open a Windows command prompt")
        else:
            text = self.tr("Open &terminal")
            tip = self.tr("Open a terminal window inside Spyder")
        console_action = create_action(self, text, None, 'cmdprompt.png', tip,
                            triggered=self.open_terminal)
        run_action = create_action(self,
                            self.tr("&Run..."), None,
                            'run_small.png', self.tr("Run a Python script"),
                            triggered=self.run_script)
        buffer_action = create_action(self,
                            self.tr("Buffer..."), None,
                            tip=self.tr("Set maximum line count"),
                            triggered=self.change_max_line_count)
        font_action = create_action(self,
                            self.tr("&Font..."), None,
                            'font.png', self.tr("Set shell font style"),
                            triggered=self.change_font)
        wrap_action = create_action(self,
                            self.tr("Wrap lines"),
                            toggled=self.toggle_wrap_mode)
        wrap_action.setChecked( CONF.get(self.ID, 'wrap') )
        calltips_action = create_action(self, self.tr("Balloon tips"),
                            toggled=self.toggle_calltips)
        calltips_action.setChecked( CONF.get(self.ID, 'calltips') )
        codecompletion_action = create_action(self,
                                          self.tr("Automatic code completion"),
                                          toggled=self.toggle_codecompletion)
        codecompletion_action.setChecked( CONF.get(self.ID,
                                                   'codecompletion/auto') )
        codecompenter_action = create_action(self,
                                    self.tr("Enter key selects completion"),
                                    toggled=self.toggle_codecompletion_enter)
        codecompenter_action.setChecked( CONF.get(self.ID,
                                                  'codecompletion/enter-key') )
        singletab_action = create_action(self,
                            self.tr("One tab per script"),
                            toggled=self.toggle_singletab)
        singletab_action.setChecked( CONF.get(self.ID, 'single_tab') )
        icontext_action = create_action(self, self.tr("Show icons and text"),
                                        toggled=self.toggle_icontext)
        icontext_action.setChecked( CONF.get(self.ID, 'show_icontext') )
        
        self.menu_actions = [interpreter_action, console_action, run_action,
                             None, buffer_action, font_action, wrap_action,
                             calltips_action, codecompletion_action,
                             codecompenter_action, singletab_action,
                             icontext_action]
        
        ipython_action = create_action(self,
                            self.tr("Open IPython interpreter"), None,
                            'ipython.png',
                            self.tr("Open an IPython interpreter"),
                            triggered=self.open_ipython)
        ipython_options_action = create_action(self,
                            self.tr("IPython interpreter options..."), None,
                            tip=self.tr("Set IPython interpreter "
                                        "command line arguments"),
                            triggered=self.set_ipython_options)
        if is_module_installed("IPython"):
            self.menu_actions.insert(5, ipython_options_action)
            self.menu_actions.insert(1, ipython_action)
        
        return (self.menu_actions, None)
    
    def open_interpreter_at_startup(self):
        """Open an interpreter at startup, IPython if module is available"""
        if is_module_installed("IPython"):
            self.open_ipython()
        else:
            self.open_interpreter()
        
    def closing_plugin(self, cancelable=False):
        """Perform actions before parent main window is closed"""
        return True
    
    def refresh_plugin(self):
        """Refresh tabwidget"""
        if self.tabwidget.count():
            editor = self.tabwidget.currentWidget().shell
            editor.setFocus()
        else:
            editor = None
        self.find_widget.set_editor(editor)
    
    #------ Public API ---------------------------------------------------------
    def open_interpreter(self):
        """Open interpreter"""
        self.start(fname=None, wdir=os.getcwdu(), ask_for_arguments=False,
                   interact=True, debug=False, python=True)
        
    def open_ipython(self):
        """Open IPython"""
        self.start(fname=None, wdir=os.getcwdu(), ask_for_arguments=False,
                   interact=True, debug=False, python=True, ipython=True,
                   arguments=CONF.get(self.ID, 'ipython_options', ""))
        
    def open_terminal(self):
        """Open terminal"""
        self.start(fname=None, wdir=os.getcwdu(), ask_for_arguments=False,
                   interact=True, debug=False, python=False)
        
    def run_script(self):
        """Run a Python script"""
        self.emit(SIGNAL('redirect_stdio(bool)'), False)
        filename = QFileDialog.getOpenFileName(self,
                      self.tr("Run Python script"), os.getcwdu(),
                      self.tr("Python scripts")+" (*.py ; *.pyw)")
        self.emit(SIGNAL('redirect_stdio(bool)'), True)
        if filename:
            self.start(fname=unicode(filename), wdir=None,
                       ask_for_arguments=False, interact=False, debug=False)
        
    def change_font(self):
        """Change console font"""
        font, valid = QFontDialog.getFont(get_font(self.ID),
                       self, self.tr("Select a new font"))
        if valid:
            for index in range(self.tabwidget.count()):
                self.tabwidget.widget(index).shell.set_font(font)
            set_font(font, self.ID)
        
    def change_max_line_count(self):
        "Change maximum line count"""
        mlc, valid = QInputDialog.getInteger(self, self.tr('Buffer'),
                                           self.tr('Maximum line count'),
                                           CONF.get(self.ID, 'max_line_count'),
                                           10, 1000000)
        if valid:
            for index in range(self.tabwidget.count()):
                self.tabwidget.widget(index).shell.setMaximumBlockCount(mlc)
            CONF.set(self.ID, 'max_line_count', mlc)
            
    def set_ipython_options(self):
        """Set IPython interpreter arguments"""
        arguments, valid = QInputDialog.getText(self,
                      self.tr('IPython'),
                      self.tr('IPython command line options:\n'
                              '(Qt4 support: -q4thread)\n'
                              '(Qt4 and matplotlib support: -q4thread -pylab)'),
                      QLineEdit.Normal, CONF.get(self.ID, 'ipython_options'))
        if valid:
            CONF.set(self.ID, 'ipython_options', unicode(arguments))
            
    def toggle_wrap_mode(self, checked):
        """Toggle wrap mode"""
        if self.tabwidget is None:
            return
        for shell in self.shells:
            shell.shell.toggle_wrap_mode(checked)
        CONF.set(self.ID, 'wrap', checked)
            
    def toggle_calltips(self, checked):
        """Toggle calltips"""
        if self.tabwidget is None:
            return
        for shell in self.shells:
            shell.shell.set_calltips(checked)
        CONF.set(self.ID, 'calltips', checked)
            
    def toggle_codecompletion(self, checked):
        """Toggle automatic code completion"""
        if self.tabwidget is None:
            return
        for shell in self.shells:
            shell.shell.set_codecompletion_auto(checked)
        CONF.set(self.ID, 'codecompletion/auto', checked)
            
    def toggle_codecompletion_enter(self, checked):
        """Toggle Enter key for code completion"""
        if self.tabwidget is None:
            return
        for shell in self.shells:
            shell.shell.set_codecompletion_enter(checked)
        CONF.set(self.ID, 'codecompletion/enter-key', checked)
        
    def toggle_singletab(self, checked):
        """Toggle single tab mode"""
        CONF.set(self.ID, 'single_tab', checked)

    def toggle_icontext(self, checked):
        """Toggle icon text"""
        CONF.set(self.ID, 'show_icontext', checked)
        if self.tabwidget is None:
            return
        for index in range(self.tabwidget.count()):
            for widget in self.tabwidget.widget(index).get_toolbar_buttons():
                if checked:
                    widget.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
                else:
                    widget.setToolButtonStyle(Qt.ToolButtonIconOnly)
                
    def go_to_error(self, text):
        """Go to error if relevant"""
        match = get_error_match(unicode(text))
        if match:
            fname, lnb = match.groups()
            self.emit(SIGNAL("edit_goto(QString,int,QString)"),
                      osp.abspath(fname), int(lnb), '')
            
    #----Drag and drop
    def __is_python_script(self, qstr):
        """Is it a valid Python script?"""
        fname = unicode(qstr)
        return osp.isfile(fname) and \
               ( fname.endswith('.py') or fname.endswith('.pyw') )
        
    def dragEnterEvent(self, event):
        """Reimplement Qt method
        Inform Qt about the types of data that the widget accepts"""
        source = event.mimeData()
        if source.hasUrls():
            if mimedata2url(source):
                event.acceptProposedAction()
            else:
                event.ignore()
        elif source.hasText() and self.__is_python_script(source.text()):
            event.acceptProposedAction()            
            
    def dropEvent(self, event):
        """Reimplement Qt method
        Unpack dropped data and handle it"""
        source = event.mimeData()
        if source.hasText():
            self.start(source.text())
        elif source.hasUrls():
            files = mimedata2url(source)
            for fname in files:
                if self.__is_python_script(fname):
                    self.start(fname)
        event.acceptProposedAction()
