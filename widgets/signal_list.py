import re
from textual.widgets import Checkbox
from textual.containers import VerticalScroll

class SignalList(VerticalScroll):
    """A widget to display a scrollable list of signals with checkboxes."""
    def __init__(self, signals):
        super().__init__()
        self.signals = signals

    def _sanitize_id(self, name: str) -> str:
        """Replaces all invalid ID characters with underscores."""
        # Replace '.', '[', ']', ':', and spaces with '_'
        return re.sub(r'[.\[\]:\s]', '_', name)

    def compose(self):
        """Creates checkboxes for each signal."""
        for signal_name in self.signals:
            label = signal_name
            # Sanitize the full signal name to create a valid ID
            sanitized_id = self._sanitize_id(signal_name)
            
            yield Checkbox(label, id=sanitized_id)
