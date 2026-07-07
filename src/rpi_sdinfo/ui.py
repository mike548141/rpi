#!/usr/bin/env python3
#
# Author:       Mike Clements, Competitive Edge
# Version:      0.1-20260705
# File:         src/rpi_sdinfo/ui.py
# License:      Apache-2.0
# Language:     Python 3.6 or later
# Source:       https://github.com/mike548141/rpi
#
# Description:
#   A tiny, dependency-free terminal styling toolkit shared by the rpi_sdinfo cli and bench modules. Pure Python
#   standard library, so it runs anywhere CPython does (Raspberry Pi Linux, macOS, Windows).
#
#   Everything degrades gracefully: colour and Unicode box-drawing are used only when the output is an
#   interactive terminal that supports them, and are switched off automatically when the output is piped or
#   redirected (so machine-readable output stays clean), when NO_COLOR is set, or on a "dumb" terminal. On
#   Windows 10+ it enables the console's ANSI (virtual terminal) support on the fly.

import os
import sys
import threading

#======================================
# Capability detection
#--------------------------------------

# Cache the one-time Windows ANSI enable so we only poke the console API once
_windows_ansi_ready = None

def _enable_windows_ansi(stream):
  # Windows 10 build 1511+ consoles understand ANSI escapes but need the flag turned on per handle. Returns
  # True if VT processing is (now) enabled, False if we could not enable it (older console, redirected, etc.)
  global _windows_ansi_ready
  if _windows_ansi_ready is not None:
    return _windows_ansi_ready
  _windows_ansi_ready = False
  try:
    import ctypes
    from ctypes import wintypes
    kernel32 = ctypes.windll.kernel32
    # -11 = STD_OUTPUT_HANDLE, -12 = STD_ERROR_HANDLE
    handle_id = -12 if stream is sys.stderr else -11
    handle = kernel32.GetStdHandle(handle_id)
    mode = wintypes.DWORD()
    if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
      ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
      if kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING):
        _windows_ansi_ready = True
  except Exception:
    _windows_ansi_ready = False
  return _windows_ansi_ready

def supports_color(stream):
  # Decide whether to emit ANSI colour. Honour the de-facto standards: NO_COLOR disables, CLICOLOR_FORCE forces,
  # and otherwise colour is only used for an interactive TTY (never when piped/redirected, so `| jq` stays clean)
  if os.environ.get('NO_COLOR') is not None:
    return False
  if os.environ.get('CLICOLOR_FORCE', '0') not in ('0', ''):
    return True
  if not hasattr(stream, 'isatty') or not stream.isatty():
    return False
  if os.environ.get('TERM') == 'dumb':
    return False
  if sys.platform == 'win32':
    return _enable_windows_ansi(stream)
  return True

def supports_unicode(stream):
  # Box-drawing / block glyphs need a UTF-capable encoding. Fall back to ASCII on legacy code pages
  encoding = getattr(stream, 'encoding', None) or ''
  return 'utf' in encoding.lower()

def term_width(default=80):
  try:
    return os.get_terminal_size().columns
  except (OSError, ValueError):
    return default

#======================================
# The console
#--------------------------------------

# ANSI SGR codes we use, by friendly name
_SGR = {
  'reset': 0, 'bold': 1, 'dim': 2, 'italic': 3, 'reverse': 7,
  'red': 31, 'green': 32, 'yellow': 33, 'blue': 34, 'magenta': 35, 'cyan': 36, 'grey': 90,
}

# Glyphs, with an ASCII fallback for terminals that cannot render the nicer Unicode set
_GLYPHS = {
  True:  {'heavy': '━', 'light': '─', 'dot': '·', 'bar_full': '█',
          'bar_empty': '░', 'tick': '✓', 'cross': '✗', 'pipe': '┃',
          'tl': '╭', 'tr': '╮', 'bl': '╰', 'br': '╯', 'h': '─', 'v': '│'},
  False: {'heavy': '=', 'light': '-', 'dot': '-', 'bar_full': '#',
          'bar_empty': '.', 'tick': 'OK', 'cross': 'X', 'pipe': '|',
          'tl': '+', 'tr': '+', 'bl': '+', 'br': '+', 'h': '-', 'v': '|'},
}

