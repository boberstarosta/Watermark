import os
import json

from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.filedialog import askopenfilenames, askdirectory

import PIL.Image, PIL.ImageTk
from .guiconstants import *
from .lib import *


def run():
	"""Call this funcion to start the application."""
	win = MainWindow()
	win.mainloop()


# ======================================================
# ==============        MainWindow        ==============
# ======================================================

class MainWindow(Tk):
	def __init__(self):
		super().__init__()
		
		self.title(MAIN_WINDOW_TITLE)
		
		# Dict containing files to be processed {"file_name": "full_path"}.
		self.files = {}

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)
		
		frame = Frame(self)
		frame.grid(row=0, column=0, sticky=NSEW)
		
		tb = Frame(frame)
		tb.pack(side=TOP, fill=X)
		btn = Button(tb, text=ADD_FILES_BUTON_TEXT, command=self.on_add_files)
		btn.pack(side=LEFT)
		btn = Button(tb, text=ADD_FOLDER_BUTTON_TEXT
					, command=self.on_add_folder)
		btn.pack(side=LEFT)
		self.remove_files_btn = Button(tb, text=REMOVE_FILES_BUTTON_TEXT
									, command=self.on_remove)
		self.remove_files_btn.pack(side=LEFT)
		self.remove_all_btn = Button(tb, text=REMOVE_ALL_FILES_BUTTON_TEXT
									, command=self.on_remove_all)
		self.remove_all_btn.pack(side=LEFT)
		
		self.listlabel = Label(frame)
		self.listlabel.pack(side=TOP)
		slb = ScrollListbox(frame)
		slb.pack(side=TOP, fill=BOTH, expand=True)
		self.listbox = slb.listbox
		self.listbox.config(selectmode=EXTENDED)
		self.listbox.bind("<<ListboxSelect>>", self.on_select_files)
		
		self.settingsframe = SettingsFrame(self)
		self.settingsframe.grid(column=1, row=0, sticky=NE)
		
		self.apply_watermarks_button = Button(self
				, text=APPLY_WATERMARK_BUTTON_TEXT \
				, command=self.on_apply_watermark, height=2, pady=4)
		self.apply_watermarks_button.grid(column=0, row=1, columnspan=2
									, sticky=EW)
		
		self.protocol("WM_DELETE_WINDOW", self.on_closing)
		
		self.update_toolbar()
		
		self.update()
		self.minsize(self.winfo_width(), self.winfo_height())
	
	def update_listbox(self):
		self.listbox.delete(0, END)
		for k in self.files.keys():
			self.listbox.insert(END, k)

	def update_toolbar(self):
		if len(self.listbox.curselection()) == 0:
			self.remove_files_btn.config(state=DISABLED)
		else:
			self.remove_files_btn.config(state=NORMAL)
			
		if self.listbox.size() == 0:
			self.remove_all_btn.config(state=DISABLED)
			self.apply_watermarks_button.config(state=DISABLED)
		else:
			self.remove_all_btn.config(state=NORMAL)
			self.apply_watermarks_button.config(state=NORMAL)
		
		self.listlabel.config(text="{} ({})".format(FILE_LIST_TITLE
					, self.listbox.size()))
		
	def add_files(self, paths):
		for path in paths:
			fn = os.path.basename(path)
			if fn not in self.files and is_file_ext_right(path):
				self.files[fn] = path
		self.update_listbox()
		self.update_toolbar()
	
	def remove_files(self, names):
		for fn in names:
			if fn in self.files:
				self.files.pop(fn, None)
		self.update_listbox()
		self.update_toolbar()
	
	def on_add_files(self, *args):
		paths = askopenfilenames(
				parent=self,
				filetypes = DIALOG_OPEN_FILES_TYPES,
				title = DIALOG_OPEN_FILES_TITLE)
		if paths:
			self.add_files(paths)
	
	def on_add_folder(self, *args):
		path = askdirectory(
				parent=self,
				mustexist = True,
				title = DIALOG_OPEN_FOLDER_TITLE)
		if path:
			self.add_files(listfiles(path))
		
	def on_remove(self, *args):
		selection = self.listbox.curselection()
		names = [self.listbox.get(i) for i in selection]
		self.remove_files(names)

	def on_remove_all(self, *args):
		self.remove_files(self.files.copy())
	
	def on_select_files(self, *args):
		self.update_toolbar()
	
	def on_apply_watermark(self, *args):
		self.settingsframe.settings.save(SETTINGS_FILE)
		if messagebox.askyesno(
							MESSAGEBOX_ASK_TITLE
							, MESSAGEBOX_ASK_TEXT.format(len(self.files))):
			win = ApplyingWindow(self)
			win.go(self.files.values(), self.settingsframe.settings)
			self.remove_files(self.files.copy())
	
	def on_closing(self, *args):
		self.settingsframe.settings.save(SETTINGS_FILE)
		self.destroy()
		
