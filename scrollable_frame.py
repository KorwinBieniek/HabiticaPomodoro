'''
Module containing a frame class with a scroll option
'''
import tkinter as tk


class ScrollableFrame(tk.Frame):
    '''
    Frame class that allows to scroll within it to hold Habitica subtasks
    '''

    def __init__(self, master, **kwargs):
        '''
        Creates a frame with Scrollbar inside
        :param master:
        :param kwargs:
        '''
        tk.Frame.__init__(self, master, **kwargs)

        # create a canvas object and a vertical scrollbar for scrolling it
        self.vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.vscrollbar.pack(side='right', fill="y", expand="false")
        self.canvas = tk.Canvas(self,
                                bg='#282828', bd=0,
                                height=100,
                                highlightthickness=0,
                                yscrollcommand=self.vscrollbar.set)
        self.canvas.pack(side="left", fill="both", expand="true")
        self.vscrollbar.config(command=self.canvas.yview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = tk.Frame(self.canvas, **kwargs)
        self.canvas.create_window(0, 0, window=self.interior, anchor="nw")


    def set_scrollregion(self, event=None):
        '''
        Set the scroll region on the canvas

        :param event:
        :return:
        '''
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
