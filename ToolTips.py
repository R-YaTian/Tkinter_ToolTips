# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Python ToolTips for Tkinter V1.0.5
#
# Copyright 2016, PedroHenriques
# http://www.pedrojhenriques.com
# https://github.com/PedroHenriques
#
# Free to use under the MIT license.
# http://www.opensource.org/licenses/mit-license.php
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import tkinter.ttk as ttk
import tkinter.font as tkFont
from time import time
from tkinter import Toplevel

class ToolTips:
    """This class will display a tooltip around a widget that is being hovered over.
    The constructor receives a list of widgets, a list of strings and an optional Tkinter font object.
    The lists should match their indexes so that the tooltip string for the first widget is in index zero, and so on.

    There are several class variables that can be used to customize the styling of the tooltips.
    """

    # class variables with the fallback font information, to be used in the tooltip text
    tt_fallback_font_family_ = 'Microsoft YaHei UI'
    tt_fallback_font_size_ = 9

    # class variables with the background and foreground colors
    bg_color_ = '#FFFFFF'
    fg_color_ = '#000000'

    # class variables used to control the vertical space between the tooltip and the event widget
    vertical_margin_ = 0

    def __init__(self, widgets, tooltip_text, font=None, delay=1, PseudoFollow=True, stime=0):
        # check if the 2 lists have the same number of items, and if not raise an exception
        if (len(widgets) != len(tooltip_text)):
            raise ValueError("The number of widgets supplied does not match the number of tooltip strings provided.")

        # instance variable pointing to a list of widgets to be managed by this instance
        self.widgets = widgets

        # instance variable pointing to a list of strings to be used by the supplied widgets
        self.tooltip_text = tooltip_text

        # instance variable to flag whether a font was supplied or not
        if font is None:
            self.font_supplied = False
        else:
            self.font_supplied = True

        # instance variable pointing to a font object, to be used on the tooltip text
        self.font = font

        # instance variable with the font object for the tooltip text
        # starts with the fallback font
        self.tt_font = tkFont.Font(family=self.tt_fallback_font_family_, size=self.tt_fallback_font_size_)

        # loop through each widget and set the necessary binds
        for widget in self.widgets:
            # set the binds
            self.setWidgetBinds(widget)
            ToolTip(self, widget, delay, PseudoFollow, stime)

        # instance variable where the tooltip widget will be stored
        self.tt_widget = None
        # instance variable where the tooltip's text will be stored
        self.tt_text = ""

    def setWidgetBinds(self, widget):
        widget.bind("<Button-1>", self.hideToolTips, '+')

    # this method will be called when widgets with tooltips are hovered over
    def showToolTips(self, event):
        # get a reference to the event widget
        widget_ref = event

        # check if we were able to grab a pointer to a widget and that we have that widget in
        # widget list supplied to the constructor
        if (widget_ref == None or widget_ref not in self.widgets):
            # either we couldn't grab a pointer to the event widget
            # or that widget is not in the list of widgets provided
            # to the constructor, so bail out
            print("The hovered widget is not in the list of widgets provided to this instance.")
            return(False)

        # grab this widget's tooltip text from the list
        try:
            self.tt_text = self.tooltip_text[self.widgets.index(widget_ref)]
        except (IndexError, ValueError):
            # either widget_ref couldn't be found in self.widgets
            # or the tooltip text couldn't be found for the widget's index, so bail out
            print("An error occured while trying to find the tooltip text for the hovered widget.")
            return(False)

        # grab the event widget's top master (will be used for both measuring the position of the tooltip
        # and will be the direct master for the tooltip)
        top_master = widget_ref.winfo_toplevel()

        # local variables used to position the tooltip
        # starting at the NW corner of the event widget
        x = widget_ref.winfo_x()
        y = widget_ref.winfo_y()

        w_master = top_master.nametowidget(widget_ref.winfo_parent())  # event widget's master
        while w_master != top_master:
            # update the x and y coords of the
            x += w_master.winfo_x()
            y += w_master.winfo_y()

            # grab next master in the hierarchy
            w_master = top_master.nametowidget(w_master.winfo_parent())

        # create the tooltip font based on the event widget's font
        self.setFont(widget_ref)

        # create the tooltip label widget and initial width + height
        self.handleTooltipWidget(top_master)

        if (y + widget_ref.winfo_height() >= top_master.winfo_height()):
            y -= self.tt_widget.winfo_reqheight() + widget_ref.winfo_height() + 10
        elif (y + widget_ref.winfo_height() + 20 >= top_master.winfo_height()):
            y -= self.tt_widget.winfo_reqheight() + widget_ref.winfo_height()

        if (x + widget_ref.winfo_width() >= top_master.winfo_width()):
            x -= widget_ref.winfo_width()

        if x == 0:
            x += 3

        # draw the tooltip
        self.tt_widget.place(x=x-3, y=y+30)

    # this method will be called when widgets with tooltips sto being hovered over
    # or "entered" by any other means (ex: tab selecting)
    def hideToolTips(self, event):
        # if there are no active tooltips bail out
        if self.tt_widget is None:
            return

        # remove the tooltip from the screen and any other tkinter internal references
        self.tt_widget.destroy()

        # free the variables
        self.tt_widget = None
        self.tt_text = ""

    # this method will create the tooltip widget, if one doesn't exist already, and will calculate
    # the required width and height of the tooltip text without any line breaks, which is used to later calculate
    # the average character width for the given font and the given tooltip text
    def handleTooltipWidget(self, top_master):
        # if the tooltip widget doesn't exist create it, otherwise update the dimensions
        if self.tt_widget is None:
            # create the tooltip label widget
            # NOTE: we start with an altered version of the intended text, because of the need to calculate the required width
            #		of the tooltip widget without any line breaks. If they are left in that calculation it will skew the
            #		the calculation (later below) of the average #characters in each line that fit the window size.
            #		The correct text will be added shortly below.
                        self.tt_widget = ttk.Label(top_master, text=self.tt_text.replace(
                            "\n", " "), background=self.bg_color_, foreground=self.fg_color_, font=self.tt_font, relief='ridge')
        else:
            # update the tooltip's text to recalculate the requested dimensions below
            self.tt_widget.configure(text=self.tt_text.replace("\n", " "))

        # move the tooltip from being on top of the event widget to a reasonable relative location
        # by default the tooltip's NW corner will be close to the event widget's SW corner
        # however this might need to be adjusted, if it would make the tooltip overflow the program's window
        # calculate the width and height of the tooltip (using the required dimension since it hasn't been drawn to screen yet, meaning there are no actual dimensions yet)
        self.tt_width = self.tt_widget.winfo_reqwidth()
        self.tt_height = self.tt_widget.winfo_reqheight()

        # now that we have calculated the initial required dimensions, we can update the widget's text to the intended one
        self.tt_widget.configure(text=self.tt_text)

    # this method creates the font based on the event widget's font family and size
    def setFont(self, event_widget):
        # grab the event widget's font info
        try:
            if (self.font_supplied):
                # a font was supplied to the constructor, so create a copy of it's current values
                self.tt_font["family"] = self.font["family"]
                self.tt_font["size"] = self.font["size"]
            else :
                # a font wasn't supplied to the constructor, try getting the event widget's font
                ew_font_info = event_widget["font"].actual()
                self.tt_font["family"] = ew_font_info["family"]
                self.tt_font["size"] = ew_font_info["size"]
        except Exception :
            # we couldn't create a tkFont object
            # most likely the event widget is using a custom tkFont object which can't be accessed and edited from here
            # or the event widget doesn't have a "font" attribute
            # use the fallback font
            self.tt_font["family"] = self.tt_fallback_font_family_
            self.tt_font["size"] = self.tt_fallback_font_size_

        # grab the tt_font's font size
        self.tt_font_size = self.tt_font["size"]

