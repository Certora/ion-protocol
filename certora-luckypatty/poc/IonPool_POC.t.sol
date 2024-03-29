// SPDX-License-Identifier: MIT
pragma solidity 0.8.21;

import { IonPool } from "../../src/IonPool.sol";
import { RAY, WadRayMath } from "../../src/libraries/math/WadRayMath.sol";
import { InterestRate, IlkData } from "../../src/InterestRate.sol";
import { SpotOracle } from "../../src/oracles/spot/SpotOracle.sol";
import { Whitelist } from "../../src/Whitelist.sol";
import { RewardModule } from "../../src/reward/RewardModule.sol";

import { IIonPoolEvents } from "../helpers/IIonPoolEvents.sol";

// import modified file
import { IonPoolSharedSetup } from "./IonPoolSharedSetup.sol";

import { ERC20PresetMinterPauser } from "../helpers/ERC20PresetMinterPauser.sol";

import { Strings } from "@openzeppelin/contracts/utils/Strings.sol";
import { IAccessControl } from "@openzeppelin/contracts/access/IAccessControl.sol";
import { PausableUpgradeable } from "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";

using Strings for uint256;
using WadRayMath for uint256;

contract IonPool_POC is IonPoolSharedSetup, IIonPoolEvents {
    function setUp() public override {
        super.setUp();

        ERC20PresetMinterPauser(_getUnderlying()).mint(lender1, INITIAL_LENDER_UNDERLYING_BALANCE);
        ERC20PresetMinterPauser(_getUnderlying()).mint(lender2, INITIAL_LENDER_UNDERLYING_BALANCE);

        vm.startPrank(lender2);
        underlying.approve(address(ionPool), type(uint256).max);
        ionPool.supply(lender2, INITIAL_LENDER_UNDERLYING_BALANCE, new bytes32[](0));
        vm.stopPrank();

        vm.prank(lender1);
        underlying.approve(address(ionPool), type(uint256).max);

        for (uint256 i = 0; i < ionPool.ilkCount(); i++) {
            ERC20PresetMinterPauser collateral = ERC20PresetMinterPauser(address(collaterals[i]));
            collateral.mint(borrower1, INITIAL_BORROWER_COLLATERAL_BALANCE);

            vm.startPrank(borrower1);
            collaterals[i].approve(address(gemJoins[i]), type(uint256).max);
            gemJoins[i].join(borrower1, INITIAL_BORROWER_COLLATERAL_BALANCE);
            vm.stopPrank();
        }
    }

    function test_CalculateRewardAndDebtDistribution_Issue() external {
        uint256 collateralDepositAmount = 10e18;
        uint256 normalizedBorrowAmount = 5e18;

        for (uint8 i = 0; i < ionPool.ilkCount(); i++) {
            vm.prank(borrower1);

            ionPool.depositCollateral(i, borrower1, borrower1, collateralDepositAmount, new bytes32[](0));

            uint256 rate = ionPool.rate(i);
            uint256 liquidityBefore = ionPool.weth();

            assertEq(ionPool.collateral(i, borrower1), collateralDepositAmount);
            assertEq(underlying.balanceOf(borrower1), normalizedBorrowAmount.rayMulDown(rate) * i);

            vm.prank(borrower1);

            ionPool.borrow(i, borrower1, borrower1, normalizedBorrowAmount, new bytes32[](0));

            uint256 liquidityRemoved = normalizedBorrowAmount.rayMulDown(rate);

            assertEq(ionPool.normalizedDebt(i, borrower1), normalizedBorrowAmount);
            assertEq(ionPool.totalNormalizedDebt(i), normalizedBorrowAmount);
            assertEq(ionPool.weth(), liquidityBefore - liquidityRemoved);
            assertEq(underlying.balanceOf(borrower1), normalizedBorrowAmount.rayMulDown(rate) * (i + 1));
        }

        vm.warp(block.timestamp + 1 hours);
        
        // expect overflow panic
        bytes memory panicCode = abi.encodeWithSelector(bytes4(keccak256("Panic(uint256)")), 0x11);
        vm.expectRevert(panicCode);
        ionPool.calculateRewardAndDebtDistribution();
    }

    function test_Withdraw_Issue() external {
        uint256 collateralDepositAmount = 10e18;
        uint256 normalizedBorrowAmount = 5e18;

        for (uint8 i = 0; i < ionPool.ilkCount(); i++) {
            vm.prank(borrower1);

            ionPool.depositCollateral(i, borrower1, borrower1, collateralDepositAmount, new bytes32[](0));

            uint256 rate = ionPool.rate(i);
            uint256 liquidityBefore = ionPool.weth();

            assertEq(ionPool.collateral(i, borrower1), collateralDepositAmount);
            assertEq(underlying.balanceOf(borrower1), normalizedBorrowAmount.rayMulDown(rate) * i);

            vm.prank(borrower1);

            ionPool.borrow(i, borrower1, borrower1, normalizedBorrowAmount, new bytes32[](0));

            uint256 liquidityRemoved = normalizedBorrowAmount.rayMulDown(rate);

            assertEq(ionPool.normalizedDebt(i, borrower1), normalizedBorrowAmount);
            assertEq(ionPool.totalNormalizedDebt(i), normalizedBorrowAmount);
            assertEq(ionPool.weth(), liquidityBefore - liquidityRemoved);
            assertEq(underlying.balanceOf(borrower1), normalizedBorrowAmount.rayMulDown(rate) * (i + 1));
        }

        vm.warp(block.timestamp + 1 hours);

        for (uint8 i = 0; i < ionPool.ilkCount(); i++) {
            vm.prank(borrower1);

            // expect overflow panic
            bytes memory panicCode = abi.encodeWithSelector(bytes4(keccak256("Panic(uint256)")), 0x11);
            vm.expectRevert(panicCode);
            ionPool.withdraw(address(underlying), normalizedBorrowAmount/2);
        }
    }

    function test_Supply_Issue() external {
        uint256 collateralDepositAmount = 10e18;
        uint256 normalizedBorrowAmount = 5e18;

        for (uint8 i = 0; i < ionPool.ilkCount(); i++) {
            vm.prank(borrower1);

            ionPool.depositCollateral(i, borrower1, borrower1, collateralDepositAmount, new bytes32[](0));

            uint256 rate = ionPool.rate(i);
            uint256 liquidityBefore = ionPool.weth();

            assertEq(ionPool.collateral(i, borrower1), collateralDepositAmount);
            assertEq(underlying.balanceOf(borrower1), normalizedBorrowAmount.rayMulDown(rate) * i);

            vm.prank(borrower1);

            ionPool.borrow(i, borrower1, borrower1, normalizedBorrowAmount, new bytes32[](0));

            uint256 liquidityRemoved = normalizedBorrowAmount.rayMulDown(rate);

            assertEq(ionPool.normalizedDebt(i, borrower1), normalizedBorrowAmount);
            assertEq(ionPool.totalNormalizedDebt(i), normalizedBorrowAmount);
            assertEq(ionPool.weth(), liquidityBefore - liquidityRemoved);
            assertEq(underlying.balanceOf(borrower1), normalizedBorrowAmount.rayMulDown(rate) * (i + 1));
        }

        vm.warp(block.timestamp + 1 hours);

        for (uint8 i = 0; i < ionPool.ilkCount(); i++) {
            vm.prank(borrower1);

            // expect overflow panic
            bytes memory panicCode = abi.encodeWithSelector(bytes4(keccak256("Panic(uint256)")), 0x11);
            vm.expectRevert(panicCode);
            ionPool.supply(borrower1, normalizedBorrowAmount/2, new bytes32[](0));
        }
    }

    function test_Borrow_Issue() external {
        uint256 collateralDepositAmount = 10e18;
        uint256 normalizedBorrowAmount = 5e18;

        for (uint8 i = 0; i < ionPool.ilkCount(); i++) {
            vm.prank(borrower1);

            ionPool.depositCollateral(i, borrower1, borrower1, collateralDepositAmount, new bytes32[](0));

            uint256 rate = ionPool.rate(i);
            uint256 liquidityBefore = ionPool.weth();

            assertEq(ionPool.collateral(i, borrower1), collateralDepositAmount);
            assertEq(underlying.balanceOf(borrower1), normalizedBorrowAmount.rayMulDown(rate) * i);

            vm.prank(borrower1);

            ionPool.borrow(i, borrower1, borrower1, normalizedBorrowAmount, new bytes32[](0));

            uint256 liquidityRemoved = normalizedBorrowAmount.rayMulDown(rate);

            assertEq(ionPool.normalizedDebt(i, borrower1), normalizedBorrowAmount);
            assertEq(ionPool.totalNormalizedDebt(i), normalizedBorrowAmount);
            assertEq(ionPool.weth(), liquidityBefore - liquidityRemoved);
            assertEq(underlying.balanceOf(borrower1), normalizedBorrowAmount.rayMulDown(rate) * (i + 1));
        }

        vm.warp(block.timestamp + 1 hours);

        for (uint8 i = 0; i < ionPool.ilkCount(); i++) {
            vm.prank(borrower1);

            // expect overflow panic
            bytes memory panicCode = abi.encodeWithSelector(bytes4(keccak256("Panic(uint256)")), 0x11);
            vm.expectRevert(panicCode);
            ionPool.borrow(i, borrower1, borrower1, normalizedBorrowAmount/2, new bytes32[](0));
        }
    }

    function test_Repay_Issue() external {
        uint256 collateralDepositAmount = 10e18;
        uint256 normalizedBorrowAmount = 5e18;

        for (uint8 i = 0; i < ionPool.ilkCount(); i++) {
            vm.prank(borrower1);

            ionPool.depositCollateral(i, borrower1, borrower1, collateralDepositAmount, new bytes32[](0));

            uint256 rate = ionPool.rate(i);
            uint256 liquidityBefore = ionPool.weth();

            assertEq(ionPool.collateral(i, borrower1), collateralDepositAmount);
            assertEq(underlying.balanceOf(borrower1), normalizedBorrowAmount.rayMulDown(rate) * i);

            vm.prank(borrower1);

            ionPool.borrow(i, borrower1, borrower1, normalizedBorrowAmount, new bytes32[](0));

            uint256 liquidityRemoved = normalizedBorrowAmount.rayMulDown(rate);

            assertEq(ionPool.normalizedDebt(i, borrower1), normalizedBorrowAmount);
            assertEq(ionPool.totalNormalizedDebt(i), normalizedBorrowAmount);
            assertEq(ionPool.weth(), liquidityBefore - liquidityRemoved);
            assertEq(underlying.balanceOf(borrower1), normalizedBorrowAmount.rayMulDown(rate) * (i + 1));
        }

        vm.warp(block.timestamp + 1 hours);

        for (uint8 i = 0; i < ionPool.ilkCount(); i++) {
            vm.prank(borrower1);

            // expect overflow panic
            bytes memory panicCode = abi.encodeWithSelector(bytes4(keccak256("Panic(uint256)")), 0x11);
            vm.expectRevert(panicCode);
            ionPool.repay(i, borrower1, borrower1, normalizedBorrowAmount/2);
        }
    }

    function test_WithdrawCollateral_Issue() external {
        uint256 collateralDepositAmount = 10e18;
        uint256 normalizedBorrowAmount = 5e18;

        for (uint8 i = 0; i < ionPool.ilkCount(); i++) {
            vm.prank(borrower1);

            ionPool.depositCollateral(i, borrower1, borrower1, collateralDepositAmount, new bytes32[](0));

            uint256 rate = ionPool.rate(i);
            uint256 liquidityBefore = ionPool.weth();

            assertEq(ionPool.collateral(i, borrower1), collateralDepositAmount);
            assertEq(underlying.balanceOf(borrower1), normalizedBorrowAmount.rayMulDown(rate) * i);

            vm.prank(borrower1);

            ionPool.borrow(i, borrower1, borrower1, normalizedBorrowAmount, new bytes32[](0));

            uint256 liquidityRemoved = normalizedBorrowAmount.rayMulDown(rate);

            assertEq(ionPool.normalizedDebt(i, borrower1), normalizedBorrowAmount);
            assertEq(ionPool.totalNormalizedDebt(i), normalizedBorrowAmount);
            assertEq(ionPool.weth(), liquidityBefore - liquidityRemoved);
            assertEq(underlying.balanceOf(borrower1), normalizedBorrowAmount.rayMulDown(rate) * (i + 1));
        }

        vm.warp(block.timestamp + 1 hours);

        for (uint8 i = 0; i < ionPool.ilkCount(); i++) {
            vm.prank(borrower1);

            // expect overflow panic
            bytes memory panicCode = abi.encodeWithSelector(bytes4(keccak256("Panic(uint256)")), 0x11);
            vm.expectRevert(panicCode);
            ionPool.withdrawCollateral(i, borrower1, borrower1, normalizedBorrowAmount/2);
        }
    }
    function test_DepositCollateral_Issue() external {
        uint256 collateralDepositAmount = 10e18;
        uint256 normalizedBorrowAmount = 5e18;

        for (uint8 i = 0; i < ionPool.ilkCount(); i++) {
            vm.prank(borrower1);

            ionPool.depositCollateral(i, borrower1, borrower1, collateralDepositAmount, new bytes32[](0));

            uint256 rate = ionPool.rate(i);
            uint256 liquidityBefore = ionPool.weth();

            assertEq(ionPool.collateral(i, borrower1), collateralDepositAmount);
            assertEq(underlying.balanceOf(borrower1), normalizedBorrowAmount.rayMulDown(rate) * i);

            vm.prank(borrower1);

            ionPool.borrow(i, borrower1, borrower1, normalizedBorrowAmount, new bytes32[](0));

            uint256 liquidityRemoved = normalizedBorrowAmount.rayMulDown(rate);

            assertEq(ionPool.normalizedDebt(i, borrower1), normalizedBorrowAmount);
            assertEq(ionPool.totalNormalizedDebt(i), normalizedBorrowAmount);
            assertEq(ionPool.weth(), liquidityBefore - liquidityRemoved);
            assertEq(underlying.balanceOf(borrower1), normalizedBorrowAmount.rayMulDown(rate) * (i + 1));
        }

        vm.warp(block.timestamp + 1 hours);

        for (uint8 i = 0; i < ionPool.ilkCount(); i++) {
            vm.prank(borrower1);

            // expect overflow panic
            bytes memory panicCode = abi.encodeWithSelector(bytes4(keccak256("Panic(uint256)")), 0x11);
            vm.expectRevert(panicCode);
            ionPool.depositCollateral(i, borrower1, borrower1, collateralDepositAmount, new bytes32[](0));
        }
    }

}

