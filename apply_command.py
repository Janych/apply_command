# __init__.py
#
# Copyright (C) 2019 - Janych <github@Janych.ru>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# The Rhythmbox authors hereby grant permission for non-GPL compatible
# GStreamer plugins to be used and distributed together with GStreamer
# and Rhythmbox. This permission is above and beyond the permissions granted
# by the GPL license by which Rhythmbox is covered. If you modify this code
# you may extend this exception to your version of the code, but you are not
# obligated to do so. If you do not wish to do so, delete this exception
# statement from your version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA.

from gi.repository import Gio, GObject, GLib, Peas
from gi.repository import PeasGtk
from gi.repository import Gtk

import gettext

import locale
from urllib.parse import unquote
from gi.repository.GLib import Variant

DCONF_DIR = 'org.gnome.rhythmbox.plugins.apply_command'

class ApplyCommandPlugin (GObject.Object, Peas.Activatable, PeasGtk.Configurable):
	__gtype_name = 'ApplyCommand'

	object = GObject.property (type = GObject.Object)

	def __init__(self):
		GObject.Object.__init__(self)
		self.settings = Gio.Settings(DCONF_DIR)

	def do_activate(self):
		self.shell = self.object

		self.__action = Gio.SimpleAction(name='open')
		self.__action.connect('activate', self.apply_command)

		app = Gio.Application.get_default()
		app.add_action(self.__action)

		# Receive fourth submenu
		menu=self.shell.props.application.get_menubar()
		assert menu.get_n_items()>3 , 'But I need fourth submenu'
		it=menu.iterate_item_links(3)
		it.next()
		self.menu=it.get_value()

		item = Gio.MenuItem()
		if locale.getlocale()[0] == 'ru_RU':
			item.set_label("Открыть...")
		else:
			item.set_label(_("Open..."))
		item.set_detailed_action('app.open')
		item.set_attribute_value('accel',Variant('s', '<Ctrl>L'))
		self.menu.append_item(item)
		app.add_plugin_menu_item('edit', 'open', item)
		app.add_plugin_menu_item('browser-popup', 'open', item)
		app.add_plugin_menu_item('playlist-popup', 'open', item)
		app.add_plugin_menu_item('queue-popup', 'open', item)

	def do_deactivate(self):
		app = Gio.Application.get_default()
		app.remove_action('open')
		self.menu.remove_item(item,self.menu.get_n_items()-1)
		app.remove_plugin_menu_item('edit', 'open')
		app.remove_plugin_menu_item('browser-popup', 'open')
		app.remove_plugin_menu_item('playlist-popup', 'open')
		app.remove_plugin_menu_item('queue-popup', 'open')
		del self.__action

	def apply_command(self, action, data):
		def uri_to_filename(uri):
			uri=unquote(uri)
			if uri[0:8]=='\'file://':
				return uri[0]+uri[8:]
			else:
				return ''
		def quote_file_name(fn):
			return '\''+fn.replace('\'', '\'\\\'\'')+'\''
		page = self.shell.props.selected_page
		if not hasattr(page, "get_entry_view"):
			return

		entries = page.get_entry_view().get_selected_entries()
		cmdline = self.settings["command"]
		Umacro=' '.join(quote_file_name(entry.get_playback_uri()) for entry in entries)
		Fmacro=' '.join(uri_to_filename(quote_file_name(entry.get_playback_uri())) for entry in entries)
		if cmdline.find('%f')!=-1 or cmdline.find('%u')!=-1:
			if len(entries)!=1:
				print("\x1b[150G selected "+str(len(entries))+" elements, macroses %f and %u acceptable only with one element, I think so")
				return
		if (((cmdline.find('%F')!=-1) or (cmdline.find('%f')!=-1)) and not Fmacro.lstrip()) or \
		   (((cmdline.find('%U')!=-1) or (cmdline.find('%u')!=-1)) and not Umacro.lstrip()):
			print("\x1b[150G Not enought filenames/urls to call "+cmdline)
			return

		cmdline = cmdline.replace('%F',Fmacro).replace('%U',Umacro).replace('%f',Fmacro).replace('%u',Umacro)
		print("\x1b[150G command="+cmdline)
		GLib.spawn_command_line_async(cmdline)

	def do_create_configure_widget(self):
		dialog = Gtk.VBox()

		hbox = Gtk.HBox()
		entry = Gtk.Entry()
		entry_buffer = Gtk.EntryBuffer()
		entry_buffer.set_text(self.settings["command"], len(self.settings["command"]))
		entry_buffer.connect("inserted-text", self.command_edited)
		entry_buffer.connect("deleted-text", self.command_edited)
		entry.set_buffer(entry_buffer)

		label = Gtk.Label()
		label.set_text("Command")

		hbox.pack_start(label, False, False, 5)
		hbox.pack_start(entry, False, False, 5)
		dialog.pack_start(hbox, False, False, 5)
		
		dialog.set_size_request(300, -1)
		
		return dialog

	def command_edited(self, entry_buffer, *args):
		self.settings["command"] = entry_buffer.get_text()

