import time
import threading
import tkinter as tk
from tkinter import ttk, PhotoImage
import requests


class PomodoroTimer:

    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry('600x600')
        self.root.title('Pomodoro Timer Habitica')
        self.root.tk.call('wm', 'iconphoto', self.root._w, PhotoImage(file='pomodoro.png'))

        self.s = ttk.Style()
        self.s.configure('TNotebook.Tab', font=('Ubuntu', 16))
        self.s.configure('TButton', font=('Ubuntu', 16))

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill='both', pady=10, expand=True)

        self.tab1 = ttk.Frame(self.tabs, width=600, height=100)
        self.tab2 = ttk.Frame(self.tabs, width=600, height=100)
        self.tab3 = ttk.Frame(self.tabs, width=600, height=100)

        self.pomodoro_timer_label = ttk.Label(self.tab1, text='25:00', font=('Ubuntu', 48))
        self.pomodoro_timer_label.pack(pady=20)

        self.short_break_timer_label = ttk.Label(self.tab2, text='05:00', font=('Ubuntu', 48))
        self.short_break_timer_label.pack(pady=20)

        self.long_break_timer_label = ttk.Label(self.tab3, text='15:00', font=('Ubuntu', 48))
        self.long_break_timer_label.pack(pady=20)

        self.checklist_label = ttk.Label(self.tab1, text='Checklist', font=('Ubuntu', 22))
        self.checklist_label.pack(pady=20)



        # Get and display Habitica tasks
        self.variable = tk.StringVar(self.root)

        self.get_habitica_tasks()

        self.checklist_box = tk.Frame(self.tab1)
        self.display_checklist()
        self.checklist_box.pack()
        # self.w = ttk.OptionMenu(self.root, self.variable, self.tasks_to_work_on[0], *self.tasks_to_work_on,
        #                         command=self.callback)
        # self.w.pack()



        self.tabs.add(self.tab1, text='Pomodoro')
        self.tabs.add(self.tab2, text='Short Break')
        self.tabs.add(self.tab3, text='Long Break')

        self.grid_layout = ttk.Frame(self.root)
        self.grid_layout.pack(pady=10)

        self.w = ttk.OptionMenu(self.grid_layout, self.variable, self.tasks_to_work_on[0], *self.tasks_to_work_on,
                                command=self.callback)
        self.w.grid(row=0, column=0, columnspan=4, pady=10)

        self.start_button = ttk.Button(self.grid_layout, text='Start', command=self.start_timer_thread)
        self.start_button.grid(row=1, column=0)

        self.skip_button = ttk.Button(self.grid_layout, text='Skip', command=self.skip_clock)
        self.skip_button.grid(row=1, column=1)

        self.reset_button = ttk.Button(self.grid_layout, text='Reset', command=self.reset_clock)
        self.reset_button.grid(row=1, column=2)

        self.finish_button = ttk.Button(self.grid_layout, text='Finish', command=self.finish_task)
        self.finish_button.grid(row=1, column=3)

        self.pomodoro_counter_label = ttk.Label(self.grid_layout, text='Pomodoros: 0', font=('Ubuntu', 16))
        self.pomodoro_counter_label.grid(row=2, column=0, columnspan=4, pady=10)

        self.pomodoros = 0
        self.skipped = False
        self.stopped = False
        self.running = False

        self.root.mainloop()

    def display_checklist(self):

        for widget in self.checklist_box.winfo_children():
            widget.destroy()

        values = [key for key in self.tasks_checklists if key.startswith('DAILY') ]
        if self.selected_task in values:
        #value = self.selected_task[7:] if self.selected_task.startswith('DAILY') else self.selected_task[6:]

            for choice in self.tasks_checklists[self.selected_task]:
                var = tk.StringVar(value=choice)
                cb = tk.Checkbutton(self.checklist_box, var=var, text=choice,
                                    onvalue=choice, offvalue="",
                                    anchor="w", width=0, background=self.checklist_box.cget("background"),
                                    relief="flat", highlightthickness=0
                                    )
                cb.pack(side="top", fill="x", anchor="w")
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

    def start_timer(self):
        self.w.configure(state='disabled')
        self.stopped = False
        self.skipped = False
        timer_id = self.tabs.index(self.tabs.select()) + 1

        if timer_id == 1:
            full_seconds = 60 * 25
            while full_seconds > 0 and not self.stopped:
                minutes, seconds = divmod(full_seconds, 60)
                self.pomodoro_timer_label.configure(text=f'{minutes:02d}:{seconds:02d}')
                self.root.update()
                time.sleep(1)
                full_seconds -= 1
            if not self.stopped or self.skipped:
                self.pomodoros += 1
                self.pomodoro_counter_label.config(text=f'Pomodoros: {self.pomodoros}')
                if self.pomodoros % 4 == 0:
                    self.tabs.select(2)
                    self.start_timer()
                else:
                    self.tabs.select(1)
                self.start_timer()

        elif timer_id == 2:
            full_seconds = 60 * 5
            while full_seconds > 0 and not self.stopped:
                minutes, seconds = divmod(full_seconds, 60)
                self.short_break_timer_label.configure(text=f'{minutes:02d}:{seconds:02d}')
                self.root.update()
                time.sleep(1)
                full_seconds -= 1
            if not self.stopped or self.skipped:
                self.tabs.select(0)
                self.start_timer()
        elif timer_id == 3:
            full_seconds = 60 * 15
            while full_seconds > 0 and not self.stopped:
                minutes, seconds = divmod(full_seconds, 60)
                self.long_break_timer_label.configure(text=f'{minutes:02d}:{seconds:02d}')
                self.root.update()
                time.sleep(1)
                full_seconds -= 1
            if not self.stopped or self.skipped:
                self.tabs.select(0)
                self.start_timer()
        else:
            print('Invalid timer ID')

    def reset_clock(self):
        self.stopped = True
        self.skipped = False
        self.pomodoros = 0
        self.pomodoro_timer_label.config(text='25:00')
        self.short_break_timer_label.config(text='05:00')
        self.long_break_timer_label.config(text='15:00')
        self.pomodoro_counter_label.config(text='Pomodoros: 0')
        self.running = False
        self.w.configure(state='enabled')

    def skip_clock(self):
        current_tab = self.tabs.index((self.tabs.select()))
        if current_tab == 0:
            self.pomodoro_timer_label.config(text='25:00')
        elif current_tab == 1:
            self.short_break_timer_label.config(text='05:00')
        elif current_tab == 2:
            self.long_break_timer_label.config(text='15:00')

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
        self.w = ttk.OptionMenu(self.grid_layout, self.variable, self.tasks_to_work_on[0], *self.tasks_to_work_on,
                                command=self.callback)
        self.w.grid(row=0, column=0, columnspan=4, pady=10)

        self.display_checklist()


PomodoroTimer()
