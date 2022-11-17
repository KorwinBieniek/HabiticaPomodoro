import time
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk, PhotoImage
from PIL import ImageTk, Image
import requests


class ScrollableFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        # create a canvas object and a vertical scrollbar for scrolling it
        self.vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        # if len(self.tasks_checklists[self.selected_task]) > 0:
        # print('hey')
        self.vscrollbar.pack(side='right', fill="y", expand="false")
        self.canvas = tk.Canvas(self,
                                bg='#fefaff', bd=0,
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

        self.bind('<Configure>', self.set_scrollregion)

    def set_scrollregion(self, event=None):
        """ Set the scroll region on the canvas"""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))


class PomodoroTimer:

    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry('600x550')
        self.root.title('Pomodoro Timer Habitica')
        self.root.tk.call('wm', 'iconphoto', self.root._w, PhotoImage(file='gui/pomodoro.png'))
        self.root.config(bg="#fefaff")

        self.start_button_img = PhotoImage(file='gui/start.png')
        self.reset_button_img = PhotoImage(file='gui/reset.png')
        self.skip_button_img = PhotoImage(file='gui/skip.png')
        self.stop_button_img = PhotoImage(file='gui/stop.png')
        self.finish_button_image = PhotoImage(file='gui/finish.png')

        self.s = ttk.Style()
        self.s.configure('TNotebook.Tab', font=('Ubuntu', 16))
        self.s.configure('TButton', font=('Ubuntu', 16))

        # self.tabs = ttk.Notebook(self.root)
        # self.tabs.pack(fill='both', pady=10, expand=True)

        frame_bg = ttk.Style()
        frame_bg.configure('My.TFrame', background='#fefaff')
        frame_style = ttk.Style()
        frame_style.configure('TFrame', background='#fefaff')
        self.tab1 = ttk.Frame(self.root, width=600, height=100, style='My.TFrame')
        self.tab1.pack()
        # self.tab2 = ttk.Frame(self.tabs, width=600, height=100, style='My.TFrame')
        # self.tab3 = ttk.Frame(self.tabs, width=600, height=100, style='My.TFrame')
        main_clock_style = ttk.Style()
        main_clock_style.configure("Purple.Label", foreground="#7712a8", background='#fefaff')
        pomodoros_count_style = ttk.Style()
        pomodoros_count_style.configure("Black.Label", foreground="black", background='#fefaff')

        # ENTRY TO CHANGE POMODORO TIME
        self.var = tk.StringVar()
        self.var.set('25')
        self.var.trace_add('write', self.change_pomodoro_timer)

        self.change_time_grid = ttk.Frame(self.tab1)
        # self.change_time_grid.pack(pady=10)

        labelDir = tk.Label(self.change_time_grid, text='Enter Pomodoro duration (in minutes)', height=1)
        # labelDir.pack(side=tk.LEFT, padx=5)

        self.change_time = ttk.Entry(self.change_time_grid, textvariable=self.var, width=2, font=("Roboto", 20, "bold"))
        self.change_time.pack(side=tk.LEFT)

        # self.pomodoro_counter_label.grid(row=2, column=0, columnspan=4, pady=10)
        canvas = tk.Canvas(self.tab1, bg="white", width=250, height=250, highlightthickness=0, background='#fefaff')
        canvas.pack()
        # img = (Image.open("gui/rsz_circle_-_copy.png"))

        # Resize the Image using resize method
        # new_image = PhotoImage(file="gui/rsz_circle_-_copy.png")
        image = Image.open("gui/circle2.png")
        # The (450, 350) is (height, width)
        # image = image.resize((250, 250), Image.ANTIALIAS)
        my_img = ImageTk.PhotoImage(image)

        label_frame_pomodoros = tk.LabelFrame(canvas, background='#fefaff', borderwidth=0)
        self.pomodoro_counter_label = ttk.Label(label_frame_pomodoros, text='#0', font=('Roboto', 16),
                                                style="Black.Label")
        self.pomodoro_counter_label.pack()

        label_frame = tk.LabelFrame(canvas, background='#fefaff', borderwidth=0)
        self.pomodoro_timer_label = ttk.Label(label_frame, text='25:00', font=('Roboto', 48), style="Purple.Label")
        # self.pomodoro_timer_label.place(x = 100, y = 50)
        self.pomodoro_timer_label.pack()

        # Add image to the Canvas Items
        canvas.create_image(0, 0, anchor='nw', image=my_img)
        canvas.create_window(125, 125, window=label_frame, anchor='center')
        canvas.create_window(125, 80, window=label_frame_pomodoros, anchor='center')

        # self.short_break_timer_label = ttk.Label(self.tab2, text='05:00', font=('Roboto', 48))
        # self.short_break_timer_label.pack(pady=20)

        # self.long_break_timer_label = ttk.Label(self.tab3, text='15:00', font=('Roboto', 48))
        # self.long_break_timer_label.pack(pady=20)

        # Get and display Habitica tasks
        self.variable = tk.StringVar(self.root)

        self.get_habitica_tasks()

        self.w = ttk.OptionMenu(self.tab1, self.variable, self.tasks_to_work_on[0], *self.tasks_to_work_on,
                                command=self.callback, style='my.TMenubutton')
        option_menu_style = ttk.Style()
        option_menu_style.configure('my.TMenubutton', font=('Roboto', 22), background='#fefaff')
        self.w.pack(pady=20)

        self.checklist_box = ttk.Frame(self.tab1, style="TFrame")
        # self.display_checklist()
        # self.checklist_box.pack()

        self.checkbox_pane = ScrollableFrame(self.tab1, bg='#fefaff')
        self.display_checklist()
        # if len(self.tasks_checklists[self.selected_task]) > 0:
        print(len(self.tasks_checklists[self.selected_task]))

        self.grid_layout = ttk.Frame(self.root, style="TFrame")
        self.grid_layout.pack(pady=10)

        self.start_button = tk.Button(self.grid_layout, text='Start', command=self.start_timer_thread,
                                      image=self.start_button_img, bd=0, background='#fefaff')

        self.skip_button = tk.Button(self.grid_layout, text='Skip', command=self.skip_clock,
                                     image=self.skip_button_img, bd=0, background='#fefaff')

        self.reset_button = tk.Button(self.grid_layout, text='Reset', command=self.reset_clock,
                                      image=self.reset_button_img, bd=0, background='#fefaff')

        self.finish_button = tk.Button(self.grid_layout, text='Finish', command=self.finish_task,
                                       image=self.finish_button_image, bd=0, background='#fefaff')

        self.start_button.grid(row=1, column=0)

        self.pomodoros = 0
        self.skipped = False
        self.stopped = False
        self.running = False

        self.root.attributes('-topmost', True)
        self.root.mainloop()

    def change_pomodoro_timer(self, *args):
        self.pomodoro_timer_label.config(text=f'{self.var.get()}:00')

    def wrong_pomodoro_timer_value(self):
        messagebox.showerror('Wrong Timer Value', 'Error: Please enter proper value (in minutes)')

    def display_checklist(self):

        for widget in self.checkbox_pane.interior.winfo_children():
            widget.destroy()

        values = [key for key in self.tasks_checklists if key.startswith('DAILY')]
        if self.selected_task in values:

            # value = self.selected_task[7:] if self.selected_task.startswith('DAILY') else self.selected_task[6:]
            # for x in range(1, 20):
            #     tk.Checkbutton(self.checkbox_pane.interior, text="hello world! %s" % x).grid(row=x, column=0)

            for choice, x in zip(self.tasks_checklists[self.selected_task],
                                 range(0, len(self.tasks_checklists[self.selected_task]))):
                var = tk.StringVar(value=choice)
                cb = tk.Checkbutton(self.checkbox_pane.interior, var=var, text=choice,
                                    onvalue=choice, offvalue="",
                                    anchor="w", width=0, background='#fefaff',
                                    relief="flat", highlightthickness=0
                                    )
                # cb.pack(side="top", anchor="w")
                cb.grid(row=x, column=0, sticky='w')
        if len(self.tasks_checklists[self.selected_task]) > 0:
            self.checkbox_pane.pack(expand="true", fill="both")
        else:
            self.checkbox_pane.pack_forget()

    def callback(self, selection):
        self.selected_task = self.variable.get()

        self.display_checklist()

    def app_on_top(self):
        self.root.lift()
        self.root.after(2000, self.app_on_top)

    def get_habitica_tasks(self):
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
        if not self.running:
            t = threading.Thread(target=self.start_timer)
            t.start()
            self.running = True

    def start_timer(self, timer_id=1):
        self.change_time.configure(state='disabled')
        self.w.configure(state='disabled')
        self.stopped = False
        self.skipped = False
        # timer_id = self.tabs.index(self.tabs.select()) + 1

        self.start_button.grid_forget()
        self.skip_button.grid(row=1, column=1)
        self.reset_button.grid(row=1, column=2)
        self.finish_button.grid(row=1, column=3)

        try:

            if timer_id == 1:
                # Increment the number to the current Pomodoro session
                self.pomodoros += 1
                self.pomodoro_counter_label.config(text=f'#{self.pomodoros}')

                if self.change_time.get() == '0':
                    raise ValueError
                full_seconds = float(60 * int(self.change_time.get()))
                while full_seconds > 0 and not self.stopped:
                    minutes, seconds = divmod(full_seconds, 60)
                    self.pomodoro_timer_label.configure(text=f'{round(int(minutes), 0)}:{round(int(seconds), 0)}')
                    self.root.update()
                    time.sleep(0.1)
                    full_seconds -= 0.1
                if not self.stopped or self.skipped:

                    if self.pomodoros % 4 == 0:
                        # self.tabs.select(2)
                        self.start_timer(3)
                    # else:
                    # self.tabs.select(1)
                    self.start_timer(2)

            elif timer_id == 2:
                full_seconds = float(60 * 5)
                while full_seconds > 0 and not self.stopped:
                    minutes, seconds = divmod(full_seconds, 60)
                    self.pomodoro_timer_label.configure(text=f'{round(int(minutes), 0)}:{round(int(seconds), 0)}')
                    self.pomodoro_counter_label.configure(text='Short Break')
                    self.root.update()
                    time.sleep(0.1)
                    full_seconds -= 0.1
                if not self.stopped or self.skipped:
                    self.tabs.select(0)
                    self.start_timer()
            elif timer_id == 3:
                full_seconds = float(60 * 15)
                while full_seconds > 0 and not self.stopped:
                    minutes, seconds = divmod(full_seconds, 60)
                    self.pomodoro_timer_label.configure(text=f'{round(int(minutes), 0)}:{round(int(seconds), 0)}')
                    self.pomodoro_counter_label.configure(text='Long Break')
                    self.root.update()
                    time.sleep(0.1)
                    full_seconds -= 0.1
                if not self.stopped or self.skipped:
                    self.tabs.select(0)
                    self.start_timer()
            else:
                print('Invalid timer ID')
        except:
            self.wrong_pomodoro_timer_value()
            self.reset_clock()

    def reset_clock(self):
        self.change_time.configure(state='enabled')
        self.stopped = True
        self.skipped = False
        self.pomodoros = 0
        self.pomodoro_timer_label.config(text=f'{self.change_time.get()}:00')
        # self.short_break_timer_label.config(text='05:00')
        # self.long_break_timer_label.config(text='15:00')
        self.pomodoro_counter_label.config(text='#0')
        self.running = False
        self.w.configure(state='enabled')

        self.start_button.grid(row=1, column=0)
        self.reset_button.grid_forget()
        self.skip_button.grid_forget()
        self.finish_button.grid_forget()

    def skip_clock(self):
        # current_tab = self.tabs.index((self.tabs.select()))
        # if current_tab == 0:
        self.pomodoro_timer_label.config(text=f'{self.change_time.get()}:00')
        # elif current_tab == 1:
        # self.short_break_timer_label.config(text='05:00')
        # elif current_tab == 2:
        # self.long_break_timer_label.config(text='15:00')

        self.stopped = True
        self.skipped = True

    def finish_task(self):
        task_index = self.tasks_to_work_on.index(self.selected_task)
        task_id_to_finish = self.tasks_ids[task_index]

        get_url = f'https://habitica.com/api/v3/tasks/{task_id_to_finish}/score/up'
        headers = {'x-api-user': f'6fb0bdb9-2db9-4bbb-be77-b55a9ad3d339',
                   'x-api-key': f'2b4d0dbf-99a9-4436-8045-4f081a62f002'}
        requests.post(get_url, headers=self.headers)

        self.reset_clock()
        self.get_habitica_tasks()
        self.selected_task = self.tasks_to_work_on[0]

        self.variable.set(self.tasks_to_work_on[0])
        self.w['menu'].delete(0, 'end')

        self.w.destroy()
        self.w = ttk.OptionMenu(self.tab1, self.variable, self.tasks_to_work_on[0], *self.tasks_to_work_on,
                                command=self.callback, style='my.TMenubutton')
        self.w.pack(pady=20)

        self.display_checklist()


PomodoroTimer()
