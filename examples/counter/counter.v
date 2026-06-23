// SPDX-License-Identifier: ISC
module counter #(parameter WIDTH = 8) (
    input  wire             clk,
    input  wire             rst,
    output reg [WIDTH-1:0]  count
);
    always @(posedge clk)
        if (rst) count <= 0;
        else     count <= count + 1;
endmodule
