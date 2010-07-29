# -*- coding: utf-8 -*-
#
# Copyright © 2009 Pierre Raybaut
# Licensed under the terms of the MIT License
# (see spyderlib/__init__.py for details)

"""
Spyder configuration management

Important note regarding shortcuts:
    For compatibility with QWERTZ keyboards, one must avoid using the following
    shortcuts:
        Ctrl + Alt + Q, W, F, G, Y, X, C, V, B, N
"""

import os, sys
import os.path as osp
from datetime import date
from PyQt4.QtGui import QLabel, QIcon, QPixmap, QFont, QFontDatabase

# Local import
from userconfig import UserConfig, get_home_dir

DATA_DEV_PATH = osp.dirname(__file__)
DOC_DEV_PATH = osp.join(DATA_DEV_PATH, 'doc')

# The two following lines are patched when making the debian package:
DATA_PATH = DATA_DEV_PATH # @@@DATA_PATH@@@
DOC_PATH = DOC_DEV_PATH # @@@DOC_PATH@@@

FILTERS = [int, long, float, list, dict, tuple, str, unicode, date]
try:
    from numpy import ndarray
    FILTERS.append(ndarray)
except ImportError:
    pass
try:
    from PIL.Image import Image
    FILTERS.append(Image)
except ImportError:
    pass

# Max number of filter iterations for worskpace display:
# (for workspace saving, itermax == -1, see Workspace.save)
ITERMAX = -1 #XXX: To be adjusted if it takes too much to compute... 2, 3?

EXCLUDED = ['nan', 'inf', 'infty', 'little_endian', 'colorbar_doc', 'typecodes',
            '__builtins__', '__main__', '__doc__']

def type2str(types):
    """Convert types to strings"""
    return [typ.__name__ for typ in types]

def str2type(strings):
    """Convert strings to types"""
    return tuple( [eval(string) for string in strings] )

SANS_SERIF = ['Sans Serif', 'DejaVu Sans', 'Bitstream Vera Sans',
              'Bitstream Charter', 'Lucida Grande', 'Verdana', 'Geneva',
              'Lucid', 'Arial', 'Helvetica', 'Avant Garde', 'sans-serif']
SANS_SERIF.insert(0, unicode(QFont().family()))

MONOSPACE = ['Monospace', 'DejaVu Sans Mono', 'Consolas', 'Courier New',
             'Bitstream Vera Sans Mono', 'Andale Mono', 'Liberation Mono',
             'Monaco', 'Courier', 'monospace', 'Fixed', 'Terminal']
MEDIUM = 10
SMALL = 9