class Console:
  # A thin wrapper around a text stream that knows whether it may use colour and Unicode, and renders the small
  # set of components rpi-sdinfo needs (banner, section, key/value rows, badges, ratio bars, boxes).
  def __init__(self, stream=None, color=None, unicode=None, width=None):
    self.stream = stream if stream is not None else sys.stdout
    self.color = supports_color(self.stream) if color is None else color
    self.unicode = supports_unicode(self.stream) if unicode is None else unicode
    self.width = min(width or term_width(), 74)
    self.g = _GLYPHS[self.unicode]

  #-- low level ------------------------------------------------------------
  def style(self, text, *names):
    # Wrap text in the named SGR codes, or return it untouched when colour is off
    if not self.color or not names:
      return text
    codes = ';'.join(str(_SGR[n]) for n in names)
    return '\x1b[' + codes + 'm' + text + '\x1b[0m'

  def out(self, text=''):
    print(text, file=self.stream)

  def flush(self):
    try:
      self.stream.flush()
    except (OSError, ValueError):
      pass

  #-- components -----------------------------------------------------------
  def banner(self, title, subtitle=''):
    rule = self.g['heavy'] * self.width
    self.out(self.style(rule, 'grey'))
    line = '  ' + self.style(title, 'bold', 'cyan')
    if subtitle:
      line += '  ' + self.style(self.g['dot'] + '  ' + subtitle, 'grey')
    self.out(line)
    self.out(self.style(rule, 'grey'))

  def section(self, title, note=''):
    self.out('')
    heading = self.style(title.upper(), 'bold')
    if note:
      heading += '  ' + self.style(self.g['dot'] + ' ' + note, 'grey')
    self.out(heading)

  def kv(self, label, value, width=20, label_style='grey', value_style=None, note=''):
    # One aligned "label   value" row. label_width keeps the value column tidy
    left = self.style((label + ':').ljust(width), label_style)
    right = self.style(str(value), value_style) if value_style else str(value)
    if note:
      right += '  ' + self.style(self.g['dot'] + ' ' + note, 'grey')
    self.out('  ' + left + right)

  def line(self, text='', indent=2):
    self.out(' ' * indent + text)

  def rule(self, light=True, indent=2):
    glyph = self.g['light'] if light else self.g['heavy']
    self.out(' ' * indent + self.style(glyph * (self.width - indent), 'grey'))

  def badge(self, text, kind='info'):
    # A small coloured PASS / FAIL / WARN chip. Uses reverse video so it reads as a solid block on colour terminals
    palette = {'pass': ('green', self.g['tick']), 'fail': ('red', self.g['cross']),
               'warn': ('yellow', '!'), 'info': ('cyan', self.g['dot'])}
    colour, mark = palette.get(kind, palette['info'])
    label = ' ' + mark + ' ' + text + ' '
    if self.color:
      return self.style(label, 'reverse', 'bold', colour)
    return '[' + text + ']'

  def bar(self, fraction, width=12):
    # A compact proportion bar (measured / target), clamped to [0, 1] for the fill but coloured by pass/fail
    fraction = max(0.0, fraction)
    filled = min(width, int(round(min(fraction, 1.0) * width)))
    bar = self.g['bar_full'] * filled + self.g['bar_empty'] * (width - filled)
    colour = 'green' if fraction >= 1.0 else ('yellow' if fraction >= 0.75 else 'red')
    return self.style(bar, colour)

  def box(self, text, kind='info'):
    # A single-line rounded box, used for the headline PASS/FAIL verdict
    palette = {'pass': 'green', 'fail': 'red', 'warn': 'yellow', 'info': 'cyan'}
    colour = palette.get(kind, 'cyan')
    inner = '  ' + text + '  '
    top = self.g['tl'] + self.g['h'] * len(inner) + self.g['tr']
    bot = self.g['bl'] + self.g['h'] * len(inner) + self.g['br']
    self.out('  ' + self.style(top, colour))
    self.out('  ' + self.style(self.g['v'], colour) + self.style(inner, 'bold', colour) + self.style(self.g['v'], colour))
    self.out('  ' + self.style(bot, colour))

#======================================
# Live status spinner
#--------------------------------------

class Spinner:
  # A lightweight, thread-driven status line for long operations (the benchmark). It animates only on a colour
  # TTY; when output is piped/redirected it prints each status update as a plain line instead, so logs stay
  # readable. All spinner output goes to its console's stream (normally stderr) and is transient there.
  _frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

  def __init__(self, console):
    self.console = console
    self.animate = console.color and hasattr(console.stream, 'isatty') and console.stream.isatty()
    self._text = ''
    self._stop = threading.Event()
    self._thread = None
    self._lock = threading.Lock()

  def _draw(self, frame):
    with self._lock:
      spin = self.console.style(frame, 'cyan')
      self.console.stream.write('\r\x1b[K  ' + spin + '  ' + self._text)
      self.console.flush()

  def _spin(self):
    i = 0
    while not self._stop.wait(0.09):
      self._draw(self._frames[i % len(self._frames)])
      i += 1

  def _pause(self):
    # Stop the animation thread and erase its line, so the caller can print a permanent row without the
    # background thread racing to redraw over it. join() guarantees the thread is gone before we return
    if self._thread is not None:
      self._stop.set()
      self._thread.join(timeout=1.0)
      self._thread = None
    with self._lock:
      self.console.stream.write('\r\x1b[K')
      self.console.flush()

  def update(self, text):
    # Show/refresh the status line. Only animates on a colour TTY; otherwise stays silent (the caller's per-run
    # rows are the heartbeat) so piped/redirected logs stay clean
    self._text = text
    if not self.animate:
      return
    if self._thread is None:
      self._stop.clear()
      self._thread = threading.Thread(target=self._spin, daemon=True)
      self._thread.start()

  def clear(self):
    # Pause the animation so the caller can print a permanent line; a later update() restarts it
    if self.animate:
      self._pause()

  def stop(self):
    if self.animate:
      self._pause()
