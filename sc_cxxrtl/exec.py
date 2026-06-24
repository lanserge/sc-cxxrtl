# SPDX-License-Identifier: ISC
"""SiliconCompiler task: run a cocotb testbench on a compiled CXXRTL sim."""

from typing import Optional

from siliconcompiler.tools._common.cocotb.cocotb_task import CocotbTask
from siliconcompiler.tools.execute.exec_input import ExecInputTask


class CxxrtlCocotbExecTask(CocotbTask, ExecInputTask):
    '''
    Runs a cocotb testbench against the compiled CXXRTL simulation executable.

    The executable from the compile task is a self-contained VPI simulator with
    cocotb's runtime linked in (it finds its libs via rpath). This task runs it
    with the cocotb environment that :class:`CocotbTask` sets up
    (COCOTB_TOPLEVEL, COCOTB_TEST_MODULES, …), so Python test modules added with
    the "python" filetype are executed. With [trace] enabled it also dumps a VCD
    waveform to ``reports/<design>.vcd``.
    '''

    def __init__(self):
        super().__init__()

        self.add_parameter(
            "trace", "bool",
            "if true, dump a VCD waveform of all signals to reports/<design>.vcd",
            defvalue=False)

    def tool(self):
        return "cxxrtl"

    def set_trace(self, enable: bool = True,
                  step: Optional[str] = None, index: Optional[str] = None):
        """Enable or disable VCD waveform tracing."""
        self.set("var", "trace", enable, step=step, index=index)

    def setup(self):
        # CocotbTask.setup (env + results.xml + python files) and
        # ExecInputTask.setup (run the single input executable) both run via the
        # MRO super() chain.
        super().setup()

        self.add_required_key("var", "trace")
        if self.get("var", "trace"):
            # The harness dumps a VCD when CXXRTL_VPI_VCD is set (cxxrtl-vpi);
            # write it under reports/, the SC convention for waveforms.
            vcd = f"reports/{self.design_topmodule}.vcd"
            self.set_environmentalvariable("CXXRTL_VPI_VCD", vcd)
            self.add_required_key("env", "CXXRTL_VPI_VCD")
