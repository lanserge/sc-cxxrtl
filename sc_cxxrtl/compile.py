# SPDX-License-Identifier: ISC
"""SiliconCompiler task: build a cocotb-driven CXXRTL simulation executable."""

import sys

from typing import Optional

from siliconcompiler import Task


class CxxrtlCocotbCompileTask(Task):
    '''
    Compiles RTL into a cocotb-driven CXXRTL simulation executable.

    Generates a CXXRTL model with Yosys and links it against the cxxrtl-vpi
    provider and cocotb's VPI runtime (via cxxrtl_vpi.cocotb_build). Outputs an
    executable ``outputs/<design>.vexe`` that is itself a VPI-speaking simulator;
    the downstream exec task runs it under cocotb.
    '''

    def __init__(self):
        super().__init__()

        self.add_parameter(
            "randomize_init", "bool",
            "if true, randomize uninitialized flip-flop state (Yosys "
            "'setundef -init -random'), the CXXRTL analogue of Verilator's "
            "--x-initial unique. CXXRTL otherwise inits to 0, hiding designs "
            "that rely on uninitialized state; vary [init_seed] across runs to "
            "expose them.",
            defvalue=False)
        self.add_parameter(
            "init_seed", "int",
            "integer seed for [randomize_init].",
            defvalue=1)

    def tool(self):
        return "cxxrtl"

    def task(self):
        return "cocotb_compile"

    def set_randomize_init(self, enable: bool = True, seed: Optional[int] = None,
                           step: Optional[str] = None, index: Optional[str] = None):
        """Enable randomized flop-init fuzzing, optionally setting the seed."""
        self.set("var", "randomize_init", enable, step=step, index=index)
        if seed is not None:
            self.set("var", "init_seed", seed, step=step, index=index)

    def setup(self):
        super().setup()

        self.set_threads()
        self.add_output_file(ext="vexe")

        self.add_required_key("var", "randomize_init")
        if self.get("var", "randomize_init"):
            self.add_required_key("var", "init_seed")

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
        randomize_init = self.get("var", "randomize_init")
        init_seed = self.get("var", "init_seed")
        if randomize_init:
            self.logger.info(f"randomizing flop init (seed {init_seed})")

        # SC runs run() in-process, so sys.executable is the SC interpreter —
        # the cocotb whose VPI we link must be the one we run the sim under.
        build_cocotb_sim(sources, top, f"outputs/{top}.vexe", python=sys.executable,
                         randomize_init=randomize_init, init_seed=init_seed)
        return 0
