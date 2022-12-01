'''
Module representing Pomodoro timer class, that allows the user
to benefit from customized Pomodoro app connected to Habitica tasks
'''

#TODO short break if resets after long breaks

import time
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk, PhotoImage
from PIL import ImageTk, Image
import tkinter.font as font
import requests
from scrollable_frame import ScrollableFrame
from dark_mode_title_bar import *


class PomodoroTimer:
    '''
    Class that represents Pomodoro Timer that allows to count time for specific tasks taken from Habitica
    '''

    def __init__(self):
        '''
        Constructor that creates all GUI elements for the timer
        '''
        self.root = tk.Tk()
        self.root.geometry('600x600')
        self.root.title('Pomodoro Timer Habitica')
        self.root.tk.call('wm', 'iconphoto', self.root._w, PhotoImage(file='gui/pomodoro.png'))
        self.root.config(bg="#282828")

        # Adding dark mode - needs to change window size on Windows 10
        dark_title_bar(self.root)
        # Changes the window size
        self.root.geometry(str(self.root.winfo_width() + 1) + "x" + str(self.root.winfo_height() + 1))
        # Returns to original size
        self.root.geometry(str(self.root.winfo_width() - 1) + "x" + str(self.root.winfo_height() - 1))


        self.root.attributes('-topmost', True)

        self.start_button_img = PhotoImage(file='gui/Start light.png')
        self.reset_button_img = PhotoImage(file='gui/Restart light.png')
        self.skip_button_img = PhotoImage(file='gui/Skip light.png')
        self.stop_button_img = PhotoImage(file='gui/Pouse light.png')
        self.finish_button_image = PhotoImage(file='gui/Finish light.png')
        self.open_config_button = PhotoImage(file='gui/Settings light.png')
        self.alt_stop_button_img = PhotoImage(file='gui/Start.png')

        self.s = ttk.Style()
        self.s.configure('TNotebook.Tab', font=('Ubuntu', 16))
        self.s.configure('TButton', font=('Ubuntu', 16))

        frame_bg = ttk.Style()
        frame_bg.configure('My.TFrame', background='#282828')
        frame_style = ttk.Style()
        frame_style.configure('TFrame', background='#282828')

        btn = tk.Button(self.root,
                        text="Click to open a new window",
                        command=self.open_configuration,
                        image=self.open_config_button,
                        bg='#282828', highlightthickness=0, borderwidth=0)
        btn.pack(anchor='se', padx=15, pady=10)

        self.tab1 = ttk.Frame(self.root, width=600, height=100, style='My.TFrame')
        self.tab1.pack()

        main_clock_style = ttk.Style()
        main_clock_style.configure("Purple.Label", foreground="#e6e6e6", background='#282828')
        pomodoros_count_style = ttk.Style()
        pomodoros_count_style.configure("Black.Label", foreground="#e6e6e6", background='#282828')

        # ENTRY TO CHANGE POMODORO TIME
        self.pomodoro_session_time = tk.StringVar()
        self.pomodoro_session_time.set('25')
        self.pomodoro_session_time.trace_add('write', self.change_pomodoro_timer)

        self.pomodoro_short_break_time = tk.StringVar()
        self.pomodoro_short_break_time.set('5')
        self.pomodoro_short_break_time.trace_add('write', self.change_pomodoro_timer)

        self.pomodoro_long_break_time = tk.StringVar()
        self.pomodoro_long_break_time.set('15')
        self.pomodoro_long_break_time.trace_add('write', self.change_pomodoro_timer)

        self.open_configuration()
        self.new_window.withdraw()

        canvas = tk.Canvas(self.tab1, bg="#282828", width=250, height=250, highlightthickness=0, background='#282828')
        canvas.pack()

        image = Image.open("gui/Clock frame_nobg.png")
        image = image.resize((250, 250), Image.ANTIALIAS)
        my_img = ImageTk.PhotoImage(image)

        label_frame_pomodoros = tk.LabelFrame(canvas, background='#282828', borderwidth=0)
        self.pomodoro_counter_label = ttk.Label(label_frame_pomodoros, text='#0', font=('Roboto', 16),
                                                style="Black.Label")
        self.pomodoro_counter_label.pack()

        label_frame = tk.LabelFrame(canvas, background='#282828', borderwidth=0)
        def_font = font.Font(family='Courier', size=48)
        self.pomodoro_timer_label = ttk.Label(label_frame, text='25:00', font=def_font, style="Purple.Label")
        self.pomodoro_timer_label.pack()

        # Add image to the Canvas Items
        canvas.create_image(0, 0, anchor='nw', image=my_img)
        canvas.create_window(125, 125, window=label_frame, anchor='center')
        canvas.create_window(125, 80, window=label_frame_pomodoros, anchor='center')

        # Get and display Habitica tasks
        self.variable = tk.StringVar(self.root)

        self.get_habitica_tasks()

        option_menu_style = ttk.Style()
        option_menu_style.configure('my.TMenubutton', foreground='#e6e6e6', font=('Roboto', 22), background='#282828')

        self.w = ttk.OptionMenu(self.tab1, self.variable, self.tasks_to_work_on[0], *self.tasks_to_work_on,
                                command=self.get_task_checklist, style='my.TMenubutton')

        self.w.pack(pady=20)

        self.checklist_box = ttk.Frame(self.tab1, style="TFrame")

        self.checkbox_pane = ScrollableFrame(self.tab1, bg='#282828')
        self.display_checklist()

        self.grid_layout = ttk.Frame(self.root, style="TFrame")
        self.grid_layout.pack(pady=10)

        self.start_button = tk.Button(self.grid_layout, text='Start', command=self.start_timer_thread,
                                      image=self.start_button_img, bd=0, background='#282828',
                                      activebackground='#282828')

        self.skip_button = tk.Button(self.grid_layout, text='Skip', command=self.skip_clock,
                                     image=self.skip_button_img, bd=0, background='#282828', activebackground='#282828')

        self.reset_button = tk.Button(self.grid_layout, text='Reset', command=self.reset_clock,
                                      image=self.reset_button_img, bd=0, background='#282828',
                                      activebackground='#282828')

        self.finish_button = tk.Button(self.grid_layout, text='Finish', command=self.finish_task,
                                       image=self.finish_button_image, bd=0, background='#282828',
                                       activebackground='#282828')

        self.stop_button = tk.Button(self.grid_layout, text='Pause', command=self.pause_clock,
                                     image=self.stop_button_img, bd=0, background='#282828', activebackground='#282828')

        self.start_button.grid(row=1, column=0)

        self.pomodoros = 0
        self.skipped = False
        self.stopped = False
        self.running = False
        self.paused = False

        self.root.mainloop()

    def open_configuration(self):
        """
        Opens configuration window to set Pomodoro and break times, initializes all elements there
        """
        self.new_window = tk.Toplevel(self.root)
        self.new_window.title("Configuration")
        self.new_window.geometry("300x210")
        self.new_window.config(bg="#282828")

        self.change_time_grid = ttk.Frame(self.new_window)
        self.change_time_grid.pack(pady=10)

        self.label_change_pomodoro_duration = tk.Label(self.change_time_grid,
                                                       text='Enter Pomodoro duration (in minutes)', height=1,
                                                       background='#282828', foreground='#e6e6e6')
        self.label_change_pomodoro_duration.grid(row=0, column=0)

        self.change_pomodoro_time = tk.Entry(self.change_time_grid, textvariable=self.pomodoro_session_time, width=2,
                                             font=("Roboto", 20, "bold"),
                                             bd=0, background='#282828', foreground='#e6e6e6')
        self.change_pomodoro_time.grid(row=0, column=1)

        self.label_change_short_break_duration = tk.Label(self.change_time_grid,
                                                          text='Enter Short Break duration (in minutes)', height=1,
                                                          background='#282828', foreground='#e6e6e6')
        self.label_change_short_break_duration.grid(row=1, column=0)

        self.change_short_break_time = tk.Entry(self.change_time_grid, textvariable=self.pomodoro_short_break_time,
                                                width=2,
                                                font=("Roboto", 20, "bold"),
                                                bd=0, background='#282828', foreground='#e6e6e6')
        self.change_short_break_time.grid(row=1, column=1)

        self.label_change_long_break_duration = tk.Label(self.change_time_grid,
                                                         text='Enter Long Break duration (in minutes)', height=1,
                                                         background='#282828', foreground='#e6e6e6')
        self.label_change_long_break_duration.grid(row=2, column=0)

        self.change_long_break_time = tk.Entry(self.change_time_grid, textvariable=self.pomodoro_long_break_time,
                                               width=2,
                                               font=("Roboto", 20, "bold"),
                                               bd=0, background='#282828', foreground='#e6e6e6')
        self.change_long_break_time.grid(row=2, column=1)

        B = tk.Button(self.new_window, text="Done", command=self.new_window.withdraw,
                      image=self.finish_button_image, bd=0, background='#282828', height=200)

        B.pack()

        self.new_window.attributes('-topmost', True)

    def change_pomodoro_timer(self, *args):
        """
        Allows to set Pomodoro duration
        :param args: values input in entry boxes
        """
        self.pomodoro_timer_label.config(text=f'{self.pomodoro_session_time.get()}:00')

    def wrong_pomodoro_timer_value(self):
        """
        Displays error box when wrong time value is input
        """
        messagebox.showerror('Wrong Timer Value', 'Error: Please enter proper value (in minutes)')

    def display_checklist(self):
        """
        Displays subtasks for a specific Habitica task
        """
        for widget in self.checkbox_pane.interior.winfo_children():
            widget.destroy()

        values = [key for key in self.tasks_checklists if key.startswith('DAILY')]
        if self.selected_task in values:

            for choice, x in zip(self.tasks_checklists[self.selected_task],
                                 range(0, len(self.tasks_checklists[self.selected_task]))):
                var = tk.StringVar(value=choice)
                cb = tk.Checkbutton(self.checkbox_pane.interior, var=var, text=choice,
                                    onvalue=choice, offvalue="",
                                    anchor="w", width=0, background='#282828', foreground='#e6e6e6',
                                    relief="flat", highlightthickness=0
                                    # image=PhotoImage(file='gui/Checkbox.png'),
                                    # selectimage=PhotoImage(file='gui/Full checkbox.png'),
                                    # indicatoron=False
                                    )

                # cb.pack(side="top", anchor="w")
                cb.grid(row=x, column=0, sticky='w')
        if self.selected_task in values and len(self.tasks_checklists[self.selected_task]) > 0:
            self.checkbox_pane.pack(expand="true", fill="both")
        else:
            self.checkbox_pane.pack_forget()

    def get_task_checklist(self, x):
        """
        Allows to choose a task from the list
        """
        self.selected_task = self.variable.get()

        self.display_checklist()

    def get_habitica_tasks(self):
        """
        Gets all tasks from Habitica from Daily and To-Do list categories
        """
        self.tasks_to_work_on = []
        self.tasks_ids = []
        self.tasks_checklists = {}
        types = ['dailys', 'todos']

        with open('api_keys.txt', 'r') as file:
            api_user, api_key = file.read().splitlines()

        self.headers = {'x-api-user': f'{api_user}',
                        'x-api-key': f'{api_key}'}

        for task_type in types:
            get_url = f'https://habitica.com/api/v3/tasks/user?type={task_type}'

            get_response = requests.get(get_url, headers=self.headers)
            r = get_response.json()

            for task in r['data']:
                if task_type == 'dailys':
                    items = []
                    if task['completed']:
                        continue
                    self.tasks_to_work_on.append(f'DAILY: {task["text"]}')

                    for item in task['checklist']:
                        items.append(item['text'])
                    self.tasks_checklists[f'DAILY: {task["text"]}'] = items

                else:
                    self.tasks_to_work_on.append(f'TODO: {task["text"]}')
                self.tasks_ids.append(task['id'])
        self.selected_task = self.tasks_to_work_on[0]

    def start_timer_thread(self):
        '''
        Starts timer in multithreaded environment
        '''
        if not self.running:
            t = threading.Thread(target=self.start_timer)
            t.start()
            self.running = True

    def start_timer(self, timer_id=1, paused=False):
        '''
        Starts specific timer (Pomodoro, short break, long break) according to the current
        :param timer_id: ID to verify which Pomodoro phase should be running right now
        '''
        pomodoro_val = self.change_pomodoro_time.get()
        short_break_val = self.change_short_break_time.get()
        long_break_val = self.change_long_break_time.get()
        self.change_pomodoro_timer()
        self.change_pomodoro_time.configure(state='disabled')
        self.change_short_break_time.configure(state='disabled')
        self.change_long_break_time.configure(state='disabled')
        self.w.configure(state='disabled')
        self.stopped = False
        self.skipped = False

        self.start_button.grid_forget()
        self.stop_button.grid(row=1, column=1)
        self.skip_button.grid(row=1, column=2)
        self.reset_button.grid(row=1, column=3)
        self.finish_button.grid(row=1, column=4)

        try:

            if timer_id == 1:
                # Increment the number to the current Pomodoro session
                self.pomodoros += 1
                self.pomodoro_counter_label.config(text=f'#{self.pomodoros}')

                if self.change_pomodoro_time.get() == '0':
                    raise ValueError
                if not paused:
                    self.full_seconds = float(60 * int(pomodoro_val))
                else:
                    self.full_seconds = self.full_seconds
                while self.full_seconds > 0 and not self.stopped:
                    minutes, seconds = divmod(self.full_seconds, 60)
                    if seconds < 10:
                        self.pomodoro_timer_label.configure(text=f'{round(int(minutes), 0)}:0{round(int(seconds), 0)}')
                    else:
                        self.pomodoro_timer_label.configure(text=f'{round(int(minutes), 0)}:{round(int(seconds), 0)}')
                    self.root.update()
                    if not self.paused:
                        time.sleep(0.1)
                        self.full_seconds -= 0.1
                if not self.stopped or self.skipped:

                    if self.pomodoros % 4 == 0:
                        self.start_timer(3)
                    else:
                        self.start_timer(2)

            elif timer_id == 2:
                self.full_seconds = float(60 * int(short_break_val))
                while self.full_seconds > 0 and not self.stopped:
                    minutes, seconds = divmod(self.full_seconds, 60)
                    if seconds < 10:
                        self.pomodoro_timer_label.configure(text=f'{round(int(minutes), 0)}:0{round(int(seconds), 0)}')
                    else:
                        self.pomodoro_timer_label.configure(text=f'{round(int(minutes), 0)}:{round(int(seconds), 0)}')
                    self.pomodoro_counter_label.configure(text='Short Break')
                    self.root.update()
                    time.sleep(0.1)
                    self.full_seconds -= 0.1
                if not self.stopped or self.skipped:
                    self.start_timer()
            elif timer_id == 3:
                self.full_seconds = float(60 * int(long_break_val))
                while self.full_seconds > 0 and not self.stopped:
                    minutes, seconds = divmod(self.full_seconds, 60)
                    self.pomodoro_timer_label.configure(text=f'{round(int(minutes), 0)}:{round(int(seconds), 0)}')
                    self.pomodoro_counter_label.configure(text='Long Break')
                    self.root.update()
                    time.sleep(0.1)
                    self.full_seconds -= 0.1
                if not self.stopped or self.skipped:
                    self.start_timer()
            else:
                print('Invalid timer ID')
        except Exception as e:
            print(e)
            self.wrong_pomodoro_timer_value()
            self.reset_clock()

    def reset_clock(self):
        '''
        Resets clock to the initial state
        '''
        self.change_pomodoro_time.configure(state='normal')
        self.change_short_break_time.configure(state='normal')
        self.change_long_break_time.configure(state='normal')
        self.stopped = True
        self.skipped = False
        self.pomodoros = 0
        self.pomodoro_timer_label.config(text=f'{self.change_pomodoro_time.get()}:00')
        self.pomodoro_counter_label.config(text='#0')
        self.running = False
        self.w.configure(state='enabled')

        self.start_button.grid(row=1, column=0)
        self.reset_button.grid_forget()
        self.skip_button.grid_forget()
        self.finish_button.grid_forget()
        self.stop_button.grid_forget()

    def skip_clock(self):
        '''
        Skips the clock to the next phase
        '''
        self.pomodoro_timer_label.config(text=f'{self.change_pomodoro_time.get()}:00')

        self.stopped = True
        self.skipped = True

    def pause_clock(self):
        '''
        Pauses/unpauses the clock
        '''
        self.paused = True if self.paused == False else False
        if self.paused:
            self.stop_button.configure(image=self.alt_stop_button_img)
        else:
            self.stop_button.configure(image=self.stop_button_img)
        if not self.paused:
            self.pomodoros -= 1
            self.start_timer(paused=True)

    def finish_task(self):
        '''
        Checks the task as completed on the Habitica site
        '''
        task_index = self.tasks_to_work_on.index(self.selected_task)
        task_id_to_finish = self.tasks_ids[task_index]

        get_url = f'https://habitica.com/api/v3/tasks/{task_id_to_finish}/score/up'
        with open('api_keys.txt', 'r') as file:
            api_user, api_key = file.read().splitlines()

        self.headers = {'x-api-user': f'{api_user}',
                        'x-api-key': f'{api_key}'}
        requests.post(get_url, headers=self.headers)

        self.reset_clock()
        self.get_habitica_tasks()
        self.selected_task = self.tasks_to_work_on[0]

        self.variable.set(self.tasks_to_work_on[0])
        self.w['menu'].delete(0, 'end')

        self.w.destroy()
        self.w = tk.OptionMenu(self.tab1, self.variable, self.tasks_to_work_on[0], *self.tasks_to_work_on,
                                command=self.get_task_checklist, style='my.TMenubutton')
        self.w.pack(pady=20)

        self.display_checklist()
