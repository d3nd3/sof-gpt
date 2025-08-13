import threading
import queue
import tkinter as tk
from tkinter import scrolledtext
from typing import Callable, Optional


class ChatUI:
    def __init__(self, on_send: Callable[[str], None]):
        self.on_send = on_send
        self._incoming: "queue.Queue[str]" = queue.Queue()
        self._thread: Optional[threading.Thread] = None
        self._root: Optional[tk.Tk] = None
        self._text: Optional[scrolledtext.ScrolledText] = None
        self._entry: Optional[tk.Entry] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run_gui, name="ChatUIThread", daemon=True)
        self._thread.start()

    def post(self, message: str) -> None:
        # Thread-safe enqueue from game thread
        self._incoming.put(message)

    # Internal methods
    def _run_gui(self) -> None:
        self._root = tk.Tk()
        self._root.title("SoF Chat")
        self._root.geometry("520x380")

        self._text = scrolledtext.ScrolledText(self._root, wrap=tk.WORD, state=tk.DISABLED)
        self._text.pack(fill=tk.BOTH, expand=True, padx=6, pady=(6, 3))

        frame = tk.Frame(self._root)
        frame.pack(fill=tk.X, padx=6, pady=(0, 6))

        self._entry = tk.Entry(frame)
        self._entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._entry.bind("<Return>", self._on_enter)

        send_btn = tk.Button(frame, text="Send", command=self._send_clicked)
        send_btn.pack(side=tk.LEFT, padx=(6, 0))

        self._pump_incoming()
        try:
            self._root.mainloop()
        except Exception:
            pass

    def _append_text(self, message: str) -> None:
        if not self._text:
            return
        self._text.configure(state=tk.NORMAL)
        self._text.insert(tk.END, message + "\n")
        self._text.see(tk.END)
        self._text.configure(state=tk.DISABLED)
        if self._root:
            try:
                self._root.bell()
            except Exception:
                pass

    def _pump_incoming(self) -> None:
        if not self._root:
            return
        try:
            while True:
                msg = self._incoming.get_nowait()
                self._append_text(msg)
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
