from vcdvcd import VCDVCD

class VCDParser:
    def __init__(self, filepath: str):
        """Initializes the parser by reading a standard VCD file."""
        self.vcd = VCDVCD(filepath, store_tvs=True)
        # Get a list of all hierarchical signal names
        self.signals = list(self.vcd.references_to_ids.keys())

    def get_signals(self) -> list[str]:
        """Returns a list of all signal names found in the VCD file."""
        return self.signals

    def get_signal_data(self, signal_name: str) -> dict:
        """Returns the width and value data for a given signal."""
        
        # --- THIS IS THE CORRECTED LOGIC ---
        # Instead of 'if signal_name not in self.vcd:', we check the
        # specific dictionary of references, which is more robust.
        if signal_name not in self.vcd.references_to_ids:
            return {}
        # ------------------------------------
            
        signal = self.vcd[signal_name]
        return {
            'width': signal.size,
            'values': signal.tv  # List of (time, value) tuples
        }
