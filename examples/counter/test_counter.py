# SPDX-License-Identifier: ISC
"""cocotb testbench for the counter, run via SiliconCompiler + sc-cxxrtl."""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge


@cocotb.test()
async def test_count_up(dut):
    """Reset, then check the counter increments each clock."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    for _ in range(2):
        await RisingEdge(dut.clk)
    dut.rst.value = 0

    await RisingEdge(dut.clk)
    prev = int(dut.count.value)
    for _ in range(10):
        await RisingEdge(dut.clk)
        cur = int(dut.count.value)
        assert cur == (prev + 1) & 0xFF, f"expected {(prev + 1) & 0xFF}, got {cur}"
        prev = cur
