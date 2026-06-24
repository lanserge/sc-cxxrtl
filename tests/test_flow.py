# SPDX-License-Identifier: ISC
import os.path
import subprocess
import sys

import pytest


def test_flow_construction():
    """The flow builds and wires the cxxrtl tasks without any EDA tools."""
    from sc_cxxrtl import CxxrtlDVFlow, CxxrtlCocotbCompileTask, CxxrtlCocotbExecTask

    flow = CxxrtlDVFlow()
    assert flow.name == "cxxrtl-cocotb"

    compile_task = CxxrtlCocotbCompileTask()
    assert compile_task.tool() == "cxxrtl"
    assert compile_task.task() == "cocotb_compile"

    exec_task = CxxrtlCocotbExecTask()
    assert exec_task.tool() == "cxxrtl"
    assert exec_task.task() == "exec_cocotb"


def test_randomize_init_param():
    """The init-fuzzing flow option is exposed on the compile task."""
    from sc_cxxrtl import CxxrtlCocotbCompileTask

    task = CxxrtlCocotbCompileTask()
    assert task.get("var", "randomize_init") is False
    assert task.get("var", "init_seed") == 1

    task.set_randomize_init(True, seed=42)
    assert task.get("var", "randomize_init") is True
    assert task.get("var", "init_seed") == 42


def test_trace_param():
    """The VCD trace flow option is exposed on the exec task."""
    from sc_cxxrtl import CxxrtlCocotbExecTask

    task = CxxrtlCocotbExecTask()
    assert task.get("var", "trace") is False
    task.set_trace(True)
    assert task.get("var", "trace") is True


def _bound_compile_task(proj):
    """A CxxrtlCocotbCompileTask bound to `proj` (so self.project is set)."""
    from siliconcompiler.scheduler import SchedulerNode
    from sc_cxxrtl import CxxrtlCocotbCompileTask

    task = CxxrtlCocotbCompileTask()
    node = SchedulerNode(proj, "compile", "0")
    with task.runtime(node) as rt:  # runtime() yields a bound copy of the task
        return {fs for _lib, fs in rt._rtl_filesets()}


def test_tool_fileset_aware(tmp_path):
    """When the design defines a 'cxxrtl' fileset, the compile task sources RTL
    from that fileset's subtree (cxxrtl + its rtl dep), excluding other tool
    filesets such as 'verilator'."""
    from siliconcompiler import Design, Project
    from sc_cxxrtl import CxxrtlDVFlow

    (tmp_path / "dut.v").write_text("module dut(input a, output b); assign b=a; endmodule\n")
    (tmp_path / "vshim.v").write_text("module vshim(); endmodule\n")

    design = Design("dut")
    design.set_dataroot("root", str(tmp_path))
    with design.active_fileset("rtl"), design.active_dataroot("root"):
        design.set_topmodule("dut")
        design.add_file("dut.v")
    with design.active_fileset("cxxrtl"):
        design.add_depfileset(design, "rtl")
    with design.active_fileset("verilator"), design.active_dataroot("root"):
        design.add_depfileset(design, "rtl")
        design.add_file("vshim.v")  # tool-specific source CXXRTL must not see

    proj = Project(design)
    for fs in ("rtl", "cxxrtl", "verilator"):
        proj.add_fileset(fs)
    proj.set_flow(CxxrtlDVFlow())

    assert _bound_compile_task(proj) == {"cxxrtl", "rtl"}


def test_tool_fileset_fallback(tmp_path):
    """Without a 'cxxrtl' fileset, the compile task uses all active filesets."""
    from siliconcompiler import Design, Project
    from sc_cxxrtl import CxxrtlDVFlow

    (tmp_path / "dut.v").write_text("module dut(input a, output b); assign b=a; endmodule\n")

    design = Design("dut")
    design.set_dataroot("root", str(tmp_path))
    with design.active_fileset("rtl"), design.active_dataroot("root"):
        design.set_topmodule("dut")
        design.add_file("dut.v")

    proj = Project(design)
    proj.add_fileset("rtl")
    proj.set_flow(CxxrtlDVFlow())

    assert _bound_compile_task(proj) == {"rtl"}


@pytest.mark.eda
def test_example_end_to_end():
    """Run the counter example through SC -> cocotb on CXXRTL (needs yosys + cocotb)."""
    here = os.path.dirname(os.path.abspath(__file__))
    make = os.path.join(here, "..", "examples", "counter", "make.py")
    proc = subprocess.run([sys.executable, make], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "PASS: cocotb test ran on CXXRTL" in proc.stdout
