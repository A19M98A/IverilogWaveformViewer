# Terminal Waveform Viewer

A modern, terminal-based application for visualizing digital logic simulation waveforms. Inspired by professional tools like GTKWave but designed to run entirely within a modern terminal, this viewer provides a fast, lightweight, and keyboard-driven way to inspect Verilog simulation results without leaving the command line.

The application is built in Python using the powerful [`textual`](https://textual.textualize.io/) TUI framework.

![Final Application Screenshot](https://storage.googleapis.com/agent-tools-public-images/01HK21HHY0A7A1J4J47E02A1R8)

## 🌟 Features

*   **Modern TUI Experience:** A responsive, mouse-aware, and keyboard-driven interface.
*   **Built-in File Browser:** Navigate your filesystem, including parent directories (`..`), to locate and load standard **Value Change Dump (`.vcd`)** files.
*   **Multi-Pane, Synchronized Layout:**
    *   **Signal List:** A checklist of all signals found in the loaded `.vcd` file.
    *   **Names Pane:** A fixed-position pane that lists the names of all currently displayed signals.
    *   **Values Pane:** A fixed-position pane showing the value of each signal at the current cursor time.
    *   **Waveform Pane:** A horizontally and vertically scrollable pane that graphically renders the signal waveforms.
    *   **Timeline Pane:** A scrollable timeline header that stays perfectly synchronized with the waveform pane.
*   **Interactive Waveform Analysis:**
    *   **Pan & Scroll:** Scroll horizontally through time using the **arrow keys** or your mouse.
    *   **Zoom:** Zoom in and out of the timeline using the **-** and **=** keys for detailed inspection.
    *   **Time Cursor:** **Click** anywhere on the timeline or a waveform to instantly move the vertical cursor and update the value display in real-time.
*   **Professional Waveform Rendering:**
    *   **Single-Bit Signals:** Clear rendering of high (`─`) and low (`_`) states with sharp vertical lines (`│`) to highlight transitions.
    *   **Multi-Bit Buses:** Rendered as a solid line (`=`), with changing hexadecimal values displayed directly within the waveform.
    *   **Color-Coded Signals:** Each signal is assigned a unique color for excellent readability.

## 🛠️ Technology Stack

*   **Language:** Python 3
*   **TUI Framework:** `textual`
*   **VCD Parsing:** `vcdvcd`

## 🚀 Getting Started

### Prerequisites

*   Python 3.8+
*   A Verilog simulator capable of producing `.vcd` files (e.g., [Icarus Verilog](http://iverilog.icarus.com/), Verilator, Vivado).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd terminal-waveform-viewer
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    # On Windows, use: venv\Scripts\activate
    ```

3.  **Install the dependencies:** Create a file named `requirements.txt` in your project directory with the following content:
    
    **`requirements.txt`**
    ```
    textual==0.58.0
    vcdvcd==1.2.1
    ```

    Then, install the requirements:
    ```bash
    pip install -r requirements.txt
    ```

## 🏃 How to Use

#### Step 1: Generate a `.vcd` File

Your Verilog simulation needs to be instructed to create a Value Change Dump file. Add the following system tasks to your main testbench file (e.g., `tb_fifo.v`).

```verilog
`timescale 1ns / 1ps

module tb_fifo;
  // ... signal declarations ...
  // ... module instantiation ...

  initial begin
    // ------------ ADD THESE TWO LINES ------------
    $dumpfile("fifo_waveform.vcd");
    $dumpvars(0, tb_fifo); // Use the name of YOUR testbench module here
    // -------------------------------------------

    // ... rest of your testbench stimulus ...
    rst = 1;
    #15;
    rst = 0;
    // ...
  end
 
endmodule
```

#### Step 2: Run the Simulation

Compile and run your Verilog code as you normally would. For Icarus Verilog, the commands are:

```bash
# Compile the Verilog files into a simulation executable
iverilog -o my_sim fifo.v tb_fifo.v

# Run the simulation
vvp my_sim
```
After this step, a new file named `fifo_waveform.vcd` will be created in your directory. **This is the file you will open.**

#### Step 3: Launch the Viewer

Run the main Python application:
```bash
python main.py
```

Use the built-in file browser to navigate to and select your `fifo_waveform.vcd` file. Signals will appear in the top-right panel. Check the boxes to add them to the waveform display.

## ⌨️ Controls

| Key           | Action                                 |
|---------------|----------------------------------------|
| `←` / `→`     | Pan the timeline and waves left/right. |
| `=`           | Zoom In.                               |
| `-`           | Zoom Out.                              |
| `q`           | Quit the application.                  |
| **Mouse Click** | Move the time cursor to the clicked location. |
| **Mouse Scroll**| Scroll panes vertically or horizontally. |

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
