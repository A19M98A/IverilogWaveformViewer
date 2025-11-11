import os
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Static, Checkbox
from vcd_parser import VCDParser
from widgets.file_browser import FileBrowser
from widgets.signal_list import SignalList
from widgets.waveform_view import WaveformDisplay

class WaveformApp(App):
    """A terminal-based waveform viewer."""
    CSS_PATH = "main.css"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("left", "pan_left", "Pan Left"),
        ("right", "pan_right", "Pan Right"),
        ("=", "zoom_in", "Zoom In"),
        ("-", "zoom_out", "Zoom Out"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="app-grid"):
            yield FileBrowser(os.getcwd(), id="file-browser")
            yield Container(Static("Load a .vcd file to see signals.", id="signal-list-label"), id="signal-list-container")
            yield WaveformDisplay()
        yield Footer()

    def on_directory_tree_file_selected(self, event: FileBrowser.FileSelected):
        file_path = str(event.path)
        if os.path.isfile(file_path) and file_path.endswith(".vcd"):
            self.parser = VCDParser(file_path)
            signals = self.parser.get_signals()
            signal_list_container = self.query_one("#signal-list-container")
            signal_list_container.remove_children()
            signal_list_container.mount(SignalList(signals))

    def on_tree_node_selected(self, event: FileBrowser.NodeSelected):
        if event.node.data.path.endswith(".."):
            parent_dir = os.path.abspath(os.path.join(self.query_one(FileBrowser).path, ".."))
            self.query_one(FileBrowser).path = parent_dir

    def on_checkbox_changed(self, event: Checkbox.Changed):
        waveform_display = self.query_one(WaveformDisplay)
        
        # --- THIS IS THE KEY CHANGE ---
        # The original, unsanitized name is stored in the checkbox's label.
        # This is much more reliable than trying to reverse the sanitization.
        original_signal_name = str(event.checkbox.label)
        
        if hasattr(self, 'parser'):
            if event.value:
                signal_data = self.parser.get_signal_data(original_signal_name)
                if signal_data:
                    waveform_display.add_signal(original_signal_name, signal_data)
            else:
                waveform_display.remove_signal(original_signal_name)
    
    def action_pan_left(self) -> None:
        self.query_one(WaveformDisplay).pan(-1)
    def action_pan_right(self) -> None:
        self.query_one(WaveformDisplay).pan(1)
    def action_zoom_in(self) -> None:
        self.query_one(WaveformDisplay).zoom(0.5)
    def action_zoom_out(self) -> None:
        self.query_one(WaveformDisplay).zoom(2.0)

if __name__ == "__main__":
    app = WaveformApp()
    app.run()
