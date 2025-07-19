import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path

class ConfigurationFrame(ctk.CTkFrame):
    def __init__(self, parent, config_type='supplier'):
        super().__init__(parent)
        
        self.config_type = config_type
        self.config_manager = None # Removed: self.config_manager = ConfigurationManager()
        self.current_config: Optional[str] = None
        self.sample_file: Optional[Path] = None

        # Styles
        self.style = {
            'button': {
                'font': ('Arial', 13),
                'corner_radius': 6,
                'fg_color': '#253d61',
                'hover_color': '#ef8018',
            },
            'label': {
                'font': ('Segoe UI', 13),
            },
            'entry': {
                'font': ('Segoe UI', 12),
                'corner_radius': 4,
            }
        }

        self._init_ui()
        self._load_configurations()

    def _init_ui(self):
        """Initialize the UI components"""
        # Main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Title
        title_font = ("Segoe UI", 20, "bold")
        label = ctk.CTkLabel(
            self.main_container, 
            text=f"Configuration: {self.config_type.title()}", 
            font=title_font
        )
        label.pack(pady=(10, 20))

        # Tabs
        self.tab_view = ctk.CTkTabview(self.main_container)
        self.tab_view.pack(fill='both', expand=True)

        # Create tabs
        self.connection_tab = self.tab_view.add("Connection")
        self.file_format_tab = self.tab_view.add("File Format")
        self.mapping_tab = self.tab_view.add("Column Mapping")

        self._init_connection_tab()
        self._init_file_format_tab()
        self._init_mapping_tab()

        # Bottom buttons
        self.button_frame = ctk.CTkFrame(self.main_container)
        self.button_frame.pack(fill='x', pady=(10, 0))

        self.save_btn = ctk.CTkButton(
            self.button_frame,
            text="Save Configuration",
            command=self._save_configuration,
            **self.style['button']
        )
        self.save_btn.pack(side='right', padx=5)

        self.test_btn = ctk.CTkButton(
            self.button_frame,
            text="Test Configuration",
            command=self._test_configuration,
            **self.style['button']
        )
        self.test_btn.pack(side='right', padx=5)

    def _init_connection_tab(self):
        """Initialize the connection settings tab"""
        # Select configuration
        select_frame = ctk.CTkFrame(self.connection_tab)
        select_frame.pack(fill='x', pady=(0, 10))

        ctk.CTkLabel(
            select_frame,
            text=f"Select {self.config_type.title()}:",
            **self.style['label']
        ).pack(side='left', padx=5)

        self.config_var = ctk.StringVar()
        self.config_dropdown = ctk.CTkOptionMenu(
            select_frame,
            variable=self.config_var,
            command=self._on_config_selected,
            **self.style['entry']
        )
        self.config_dropdown.pack(side='left', padx=5)

        # Connection details
        details_frame = ctk.CTkFrame(self.connection_tab)
        details_frame.pack(fill='both', expand=True)

        # Host
        host_frame = ctk.CTkFrame(details_frame)
        host_frame.pack(fill='x', pady=2)
        
        ctk.CTkLabel(
            host_frame,
            text="Host:",
            **self.style['label']
        ).pack(side='left', padx=5)
        
        self.host_entry = ctk.CTkEntry(
            host_frame,
            **self.style['entry']
        )
        self.host_entry.pack(side='left', fill='x', expand=True, padx=5)

        # Port
        port_frame = ctk.CTkFrame(details_frame)
        port_frame.pack(fill='x', pady=2)
        
        ctk.CTkLabel(
            port_frame,
            text="Port:",
            **self.style['label']
        ).pack(side='left', padx=5)
        
        self.port_entry = ctk.CTkEntry(
            port_frame,
            **self.style['entry']
        )
        self.port_entry.pack(side='left', fill='x', expand=True, padx=5)

        # Username
        user_frame = ctk.CTkFrame(details_frame)
        user_frame.pack(fill='x', pady=2)
        
        ctk.CTkLabel(
            user_frame,
            text="Username:",
            **self.style['label']
        ).pack(side='left', padx=5)
        
        self.username_entry = ctk.CTkEntry(
            user_frame,
            **self.style['entry']
        )
        self.username_entry.pack(side='left', fill='x', expand=True, padx=5)

        # Password
        pass_frame = ctk.CTkFrame(details_frame)
        pass_frame.pack(fill='x', pady=2)
        
        ctk.CTkLabel(
            pass_frame,
            text="Password:",
            **self.style['label']
        ).pack(side='left', padx=5)
        
        self.password_entry = ctk.CTkEntry(
            pass_frame,
            show="*",
            **self.style['entry']
        )
        self.password_entry.pack(side='left', fill='x', expand=True, padx=5)

    def _init_file_format_tab(self):
        """Initialize the file format settings tab"""
        # File pattern
        pattern_frame = ctk.CTkFrame(self.file_format_tab)
        pattern_frame.pack(fill='x', pady=2)
        
        ctk.CTkLabel(
            pattern_frame,
            text="File Pattern:",
            **self.style['label']
        ).pack(side='left', padx=5)
        
        self.pattern_entry = ctk.CTkEntry(
            pattern_frame,
            **self.style['entry']
        )
        self.pattern_entry.pack(side='left', fill='x', expand=True, padx=5)

        # Has headers
        header_frame = ctk.CTkFrame(self.file_format_tab)
        header_frame.pack(fill='x', pady=2)
        
        self.has_headers_var = ctk.BooleanVar(value=True)
        self.has_headers_cb = ctk.CTkCheckBox(
            header_frame,
            text="File has headers",
            variable=self.has_headers_var,
            **self.style['entry']
        )
        self.has_headers_cb.pack(side='left', padx=5)

        # Description
        desc_frame = ctk.CTkFrame(self.file_format_tab)
        desc_frame.pack(fill='x', pady=2)
        
        ctk.CTkLabel(
            desc_frame,
            text="Description:",
            **self.style['label']
        ).pack(side='left', padx=5)
        
        self.description_entry = ctk.CTkEntry(
            desc_frame,
            **self.style['entry']
        )
        self.description_entry.pack(side='left', fill='x', expand=True, padx=5)

        # Sample file
        sample_frame = ctk.CTkFrame(self.file_format_tab)
        sample_frame.pack(fill='x', pady=2)
        
        ctk.CTkButton(
            sample_frame,
            text="Load Sample File",
            command=self._load_sample_file,
            **self.style['button']
        ).pack(side='left', padx=5)
        
        self.sample_label = ctk.CTkLabel(
            sample_frame,
            text="No file loaded",
            **self.style['label']
        )
        self.sample_label.pack(side='left', padx=5)

    def _init_mapping_tab(self):
        """Initialize the column mapping tab"""
        # Reference column
        ref_frame = ctk.CTkFrame(self.mapping_tab)
        ref_frame.pack(fill='x', pady=2)
        
        ctk.CTkLabel(
            ref_frame,
            text="Reference Column:",
            **self.style['label']
        ).pack(side='left', padx=5)
        
        self.ref_var = ctk.StringVar()
        self.ref_entry = ctk.CTkEntry(
            ref_frame,
            textvariable=self.ref_var,
            **self.style['entry']
        )
        self.ref_entry.pack(side='left', fill='x', expand=True, padx=5)

        # Stock column
        stock_frame = ctk.CTkFrame(self.mapping_tab)
        stock_frame.pack(fill='x', pady=2)
        
        ctk.CTkLabel(
            stock_frame,
            text="Stock Column:",
            **self.style['label']
        ).pack(side='left', padx=5)
        
        self.stock_var = ctk.StringVar()
        self.stock_entry = ctk.CTkEntry(
            stock_frame,
            textvariable=self.stock_var,
            **self.style['entry']
        )
        self.stock_entry.pack(side='left', fill='x', expand=True, padx=5)

        # Auto-detect button
        detect_frame = ctk.CTkFrame(self.mapping_tab)
        detect_frame.pack(fill='x', pady=2)
        
        ctk.CTkButton(
            detect_frame,
            text="Auto-detect Columns",
            command=self._auto_detect_columns,
            **self.style['button']
        ).pack(side='left', padx=5)

    def _load_configurations(self):
        """Load existing configurations"""
        try:
            # Removed: self.config_manager.load_all_configurations()
            # Removed: configs = list(self.config_manager.configs.keys())
            # Removed: self.config_dropdown.configure(values=configs)
            # Removed: if configs:
            # Removed:     self.config_dropdown.set(configs[0])
            # Removed:     self._on_config_selected(configs[0])
            pass # No configurations to load
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configurations: {str(e)}")

    def _on_config_selected(self, name: str):
        """Handle configuration selection"""
        self.current_config = name
        # Removed: config = self.config_manager.configs.get(name)
        if self.current_config: # Assuming a default config exists or is handled
            # Fill connection details
            self.host_entry.delete(0, 'end')
            self.host_entry.insert(0, '') # Placeholder, actual config loading removed
            
            self.port_entry.delete(0, 'end')
            self.port_entry.insert(0, '21') # Placeholder
            
            self.username_entry.delete(0, 'end')
            self.username_entry.insert(0, '') # Placeholder
            
            self.password_entry.delete(0, 'end')
            self.password_entry.insert(0, '') # Placeholder

            # Fill file format
            self.pattern_entry.delete(0, 'end')
            self.pattern_entry.insert(0, '') # Placeholder
            
            self.has_headers_var.set(True) # Placeholder
            
            self.description_entry.delete(0, 'end')
            self.description_entry.insert(0, '') # Placeholder

            # Fill mappings
            self.ref_var.set('') # Placeholder
            self.stock_var.set('') # Placeholder

    def _load_sample_file(self):
        """Load a sample file for testing"""
        file_path = filedialog.askopenfilename(
            filetypes=[
                ('All Supported Files', '*.csv;*.xlsx;*.xls;*.txt'),
                ('CSV Files', '*.csv'),
                ('Excel Files', '*.xlsx;*.xls'),
                ('Text Files', '*.txt')
            ]
        )
        if file_path:
            self.sample_file = Path(file_path)
            self.sample_label.configure(text=self.sample_file.name)
            self._auto_detect_columns()

    def _auto_detect_columns(self):
        """Auto-detect columns from sample file"""
        if not self.sample_file:
            messagebox.showwarning("Warning", "Please load a sample file first")
            return

        # Removed: suggestions = self.config_manager.detect_columns(self.sample_file)
        suggestions = {'reference_columns': [], 'stock_columns': []} # Placeholder
        if suggestions['reference_columns'] or suggestions['stock_columns']:
            # Show suggestion dialog
            dialog = ColumnSuggestionDialog(
                self,
                suggestions['reference_columns'],
                suggestions['stock_columns']
            )
            if dialog.result:
                self.ref_var.set(dialog.result.get('reference', ''))
                self.stock_var.set(dialog.result.get('stock', ''))
        else:
            messagebox.showinfo("Info", "No column suggestions found")

    def _save_configuration(self):
        """Save the current configuration"""
        if not self.current_config:
            messagebox.showerror("Error", "No configuration selected")
            return

        try:
            # Removed: config = ConfigurationItem(...)
            # Removed: self.config_manager.save_configuration(self.current_config, config)
            messagebox.showinfo("Success", "Configuration saved successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

    def _test_configuration(self):
        """Test the current configuration"""
        if not self.current_config:
            messagebox.showerror("Error", "No configuration selected")
            return

        if not self.sample_file:
            messagebox.showwarning("Warning", "Please load a sample file first")
            return

        # Removed: results = self.config_manager.validate_configuration(...)
        results = {'valid': True, 'errors': []} # Placeholder

        if results['valid']:
            messagebox.showinfo("Success", "Configuration is valid!")
        else:
            errors = "\n".join(results['errors'])
            messagebox.showerror("Validation Failed", f"Errors found:\n{errors}")

class ColumnSuggestionDialog(ctk.CTkToplevel):
    def __init__(self, parent, ref_suggestions, stock_suggestions):
        super().__init__(parent)
        
        self.title("Column Suggestions")
        self.result = None

        # Reference column selection
        ref_frame = ctk.CTkFrame(self)
        ref_frame.pack(fill='x', padx=10, pady=5)
        
        ctk.CTkLabel(
            ref_frame,
            text="Reference Column:"
        ).pack(side='left', padx=5)
        
        self.ref_var = ctk.StringVar()
        ref_menu = ctk.CTkOptionMenu(
            ref_frame,
            variable=self.ref_var,
            values=ref_suggestions or []
        )
        ref_menu.pack(side='left', padx=5)

        # Stock column selection
        stock_frame = ctk.CTkFrame(self)
        stock_frame.pack(fill='x', padx=10, pady=5)
        
        ctk.CTkLabel(
            stock_frame,
            text="Stock Column:"
        ).pack(side='left', padx=5)
        
        self.stock_var = ctk.StringVar()
        stock_menu = ctk.CTkOptionMenu(
            stock_frame,
            variable=self.stock_var,
            values=stock_suggestions or []
        )
        stock_menu.pack(side='left', padx=5)

        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        ctk.CTkButton(
            button_frame,
            text="Apply",
            command=self._apply
        ).pack(side='right', padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._cancel
        ).pack(side='right', padx=5)

        if ref_suggestions:
            self.ref_var.set(ref_suggestions[0])
        if stock_suggestions:
            self.stock_var.set(stock_suggestions[0])

        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)

    def _apply(self):
        self.result = {
            'reference': self.ref_var.get(),
            'stock': self.stock_var.get()
        }
        self.destroy()

    def _cancel(self):
        self.destroy()
