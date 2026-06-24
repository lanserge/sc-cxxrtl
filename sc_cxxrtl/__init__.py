# SPDX-License-Identifier: ISC
"""
sc-cxxrtl: SiliconCompiler glue for the CXXRTL cocotb simulator.

Installing this package adds a CXXRTL cocotb simulator to SiliconCompiler
*without modifying SiliconCompiler* — SC executes any Task/Flowgraph subclasses
a flow contains, and these live here. Use it by setting the flow on a project:

    from sc_cxxrtl import CxxrtlDVFlow
    proj.set_flow(CxxrtlDVFlow())
    proj.run()

Built on cxxrtl-vpi (the engine adapter) + cocotb.
"""

from sc_cxxrtl.compile import CxxrtlCocotbCompileTask
from sc_cxxrtl.exec import CxxrtlCocotbExecTask
from sc_cxxrtl.flow import CxxrtlDVFlow

__version__ = "0.0.1"
__all__ = ["CxxrtlCocotbCompileTask", "CxxrtlCocotbExecTask", "CxxrtlDVFlow"]
