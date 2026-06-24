# sc-cxxrtl

**A CXXRTL cocotb simulator for [SiliconCompiler](https://github.com/siliconcompiler/siliconcompiler) — installed, not patched in.**

`pip install sc-cxxrtl` adds the Yosys **CXXRTL** engine as a cocotb simulator to
SiliconCompiler **without modifying SiliconCompiler**. SC executes whatever
`Task`/`Flowgraph` subclasses a flow contains, and those live in this package —
so no SC source change is needed.

Built on:
- [**cxxrtl-vpi**](https://github.com/lanserge/cxxrtl-vpi) — the engine adapter
  that makes cocotb drive a CXXRTL model (an IEEE-1364 VPI implementation over
  `cxxrtl_capi`),
- **cocotb** ≥ 2.0 — the Python testbench framework,
- **Yosys** — `write_cxxrtl` + a C++ compiler (external, like every SC simulator).

## Install

Not on PyPI yet — install both packages from source (cocotb requires Python
≤ 3.13):

```sh
pip install git+https://github.com/lanserge/cxxrtl-vpi
pip install git+https://github.com/lanserge/sc-cxxrtl
```

You also need **Yosys** (`yosys` / `yosys-config`) and a **C++ compiler** on
`PATH` — the same external precondition as every SiliconCompiler simulator. See
[cxxrtl-vpi](https://github.com/lanserge/cxxrtl-vpi) for toolchain details.

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

### Init fuzzing (X-dependence detection)

CXXRTL is 2-state and inits flop state to 0, so a design that secretly relies on
uninitialized state passes silently. The compile task exposes Verilator-style
`--x-initial unique` fuzzing:

```python
from sc_cxxrtl import CxxrtlCocotbCompileTask
CxxrtlCocotbCompileTask.find_task(proj).set_randomize_init(True, seed=42)
```

This seeds uninitialized flops with `setundef -init -random`; vary the seed
across runs to expose X-dependence.

### Waveform tracing

Enable a VCD dump (written to `reports/<design>.vcd`) on the exec task:

```python
from sc_cxxrtl import CxxrtlCocotbExecTask
CxxrtlCocotbExecTask.find_task(proj).set_trace(True)
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
