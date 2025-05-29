import tkinter as tk
from tkinter import ttk, messagebox
import math
import re

class AdvancedCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Calculator")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        self.root.configure(bg='#2c3e50')
        
        # Variables
        self.display_var = tk.StringVar()
        self.display_var.set("0")
        self.current_expression = ""
        self.history = []
        
        # Configure styles
        self.setup_styles()
        
        # Create GUI
        self.create_display()
        self.create_buttons()
        self.create_menu()
        
        # Bind keyboard events
        self.bind_keyboard_events()
        
    def setup_styles(self):
        """Configure custom styles for ttk widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Button styles
        style.configure('Number.TButton', 
                       font=('Arial', 14, 'bold'),
                       foreground='white',
                       background='#34495e',
                       borderwidth=1,
                       focuscolor='none')
        
        style.configure('Operator.TButton',
                       font=('Arial', 14, 'bold'),
                       foreground='white',
                       background='#e74c3c',
                       borderwidth=1,
                       focuscolor='none')
        
        style.configure('Function.TButton',
                       font=('Arial', 12, 'bold'),
                       foreground='white',
                       background='#3498db',
                       borderwidth=1,
                       focuscolor='none')
        
        style.configure('Clear.TButton',
                       font=('Arial', 14, 'bold'),
                       foreground='white',
                       background='#e67e22',
                       borderwidth=1,
                       focuscolor='none')
        
    def create_display(self):
        """Create the display area"""
        display_frame = tk.Frame(self.root, bg='#2c3e50', pady=20)
        display_frame.pack(fill=tk.X, padx=10)
        
        # Main display
        self.display = tk.Entry(display_frame,
                               textvariable=self.display_var,
                               font=('Arial', 24, 'bold'),
                               justify='right',
                               state='readonly',
                               bg='#ecf0f1',
                               fg='#2c3e50',
                               relief='flat',
                               bd=10)
        self.display.pack(fill=tk.X, ipady=10)
        
        # Expression display (shows current calculation)
        self.expr_var = tk.StringVar()
        self.expr_display = tk.Label(display_frame,
                                    textvariable=self.expr_var,
                                    font=('Arial', 12),
                                    bg='#2c3e50',
                                    fg='#bdc3c7',
                                    anchor='e')
        self.expr_display.pack(fill=tk.X, pady=(5, 0))
        
    def create_buttons(self):
        """Create calculator buttons"""
        button_frame = tk.Frame(self.root, bg='#2c3e50')
        button_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Button layout
        buttons = [
            ['C', '⌫', '±', '÷'],
            ['sin', 'cos', 'tan', '×'],
            ['7', '8', '9', '-'],
            ['4', '5', '6', '+'],
            ['1', '2', '3', '='],
            ['√', '0', '.', '=']
        ]
        
        # Create buttons
        for i, row in enumerate(buttons):
            for j, text in enumerate(row):
                if text == '=':
                    if i == 4:  # First equals button
                        btn = ttk.Button(button_frame, text=text, style='Operator.TButton',
                                       command=self.calculate)
                        btn.grid(row=i, column=j, sticky='nsew', padx=2, pady=2, rowspan=2)
                    continue
                elif text in ['C', '⌫', '±']:
                    style = 'Clear.TButton'
                    command = self.get_button_command(text)
                elif text in ['÷', '×', '-', '+']:
                    style = 'Operator.TButton'
                    command = lambda t=text: self.add_operator(t)
                elif text in ['sin', 'cos', 'tan', '√']:
                    style = 'Function.TButton'
                    command = lambda t=text: self.apply_function(t)
                else:
                    style = 'Number.TButton'
                    command = lambda t=text: self.add_number(t)
                
                btn = ttk.Button(button_frame, text=text, style=style, command=command)
                btn.grid(row=i, column=j, sticky='nsew', padx=2, pady=2)
        
        # Configure grid weights
        for i in range(6):
            button_frame.grid_rowconfigure(i, weight=1)
        for j in range(4):
            button_frame.grid_columnconfigure(j, weight=1)
    
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # History menu
        history_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="History", menu=history_menu)
        history_menu.add_command(label="Show History", command=self.show_history)
        history_menu.add_command(label="Clear History", command=self.clear_history)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_about)
    
    def get_button_command(self, text):
        """Get appropriate command for special buttons"""
        if text == 'C':
            return self.clear
        elif text == '⌫':
            return self.backspace
        elif text == '±':
            return self.toggle_sign
    
    def add_number(self, number):
        """Add number to display"""
        current = self.display_var.get()
        if current == "0" or current == "Error":
            self.display_var.set(number)
        else:
            self.display_var.set(current + number)
        
        self.current_expression += number
        self.update_expression_display()
    
    def add_operator(self, operator):
        """Add operator to expression"""
        # Convert symbols for calculation
        op_map = {'÷': '/', '×': '*'}
        calc_op = op_map.get(operator, operator)
        
        if self.current_expression and self.current_expression[-1] not in '+-*/':
            self.current_expression += calc_op
            self.display_var.set("0")
            self.update_expression_display()
    
    def apply_function(self, function):
        """Apply mathematical functions"""
        try:
            current_value = float(self.display_var.get())
            
            if function == 'sin':
                result = math.sin(math.radians(current_value))
            elif function == 'cos':
                result = math.cos(math.radians(current_value))
            elif function == 'tan':
                result = math.tan(math.radians(current_value))
            elif function == '√':
                if current_value < 0:
                    raise ValueError("Cannot calculate square root of negative number")
                result = math.sqrt(current_value)
            
            self.display_var.set(str(result))
            self.current_expression = str(result)
            self.update_expression_display()
            
        except Exception as e:
            self.display_var.set("Error")
            self.current_expression = ""
    
    def calculate(self):
        """Perform calculation"""
        try:
            if self.current_expression:
                # Add current display value if expression doesn't end with operator
                if self.current_expression[-1] in '+-*/':
                    self.current_expression += self.display_var.get()
                
                # Evaluate expression
                result = eval(self.current_expression)
                
                # Add to history
                self.history.append(f"{self.current_expression} = {result}")
                if len(self.history) > 20:  # Keep only last 20 calculations
                    self.history.pop(0)
                
                # Update display
                self.display_var.set(str(result))
                self.current_expression = str(result)
                self.update_expression_display()
                
        except Exception as e:
            self.display_var.set("Error")
            self.current_expression = ""
            self.update_expression_display()
    
    def clear(self):
        """Clear calculator"""
        self.display_var.set("0")
        self.current_expression = ""
        self.update_expression_display()
    
    def backspace(self):
        """Remove last character"""
        current = self.display_var.get()
        if len(current) > 1:
            self.display_var.set(current[:-1])
        else:
            self.display_var.set("0")
        
        if self.current_expression:
            self.current_expression = self.current_expression[:-1]
            self.update_expression_display()
    
    def toggle_sign(self):
        """Toggle positive/negative sign"""
        current = self.display_var.get()
        if current != "0" and current != "Error":
            if current.startswith('-'):
                self.display_var.set(current[1:])
            else:
                self.display_var.set('-' + current)
    
    def update_expression_display(self):
        """Update the expression display"""
        # Convert operators back to symbols for display
        display_expr = self.current_expression
        display_expr = display_expr.replace('/', '÷').replace('*', '×')
        self.expr_var.set(display_expr)
    
    def bind_keyboard_events(self):
        """Bind keyboard shortcuts"""
        self.root.bind('<Key>', self.on_key_press)
        self.root.focus_set()
    
    def on_key_press(self, event):
        """Handle keyboard input"""
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
    
    def show_history(self):
        """Show calculation history"""
        history_window = tk.Toplevel(self.root)
        history_window.title("Calculation History")
        history_window.geometry("400x300")
        history_window.configure(bg='#2c3e50')
        
        # Create scrollable text widget
        frame = tk.Frame(history_window, bg='#2c3e50')
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        history_text = tk.Text(frame, 
                              yscrollcommand=scrollbar.set,
                              bg='#ecf0f1',
                              fg='#2c3e50',
                              font=('Arial', 12),
                              state='normal')
        history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=history_text.yview)
        
        # Add history entries
        if self.history:
            for entry in self.history:
                history_text.insert(tk.END, entry + '\n')
        else:
            history_text.insert(tk.END, "No calculations yet.")
        
        history_text.config(state='disabled')
    
    def clear_history(self):
        """Clear calculation history"""
        self.history.clear()
        messagebox.showinfo("History Cleared", "Calculation history has been cleared.")
    
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts_text = """
Keyboard Shortcuts:

Numbers (0-9): Enter numbers
+, -, *, /: Basic operations
Enter or =: Calculate result
Backspace: Delete last character
Escape: Clear all
.: Decimal point

Mouse clicks work for all functions.
        """
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
Advanced Calculator v1.0

Features:
• Basic arithmetic operations
• Trigonometric functions
• Square root calculation
• Calculation history
• Keyboard shortcuts
• Modern GUI design

Created with Python & Tkinter
        """
        messagebox.showinfo("About", about_text)

def main():
    root = tk.Tk()
    calculator = AdvancedCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()