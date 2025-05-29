import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import json
import os
from datetime import datetime
import threading
import time
import re
from typing import List, Dict, Any
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class AdvancedCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Scientific Calculator Pro")
        self.root.geometry("800x900")
        self.root.minsize(600, 700)
        self.root.configure(bg='#0a0a0a')
        
        # Variables
        self.display_var = tk.StringVar()
        self.display_var.set("0")
        self.current_expression = ""
        self.history = []
        self.memory_value = 0
        self.variables = {}  # For storing variables (x, y, etc.)
        self.theme = "dark"  # Default theme
        self.precision = 10  # Decimal precision
        
        # Data for graphing
        self.plot_data = {'x': [], 'y': []}
        
        # Load settings
        self.load_settings()
        
        # Configure styles
        self.setup_styles()
        
        # Create GUI
        self.create_display()
        self.create_notebook()  # Tabbed interface
        self.create_menu()
        self.create_status_bar()
        
        # Bind keyboard events
        self.bind_keyboard_events()
        
        # Auto-save timer
        self.start_auto_save()
        
    def setup_styles(self):
        """Configure modern styles with theme support"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        if self.theme == "dark":
            colors = {
                'bg': '#0a0a0a',
                'fg': '#ffffff',
                'select_bg': '#1e1e1e',
                'button_bg': '#2d2d2d',
                'operator_bg': '#ff6b35',
                'function_bg': '#4a90e2',
                'number_bg': '#3a3a3a',
                'clear_bg': '#ff4757',
                'memory_bg': '#7bed9f'
            }
        else:  # light theme
            colors = {
                'bg': '#f8f9fa',
                'fg': '#343a40',
                'select_bg': '#e9ecef',
                'button_bg': '#ffffff',
                'operator_bg': '#007bff',
                'function_bg': '#28a745',
                'number_bg': '#6c757d',
                'clear_bg': '#dc3545',
                'memory_bg': '#17a2b8'
            }
        
        # Configure styles
        button_styles = [
            ('Number.TButton', colors['number_bg']),
            ('Operator.TButton', colors['operator_bg']),
            ('Function.TButton', colors['function_bg']),
            ('Clear.TButton', colors['clear_bg']),
            ('Memory.TButton', colors['memory_bg'])
        ]
        
        for style_name, bg_color in button_styles:
            self.style.configure(style_name,
                               font=('JetBrains Mono', 12, 'bold'),
                               foreground='white',
                               background=bg_color,
                               borderwidth=0,
                               focuscolor='none',
                               relief='flat')
            
            self.style.map(style_name,
                          background=[('active', bg_color),
                                    ('pressed', bg_color)])
        
    def create_display(self):
        """Create enhanced display with multiple lines"""
        display_frame = tk.Frame(self.root, bg='#0a0a0a', pady=15)
        display_frame.pack(fill=tk.X, padx=15)
        
        # Memory indicator
        self.memory_indicator = tk.Label(display_frame,
                                       text="M" if self.memory_value != 0 else "",
                                       font=('JetBrains Mono', 10, 'bold'),
                                       bg='#0a0a0a',
                                       fg='#ff6b35')
        self.memory_indicator.pack(anchor='w')
        
        # Variable display
        self.var_display = tk.Label(display_frame,
                                  text=self.format_variables(),
                                  font=('JetBrains Mono', 10),
                                  bg='#0a0a0a',
                                  fg='#4a90e2',
                                  anchor='w')
        self.var_display.pack(fill=tk.X)
        
        # Expression display
        self.expr_var = tk.StringVar()
        self.expr_display = tk.Label(display_frame,
                                   textvariable=self.expr_var,
                                   font=('JetBrains Mono', 14),
                                   bg='#0a0a0a',
                                   fg='#7f8c8d',
                                   anchor='e',
                                   wraplength=700)
        self.expr_display.pack(fill=tk.X, pady=(0, 5))
        
        # Main display with gradient effect
        display_container = tk.Frame(display_frame, bg='#1e1e1e', relief='flat', bd=2)
        display_container.pack(fill=tk.X, ipady=5, ipadx=10)
        
        self.display = tk.Entry(display_container,
                               textvariable=self.display_var,
                               font=('JetBrains Mono', 28, 'bold'),
                               justify='right',
                               state='readonly',
                               bg='#1e1e1e',
                               fg='#00ff88',
                               relief='flat',
                               bd=0,
                               insertwidth=0)
        self.display.pack(fill=tk.X, pady=10)
        
    def create_notebook(self):
        """Create tabbed interface for different calculator modes"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Basic Calculator Tab
        self.basic_frame = tk.Frame(self.notebook, bg='#0a0a0a')
        self.notebook.add(self.basic_frame, text="Basic")
        self.create_basic_buttons()
        
        # Scientific Calculator Tab
        self.scientific_frame = tk.Frame(self.notebook, bg='#0a0a0a')
        self.notebook.add(self.scientific_frame, text="Scientific")
        self.create_scientific_buttons()
        
        # Programming Tab
        self.programmer_frame = tk.Frame(self.notebook, bg='#0a0a0a')
        self.notebook.add(self.programmer_frame, text="Programming")
        self.create_programmer_buttons()
        
        # Statistics Tab
        self.stats_frame = tk.Frame(self.notebook, bg='#0a0a0a')
        self.notebook.add(self.stats_frame, text="Statistics")
        self.create_statistics_interface()
        
        # Graphing Tab
        self.graph_frame = tk.Frame(self.notebook, bg='#0a0a0a')
        self.notebook.add(self.graph_frame, text="Graphing")
        self.create_graphing_interface()
        
    def create_basic_buttons(self):
        """Create basic calculator buttons with modern layout"""
        button_frame = tk.Frame(self.basic_frame, bg='#0a0a0a')
        button_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Memory buttons row
        memory_buttons = [
            ('MC', 'Memory.TButton', lambda: self.memory_clear()),
            ('MR', 'Memory.TButton', lambda: self.memory_recall()),
            ('M+', 'Memory.TButton', lambda: self.memory_add()),
            ('M-', 'Memory.TButton', lambda: self.memory_subtract()),
            ('MS', 'Memory.TButton', lambda: self.memory_store())
        ]
        
        for i, (text, style, command) in enumerate(memory_buttons):
            btn = ttk.Button(button_frame, text=text, style=style, command=command)
            btn.grid(row=0, column=i, sticky='nsew', padx=2, pady=2)
        
        # Main calculator buttons
        buttons = [
            ['C', 'CE', '⌫', '÷'],
            ['x²', '√', '%', '×'],
            ['7', '8', '9', '-'],
            ['4', '5', '6', '+'],
            ['1', '2', '3', '='],
            ['±', '0', '.', '=']
        ]
        
        for i, row in enumerate(buttons, 1):
            for j, text in enumerate(row):
                if text == '=' and i == 5:  # First equals button
                    btn = ttk.Button(button_frame, text=text, style='Operator.TButton',
                                   command=self.calculate)
                    btn.grid(row=i, column=j, sticky='nsew', padx=2, pady=2, rowspan=2)
                    continue
                elif text == '=' and i == 6:
                    continue
                    
                style, command = self.get_button_style_command(text)
                btn = ttk.Button(button_frame, text=text, style=style, command=command)
                btn.grid(row=i, column=j, sticky='nsew', padx=2, pady=2)
        
        # Configure grid
        for i in range(7):
            button_frame.grid_rowconfigure(i, weight=1)
        for j in range(5):
            button_frame.grid_columnconfigure(j, weight=1)
    
    def create_scientific_buttons(self):
        """Create scientific calculator interface"""
        button_frame = tk.Frame(self.scientific_frame, bg='#0a0a0a')
        button_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scientific_buttons = [
            ['2nd', 'π', 'e', 'C', '⌫'],
            ['x²', '1/x', '|x|', 'exp', 'mod'],
            ['√', '∛', 'xʸ', 'log', 'ln'],
            ['sin', 'cos', 'tan', '(', ')'],
            ['asin', 'acos', 'atan', 'n!', '÷'],
            ['7', '8', '9', '×', 'x!'],
            ['4', '5', '6', '-', 'nPr'],
            ['1', '2', '3', '+', 'nCr'],
            ['±', '0', '.', '=', '=']
        ]
        
        for i, row in enumerate(scientific_buttons):
            for j, text in enumerate(row):
                if text == '=' and i == 8 and j == 3:
                    btn = ttk.Button(button_frame, text=text, style='Operator.TButton',
                                   command=self.calculate)
                    btn.grid(row=i, column=j, sticky='nsew', padx=1, pady=1, columnspan=2)
                    break
                
                style, command = self.get_button_style_command(text)
                btn = ttk.Button(button_frame, text=text, style=style, command=command)
                btn.grid(row=i, column=j, sticky='nsew', padx=1, pady=1)
        
        # Configure grid
        for i in range(9):
            button_frame.grid_rowconfigure(i, weight=1)
        for j in range(5):
            button_frame.grid_columnconfigure(j, weight=1)
    
    def create_programmer_buttons(self):
        """Create programmer calculator for different number bases"""
        # Number base selection
        base_frame = tk.Frame(self.programmer_frame, bg='#0a0a0a')
        base_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.number_base = tk.StringVar(value="DEC")
        bases = [("HEX", "HEX"), ("DEC", "DEC"), ("OCT", "OCT"), ("BIN", "BIN")]
        
        for text, value in bases:
            rb = tk.Radiobutton(base_frame, text=text, variable=self.number_base,
                              value=value, bg='#0a0a0a', fg='#ffffff',
                              selectcolor='#4a90e2', font=('JetBrains Mono', 12))
            rb.pack(side=tk.LEFT, padx=10)
        
        # Binary display
        self.binary_display = tk.Label(self.programmer_frame,
                                     text="Binary: 0",
                                     font=('JetBrains Mono', 12),
                                     bg='#0a0a0a', fg='#7f8c8d')
        self.binary_display.pack(fill=tk.X, padx=10, pady=5)
        
        # Programmer buttons
        prog_frame = tk.Frame(self.programmer_frame, bg='#0a0a0a')
        prog_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        prog_buttons = [
            ['A', 'B', 'C', 'D', 'E', 'F'],
            ['(', ')', 'mod', 'C', '⌫', '÷'],
            ['OR', 'XOR', 'NOT', 'AND', '<<', '>>'],
            ['7', '8', '9', '×', 'RoL', 'RoR'],
            ['4', '5', '6', '-', 'LSH', 'RSH'],
            ['1', '2', '3', '+', '=', '='],
            ['±', '0', '.', '=', '=', '=']
        ]
        
        for i, row in enumerate(prog_buttons):
            for j, text in enumerate(row):
                if text == '=' and i >= 5:
                    if i == 5 and j == 4:
                        btn = ttk.Button(prog_frame, text=text, style='Operator.TButton',
                                       command=self.calculate)
                        btn.grid(row=i, column=j, sticky='nsew', padx=1, pady=1, columnspan=2, rowspan=2)
                        break
                    continue
                
                style, command = self.get_button_style_command(text)
                btn = ttk.Button(prog_frame, text=text, style=style, command=command)
                btn.grid(row=i, column=j, sticky='nsew', padx=1, pady=1)
        
        # Configure grid
        for i in range(7):
            prog_frame.grid_rowconfigure(i, weight=1)
        for j in range(6):
            prog_frame.grid_columnconfigure(j, weight=1)
    
    def create_statistics_interface(self):
        """Create statistics calculator interface"""
        # Data input area
        input_frame = tk.Frame(self.stats_frame, bg='#0a0a0a')
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(input_frame, text="Data Points (comma-separated):",
                font=('JetBrains Mono', 12), bg='#0a0a0a', fg='#ffffff').pack(anchor='w')
        
        self.data_entry = tk.Text(input_frame, height=3, font=('JetBrains Mono', 11),
                                bg='#1e1e1e', fg='#ffffff', insertbackground='#ffffff')
        self.data_entry.pack(fill=tk.X, pady=5)
        
        # Statistics buttons
        stats_btn_frame = tk.Frame(self.stats_frame, bg='#0a0a0a')
        stats_btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        stats_buttons = [
            ("Mean", self.calc_mean),
            ("Median", self.calc_median),
            ("Mode", self.calc_mode),
            ("Std Dev", self.calc_std_dev),
            ("Variance", self.calc_variance),
            ("Range", self.calc_range)
        ]
        
        for i, (text, command) in enumerate(stats_buttons):
            btn = ttk.Button(stats_btn_frame, text=text, style='Function.TButton',
                           command=command)
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky='ew')
        
        # Results display
        self.stats_result = tk.Text(self.stats_frame, height=8, font=('JetBrains Mono', 11),
                                  bg='#1e1e1e', fg='#00ff88', state='disabled')
        self.stats_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
    def create_graphing_interface(self):
        """Create graphing calculator interface"""
        # Function input
        func_frame = tk.Frame(self.graph_frame, bg='#0a0a0a')
        func_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(func_frame, text="Function f(x) =",
                font=('JetBrains Mono', 12), bg='#0a0a0a', fg='#ffffff').pack(side=tk.LEFT)
        
        self.function_entry = tk.Entry(func_frame, font=('JetBrains Mono', 12),
                                     bg='#1e1e1e', fg='#ffffff', insertbackground='#ffffff')
        self.function_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(func_frame, text="Plot", style='Function.TButton',
                  command=self.plot_function).pack(side=tk.RIGHT)
        
        # Range controls
        range_frame = tk.Frame(self.graph_frame, bg='#0a0a0a')
        range_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(range_frame, text="X Range:", bg='#0a0a0a', fg='#ffffff').pack(side=tk.LEFT)
        self.x_min = tk.Entry(range_frame, width=10, bg='#1e1e1e', fg='#ffffff')
        self.x_min.insert(0, "-10")
        self.x_min.pack(side=tk.LEFT, padx=2)
        
        tk.Label(range_frame, text="to", bg='#0a0a0a', fg='#ffffff').pack(side=tk.LEFT)
        self.x_max = tk.Entry(range_frame, width=10, bg='#1e1e1e', fg='#ffffff')
        self.x_max.insert(0, "10")
        self.x_max.pack(side=tk.LEFT, padx=2)
        
        # Graph canvas
        self.create_graph_canvas()
    
    def create_graph_canvas(self):
        """Create matplotlib canvas for graphing"""
        self.fig, self.ax = plt.subplots(figsize=(8, 6), facecolor='#0a0a0a')
        self.ax.set_facecolor('#1e1e1e')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlabel('X', color='#ffffff')
        self.ax.set_ylabel('Y', color='#ffffff')
        self.ax.tick_params(colors='#ffffff')
        
        self.canvas = FigureCanvasTkAgg(self.fig, self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def create_menu(self):
        """Create comprehensive menu system"""
        menubar = tk.Menu(self.root, bg='#2d2d2d', fg='#ffffff')
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='#ffffff')
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import Data", command=self.import_data)
        file_menu.add_command(label="Export History", command=self.export_history)
        file_menu.add_command(label="Save Session", command=self.save_session)
        file_menu.add_command(label="Load Session", command=self.load_session)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='#ffffff')
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy Result", command=self.copy_result)
        edit_menu.add_command(label="Paste", command=self.paste_value)
        edit_menu.add_command(label="Clear All", command=self.clear_all)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='#ffffff')
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        view_menu.add_command(label="History", command=self.show_history)
        view_menu.add_command(label="Variables", command=self.show_variables)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='#ffffff')
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Unit Converter", command=self.open_unit_converter)
        tools_menu.add_command(label="Currency Converter", command=self.open_currency_converter)
        tools_menu.add_command(label="Settings", command=self.open_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='#ffffff')
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_status_bar(self):
        """Create status bar with useful information"""
        self.status_bar = tk.Frame(self.root, bg='#1e1e1e', relief='sunken', bd=1)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_left = tk.Label(self.status_bar, text="Ready",
                                  bg='#1e1e1e', fg='#7f8c8d', anchor='w')
        self.status_left.pack(side=tk.LEFT, padx=5)
        
        self.status_right = tk.Label(self.status_bar, text=f"Precision: {self.precision}",
                                   bg='#1e1e1e', fg='#7f8c8d', anchor='e')
        self.status_right.pack(side=tk.RIGHT, padx=5)
    
    def get_button_style_command(self, text):
        """Enhanced button style and command mapping"""
        if text in ['C', 'CE', '⌫', '±']:
            return 'Clear.TButton', self.get_special_command(text)
        elif text in ['÷', '×', '-', '+', '=', 'mod']:
            return 'Operator.TButton', lambda t=text: self.add_operator(t) if t != '=' else self.calculate()
        elif text in ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'log', 'ln', 'exp', 
                     '√', '∛', 'x²', '1/x', '|x|', 'π', 'e', 'n!', 'x!', 'xʸ',
                     'OR', 'XOR', 'NOT', 'AND', '<<', '>>', 'RoL', 'RoR']:
            return 'Function.TButton', lambda t=text: self.apply_function(t)
        elif text in ['MC', 'MR', 'M+', 'M-', 'MS']:
            return 'Memory.TButton', self.get_memory_command(text)
        elif text in ['A', 'B', 'C', 'D', 'E', 'F'] and self.number_base.get() == 'HEX':
            return 'Function.TButton', lambda t=text: self.add_number(t)
        else:
            return 'Number.TButton', lambda t=text: self.add_number(t)
    
    def get_special_command(self, text):
        """Get command for special buttons"""
        commands = {
            'C': self.clear,
            'CE': self.clear_entry,
            '⌫': self.backspace,
            '±': self.toggle_sign
        }
        return commands.get(text, lambda: None)
    
    def get_memory_command(self, text):
        """Get memory operation commands"""
        commands = {
            'MC': self.memory_clear,
            'MR': self.memory_recall,
            'M+': self.memory_add,
            'M-': self.memory_subtract,
            'MS': self.memory_store
        }
        return commands.get(text, lambda: None)
    
    # Enhanced calculation methods
    def apply_function(self, function):
        """Enhanced function application with more operations"""
        try:
            current_value = float(self.display_var.get().replace(',', ''))
            
            # Trigonometric functions
            if function == 'sin':
                result = math.sin(math.radians(current_value))
            elif function == 'cos':
                result = math.cos(math.radians(current_value))
            elif function == 'tan':
                result = math.tan(math.radians(current_value))
            elif function == 'asin':
                if -1 <= current_value <= 1:
                    result = math.degrees(math.asin(current_value))
                else:
                    raise ValueError("Input out of range for asin")
            elif function == 'acos':
                if -1 <= current_value <= 1:
                    result = math.degrees(math.acos(current_value))
                else:
                    raise ValueError("Input out of range for acos")
            elif function == 'atan':
                result = math.degrees(math.atan(current_value))
            
            # Logarithmic and exponential
            elif function == 'log':
                if current_value > 0:
                    result = math.log10(current_value)
                else:
                    raise ValueError("Cannot take log of non-positive number")
            elif function == 'ln':
                if current_value > 0:
                    result = math.log(current_value)
                else:
                    raise ValueError("Cannot take ln of non-positive number")
            elif function == 'exp':
                result = math.exp(current_value)
            
            # Power and root functions
            elif function == '√':
                if current_value >= 0:
                    result = math.sqrt(current_value)
                else:
                    raise ValueError("Cannot take square root of negative number")
            elif function == '∛':
                result = current_value ** (1/3) if current_value >= 0 else -(abs(current_value) ** (1/3))
            elif function == 'x²':
                result = current_value ** 2
            elif function == '1/x':
                if current_value != 0:
                    result = 1 / current_value
                else:
                    raise ValueError("Cannot divide by zero")
            elif function == '|x|':
                result = abs(current_value)
            
            # Factorial
            elif function in ['n!', 'x!']:
                if current_value >= 0 and current_value == int(current_value) and current_value <= 170:
                    result = math.factorial(int(current_value))
                else:
                    raise ValueError("Factorial only for non-negative integers ≤ 170")
            
            # Constants
            elif function == 'π':
                result = math.pi
            elif function == 'e':
                result = math.e
            
            # Bitwise operations (for programming mode)
            elif function in ['OR', 'XOR', 'NOT', 'AND', '<<', '>>', 'RoL', 'RoR']:
                result = self.apply_bitwise_operation(function, int(current_value))
            
            else:
                return
            
            self.display_var.set(self.format_number(result))
            self.current_expression = str(result)
            self.update_displays()
            self.update_status("Function applied")
            
        except Exception as e:
            self.display_var.set("Error")
            self.current_expression = ""
            self.update_status(f"Error: {str(e)}")
    
    def apply_bitwise_operation(self, operation, value):
        """Apply bitwise operations for programming mode"""
        if operation == 'NOT':
            return ~value & 0xFFFFFFFF  # 32-bit NOT
        # Add more bitwise operations as needed
        return value
    
    # Memory operations
    def memory_clear(self):
        """Clear memory"""
        self.memory_value = 0
        self.update_memory_indicator()
        self.update_status("Memory cleared")
    
    def memory_recall(self):
        """Recall value from memory"""
        self.display_var.set(self.format_number(self.memory_value))
        self.current_expression = str(self.memory_value)
        self.update_status("Memory recalled")
    
    def memory_store(self):
        """Store current value in memory"""
        try:
            self.memory_value = float(self.display_var.get().replace(',', ''))
            self.update_memory_indicator()
            self.update_status("Value stored in memory")
        except:
            self.update_status("Error storing in memory")
    
    def memory_add(self):
        """Add current value to memory"""
        try:
            current = float(self.display_var.get().replace(',', ''))
            self.memory_value += current
            self.update_memory_indicator()
            self.update_status("Value added to memory")
        except:
            self.update_status("Error adding to memory")
    
    def memory_subtract(self):
        """Subtract current value from memory"""
        try:
            current = float(self.display_var.get().replace(',', ''))
            self.memory_value -= current
            self.update_memory_indicator()
            self.update_status("Value subtracted from memory")
        except:
            self.update_status("Error subtracting from memory")
    
    def update_memory_indicator(self):
        """Update memory indicator"""
        self.memory_indicator.config(text="M" if self.memory_value != 0 else "")
    
    # Statistics functions
    def get_data_points(self):
        """Parse data points from text input"""
        data_text = self.data_entry.get("1.0", tk.END).strip()
        if not data_text:
            return []
        
        try:
            # Split by comma and convert to float
            data = [float(x.strip()) for x in data_text.split(',') if x.strip()]
            return data
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers separated by commas")
            return []
    
    def calc_mean(self):
        """Calculate mean"""
        data = self.get_data_points()
        if data:
            mean = sum(data) / len(data)
            self.display_stats_result(f"Mean: {mean:.6f}")
    
    def calc_median(self):
        """Calculate median"""
        data = self.get_data_points()
        if data:
            sorted_data = sorted(data)
            n = len(sorted_data)
            if n % 2 == 0:
                median = (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
            else:
                median = sorted_data[n//2]
            self.display_stats_result(f"Median: {median:.6f}")
    
    def calc_mode(self):
        """Calculate mode"""
        data = self.get_data_points()
        if data:
            from collections import Counter
            counter = Counter(data)
            max_count = max(counter.values())
            modes = [k for k, v in counter.items() if v == max_count]
            self.display_stats_result(f"Mode: {modes}")
    
    def calc_std_dev(self):
        """Calculate standard deviation"""
        data = self.get_data_points()
        if data and len(data) > 1:
            mean = sum(data) / len(data)
            variance = sum((x - mean) ** 2 for x in data) / (len(data) - 1)
            std_dev = math.sqrt(variance)
            self.display_stats_result(f"Standard Deviation: {std_dev:.6f}")
    
    def calc_variance(self):
        """Calculate variance"""
        data = self.get_data_points()
        if data and len(data) > 1:
            mean = sum(data) / len(data)
            variance = sum((x - mean) ** 2 for x in data) / (len(data) - 1)
            self.display_stats_result(f"Variance: {variance:.6f}")
    
    def calc_range(self):
        """Calculate range"""
        data = self.get_data_points()
        if data:
            range_val = max(data) - min(data)
            self.display_stats_result(f"Range: {range_val:.6f}")
    
    def display_stats_result(self, result):
        """Display statistics result"""
        self.stats_result.config(state='normal')
        self.stats_result.insert(tk.END, result + '\n')
        self.stats_result.config(state='disabled')
        self.stats_result.see(tk.END)
    
    # Graphing functions
    def plot_function(self):
        """Plot mathematical function"""
        try:
            func_str = self.function_entry.get()
            x_min = float(self.x_min.get())
            x_max = float(self.x_max.get())
            
            # Create x values
            x = np.linspace(x_min, x_max, 1000)
            
            # Replace common math functions
            func_str = func_str.replace('^', '**')
            func_str = func_str.replace('sin', 'np.sin')
            func_str = func_str.replace('cos', 'np.cos')
            func_str = func_str.replace('tan', 'np.tan')
            func_str = func_str.replace('log', 'np.log10')
            func_str = func_str.replace('ln', 'np.log')
            func_str = func_str.replace('sqrt', 'np.sqrt')
            func_str = func_str.replace('exp', 'np.exp')
            func_str = func_str.replace('pi', 'np.pi')
            func_str = func_str.replace('e', 'np.e')
            
            # Evaluate function
            y = eval(func_str)
            
            # Plot
            self.ax.clear()
            self.ax.plot(x, y, color='#00ff88', linewidth=2)
            self.ax.grid(True, alpha=0.3, color='#7f8c8d')
            self.ax.set_facecolor('#1e1e1e')
            self.ax.set_xlabel('X', color='#ffffff')
            self.ax.set_ylabel('Y', color='#ffffff')
            self.ax.tick_params(colors='#ffffff')
            self.ax.set_title(f'f(x) = {self.function_entry.get()}', color='#ffffff')
            
            self.canvas.draw()
            self.update_status("Function plotted successfully")
            
        except Exception as e:
            messagebox.showerror("Plot Error", f"Error plotting function: {str(e)}")
            self.update_status("Plot error")
    
    # Enhanced calculation and display methods
    def calculate(self):
        """Enhanced calculation with error handling and history"""
        try:
            if self.current_expression:
                # Add current display value if expression doesn't end with operator
                if self.current_expression[-1] in '+-*/':
                    self.current_expression += self.display_var.get().replace(',', '')
                
                # Replace display operators with calculation operators
                calc_expr = self.current_expression
                calc_expr = calc_expr.replace('÷', '/').replace('×', '*')
                
                # Evaluate expression with enhanced precision
                result = eval(calc_expr)
                
                # Format result based on precision setting
                formatted_result = self.format_number(result)
                
                # Add to history with timestamp
                timestamp = datetime.now().strftime("%H:%M:%S")
                history_entry = {
                    'expression': self.current_expression,
                    'result': result,
                    'timestamp': timestamp
                }
                self.history.append(history_entry)
                if len(self.history) > 100:  # Keep only last 100 calculations
                    self.history.pop(0)
                
                # Update display
                self.display_var.set(formatted_result)
                self.current_expression = str(result)
                self.update_displays()
                self.update_status("Calculation completed")
                
        except Exception as e:
            self.display_var.set("Error")
            self.current_expression = ""
            self.update_displays()
            self.update_status(f"Error: {str(e)}")
    
    def format_number(self, number):
        """Format number with appropriate precision and thousand separators"""
        if isinstance(number, complex):
            if number.imag == 0:
                number = number.real
            else:
                return f"{number.real:.{self.precision}g} + {number.imag:.{self.precision}g}i"
        
        if abs(number) < 1e-10:
            number = 0
        
        if number == int(number) and abs(number) < 1e15:
            return f"{int(number):,}"
        else:
            return f"{number:.{self.precision}g}"
    
    def add_number(self, number):
        """Enhanced number input with validation"""
        current = self.display_var.get()
        if current == "0" or current == "Error":
            self.display_var.set(number)
        else:
            self.display_var.set(current + number)
        
        self.current_expression += number
        self.update_displays()
    
    def add_operator(self, operator):
        """Enhanced operator handling"""
        # Convert symbols for calculation
        op_map = {'÷': '/', '×': '*'}
        calc_op = op_map.get(operator, operator)
        
        if self.current_expression and self.current_expression[-1] not in '+-*/':
            self.current_expression += calc_op
            self.display_var.set("0")
            self.update_displays()
    
    def clear(self):
        """Clear all"""
        self.display_var.set("0")
        self.current_expression = ""
        self.update_displays()
        self.update_status("Cleared")
    
    def clear_entry(self):
        """Clear current entry only"""
        self.display_var.set("0")
        self.update_status("Entry cleared")
    
    def backspace(self):
        """Enhanced backspace"""
        current = self.display_var.get()
        if len(current) > 1:
            self.display_var.set(current[:-1])
        else:
            self.display_var.set("0")
        
        if self.current_expression:
            self.current_expression = self.current_expression[:-1]
            self.update_displays()
    
    def toggle_sign(self):
        """Toggle positive/negative sign"""
        current = self.display_var.get()
        if current != "0" and current != "Error":
            if current.startswith('-'):
                self.display_var.set(current[1:])
            else:
                self.display_var.set('-' + current)
    
    def update_displays(self):
        """Update all display elements"""
        # Update expression display
        display_expr = self.current_expression
        display_expr = display_expr.replace('/', '÷').replace('*', '×')
        self.expr_var.set(display_expr)
        
        # Update variable display
        self.var_display.config(text=self.format_variables())
        
        # Update binary display for programmer mode
        if hasattr(self, 'binary_display'):
            try:
                current_val = int(float(self.display_var.get().replace(',', '')))
                binary_str = bin(current_val)[2:]  # Remove '0b' prefix
                self.binary_display.config(text=f"Binary: {binary_str}")
            except:
                self.binary_display.config(text="Binary: 0")
    
    def format_variables(self):
        """Format variables for display"""
        if self.variables:
            var_str = "Variables: " + ", ".join([f"{k}={v}" for k, v in self.variables.items()])
            return var_str[:50] + "..." if len(var_str) > 50 else var_str
        return ""
    
    def update_status(self, message):
        """Update status bar"""
        self.status_left.config(text=message)
        # Auto-clear status after 3 seconds
        self.root.after(3000, lambda: self.status_left.config(text="Ready"))
    
    # File operations
    def import_data(self):
        """Import data from file"""
        file_path = filedialog.askopenfilename(
            title="Import Data",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    data = file.read()
                    self.data_entry.delete("1.0", tk.END)
                    self.data_entry.insert("1.0", data)
                self.update_status("Data imported successfully")
            except Exception as e:
                messagebox.showerror("Import Error", f"Error importing data: {str(e)}")
    
    def export_history(self):
        """Export calculation history"""
        if not self.history:
            messagebox.showinfo("Export", "No history to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export History",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    json.dump(self.history, file, indent=2)
                self.update_status("History exported successfully")
            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting history: {str(e)}")
    
    def save_session(self):
        """Save current session"""
        session_data = {
            'history': self.history,
            'memory': self.memory_value,
            'variables': self.variables,
            'theme': self.theme,
            'precision': self.precision
        }
        
        file_path = filedialog.asksaveasfilename(
            title="Save Session",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    json.dump(session_data, file, indent=2)
                self.update_status("Session saved successfully")
            except Exception as e:
                messagebox.showerror("Save Error", f"Error saving session: {str(e)}")
    
    def load_session(self):
        """Load saved session"""
        file_path = filedialog.askopenfilename(
            title="Load Session",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    session_data = json.load(file)
                
                self.history = session_data.get('history', [])
                self.memory_value = session_data.get('memory', 0)
                self.variables = session_data.get('variables', {})
                self.theme = session_data.get('theme', 'dark')
                self.precision = session_data.get('precision', 10)
                
                self.update_memory_indicator()
                self.update_displays()
                self.setup_styles()
                self.update_status("Session loaded successfully")
                
            except Exception as e:
                messagebox.showerror("Load Error", f"Error loading session: {str(e)}")
    
    # Settings and preferences
    def load_settings(self):
        """Load user settings"""
        settings_file = "calculator_settings.json"
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as file:
                    settings = json.load(file)
                    self.theme = settings.get('theme', 'dark')
                    self.precision = settings.get('precision', 10)
                    self.memory_value = settings.get('memory', 0)
            except:
                pass  # Use defaults if loading fails
    
    def save_settings(self):
        """Save user settings"""
        settings = {
            'theme': self.theme,
            'precision': self.precision,
            'memory': self.memory_value
        }
        
        try:
            with open("calculator_settings.json", 'w') as file:
                json.dump(settings, file, indent=2)
        except:
            pass  # Fail silently
    
    def start_auto_save(self):
        """Start auto-save timer"""
        def auto_save():
            self.save_settings()
            # Schedule next auto-save in 5 minutes
            self.root.after(300000, auto_save)
        
        # Start auto-save after 5 minutes
        self.root.after(300000, auto_save)
    
    # UI enhancements
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.theme = "light" if self.theme == "dark" else "dark"
        self.setup_styles()
        self.update_status(f"Switched to {self.theme} theme")
    
    def copy_result(self):
        """Copy current result to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.display_var.get())
        self.update_status("Result copied to clipboard")
    
    def paste_value(self):
        """Paste value from clipboard"""
        try:
            clipboard_value = self.root.clipboard_get()
            # Validate that it's a number
            float(clipboard_value)
            self.display_var.set(clipboard_value)
            self.current_expression = clipboard_value
            self.update_displays()
            self.update_status("Value pasted")
        except:
            self.update_status("Cannot paste - invalid number")
    
    def clear_all(self):
        """Clear everything including history and memory"""
        self.clear()
        self.history.clear()
        self.memory_value = 0
        self.variables.clear()
        self.update_memory_indicator()
        self.update_displays()
        self.update_status("Everything cleared")
    
    # Enhanced dialogs
    def show_history(self):
        """Show enhanced calculation history"""
        history_window = tk.Toplevel(self.root)
        history_window.title("Calculation History")
        history_window.geometry("600x400")
        history_window.configure(bg='#0a0a0a')
        
        # Create treeview for better history display
        columns = ("Time", "Expression", "Result")
        tree = ttk.Treeview(history_window, columns=columns, show="headings", height=15)
        
        # Configure columns
        tree.heading("Time", text="Time")
        tree.heading("Expression", text="Expression")
        tree.heading("Result", text="Result")
        
        tree.column("Time", width=100)
        tree.column("Expression", width=300)
        tree.column("Result", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Populate history
        for entry in self.history:
            if isinstance(entry, dict):
                tree.insert("", "end", values=(
                    entry.get('timestamp', ''),
                    entry.get('expression', ''),
                    self.format_number(entry.get('result', 0))
                ))
        
        # Buttons frame
        btn_frame = tk.Frame(history_window, bg='#0a0a0a')
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Clear History",
                  command=lambda: [self.history.clear(), history_window.destroy()]).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Export History",
                  command=self.export_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close",
                  command=history_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def show_variables(self):
        """Show variables dialog"""
        var_window = tk.Toplevel(self.root)
        var_window.title("Variables")
        var_window.geometry("400x300")
        var_window.configure(bg='#0a0a0a')
        
        # Variables display
        var_text = tk.Text(var_window, font=('JetBrains Mono', 12),
                          bg='#1e1e1e', fg='#ffffff', height=10)
        var_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Display current variables
        if self.variables:
            for var, value in self.variables.items():
                var_text.insert(tk.END, f"{var} = {value}\n")
        else:
            var_text.insert(tk.END, "No variables defined")
        
        var_text.config(state='disabled')
    
    def open_unit_converter(self):
        """Open unit converter dialog"""
        messagebox.showinfo("Unit Converter", "Unit converter feature coming soon!")
    
    def open_currency_converter(self):
        """Open currency converter dialog"""
        messagebox.showinfo("Currency Converter", "Currency converter feature coming soon!")
    
    def open_settings(self):
        """Open settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg='#0a0a0a')
        
        # Precision setting
        tk.Label(settings_window, text="Decimal Precision:", 
                bg='#0a0a0a', fg='#ffffff', font=('JetBrains Mono', 12)).pack(pady=10)
        
        precision_var = tk.IntVar(value=self.precision)
        precision_scale = tk.Scale(settings_window, from_=1, to=15, orient=tk.HORIZONTAL,
                                 variable=precision_var, bg='#0a0a0a', fg='#ffffff',
                                 highlightbackground='#0a0a0a')
        precision_scale.pack(pady=5)
        
        # Theme setting
        tk.Label(settings_window, text="Theme:", 
                bg='#0a0a0a', fg='#ffffff', font=('JetBrains Mono', 12)).pack(pady=10)
        
        theme_var = tk.StringVar(value=self.theme)
        tk.Radiobutton(settings_window, text="Dark", variable=theme_var, value="dark",
                      bg='#0a0a0a', fg='#ffffff', selectcolor='#4a90e2').pack()
        tk.Radiobutton(settings_window, text="Light", variable=theme_var, value="light",
                      bg='#0a0a0a', fg='#ffffff', selectcolor='#4a90e2').pack()
        
        # Apply button
        def apply_settings():
            self.precision = precision_var.get()
            self.theme = theme_var.get()
            self.setup_styles()
            self.status_right.config(text=f"Precision: {self.precision}")
            settings_window.destroy()
            self.update_status("Settings applied")
        
        ttk.Button(settings_window, text="Apply", command=apply_settings).pack(pady=20)
    
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts_text = """
KEYBOARD SHORTCUTS:

Numbers & Operations:
• 0-9: Enter numbers
• +, -, *, /: Basic operations
• Enter or =: Calculate result
• Backspace: Delete last character
• Escape: Clear all
• .: Decimal point

Function Keys:
• F1: Show help
• F2: Toggle theme
• F9: Show history
• Ctrl+C: Copy result
• Ctrl+V: Paste value

Memory Operations:
• Ctrl+M: Memory store
• Ctrl+R: Memory recall
• Ctrl+L: Memory clear

Advanced:
• Tab: Switch calculator tabs
• Ctrl+S: Save session
• Ctrl+O: Load session
        """
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)
    
    def show_documentation(self):
        """Show documentation"""
        doc_text = """
ADVANCED CALCULATOR DOCUMENTATION:

FEATURES:
• Basic arithmetic operations
• Scientific functions (trig, log, exp)
• Programming mode (hex, oct, bin)
• Statistical calculations
• Function graphing
• Memory operations
• Variable storage
• Calculation history
• Session save/load
• Multiple themes

TABS:
• Basic: Standard calculator
• Scientific: Advanced math functions  
• Programming: Number base conversions
• Statistics: Data analysis
• Graphing: Function plotting

For more help, visit the GitHub repository.
        """
        messagebox.showinfo("Documentation", doc_text)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
Advanced Scientific Calculator Pro v2.0

A comprehensive calculator application with:
✓ Modern dark/light theme UI
✓ Scientific & programming modes
✓ Statistical analysis tools
✓ Function graphing capabilities
✓ Session management
✓ Keyboard shortcuts
✓ Memory operations
✓ Export/import functionality

Built with Python, Tkinter, Matplotlib & NumPy
Designed for professionals, students & developers

© 2024 - Open Source Project
        """
        messagebox.showinfo("About Calculator Pro", about_text)
    
    def bind_keyboard_events(self):
        """Enhanced keyboard event binding"""
        self.root.bind('<Key>', self.on_key_press)
        self.root.bind('<Control-c>', lambda e: self.copy_result())
        self.root.bind('<Control-v>', lambda e: self.paste_value())
        self.root.bind('<Control-s>', lambda e: self.save_session())
        self.root.bind('<Control-o>', lambda e: self.load_session())
        self.root.bind('<Control-m>', lambda e: self.memory_store())
        self.root.bind('<Control-r>', lambda e: self.memory_recall())
        self.root.bind('<Control-l>', lambda e: self.memory_clear())
        self.root.bind('<F1>', lambda e: self.show_shortcuts())
        self.root.bind('<F2>', lambda e: self.toggle_theme())
        self.root.bind('<F9>', lambda e: self.show_history())
        self.root.focus_set()
    
    def on_key_press(self, event):
        """Enhanced keyboard input handling"""
        key = event.char
        
        if key.isdigit() or key == '.':
            self.add_number(key)
        elif key in '+-*/':
            op_map = {'/': '÷', '*': '×'}
            self.add_operator(op_map.get(key, key))
        elif key == '\r' or key == '=':  # Enter key
            self.calculate()
        elif event.keysym == 'BackSpace':
            self.backspace()
        elif event.keysym == 'Escape':
            self.clear()
        elif event.keysym == 'Delete':
            self.clear_entry()
    
    def __del__(self):
        """Cleanup when calculator is destroyed"""
        self.save_settings()

def main():
    root = tk.Tk()
    
    # Set window icon if available
    try:
        root.iconbitmap('calculator_icon.ico')
    except:
        pass
    
    calculator = AdvancedCalculator(root)
    
    # Handle window closing
    def on_closing():
        calculator.save_settings()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()