DEFAULTS = [
            ('main',
             {
              'translation': True,
              'window/size': (1260, 740),
              'window/is_maximized': False,
              'window/is_fullscreen': False,
              'window/position': (10, 10),
              'lightwindow/size': (650, 400),
              'lightwindow/position': (30, 30),
              }),
            ('shell_appearance',
             {
              'default_style/foregroundcolor': 0x000000,
              'default_style/backgroundcolor': 0xFFFFFF,
              'default_style/bold': False,
              'default_style/italic': False,
              'default_style/underline': False,
              'error_style/foregroundcolor': 0xFF0000,
              'error_style/backgroundcolor': 0xFFFFFF,
              'error_style/bold': False,
              'error_style/italic': False,
              'error_style/underline': False,
              'traceback_link_style/foregroundcolor': 0x0000FF,
              'traceback_link_style/backgroundcolor': 0xFFFFFF,
              'traceback_link_style/bold': True,
              'traceback_link_style/italic': False,
              'traceback_link_style/underline': True,
              'prompt_style/foregroundcolor': 0x00AA00,
              'prompt_style/backgroundcolor': 0xFFFFFF,
              'prompt_style/bold': True,
              'prompt_style/italic': False,
              'prompt_style/underline': False,
              'calltips/font/family': MONOSPACE,
              'calltips/font/size': SMALL,
              'calltips/font/italic': False,
              'calltips/font/bold': False,
              'calltips/size': 600,
              # This only applys to QPlainTextEdit-based widgets:
              'completion/font/family': MONOSPACE,
              'completion/font/size': SMALL,
              'completion/font/italic': False,
              'completion/font/bold': False,
              'completion/size': (300, 180),
              }),
            ('internal_console',
             {
              'max_line_count': 300,
              'working_dir_history': 30,
              'working_dir_adjusttocontents': False,
              'font/family': MONOSPACE,
              'font/size': MEDIUM,
              'font/italic': False,
              'font/bold': False,
              'wrap': True,
              'calltips': True,
              'codecompletion/auto': False,
              'codecompletion/enter-key': True,
              'codecompletion/case-sensitivity': True,
              'codecompletion/select-single': True,
              'codecompletion/from-document': False,
              'external_editor/path': 'SciTE',
              'external_editor/gotoline': '-goto:',
              }),
            ('console',
             {
              'shortcut': "Ctrl+Shift+C",
              'max_line_count': 300,
              'font/family': MONOSPACE,
              'font/size': MEDIUM,
              'font/italic': False,
              'font/bold': False,
              'wrap': True,
              'single_tab': True,
              'calltips': True,
              'codecompletion/auto': False,
              'codecompletion/enter-key': True,
              'codecompletion/case-sensitivity': True,
              'codecompletion/select-single': True,
              'codecompletion/from-document': False,
              'filters': type2str(FILTERS),
              'itermax': ITERMAX,
              'excluded_names': EXCLUDED,
              'exclude_private': True,
              'exclude_upper': True,
              'exclude_unsupported': True,
              'inplace': False,
              'truncate': True,
              'minmax': True,
              'collvalue': False,
              'show_icontext': False,
              'mpl_patch/enabled': True,
              'umd/enabled': True,
              'umd/verbose': True,
              'umd/namelist': ['guidata', 'guiqwt'],
              }),
            ('editor',
             {
              'shortcut': "Ctrl+Shift+E",
              'printer_header/font/family': SANS_SERIF,
              'printer_header/font/size': MEDIUM,
              'printer_header/font/italic': False,
              'printer_header/font/bold': False,
              'font/family': MONOSPACE,
              'font/size': MEDIUM,
              'font/italic': False,
              'font/bold': False,
              'wrap': False,
              'wrapflag': True,
              'code_analysis': True,
              'class_browser': True,
              'line_numbers': True,
              'toolbox_panel': True,
              'calltips': True,
              'go_to_definition': True,
              'object_inspector': True,
              'codecompletion/auto': False,
              'codecompletion/enter-key': False,
              'check_eol_chars': True,
              'tab_always_indent': True,
              'fullpath_sorting': True,
              'max_recent_files': 20,
              }),
            ('historylog',
             {
              'shortcut': "Ctrl+Shift+H",
              'enable': True,
              'max_entries': 100,
              'font/family': MONOSPACE,
              'font/size': MEDIUM,
              'font/italic': False,
              'font/bold': False,
              'wrap': True,
              }),
            ('inspector',
             {
              'shortcut': "Ctrl+Shift+I",
              'enable': True,
              'max_history_entries': 20,
              'font/family': MONOSPACE,
              'font/size': SMALL,
              'font/italic': False,
              'font/bold': False,
              'wrap': True,
              'automatic_import': True,
              }),
            ('onlinehelp',
             {
              'shortcut': "Ctrl+Shift+D",
              'enable': True,
              'zoom_factor': .8,
              'max_history_entries': 20,
              }),
            ('project_explorer',
             {
              'shortcut': "Ctrl+Shift+P",
              'enable': True,
              }),
            ('arrayeditor',
             {
              'font/family': MONOSPACE,
              'font/size': SMALL,
              'font/italic': False,
              'font/bold': False,
              }),
            ('texteditor',
             {
              'font/family': MONOSPACE,
              'font/size': MEDIUM,
              'font/italic': False,
              'font/bold': False,
              }),
            ('dicteditor',
             {
              'font/family': MONOSPACE,
              'font/size': SMALL,
              'font/italic': False,
              'font/bold': False,
              }),
            ('explorer',
             {
              'enable': True,
              'wrap': True,
              'name_filters': ['*.py', '*.pyw', '*.pth',
                               '*.npy', '*.mat', '*.spydata'],
              'valid_filetypes': ['', '.py', '.pyw', '.spydata', '.npy', '.pth',
                                  '.txt', '.csv', '.mat', '.h5'],
              'show_hidden': True,
              'show_all': False,
              'show_toolbar': True,
              'show_icontext': True,
              }),
            ('find_in_files',
             {
              'enable': True,
              'supported_encodings': ["utf-8", "iso-8859-1", "cp1252"],
              'include': [r'\.pyw?$|\.txt$|\.c$|\.cpp$|\.h$|\.hpp$|\.f$|\.ini$', '.'],
              'include_regexp': True,
              'exclude': [r'\.pyc$|\.pyo$|\.orig$|\.hg|\.svn'],
              'exclude_regexp': True,
              'search_text_regexp': True,
              'search_text': [''],
              'search_text_samples': [r'# ?TODO|# ?FIXME|# ?XXX'],
              'in_python_path': False,
              'more_options': True,
              }),
            ]

