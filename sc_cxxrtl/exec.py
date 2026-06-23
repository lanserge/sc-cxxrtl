# SPDX-License-Identifier: ISC
"""SiliconCompiler task: run a cocotb testbench on a compiled CXXRTL sim."""

from siliconcompiler.tools._common.cocotb.cocotb_task import CocotbTask
from siliconcompiler.tools.execute.exec_input import ExecInputTask


class CxxrtlCocotbExecTask(CocotbTask, ExecInputTask):
    '''
    Runs a cocotb testbench against the compiled CXXRTL simulation executable.

    The executable from the compile task is a self-contained VPI simulator with
    cocotb's runtime linked in (it finds its libs via rpath and enables inertial
    writes itself). This task just runs it with the cocotb environment that
    :class:`CocotbTask` sets up (COCOTB_TOPLEVEL, COCOTB_TEST_MODULES, …), so
    Python test modules added with the "python" filetype are executed.
    '''

    def tool(self):
        return "cxxrtl"

    def setup(self):
        # CocotbTask.setup (env + results.xml + python files) and
        # ExecInputTask.setup (run the single input executable) both run via the
        # MRO super() chain.
        super().setup()