class ToolTip(Toplevel):
    # ToolTipPseudoToplevel
    def __init__(self, ToolTips, wdgt, delay=1, PseudoFollow=True, stime=0):
        self.ToolTips = ToolTips
        self.wdgt = wdgt
        self.parent = self.wdgt.master                                          # The parent of the ToolTip is the parent of the ToolTips widget
        Toplevel.__init__(self, self.parent, bg='black', padx=1, pady=1)
        self.withdraw()                                                         # Hide initially
        self.overrideredirect(True)                                             # The ToolTip Toplevel should have no frame or title bar
        self.delay = delay
        self.visible = 0
        self.lastMotion = 0
        self.follow = PseudoFollow
        self.stime = stime
        self.timer_id = None
        self.wdgt.bind('<Enter>', self.spawn, '+')                              # Add bindings to the widget.This will NOT override bindings that the widget already has
        self.wdgt.bind('<Leave>', self.hide, '+')
        self.wdgt.bind('<Motion>', self.move, '+')

    def spawn(self, event=None):
        #Spawn the ToolTip.This simply makes the ToolTip eligible for display
        #Usually this is caused by entering the widget
        """
        Arguments:
          event: The event that called this funciton
        """
        self.visible = 1
        if self.delay == 0:
            self.show()
        elif self.timer_id is None:
            self.timer_id = self.after(int((self.delay + 1) * 1000), self.show) # The after function takes a time argument in miliseconds

    def show(self):
        #Displays the ToolTip if the time delay has been long enough
        if self.visible == 1 and time() - self.lastMotion >= self.delay:
            self.visible = 2
        if self.visible == 2:
            ToolTips.showToolTips(self.ToolTips, self.wdgt)
        if self.stime != 0:
            self.timer_id = self.after(int((self.stime + 1) * 1000), self.hide)

    def move(self, event):
        #Processes motion within the widget
        """
        Arguments:
          event: The event that called this function
        """
        self.lastMotion = time()
        if self.follow == False and self.delay != 0 and self.stime == 0:
            ToolTips.hideToolTips(self.ToolTips, self.wdgt)
            self.visible = 1
            self.after(int((self.delay + 1) * 1000), self.show)

    def hide(self, event=None):
        #Hide the ToolTip.Usually this is caused by leaving the widget
        """
        Arguments:
          event: The event that called this function
        """
        if self.timer_id is not None:
            tid = self.timer_id
            self.timer_id = None
            self.after_cancel(tid)
        ToolTips.hideToolTips(self.ToolTips, self.wdgt)
        self.visible = 0
