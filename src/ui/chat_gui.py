import threading
import queue
import subprocess
import tkinter as tk
from tkinter import scrolledtext, ttk
from typing import Callable, Optional
try:
    import pygame
    _HAS_PYGAME = True
except Exception:
    _HAS_PYGAME = False


class ChatUI:
    def __init__(self, on_send: Callable[[str], None], title: str = "SoF Chat", on_settings_changed: Optional[Callable[[], None]] = None):
        self.on_send = on_send
        self.on_settings_changed = on_settings_changed
        self._title = title
        self._incoming: "queue.Queue[str]" = queue.Queue()
        self._thread: Optional[threading.Thread] = None
        self._root: Optional[tk.Tk] = None
        self._text: Optional[scrolledtext.ScrolledText] = None
        self._entry: Optional[tk.Entry] = None
        self._visible: bool = True
        self._sound_initialized = False
        self._sound_enabled = True
        
        # Notification type settings
        self._notification_settings = {
            "chat_messages": True,      # Player chat messages
            "server_messages": True,     # Server prints (svc_print)
            "string_package_prints": True,  # String package prints (svc_sp_print*)
            "sounds": True              # Audio notifications
        }
        
        # Message type patterns for filtering
        self._message_patterns = {
            "chat_messages": r"^\[\d+\]\s+\w+:\s+",  # [slot] name: message
            "server_messages": r"^\[PRINT\]\s+",      # [PRINT] message
            "string_package_prints": r"^\[(GENERAL|WEAPONS/ITEMS|SOFPLUS|dm_ctf|BOT|SOFPLUS_CUSTOM)\]\s+",  # String package prints
        }

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run_gui, name="ChatUIThread", daemon=True)
        self._thread.start()

    def post(self, message: str, play_sound: bool = False) -> None:
        # Thread-safe enqueue from game thread
        self._incoming.put((message, play_sound))
        # If called very early, UI thread may not have started yet.
        # Try to start lazily to ensure messages can be seen.
        if not self._thread or not self._thread.is_alive():
            self.start()

    # Internal methods
    def _run_gui(self) -> None:
        self._root = tk.Tk()
        self._root.title(self._title)
        self._root.geometry("600x500")  # Increased height for notification panel

        # Use grid to ensure proper layout
        self._root.rowconfigure(0, weight=1)  # Chat text area
        self._root.rowconfigure(1, weight=0)  # Notification panel
        self._root.rowconfigure(2, weight=0)  # Input row
        self._root.columnconfigure(0, weight=1)
        self._root.columnconfigure(1, weight=0)

        # Chat text area
        self._text = scrolledtext.ScrolledText(self._root, wrap=tk.WORD, state=tk.DISABLED)
        self._text.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=6, pady=(6, 3))

        # Notification settings panel
        self._create_notification_panel()
        
        # Input row
        self._entry = tk.Entry(self._root)
        self._entry.grid(row=2, column=0, sticky="ew", padx=(6, 0), pady=(0, 6))
        self._entry.bind("<Return>", self._on_enter)

        send_btn = tk.Button(self._root, text="Send", command=self._send_clicked)
        send_btn.grid(row=2, column=1, sticky="e", padx=(6, 6), pady=(0, 6))

        # Intercept window close to hide instead of destroy (avoid crashes on some platforms)
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._pump_incoming()
        try:
            self._root.mainloop()
        except Exception:
            pass

    def _create_notification_panel(self):
        """Create the notification settings panel with checkboxes"""
        # Create a frame for the notification panel
        notif_frame = ttk.LabelFrame(self._root, text="Notification Settings", padding="5")
        notif_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=6, pady=(0, 3))
        
        # Configure the frame to expand horizontally
        notif_frame.columnconfigure(0, weight=1)
        notif_frame.columnconfigure(1, weight=1)
        notif_frame.columnconfigure(2, weight=1)
        
        # Create checkboxes for each notification type
        row = 0
        col = 0
        for setting_name, default_value in self._notification_settings.items():
            if setting_name == "sounds":
                # Skip sounds checkbox for now, it's handled separately
                continue
                
            var = tk.BooleanVar(value=default_value)
            self._notification_settings[setting_name] = var
            
            # Create a more user-friendly label
            label = setting_name.replace("_", " ").title()
            if setting_name == "chat_messages":
                label = "Chat Messages"
            elif setting_name == "server_messages":
                label = "Server Messages"
            elif setting_name == "string_package_prints":
                label = "String Package Prints"
            
            cb = ttk.Checkbutton(notif_frame, text=label, variable=var, 
                               command=self._on_notification_setting_changed)
            cb.grid(row=row, column=col, sticky="w", padx=(0, 10))
            
            col += 1
            if col >= 3:  # 3 columns
                col = 0
                row += 1
        
        # Add a separator line
        separator = ttk.Separator(notif_frame, orient="horizontal")
        separator.grid(row=row+1, column=0, columnspan=3, sticky="ew", pady=(5, 0))

    def _on_notification_setting_changed(self):
        """Called when notification settings are changed"""
        # Update the internal settings dictionary with current checkbox values
        for setting_name, var in self._notification_settings.items():
            if isinstance(var, tk.BooleanVar):
                self._notification_settings[setting_name] = var.get()
        
        # Notify external handler if provided
        if self.on_settings_changed:
            self.on_settings_changed()

    def _should_show_message(self, message: str) -> bool:
        """Check if a message should be displayed based on notification settings"""
        import re
        
        # Check each message type pattern
        for msg_type, pattern in self._message_patterns.items():
            if re.match(pattern, message):
                return self._notification_settings.get(msg_type, True)
        
        # If no pattern matches, show the message (default behavior)
        return True

    def _should_play_sound(self, message: str, play_sound: bool) -> bool:
        """Check if sound should be played based on notification settings"""
        if not play_sound:
            return False
        
        # Only play sound if sounds are enabled AND the message should be shown
        return (self._notification_settings.get("sounds", True) and 
                self._should_show_message(message))

    def show(self) -> None:
        if self._root:
            try:
                self._root.deiconify()
                self._root.lift()
                self._root.focus_force()
                self._visible = True
                if self._entry:
                    self._entry.focus_set()
            except Exception:
                pass

    def hide(self) -> None:
        if self._root:
            try:
                self._root.withdraw()
                self._visible = False
            except Exception:
                pass

    def is_visible(self) -> bool:
        return bool(self._visible)

    def _append_text(self, message: str, play_sound: bool = False) -> None:
        if not self._text:
            return
        
        # Check if message should be displayed
        if not self._should_show_message(message):
            return
            
        self._text.configure(state=tk.NORMAL)
        self._text.insert(tk.END, message + "\n")
        self._text.see(tk.END)
        self._text.configure(state=tk.DISABLED)
        
        # Optional audio cue (no desktop bell)
        if self._should_play_sound(message, play_sound):
            self._play_sound()

    def _pump_incoming(self) -> None:
        if not self._root:
            return
        try:
            while True:
                msg, play_sound = self._incoming.get_nowait()
                self._append_text(msg, play_sound)
        except queue.Empty:
            pass
        self._root.after(100, self._pump_incoming)

    def _on_enter(self, event=None):
        self._send_clicked()

    def _send_clicked(self):
        if not self._entry:
            return
        text = self._entry.get().strip()
        if not text:
            return
        self._entry.delete(0, tk.END)
        try:
            self.on_send(text)
        except Exception:
            # Avoid crashing UI thread on send errors
            pass

    def _on_close(self):
        # Hide window instead of destroying to avoid segfaults due to thread-event loop teardown
        self.hide()

    def _play_sound(self):
        # Prefer system sound themes via canberra if available
        try:
            subprocess.Popen(["canberra-gtk-play", "-i", "message-new-instant"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except Exception:
            pass
        # Fallback to playing a standard freedesktop sound file via pygame if available
        if _HAS_PYGAME:
            try:
                if not self._sound_initialized:
                    pygame.mixer.init()
                    self._sound_initialized = True
                sound_path_candidates = [
                    "/usr/share/sounds/freedesktop/stereo/message-new-instant.oga",
                    "/usr/share/sounds/freedesktop/stereo/dialog-information.oga",
                ]
                sound = None
                for p in sound_path_candidates:
                    try:
                        sound = pygame.mixer.Sound(p)
                        break
                    except Exception:
                        continue
                if sound is not None:
                    sound.play()
            except Exception:
                pass

    # Public API
    def set_sound_enabled(self, enabled: bool) -> None:
        self._sound_enabled = bool(enabled)
        self._notification_settings["sounds"] = enabled

    def get_notification_settings(self) -> dict:
        """Get current notification settings"""
        return {k: v.get() if isinstance(v, tk.BooleanVar) else v 
                for k, v in self._notification_settings.items()}

    def set_notification_settings(self, settings: dict) -> None:
        """Set notification settings from external source"""
        for key, value in settings.items():
            if key in self._notification_settings:
                if isinstance(self._notification_settings[key], tk.BooleanVar):
                    self._notification_settings[key].set(value)
                else:
                    self._notification_settings[key] = value
