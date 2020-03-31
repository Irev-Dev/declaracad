# -*- coding: utf-8 -*-
"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the GPL v3 License.

The full license is in the file LICENSE, distributed with this software.

Created on Dec 10, 2015

@author: jrm
"""
import os
import re
import jedi
import enaml
import traceback
from textwrap import dedent
from atom.api import (
    Enum, ContainerList, Unicode, Tuple, Bool, List, Int, Instance, Dict,
    observe
)

from declaracad.core.api import Plugin, Model, log
from enaml.scintilla.themes import THEMES
from enaml.scintilla.mono_font import MONO_FONT
from enaml.application import timed_call
from enaml.core.enaml_compiler import EnamlCompiler
from enaml.workbench.core.execution_event import ExecutionEvent
from enaml.layout.api import InsertItem, InsertTab, RemoveItem
from types import ModuleType
from glob import glob


def editor_item_factory():
    with enaml.imports():
        from .view import EditorDockItem
    return EditorDockItem


def create_editor_item(*args, **kwargs):
    EditorDockItem = editor_item_factory()
    return EditorDockItem(*args, **kwargs)


class Document(Model):
    #: Name of the current document
    name = Unicode().tag(config=True)

    #: Source code
    source = Unicode()
    cursor = Tuple(default=(0, 0))

    #: Any unsaved changes
    unsaved = Bool(False)

    #: Version number
    version = Int(1)

    #: Any linting errors
    errors = List()

    #: Any script output
    output = ContainerList()

    #: Any autocomplete suggestions
    suggestions = List()

    def _default_source(self):
        """ Load the document from the path given by `name`.
        If it fails to load, nothing will be returned and an error
        will be set.
        """
        try:
            log.debug("Loading '{}' from disk.".format(self.name))
            with open(self.name) as f:
                return f.read()
        except Exception as e:
            self.errors = [str(e)]
        return ""

    def _observe_unsaved(self, change):
        """ Increment the version number when unsaved is changed to false

        """
        if change['type'] == 'update' and not change['value']:
            self.version += 1

    def _observe_source(self, change):
        ext = os.path.splitext(self.name.lower())[-1]
        if ext in ['.py', '.enaml']:
            self.errors = []
            self._update_suggestions(change)
        if change['type'] == 'update':
            try:
                with open(self.name) as f:
                    self.unsaved = f.read() != self.source
            except:
                pass

    def _update_suggestions(self, change):
        """ Determine code completion suggestions for the current cursor
        position in the document.
        """
        from declaracad.core.workbench import DeclaracadWorkbench
        workbench = DeclaracadWorkbench.instance()
        plugin = workbench.get_plugin('declaracad.editor')
        self.suggestions = plugin.autocomplete(self.source, self.cursor)


class EditorPlugin(Plugin):
    #: Opened files
    documents = ContainerList(Document).tag(config=True)
    active_document = Instance(Document, ()).tag(config=True)
    last_path = Unicode(os.path.expanduser('~/')).tag(config=True)
    project_path = Unicode(os.path.expanduser('~/')).tag(config=True)

    #: Editor settings
    theme = Enum('friendly', *THEMES.keys()).tag(config=True)
    zoom = Int(0).tag(config=True)  #: Relative to default
    show_line_numbers = Bool(True).tag(config=True)
    code_folding = Bool(True).tag(config=True)
    font_size = Int(12).tag(config=True)  #: Default is 12 pt
    font_family = Unicode(MONO_FONT.split()[-1]).tag(config=True)
    show_scrollbars = Bool(True).tag(config=True)
    file_associations = Dict(default={
        'py': 'python',
        'pyx': 'python',
        'pyd': 'python',
        'pyi': 'python',
        'ino': 'cpp',
        'sh': 'bash',
        'yml': 'yaml',
        'js': 'javascript',
        'ts': 'javascript',
        'jsx': 'javascript',
        'md': 'markdown',
    }).tag(config=True)

    #: Key mappings
    key_mapping = Dict(default={
        'find': '\x06',  # Ctrl+F
        'replace': '\x12',  # Ctrl+R
        'goto': '\x0c',  # Ctrl + L
    }).tag(config=True)

    #: Editor sys path
    sys_path = List().tag(config=True)
    _area_saves_pending = Int()

    def start(self):
        """ Make sure the documents all open on startup """
        super(EditorPlugin, self).start()
        self.workbench.application.deferred_call(
            self._update_area_layout, {'type': 'load'})

    # -------------------------------------------------------------------------
    # Editor API
    # -------------------------------------------------------------------------
    @observe('documents')
    def _update_area_layout(self, change):
        """ When a document is opened or closed, add or remove it
        from the currently active TabLayout.

        The layout update is deferred so it fires after the items are
        updated by the Looper.

        """
        if change['type'] == 'create':
            return

        #: Get the dock area
        area = self.get_dock_area()

        #: Refresh the dock items
        #area.looper.iterable = self.documents[:]

        #: Determine what change to apply
        removed = set()
        added = set()
        if change['type'] == 'container':
            op = change['operation']
            if op in ['append', 'insert']:
                added = set([change['item']])
            elif op == 'extend':
                added = set(change['items'])
            elif op in ['pop', 'remove']:
                removed = set([change['item']])
        elif change['type'] == 'update':
            old = set(change['oldvalue'])
            new = set(change['value'])

            #: Determine which changed
            removed = old.difference(new)
            added = new.difference(old)
        elif change['type'] == 'load':
            removed = {item.doc for item in self.get_editor_items()}
            added = set(self.documents)

        #: Update operations to apply
        ops = []
        removed_targets = set()

        #: Remove any old items
        for doc in removed:
            for item in self.get_editor_items():
                if item.doc == doc:
                    removed_targets.add(item.name)
                    ops.append(RemoveItem(item=item.name))

        # Remove ops
        if ops:
            log.debug(ops)
            area.update_layout(ops)

        # Add each one at a time
        targets = set([item.name for item in area.dock_items()
                   if (item.name.startswith("editor-item") and
                   item.name not in removed_targets)])

        log.debug("Editor added=%s removed=%s targets=%s", added, removed, targets)

        # Sort documents so active is last so it's on top when we restore
        # from a previous state
        for doc in sorted(added, key=lambda d: int(d == self.active_document)):
            item = create_editor_item(area, plugin=self, doc=doc)
            if targets:
                op = InsertTab(item=item.name, target=list(targets)[-1])
            else:
                op = InsertItem(item=item.name)
            targets.add(item.name)
            log.debug(op)
            try:
                area.update_layout(op)
            except Exception as e:
                log.exception(e)

        # Now save it
        self.save_dock_area(change)

    def save_dock_area(self, change):
        """ Save the dock area """
        self._area_saves_pending += 1

        def do_save():
            self._area_saves_pending -= 1
            if self._area_saves_pending != 0:
                return
            #: Now save it
            ui = self.workbench.get_plugin('enaml.workbench.ui')
            ui.workspace.save_area()
        timed_call(350, do_save)

    def get_dock_area(self):
        """ Alias to the `declaracad.ui` plugins `get_dock_area()`

        """
        ui = self.workbench.get_plugin('declaracad.ui')
        return ui.get_dock_area()

    def get_editor(self, document=None):
        """ Get the editor item for the currently active document

        """
        doc = document or self.active_document
        for item in self.get_editor_items():
            if item.doc == doc:
                return item.editor

    def get_editor_items(self):
        dock = self.get_dock_area()
        EditorDockItem = editor_item_factory()
        for item in dock.dock_items():
            if isinstance(item, EditorDockItem):
                yield item

    # -------------------------------------------------------------------------
    # Document API
    # -------------------------------------------------------------------------
    def _default_documents(self):
        return [Document()]

    def _default_active_document(self):
        if not self.documents:
            self.documents = self._default_documents()
        return self.documents[0]

    def new_file(self, event):
        """ Create a new file with the given path

        """
        path = event.parameters.get('path')
        if not path:
            return
        doc = Document(
            name=os.path.join(self.project_path, path),
            source=dedent("""
                # Created in DeclaraCAD
                from declaracad.occ.api import *

                enamldef Assembly(Part):
                    Box:
                        pass
                """).lstrip())
        self.documents.append(doc)
        self.active_document = doc

    def close_file(self, event):
        """ Close the file with the given path and remove it from
        the document list. If multiple documents with the same file
        are open this only closes the first one it finds.

        """
        if isinstance(event, ExecutionEvent):
            path = event.parameters.get('path')
        else:
            path = event

        # Default to current document
        if path is None:
            path = self.active_document.name
        docs = self.documents
        opened = [d for d in docs if d.name == path]
        if not opened:
            return
        log.debug("Closing '%s'", path)
        doc = opened[0]
        self.documents.remove(doc)

        # If any viewer was bound to this document, unbind it
        for viewer in self.get_viewers():
            if viewer.document == doc:
                viewer.document = None

        # If we removed all of them create a new empty one
        if not self.documents:
            self.documents = self._default_documents()
            self.active_document = self.documents[0]

        # If we closed the active document
        elif self.active_document == doc:
            self.active_document = self.documents[0]

    def open_file(self, event):
        """ Open a file from the local filesystem

        """
        path = event.parameters['path']

        #: Check if the document is already open
        for doc in self.documents:
            if doc.name == path:
                self.active_document = doc
                return
        log.debug("Opening '%s'", path)

        #: Otherwise open it
        doc = Document(name=path, unsaved=False)
        with open(path) as f:
            doc.source = f.read()
        self.documents.append(doc)
        self.active_document = doc
        editor = self.get_editor()
        if editor:
            editor.set_text(doc.source)

    def save_file(self, event):
        """ Save the currently active document to disk

        """
        # Make sure it's in sync with the editor first
        editor = self.get_editor()
        doc = self.active_document
        doc.source = editor.get_text()
        assert doc.name, "Can't save a document without a name"
        file_dir = os.path.dirname(doc.name)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        with open(doc.name, 'w') as f:
            f.write(doc.source)
        doc.unsaved = False

    def save_file_as(self, event):
        """ Save the currently active document as the given name
        overwriting and creating the directory path if necessary.

        """
        doc = self.active_document
        path = event.parameters['path']

        if not doc.name:
            doc.name = path
            doc.unsaved = False

        doc_dir = os.path.dirname(path)
        if not os.path.exists(doc_dir):
            os.makedirs(doc_dir)

        with open(path, 'w') as f:
            f.write(doc.source)

    #@observe('active_document',  #'active_document.source',
             #'active_document.unsaved')
    #def refresh_view(self, change):
        #""" Refresh the renderer when the document is saved

        #"""
        #plugin = self.workbench.get_plugin('declaracad.viewer')
        #doc = self.active_document
        #path, ext = os.path.splitext(doc.name)
        #if ext not in ('.py', '.enaml'):
            #return
        #for viewer in plugin.get_viewers():
            #If the viewer is watching another document ignore changes
            #unless it's the active document
            #if viewer.document is None or viewer.document == doc:
                #viewer.renderer.filename = doc.name
                #Clear source so it loads from disk and force a version
                #change to ensure it updates if the filename was not changed
                #viewer.renderer.set_source("")
                #viewer.renderer.version += 1

    # -------------------------------------------------------------------------
    # Code inspection API
    # -------------------------------------------------------------------------
    def _default_sys_path(self):
        """ Determine the sys path"""
        return [self.project_path]

    @observe('project_path')
    def _refresh_sys_path(self, change):
        if change['type'] == 'update':
            self.sys_path = self._default_sys_path()

    def autocomplete(self, source, cursor):
        """ Return a list of autocomplete suggestions for the given text.
        Results are based on the modules loaded.

        Parameters
        ----------
            source: str
                Source code to autocomplete
            cursor: (line, column)
                Position of the editor
        Return
        ------
            result: list
                List of autocompletion strings
        """
        return []
        try:
            #: TODO: Move to separate process
            line, column = cursor
            script = jedi.Script(source, line+1, column,
                                 sys_path=self.sys_path)

            #: Get suggestions
            results = []
            for c in script.completions():
                results.append(c.name)

                #: Try to get a signature if the docstring matches
                #: something Scintilla will use (ex "func(..." or "Class(...")
                #: Scintilla ignores docstrings without a comma in the args
                if c.type in ['function', 'class', 'instance']:
                    docstring = c.docstring()

                    #: Remove self arg
                    docstring = docstring.replace("(self,", "(")

                    if docstring.startswith("{}(".format(c.name)):
                        results.append(docstring)
                        continue

            return results
        except Exception:
            #: Autocompletion may fail for random reasons so catch all errors
            #: as we don't want the editor to exit because of this
            return []
