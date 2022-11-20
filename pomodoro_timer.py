import time
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk, PhotoImage
from PIL import ImageTk, Image
import tkinter.font as font
import requests
from scrollable_frame import ScrollableFrame


class PomodoroTimer:

    def move_app(self, e):
        self.root.geometry(f'+{e.x_root}+{e.y_root}')

    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry('600x600')
        self.root.title('Pomodoro Timer Habitica')
        self.root.tk.call('wm', 'iconphoto', self.root._w, PhotoImage(file='gui/pomodoro.png'))
        self.root.config(bg="#282828")
        # self.root.overrideredirect(1)
        # self.root.wm_attributes("-transparentcolor", "grey")
        # self.root.bind("<B1-Motion>", self.move_app)

        self.root.attributes('-topmost', True)

        # frame_photo = PhotoImage(file='gui/Pomodoro frame dark.png')
        # frame_label = tk.Label(self.root, border=0, bg='grey', image=frame_photo)
        # frame_label.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.start_button_img = PhotoImage(file='gui/Start light.png')
        self.reset_button_img = PhotoImage(file='gui/Restart light.png')
        self.skip_button_img = PhotoImage(file='gui/Skip light.png')
        self.stop_button_img = PhotoImage(file='gui/Pouse light.png')
        self.finish_button_image = PhotoImage(file='gui/Finish light.png')
        self.open_config_button = PhotoImage(file='gui/Settings light.png')

        self.s = ttk.Style()
        self.s.configure('TNotebook.Tab', font=('Ubuntu', 16))
        self.s.configure('TButton', font=('Ubuntu', 16))

        # self.tabs = ttk.Notebook(self.root)
        # self.tabs.pack(fill='both', pady=10, expand=True)

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
        # self.tab1.bind("<B1-Motion>", self.move_app)

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

        # self.pomodoro_counter_label.grid(row=2, column=0, columnspan=4, pady=10)
        canvas = tk.Canvas(self.tab1, bg="#282828", width=250, height=250, highlightthickness=0, background='#282828')
        canvas.pack()
        # img = (Image.open("gui/rsz_circle_-_copy.png"))

        # Resize the Image using resize method
        # new_image = PhotoImage(file="gui/rsz_circle_-_copy.png")
        image = Image.open("gui/Clock frame_nobg.png")
        # The (450, 350) is (height, width)
        image = image.resize((250, 250), Image.ANTIALIAS)
        my_img = ImageTk.PhotoImage(image)

        label_frame_pomodoros = tk.LabelFrame(canvas, background='#282828', borderwidth=0)
        self.pomodoro_counter_label = ttk.Label(label_frame_pomodoros, text='#0', font=('Roboto', 16),
                                                style="Black.Label")
        self.pomodoro_counter_label.pack()

        label_frame = tk.LabelFrame(canvas, background='#282828', borderwidth=0)
        def_font = font.Font(family='Courier', size=48)
        self.pomodoro_timer_label = ttk.Label(label_frame, text='25:00', font=def_font, style="Purple.Label")
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

        option_menu_style = ttk.Style()
        option_menu_style.configure('my.TMenubutton', foreground='#e6e6e6', font=('Roboto', 22), background='#282828')

        self.w = ttk.OptionMenu(self.tab1, self.variable, self.tasks_to_work_on[0], *self.tasks_to_work_on,
                                command=self.callback, style='my.TMenubutton')

        self.w.pack(pady=20)

        self.checklist_box = ttk.Frame(self.tab1, style="TFrame")
        # self.display_checklist()
        # self.checklist_box.pack()

        self.checkbox_pane = ScrollableFrame(self.tab1, bg='#282828')
        self.display_checklist()
        # if len(self.tasks_checklists[self.selected_task]) > 0:

        self.grid_layout = ttk.Frame(self.root, style="TFrame")
        self.grid_layout.pack(pady=10)

        self.start_button = tk.Button(self.grid_layout, text='Start', command=self.start_timer_thread,
                                      image=self.start_button_img, bd=0, background='#282828')

        self.skip_button = tk.Button(self.grid_layout, text='Skip', command=self.skip_clock,
                                     image=self.skip_button_img, bd=0, background='#282828')

        self.reset_button = tk.Button(self.grid_layout, text='Reset', command=self.reset_clock,
                                      image=self.reset_button_img, bd=0, background='#282828')

        self.finish_button = tk.Button(self.grid_layout, text='Finish', command=self.finish_task,
                                       image=self.finish_button_image, bd=0, background='#282828')

        self.stop_button = tk.Button(self.grid_layout, text='Finish',
                                     image=self.stop_button_img, bd=0, background='#282828')

        self.start_button.grid(row=1, column=0)

        self.pomodoros = 0
        self.skipped = False
        self.stopped = False
        self.running = False

        self.root.mainloop()

    def open_configuration(self):

        self.new_window = tk.Toplevel(self.root)
        self.new_window.title("Configuration")
        self.new_window.geometry("300x210")
        self.new_window.config(bg="#282828")
        # self.new_window.overrideredirect(1)

        self.change_time_grid = ttk.Frame(self.new_window)
        self.change_time_grid.pack(pady=10)

        # label_change_pomodoro_duration.pack(side=tk.LEFT, padx=5)
        self.label_change_pomodoro_duration = tk.Label(self.change_time_grid,
                                                       text='Enter Pomodoro duration (in minutes)', height=1,
                                                       background='#282828', foreground='#e6e6e6')
        self.label_change_pomodoro_duration.grid(row=0, column=0)

        # self.change_pomodoro_time.pack(side=tk.LEFT)
        self.change_pomodoro_time = tk.Entry(self.change_time_grid, textvariable=self.pomodoro_session_time, width=2,
                                             font=("Roboto", 20, "bold"),
                                             bd=0, background='#282828', foreground='#e6e6e6')
        self.change_pomodoro_time.grid(row=0, column=1)

        # label_change_pomodoro_duration.pack(side=tk.LEFT, padx=5)
        self.label_change_short_break_duration = tk.Label(self.change_time_grid,
                                                          text='Enter Short Break duration (in minutes)', height=1,
                                                          background='#282828', foreground='#e6e6e6')
        self.label_change_short_break_duration.grid(row=1, column=0)

        # self.change_short_break_time.pack(side=tk.LEFT)
        self.change_short_break_time = tk.Entry(self.change_time_grid, textvariable=self.pomodoro_short_break_time,
                                                width=2,
                                                font=("Roboto", 20, "bold"),
                                                bd=0, background='#282828', foreground='#e6e6e6')
        self.change_short_break_time.grid(row=1, column=1)

        # label_change_pomodoro_duration.pack(side=tk.LEFT, padx=5)
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
        self.pomodoro_timer_label.config(text=f'{self.pomodoro_session_time.get()}:00')

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
                                    anchor="w", width=0, background='#282828', foreground='#e6e6e6',
                                    relief="flat", highlightthickness=0
                                    # image=PhotoImage(file='gui/Checkbox.png'),
                                    # selectimage=PhotoImage(file='gui/Full checkbox.png'),
                                    # indicatoron=False
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
        self.change_pomodoro_timer()
        self.change_pomodoro_time.configure(state='disabled')
        self.change_short_break_time.configure(state='disabled')
        self.change_long_break_time.configure(state='disabled')
        self.w.configure(state='disabled')
        self.stopped = False
        self.skipped = False
        # timer_id = self.tabs.index(self.tabs.select()) + 1

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
                full_seconds = float(60 * int(self.change_pomodoro_time.get()))
                while full_seconds > 0 and not self.stopped:
                    minutes, seconds = divmod(full_seconds, 60)
                    if seconds < 10:
                        self.pomodoro_timer_label.configure(text=f'{round(int(minutes), 0)}:0{round(int(seconds), 0)}')
                    else:
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
                full_seconds = float(60 * int(self.change_short_break_time.get()))
                while full_seconds > 0 and not self.stopped:
                    minutes, seconds = divmod(full_seconds, 60)
                    if seconds < 10:
                        self.pomodoro_timer_label.configure(text=f'{round(int(minutes), 0)}:0{round(int(seconds), 0)}')
                    else:
                        self.pomodoro_timer_label.configure(text=f'{round(int(minutes), 0)}:{round(int(seconds), 0)}')
                    self.pomodoro_counter_label.configure(text='Short Break')
                    self.root.update()
                    time.sleep(0.1)
                    full_seconds -= 0.1
                if not self.stopped or self.skipped:
                    # self.tabs.select(0)
                    self.start_timer()
            elif timer_id == 3:
                full_seconds = float(60 * int(self.change_long_break_time.get()))
                while full_seconds > 0 and not self.stopped:
                    minutes, seconds = divmod(full_seconds, 60)
                    self.pomodoro_timer_label.configure(text=f'{round(int(minutes), 0)}:{round(int(seconds), 0)}')
                    self.pomodoro_counter_label.configure(text='Long Break')
                    self.root.update()
                    time.sleep(0.1)
                    full_seconds -= 0.1
                if not self.stopped or self.skipped:
                    # self.tabs.select(0)
                    self.start_timer()
            else:
                print('Invalid timer ID')
        except Exception as e:
            print(e)
            self.wrong_pomodoro_timer_value()
            self.reset_clock()

    def reset_clock(self):
        self.change_pomodoro_time.configure(state='normal')
        self.change_short_break_time.configure(state='normal')
        self.change_long_break_time.configure(state='normal')
        self.stopped = True
        self.skipped = False
        self.pomodoros = 0
        self.pomodoro_timer_label.config(text=f'{self.change_pomodoro_time.get()}:00')
        # self.short_break_timer_label.config(text='05:00')
        # self.long_break_timer_label.config(text='15:00')
        self.pomodoro_counter_label.config(text='#0')
        self.running = False
        self.w.configure(state='enabled')

        self.start_button.grid(row=1, column=0)
        self.reset_button.grid_forget()
        self.skip_button.grid_forget()
        self.finish_button.grid_forget()
        self.stop_button.grid_forget()

    def skip_clock(self):
        # current_tab = self.tabs.index((self.tabs.select()))
        # if current_tab == 0:
        self.pomodoro_timer_label.config(text=f'{self.change_pomodoro_time.get()}:00')
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
