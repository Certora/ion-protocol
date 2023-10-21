// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.21;

import { Test } from "forge-std/Test.sol";
import { LidoLibrary } from "../../src/libraries/LidoLibrary.sol";
import { ILidoWStEthDeposit } from "../../src/interfaces/DepositInterfaces.sol";
import { ILidoStEthDeposit } from "../../src/interfaces/DepositInterfaces.sol";
import { IERC20 } from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

import { safeconsole as console } from "forge-std/safeconsole.sol";

contract LidoLibrary_DifferentialTest is Test {
    ILidoWStEthDeposit private constant MAINNET_WSTETH = ILidoWStEthDeposit(0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0);

    function setUp() external {
        vm.createSelectFork(vm.envString("MAINNET_RPC_URL"));
    }

    // Checks that ethAmountIn given by function
    function testDifferential_getEthAmountInForLstAmount(uint256 lstAmount) external {
        vm.assume(lstAmount != 0);
        vm.assume(lstAmount < type(uint128).max);

        uint256 ethAmountIn = LidoLibrary.getEthAmountInForLstAmount(MAINNET_WSTETH, lstAmount);

        ILidoStEthDeposit stEth = ILidoStEthDeposit(MAINNET_WSTETH.stETH());
        vm.assume(ethAmountIn < stEth.getCurrentStakeLimit());

        (bool success,) = address(MAINNET_WSTETH).call{ value: ethAmountIn }("");
        require(success, "Failed transfer");
        assertEq(IERC20(address(MAINNET_WSTETH)).balanceOf(address(this)), lstAmount);
    }
}
