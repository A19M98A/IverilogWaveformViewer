from textual.containers import Horizontal, Vertical
from textual.widgets import Static
from rich.text import Text
from textual.reactive import reactive
from textual.events import Click
from textual.geometry import Size
from textual.scroll_view import ScrollView

# --- Color Palette ---
COLORS = ["bright_green", "bright_cyan", "bright_magenta", "bright_yellow", "bright_blue", "bright_red"]

# --- Helper Function for Formatting Time ---
def format_time(time_ps: int) -> str:
    if time_ps == 0: return "0.0ps"
    if time_ps < 1000: return f"{time_ps}ps"
    if time_ps < 1_000_000: return f"{time_ps/1000:.1f}ns"
    if time_ps < 1_000_000_000: return f"{time_ps/1_000_000:.1f}us"
    return f"{time_ps/1_000_000_000:.1f}ms"

# --- Main Display Container ---

class WaveformDisplay(Static):
    """The main container that holds and synchronizes all waveform components."""
    
    cursor_time = reactive(0)
    time_per_char = reactive(8000)
    start_time = reactive(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.signals = {}; self.sorted_signals = []; self.signal_colors = {}
        self.color_index = 0; self.end_time = 0; self._is_scrolling = False
        self.name_width = 30; self.value_width = 15

    # --- Child Widgets with Correct Event Handlers ---
    class NamesPane(ScrollView):
        def __init__(self, main_display, **kwargs):
            super().__init__(**kwargs); self.main_display = main_display
        def on_scroll(self): self.main_display.sync_scroll(self)
        def render(self) -> Text: return self.main_display.render_names()

    class ValuesPane(ScrollView):
        def __init__(self, main_display, **kwargs):
            super().__init__(**kwargs); self.main_display = main_display
        def on_scroll(self): self.main_display.sync_scroll(self)
        def render(self) -> Text: return self.main_display.render_values()

    class WavesPane(ScrollView):
        def __init__(self, main_display, **kwargs):
            super().__init__(**kwargs); self.main_display = main_display
        def on_scroll(self): self.main_display.sync_scroll(self)
        def on_click(self, event: Click): self.main_display.set_cursor_from_click(event)
        def render(self) -> Text: return self.main_display.render_waves()

    class TimelinePane(ScrollView):
        def __init__(self, main_display, **kwargs):
            super().__init__(**kwargs); self.main_display = main_display
        def on_scroll(self): self.main_display.sync_scroll(self)
        def on_click(self, event: Click): self.main_display.set_cursor_from_click(event)
        def render(self) -> Text: return self.main_display.render_timeline()

    class Cursor(Static):
        def render(self) -> Text: return Text("│" * self.size.height, style="bold yellow")

    def compose(self) -> None:
        with Vertical():
            with Horizontal(id="header-container"):
                yield Static(id="timeline-spacer")
                yield self.TimelinePane(self, id="timeline-pane")
            with Horizontal(id="data-container"):
                yield self.NamesPane(self, id="names-pane")
                yield self.ValuesPane(self, id="values-pane")
                yield self.WavesPane(self, id="wave-pane")
        yield self.Cursor(id="cursor")

    def add_signal(self, name: str, data: dict):
        if name not in self.signals:
            self.signals[name] = data; self.sorted_signals = sorted(self.signals.keys())
            self.signal_colors[name] = COLORS[self.color_index % len(COLORS)]; self.color_index += 1
            if data['values'] and data['values'][-1][0] > self.end_time: self.end_time = data['values'][-1][0]
            self.update_panes()

    def remove_signal(self, name: str):
        if name in self.signals:
            del self.signals[name]; self.sorted_signals = sorted(self.signals.keys())
            del self.signal_colors[name]
            self.update_panes()

    def _get_value_at_time(self, data: list, time: int) -> str:
        current_value = 'x'; value_tuple = ('x', 'z')
        for t, v in data:
            if t <= time: current_value = v
            else: break
        return value_tuple[current_value] if isinstance(current_value, int) else current_value

    def _find_next_change_time(self, data: list, time: int) -> int:
        for t, v in data:
            if t > time: return t
        return self.end_time + self.time_per_char

    def update_panes(self):
        v_size = Size(max(50, int(self.end_time / self.time_per_char) + 50), len(self.signals))
        for pane_class in (self.NamesPane, self.ValuesPane, self.WavesPane, self.TimelinePane):
            pane = self.query_one(pane_class)
            pane.virtual_size = v_size
            pane.refresh()

    def watch_cursor_time(self, time: int):
        self.query_one(self.ValuesPane).refresh()
        self.update_cursor()

    def render_names(self) -> Text:
        text = Text()
        for i, name in enumerate(self.sorted_signals):
            text.append(f"{name}", style=self.signal_colors.get(name, "white"))
            if i < len(self.sorted_signals) - 1: text.append("\n")
        return text

    def render_values(self) -> Text:
        text = Text()
        for i, name in enumerate(self.sorted_signals):
            data = self.signals[name]
            val = self._get_value_at_time(data['values'], self.cursor_time)
            display_val = f" {int(val, 2):X}" if val not in ('x', 'z') else f" {val}"
            text.append(display_val, style=f"bold {self.signal_colors.get(name, 'white')}")
            if i < len(self.sorted_signals) - 1: text.append("\n")
        return text
    
    def render_waves(self) -> Text:
        wave_lines = []
        for name in self.sorted_signals:
            data, color = self.signals[name], self.signal_colors.get(name, "white")
            line = Text(no_wrap=True, end="")
            char_x, current_time = 0, self.start_time
            width = self.query_one(self.WavesPane).virtual_size.width
            while char_x < width:
                val = self._get_value_at_time(data['values'], current_time)
                next_change = self._find_next_change_time(data['values'], current_time)
                chars_until_change = max(1, int((next_change - current_time) / self.time_per_char))
                if data['width'] == 1:
                    prev_val = self._get_value_at_time(data['values'], current_time - self.time_per_char)
                    transition_char = "│" if val != prev_val and current_time > 0 else " "
                    if val == '0': char = "_"
                    elif val == '1': char = "─"
                    elif val == 'x': char = "▒"
                    else: char = " "
                    style = color if val in ('0', '1') else "bright_red" if val == 'x' else "dim " + color
                    line.append(transition_char if char_x > 0 else char, style=style); line.append(char * (chars_until_change - 1), style=style)
                else:
                    hex_val = f"{int(val, 2):X}" if val not in ('x', 'z') else val.upper()
                    bus_text = f" {hex_val} "
                    line.append("=", style=color)
                    if len(bus_text) <= chars_until_change - 2:
                        line.append(Text(bus_text.center(chars_until_change - 2, " "), style=f"reverse {color}"))
                    else:
                        line.append("=" * (chars_until_change - 2), style=color)
                    line.append("=", style=color)
                char_x += chars_until_change; current_time += chars_until_change * self.time_per_char
            wave_lines.append(line)
        return Text("\n").join(wave_lines)

    def render_timeline(self) -> Text:
        width, text = self.query_one(self.TimelinePane).virtual_size.width, Text(no_wrap=True)
        spacing_time = 12 * self.time_per_char
        if spacing_time <= 0: return text
        first_tick = (self.start_time // spacing_time + 1) * spacing_time
        current_tick = first_tick
        while True:
            pos = int((current_tick - self.start_time) / self.time_per_char)
            if pos >= width: break
            label = f"| {format_time(int(current_tick))}"
            if pos >= 0: text.pad_left(pos - len(text)); text.append(label)
            current_tick += spacing_time
        return text

    def sync_scroll(self, source: ScrollView):
        """The master scroll handler called by child panes."""
        if self._is_scrolling: return
        self._is_scrolling = True
        for pane in self.query(ScrollView):
            if pane is not source and pane.scroll_y != source.scroll_y:
                pane.scroll_y = source.scroll_y
        wave_pane = self.query_one(self.WavesPane)
        timeline_pane = self.query_one(self.TimelinePane)
        if source is wave_pane and timeline_pane.scroll_x != wave_pane.scroll_x:
            timeline_pane.scroll_x = wave_pane.scroll_x
        elif source is timeline_pane and wave_pane.scroll_x != timeline_pane.scroll_x:
            wave_pane.scroll_x = timeline_pane.scroll_x
        self.start_time = self.query_one(self.WavesPane).scroll_x * self.time_per_char
        self.refresh_scrolled_panes()
        self._is_scrolling = False

    def refresh_scrolled_panes(self):
        self.query_one(self.WavesPane).refresh()
        self.query_one(self.TimelinePane).refresh()
        self.update_cursor()

    def set_cursor_from_click(self, event: Click):
        pane = event.widget
        self.cursor_time = int((pane.scroll_x + event.x) * self.time_per_char)

    def update_cursor(self):
        cursor, wave_pane = self.query_one(self.Cursor), self.query_one(self.WavesPane)
        time_span = wave_pane.size.width * self.time_per_char
        if self.start_time <= self.cursor_time < self.start_time + time_span:
            cursor.styles.display = "block"
            cursor_x = int((self.cursor_time - self.start_time) / self.time_per_char)
            cursor.styles.offset = (cursor_x + self.name_width + self.value_width, 1)
        else:
            cursor.styles.display = "none"

    def pan(self, direction: int):
        self.query_one(self.WavesPane).scroll_by(x=direction * int(self.query_one(self.WavesPane).size.width * 0.2), animate=False)

    def zoom(self, factor: float):
        self.time_per_char = max(1, int(self.time_per_char * factor))
        self.update_panes()