DEV = not __file__.startswith(sys.prefix)
DEV = False
from spyderlib import __version__
_subfolder = '.spyder%s' % __version__.split('.')[0]
CONF = UserConfig('spyder', defaults=DEFAULTS, load=(not DEV),
                  version='1.0.6', subfolder=_subfolder)
# Removing old .spyder.ini location:
old_location = osp.join(get_home_dir(), '.spyder.ini')
if osp.isfile(old_location):
    os.remove(old_location)

def get_conf_path(filename=None):
    """Return absolute path for configuration file with specified filename"""
    conf_dir = osp.join(get_home_dir(), _subfolder)
    if not osp.isdir(conf_dir):
        os.mkdir(conf_dir)
    if filename is None:
        return conf_dir
    else:
        return osp.join(conf_dir, filename)

IMG_PATH = []
def add_image_path(path):
    if not osp.isdir(path):
        return
    global IMG_PATH
    IMG_PATH.append(path)
    for _root, dirs, _files in os.walk(path):
        for dir in dirs:
            IMG_PATH.append(osp.join(path, dir))

add_image_path(osp.join(DATA_PATH, 'images'))

def get_image_path( name, default="not_found.png" ):
    """Return image absolute path"""
    for img_path in IMG_PATH:
        full_path = osp.join(img_path, name)
        if osp.isfile(full_path):
            return osp.abspath(full_path)
    if default is not None:
        return osp.abspath(osp.join(img_path, default))

def get_icon( name, default=None ):
    """Return image inside a QIcon object"""
    if default is None:
        return QIcon(get_image_path(name))
    elif isinstance(default, QIcon):
        icon_path = get_image_path(name, default=None)
        return default if icon_path is None else QIcon(icon_path)
    else:
        return QIcon(get_image_path(name, default))

def get_image_label( name, default="not_found.png" ):
    """Return image inside a QLabel object"""
    label = QLabel()
    label.setPixmap(QPixmap(get_image_path(name, default)))
    return label

def font_is_installed(font):
    """Check if font is installed"""
    return [fam for fam in QFontDatabase().families() if unicode(fam)==font]
    
def get_family(families):
    """Return the first installed font family in family list"""
    if not isinstance(families, list):
        families = [ families ]
    for family in families:
        if font_is_installed(family):
            return family
    else:
        print "Warning: None of the following fonts is installed: %r" % families
        return QFont().family()
    
FONT_CACHE = {}
def get_font(section, option=None):
    """Get console font properties depending on OS and user options"""
    font = FONT_CACHE.get((section, option))
    if font is None:
        if option is None:
            option = 'font'
        else:
            option += '/font'
        families = CONF.get(section, option+"/family", None)
        if families is None:
            return QFont()
        family = get_family(families)
        weight = QFont.Normal
        italic = CONF.get(section, option+'/italic', False)
        if CONF.get(section, option+'/bold', False):
            weight = QFont.Bold
        size = CONF.get(section, option+'/size', 9)
        font = QFont(family, size, weight)
        font.setItalic(italic)
        FONT_CACHE[(section, option)] = font
    return font

def set_font(font, section, option=None):
    """Set font"""
    if option is None:
        option = 'font'
    else:
        option += '/font'
    CONF.set(section, option+'/family', unicode(font.family()))
    CONF.set(section, option+'/size', float(font.pointSize()))
    CONF.set(section, option+'/italic', int(font.italic()))
    CONF.set(section, option+'/bold', int(font.bold()))
    FONT_CACHE[(section, option)] = font


PLUGIN_PATH = None
from spyderlib.utils import programs
if programs.is_module_installed("spyderplugins"):
    import spyderplugins
    PLUGIN_PATH = spyderplugins.__path__[0]
    add_image_path(osp.join(PLUGIN_PATH, 'images'))

def get_spyderplugins(prefix, extension):
    """Scan spyderplugins module and
    return the list of files matching *prefix* and *extension*"""
    plist = []
    if PLUGIN_PATH is not None:
        for name in os.listdir(PLUGIN_PATH):
            modname, ext = osp.splitext(name)
            if prefix is not None and not name.startswith(prefix):
                continue
            if extension is not None and ext != extension:
                continue
            plist.append(modname)
    return plist
