# sc-cxxrtl

**A CXXRTL cocotb simulator for [SiliconCompiler](https://github.com/siliconcompiler/siliconcompiler) — installed, not patched in.**

`pip install sc-cxxrtl` adds the Yosys **CXXRTL** engine as a cocotb simulator to
SiliconCompiler **without modifying SiliconCompiler**. SC executes whatever
`Task`/`Flowgraph` subclasses a flow contains, and those live in this package —
so no SC source change is needed.

Built on:
- [**cxxrtl-vpi**](../cxxrtl-vpi) — the engine adapter that makes cocotb drive a
  CXXRTL model (an IEEE-1364 VPI implementation over `cxxrtl_capi`),
- **cocotb** ≥ 2.0 — the Python testbench framework,
- **Yosys** — `write_cxxrtl` + a C++ compiler (external, like every SC simulator).

## Use

```python
from siliconcompiler import Design, Project
from sc_cxxrtl import CxxrtlDVFlow

design = Design("counter")
with design.active_fileset("rtl"):
    design.set_topmodule("counter")
    design.add_file("counter.v")
with design.active_fileset("tb"):
    design.add_file("test_counter.py")   # a cocotb test (filetype: python)

proj = Project(design)
proj.add_fileset("rtl")
proj.add_fileset("tb")
proj.set_flow(CxxrtlDVFlow())             # <- the only line that mentions cxxrtl
proj.run()
```

The flow is two nodes:

```
compile   (cxxrtl/cocotb_compile)  RTL -> CXXRTL model -> link cxxrtl-vpi + cocotb -> outputs/<top>.vexe
   │
simulate  (cxxrtl/exec_cocotb)     run the executable under cocotb -> results.xml
```

A complete, runnable example is in [`examples/counter/`](examples/counter)
(`python make.py`). It passes:

```
test_counter.test_count_up     PASS
TESTS=1 PASS=1 FAIL=0 SKIP=0
PASS: cocotb test ran on CXXRTL via SiliconCompiler
```

## Why no SC patch is needed

SC's flow/task model is open by composition: a flow instantiates `Task`
subclasses, which may live in any installed package. `CxxrtlDVFlow` wires
`CxxrtlCocotbCompileTask` + `CxxrtlCocotbExecTask` (the latter reuses SC's own
`CocotbTask` for environment setup, exactly like the built-in `verilator-cocotb`
tasks). The only thing SC's *built-in* `DVFlow(tool=…)` can't do is grow a
`"cxxrtl"` branch on its own — which is why this package ships its own flow.
(Making the built-in `DVFlow` auto-discover plugins via a `siliconcompiler.flows`
entry-point group would be a small, generic upstream contribution.)

## License

ISC.
