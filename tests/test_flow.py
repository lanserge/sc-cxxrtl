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


@pytest.mark.eda
def test_example_end_to_end():
    """Run the counter example through SC -> cocotb on CXXRTL (needs yosys + cocotb)."""
    here = os.path.dirname(os.path.abspath(__file__))
    make = os.path.join(here, "..", "examples", "counter", "make.py")
    proc = subprocess.run([sys.executable, make], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "PASS: cocotb test ran on CXXRTL" in proc.stdout
