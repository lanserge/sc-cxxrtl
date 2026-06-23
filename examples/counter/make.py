# SPDX-License-Identifier: ISC
"""
Run a cocotb test on the counter through SiliconCompiler + the CXXRTL simulator,
with no changes to SiliconCompiler itself.

    python make.py
"""

import os.path

from siliconcompiler import Design, Project
from sc_cxxrtl import CxxrtlDVFlow


def main():
    here = os.path.dirname(os.path.abspath(__file__))

    design = Design("counter")
    design.set_dataroot("root", here)
    with design.active_fileset("rtl"), design.active_dataroot("root"):
        design.set_topmodule("counter")
        design.add_file("counter.v")
    with design.active_fileset("tb"), design.active_dataroot("root"):
        design.add_file("test_counter.py")

    proj = Project(design)
    proj.add_fileset("rtl")
    proj.add_fileset("tb")
    proj.set_flow(CxxrtlDVFlow())

    assert proj.run(), "run() failed"

    errors = proj.history("job0").get("metric", "errors", step="simulate", index="0")
    print(f"\ncocotb errors: {errors}")
    assert errors == 0, "cocotb test failed"
    print("PASS: cocotb test ran on CXXRTL via SiliconCompiler")


if __name__ == "__main__":
    main()
