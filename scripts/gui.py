import tkinter as tk
from ctypes import windll
from tkinter import Tk, END
import tkinter.ttk as ttk
from scripts import connection

windll.shcore.SetProcessDpiAwareness(1)


class UI:
    def __init__(self):
        self.connections = {
            'Source': None,
            'Destination': None
        }
        self.stored_credentials = {
            'Source': None,
            'Destination': None
        }
        self.window = Tk()
        self.window.title('dbCopy')
        self.style = ttk.Style()
        self._create_styles()
        self._pack_frames()
        self.database_table('Source')
        self.database_table('Destination')
        self.query_box()

    def database_table(self, title):
        def return_connection_creds():
            return {
                'host': host_var.get(),
                'port': port_var.get(),
                'user': user_var.get(),
                'pass': pass_var.get(),
                'db': db_var.get()
            }

        def new_connection():
            creds = return_connection_creds()
            connect(creds)
            print(creds)

        def refresh_connection():
            creds = self.stored_credentials[title]
            if creds is not None:
                connect(creds)
            else:
                print('No connection to refresh')

        def connect(creds):
            # close old connection if it exists
            if self.connections[title] is not None:
                connection.close_connection(self.connections[title])
            # try to connect
            db_connection = connection.create_connection(creds)
            # handle connection attempt
            if db_connection['response']:
                self.connections[title] = db_connection['payload']
                connection_status.configure(text='Connected')
                self.stored_credentials[title] = creds
            else:
                self.connections[title] = None
                connection_status.configure(text='Disconnected')
                print(db_connection['payload'])

        def disconnect():
            # close connection if it exists
            if self.connections[title] is not None:
                connection.close_connection(self.connections[title])
                connection_status.configure(text='Disconnected')

        if title == 'Source':
            column = 1
        else:
            column = 3

        padding = ttk.Frame(self.database_frame, style='card.TFrame')
        padding.grid(row=0, column=column)
        db_table_frame = ttk.Frame(padding, style='card.TFrame')
        db_table_frame.columnconfigure(1, weight=1)
        db_table_frame.pack(side='left', fill='both', padx=50)

        ttk.Label(db_table_frame, text=title, style="title.TLabel").grid(column=0, row=0, columnspan=2, pady=50)

        ttk.Label(db_table_frame, text='Host').grid(column=0, row=1, sticky='nsew', padx=5, pady=(0, 5))
        host_var = tk.StringVar()
        ttk.Entry(db_table_frame, textvariable=host_var, style="EntryStyle.TEntry").grid(
            column=1, row=1, sticky='nsew', padx=5, pady=(0, 5))

        ttk.Label(db_table_frame, text='Port').grid(column=0, row=2, sticky='nsew', padx=5, pady=(0, 5))
        port_var = tk.StringVar()
        ttk.Entry(db_table_frame, textvariable=port_var).grid(column=1, row=2, sticky='nsew', padx=5, pady=(0, 5))

        ttk.Label(db_table_frame, text='User').grid(column=0, row=3, sticky='nsew', padx=5, pady=(0, 5))
        user_var = tk.StringVar()
        ttk.Entry(db_table_frame, textvariable=user_var).grid(column=1, row=3, sticky='nsew', padx=5, pady=(0, 5))

        ttk.Label(db_table_frame, text='Pass').grid(column=0, row=4, sticky='nsew', padx=5, pady=(0, 5))
        pass_var = tk.StringVar()
        ttk.Entry(db_table_frame, textvariable=pass_var).grid(column=1, row=4, sticky='nsew', padx=5, pady=(0, 5))

        ttk.Label(db_table_frame, text='DB').grid(column=0, row=5, sticky='nsew', padx=5)
        db_var = tk.StringVar()
        ttk.Entry(db_table_frame, textvariable=db_var).grid(column=1, row=5, sticky='nsew', padx=5)

        button_frame = ttk.Frame(db_table_frame, style='card.TFrame')
        button_frame.grid(column=0, row=6, columnspan=2, pady=50)
        reconnect_button = ttk.Button(button_frame, text='connect', command=new_connection)
        reconnect_button.grid(column=0, row=0)
        connect_button = ttk.Button(button_frame, text='reconnect', command=refresh_connection)
        connect_button.grid(column=1, row=0)
        disconnect_button = ttk.Button(button_frame, text='disconnect', command=disconnect)
        disconnect_button.grid(column=2, row=0)
        connection_status = ttk.Label(button_frame, text='Disconnected')
        connection_status.grid(column=0, row=1, columnspan=3, pady=(50, 0))

    def query_box(self):
        def return_query():
            print(query.get("1.0", END))
            print(self.connections)

        ttk.Label(self.query_frame, text='Query', style="title.TLabel").pack(fill='y', pady=50)
        query = tk.Text(self.query_frame)
        query.pack(padx=50)
        ttk.Button(self.query_frame, text='TRANSFER', command=return_query).pack(pady=50)

    def _create_styles(self):
        primary = "#2C3333"
        secondary = '#395B64'
        tert = '#A5C9CA'
        quart = '#E7F6F2'
        self.window.configure(background=primary)
        self.style.configure("TFrame", background=primary)
        self.style.configure("TButton", background=secondary, foreground=primary)
        self.style.configure("card.TFrame", background=secondary)
        self.style.configure("title.TLabel", background=secondary, foreground=tert, font=('Poplar Std', 18))
        self.style.configure("TLabel", background=secondary, foreground=tert, font=('Poplar Std', 12), anchor=tk.E)
        self.style.configure("TEntry", background=secondary, foreground=tert, fieldbackgroud=primary)
        self.style.element_create("plain.field", "from", "clam")
        self.style.layout("TEntry",
                          [('Entry.plain.field', {'children': [(
                              'Entry.background', {'children': [(
                                  'Entry.padding', {'children': [(
                                      'Entry.textarea', {'sticky': 'nswe'})],
                                      'sticky': 'nswe'})], 'sticky': 'nswe'})],
                              'border': '2', 'sticky': 'nswe'})])
        self.style.configure("TEntry",
                             foreground=quart,
                             fieldbackground=secondary,
                             insertcolor=quart)

    def _pack_frames(self):
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.database_frame = ttk.Frame(self.window, style="TFrame")
        self.database_frame.columnconfigure(0, weight=1)
        self.database_frame.columnconfigure(2, weight=1)
        self.database_frame.columnconfigure(4, weight=1)
        self.database_frame.grid(row=1, column=1, sticky='nsew', padx=50, pady=(50, 0))

        self.query_frame = ttk.Frame(self.window, style="card.TFrame")
        self.query_frame.grid(row=3, column=1, sticky='nsew', padx=50, pady=50)