# ============== End of class MainWindow ==============


# ======================================================
# =============        SettingsFrame        ============
# ======================================================

class SettingsFrame(Frame):
	def __init__(self, *args, **kw):
		super().__init__(*args, **kw)
		
		l = Label(self, text=SETTINGS_TITLE)
		l.grid(column=0, row=0, columnspan=2)
		
		l = Label(self, text=SETTINGS_TEXT_LABEL)
		l.grid(column=0, row=1, sticky=W)
		self.svtext = StringVar()
		e = Entry(self, textvariable=self.svtext)
		e.grid(column=1, row=1, sticky=EW)
		self.svtext.trace("w", self.on_text_changed)
		
		l = Label(self, text=SETTINGS_ALPHA_LABEL)
		l.grid(column=0, row=2, sticky=W)
		self.ivalpha = IntVar()
		s = Scale(self, from_=SETTINGS_ALPHA_MIN, to=SETTINGS_ALPHA_MAX
					, orient=HORIZONTAL, variable=self.ivalpha
					, showvalue=False)
		s.grid(column=1, row=2, sticky=EW)
		self.ivalpha.trace("w", self.on_alpha_changed)
		
		l = Label(self, text=SETTINGS_SIZEFACTOR_LABEL)
		l.grid(column=0, row=3, sticky=W)
		self.ivsizefactor = IntVar()
		s = Scale(self
				, from_=SETTINGS_SIZEFACTOR_MIN, to=SETTINGS_SIZEFACTOR_MAX \
				, orient=HORIZONTAL, variable=self.ivsizefactor
				, showvalue=False)
		s.grid(column=1, row=3, sticky=EW)
		self.ivsizefactor.trace("w", self.on_sizefactor_changed)
		
		l = Label(self, text=SETTINGS_XMARGIN_LABEL)
		l.grid(column=0, row=4, sticky=W)
		self.ivxmargin = IntVar()
		s = Scale(self, from_=SETTINGS_MARGIN_MIN, to=SETTINGS_MARGIN_MAX
					, orient=HORIZONTAL, variable=self.ivxmargin
					, showvalue=False)
		s.grid(column=1, row=4, sticky=EW)
		self.ivxmargin.trace("w", self.on_xmargin_changed)

		l = Label(self, text=SETTINGS_YMARGIN_LABEL)
		l.grid(column=0, row=5, sticky=W)
		self.ivymargin = IntVar()
		s = Scale(self, from_=SETTINGS_MARGIN_MIN, to=SETTINGS_MARGIN_MAX
					, orient=HORIZONTAL, variable=self.ivymargin
					, showvalue=False)
		s.grid(column=1, row=5, sticky=EW)
		self.ivymargin.trace("w", self.on_ymargin_changed)
		
		l = Label(self, text=SETTINGS_POSITIONS_LABEL)
		l.grid(column=0, row=6, sticky=W)
		f = Frame(self)
		f.grid(column=1, row=6, sticky=EW)
		self.ivcenter = IntVar()
		ce = Checkbutton(f, variable=self.ivcenter)
		ce.grid(column=1, row=1)
		self.ivtopleft = IntVar()
		tl = Checkbutton(f, variable=self.ivtopleft)
		tl.grid(column=0, row=0)
		self.ivtopright = IntVar()
		tr = Checkbutton(f, variable=self.ivtopright)
		tr.grid(column=2, row=0)
		self.ivbottomleft = IntVar()
		bl = Checkbutton(f, variable=self.ivbottomleft)
		bl.grid(column=0, row=2)
		self.ivbottomright = IntVar()
		br = Checkbutton(f, variable=self.ivbottomright)
		br.grid(column=2, row=2)
		
		self.ivcenter.trace("w", self.on_pos_center_changed)
		self.ivtopleft.trace("w", self.on_pos_topleft_changed)
		self.ivtopright.trace("w", self.on_pos_topright_changed)
		self.ivbottomleft.trace("w", self.on_pos_bottomleft_changed)
		self.ivbottomright.trace("w", self.on_pos_bottomright_changed)
		
		l = Label(self, text=SETTINGS_PREVIEW_LABEL)
		l.grid(column=0, row=7, columnspan=2)
		self.imglabel = Label(self)
		self.imglabel.grid(column=0, row=8, columnspan=2)
		
		self.previewimage = PIL.Image.open(SETTINGS_PREVIEW_FILE)
		self.previewimage.thumbnail(SETTINGS_PREVIEW_SIZE)
		
		self.settings = Settings.load(SETTINGS_FILE)
		self.update_widgets()
		self.show_preview()
	
	def update_widgets(self):
		self.svtext.set(self.settings.text)
		self.ivalpha.set(self.settings.alpha)
		self.ivsizefactor.set(self.settings.sizefactor)
		self.ivxmargin.set(self.settings.xmargin)
		self.ivymargin.set(self.settings.ymargin)
		self.ivcenter.set(self.settings.center)
		self.ivtopleft.set(self.settings.topleft)
		self.ivtopright.set(self.settings.topright)
		self.ivbottomleft.set(self.settings.bottomleft)
		self.ivbottomright.set(self.settings.bottomright)
	
	def on_text_changed(self, *args):
		self.settings.text = self.svtext.get()
		self.show_preview()
		
	def on_alpha_changed(self, *args):
		self.settings.alpha = self.ivalpha.get()
		self.show_preview()

	def on_sizefactor_changed(self, *args):
		self.settings.sizefactor = self.ivsizefactor.get()
		self.show_preview()
	
	def on_xmargin_changed(self, *args):
		self.settings.xmargin = self.ivxmargin.get()
		self.show_preview()
	
	def on_ymargin_changed(self, *args):
		self.settings.ymargin = self.ivymargin.get()
		self.show_preview()
	
	def on_pos_center_changed(self, *args):
		self.settings.center = bool(self.ivcenter.get())
		self.show_preview()
		
	def on_pos_topleft_changed(self, *args):
		self.settings.topleft = bool(self.ivtopleft.get())
		self.show_preview()
		
	def on_pos_topright_changed(self, *args):
		self.settings.topright = bool(self.ivtopright.get())
		self.show_preview()
		
	def on_pos_bottomleft_changed(self, *args):
		self.settings.bottomleft = bool(self.ivbottomleft.get())
		self.show_preview()
		
	def on_pos_bottomright_changed(self, *args):
		self.settings.bottomright = bool(self.ivbottomright.get())
		self.show_preview()
		
	def show_preview(self):
		#image = PIL.Image.new("RGB", SETTINGS_PREVIEW_SIZE, (0,0,0))
		image = add_watermark(self.previewimage, self.settings)
		self.tkimage = PIL.ImageTk.PhotoImage(image)
		self.imglabel.config(image=self.tkimage)

