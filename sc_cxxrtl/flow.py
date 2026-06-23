# SPDX-License-Identifier: ISC
"""A cocotb DV flow for the CXXRTL simulator: compile -> simulate."""

from siliconcompiler import Flowgraph

from sc_cxxrtl.compile import CxxrtlCocotbCompileTask
from sc_cxxrtl.exec import CxxrtlCocotbExecTask


class CxxrtlDVFlow(Flowgraph):
    '''
    Compiles a design into a cocotb-driven CXXRTL simulation and runs the cocotb
    testbench. Mirrors SiliconCompiler's built-in verilator-cocotb flow, but for
    the Yosys CXXRTL engine — and lives out-of-tree, so installing this package
    adds the simulator without modifying SiliconCompiler.

    Args:
        name (str): flow name (default "cxxrtl-cocotb").
        np (int): number of parallel simulation jobs.
    '''
    def __init__(self, name: str = None, np: int = 1):
        if name is None:
            name = "cxxrtl-cocotb"
        super().__init__(name)

        self.node("compile", CxxrtlCocotbCompileTask())
        sim_task = CxxrtlCocotbExecTask()
        for n in range(np):
            self.node("simulate", sim_task, index=n)
            self.edge("compile", "simulate", head_index=n)
