# SPDX-License-Identifier: ISC
"""SiliconCompiler task: build a cocotb-driven CXXRTL simulation executable."""

import sys

from siliconcompiler import Task


class CxxrtlCocotbCompileTask(Task):
    '''
    Compiles RTL into a cocotb-driven CXXRTL simulation executable.

    Generates a CXXRTL model with Yosys and links it against the cxxrtl-vpi
    provider and cocotb's VPI runtime (via cxxrtl_vpi.cocotb_build). Outputs an
    executable ``outputs/<design>.vexe`` that is itself a VPI-speaking simulator;
    the downstream exec task runs it under cocotb.
    '''

    def tool(self):
        return "cxxrtl"

    def task(self):
        return "cocotb_compile"

    def setup(self):
        super().setup()

        self.set_threads()
        self.add_output_file(ext="vexe")

        self.add_required_key("option", "design")
        self.add_required_key("option", "fileset")
        if self.project.get("option", "alias"):
            self.add_required_key("option", "alias")

        for lib, fileset in self.project.get_filesets():
            if lib.has_idir(fileset):
                self.add_required_key(lib, "fileset", fileset, "idir")
            if lib.get("fileset", fileset, "define"):
                self.add_required_key(lib, "fileset", fileset, "define")
            if lib.has_file(fileset=fileset, filetype="systemverilog"):
                self.add_required_key(lib, "fileset", fileset, "file", "systemverilog")
            if lib.has_file(fileset=fileset, filetype="verilog"):
                self.add_required_key(lib, "fileset", fileset, "file", "verilog")

    def run(self):
        from cxxrtl_vpi.cocotb_build import build_cocotb_sim

        sources = []
        for lib, fileset in self.project.get_filesets():
            sources.extend(lib.get_file(fileset=fileset, filetype="systemverilog"))
            sources.extend(lib.get_file(fileset=fileset, filetype="verilog"))

        if not sources:
            self.logger.error("no Verilog/SystemVerilog sources found")
            return 1

        top = self.design_topmodule
        # SC runs run() in-process, so sys.executable is the SC interpreter —
        # the cocotb whose VPI we link must be the one we run the sim under.
        build_cocotb_sim(sources, top, f"outputs/{top}.vexe", python=sys.executable)
        return 0