# ============== End of class ConfigFrame ==============


# ======================================================
# ============        ApplyingWindow        ============
# ======================================================

class ApplyingWindow(Toplevel):
	def __init__(self, parent):
		super().__init__(parent)
		
		self.title(APPLY_WINDOW_TITLE)
		
		self.overrideredirect(True)
		
		self.progress = ttk.Progressbar(self, orient="horizontal"
									, mode="determinate", length=600)
		self.progress.grid(column=0, row=0, sticky=EW)

		self.label = Label(self)
		self.label.grid(column=0, row=1, sticky=NSEW)
		
		self.closebtn = Button(self, text=APPLY_WINDOW_CLOSE
								, command=self.destroy, state=DISABLED)
		self.closebtn.grid(column=0, row=2, pady = 4)
		
		self.center()
		
		self.grab_set()
		self.focus_set()
		self.update()

	def go(self, paths, settings):
		total_files = len(paths)
		done_files = 0
		self.progress["value"] = 0
		self.progress["maximum"] = total_files

		for path in paths:
			if add_watermark_to_file(path, settings):
				done_files += 1
			self.progress["value"] += 1
			self.label.config(text=APPLY_WINDOW_LABEL.format(done_files
										, total_files, ""))
			self.update_idletasks()
			
		self.label.config(text=APPLY_WINDOW_LABEL.format(done_files
									, total_files, APPLY_WINDOW_READY))
		self.closebtn.config(state=NORMAL)
		self.closebtn.focus_set()

	def center(self):
		self.update()
		w = self.winfo_screenwidth()
		h = self.winfo_screenheight()
		size = tuple(int(a) for a in self.geometry().split('+')[0].split('x'))
		x = w/2 - size[0]/2
		y = h/2 - size[1]/2
		self.geometry("%dx%d+%d+%d" % (size + (x, y)))

# ============== End of class ConfigFrame ==============


# ======================================================
# ============        ScrollListbox        =============
# ======================================================

class ScrollListbox(Frame):
	"""
		Usage:
			Use the 'listbox' attribute to access the listbox,
			construct and pack/place/grid normally.
	"""
	
	def __init__(self, *args, **kw):
		super().__init__(*args, **kw)
		
		scrollbar = Scrollbar(self)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox = Listbox(self)
		self.listbox.pack(fill=BOTH, expand=True)
		self.listbox.config(yscrollcommand=scrollbar.set)
		scrollbar.config(command=self.listbox.yview)

# ========== End of class ScrollListbox ==========

