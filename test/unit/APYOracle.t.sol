// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import { Test } from "forge-std/Test.sol";
import { ApyOracle, LOOK_BACK, ILK_COUNT } from "../../src/ApyOracle.sol";
import {
    ApyOracleSharedSetup,
    WST_ETH_EXCHANGE_RATE,
    STADER_ETH_EXCHANGE_RATE,
    SWELL_ETH_EXCHANGE_RATE
} from "../helpers/ApyOracleSharedSetup.sol";
import { RoundedMath } from "../../src/math/RoundedMath.sol";
import { SafeCast } from "@openzeppelin/contracts/utils/math/SafeCast.sol";
import { safeconsole as console } from "forge-std/safeconsole.sol";

contract ApyOracleTest is ApyOracleSharedSetup {
    function test_UpdatingWithChangingExchangeRates() external {
        uint256 increaseInExchangeRate = 0.072935829352e18;
        uint256 amountOfUpdatesToTest = 10;

        uint256 newWstRate = WST_ETH_EXCHANGE_RATE;
        uint256 newStaderRate = STADER_ETH_EXCHANGE_RATE;
        uint256 newSwellRate = SWELL_ETH_EXCHANGE_RATE;
        // Update exchange rates
        for (uint256 i = 0; i < amountOfUpdatesToTest; i++) {
            vm.warp(block.timestamp + 1 days);

            newWstRate += increaseInExchangeRate;
            newStaderRate += increaseInExchangeRate;
            newSwellRate += increaseInExchangeRate;

            uint256[ILK_COUNT] memory newRates = [newWstRate, newStaderRate, newSwellRate];

            uint256 indexToUpdate = oracle.currentIndex();

            uint32[ILK_COUNT][LOOK_BACK] memory ratesBefore;
            for (uint256 j = 0; j < ILK_COUNT; j++) {
                for (uint256 k = 0; k < LOOK_BACK; k++) {
                    ratesBefore[k][j] = oracle.historicalExchangeRates(k, j);
                }
            }

            lidoOracle.setNewRate(newWstRate);
            staderOracle.setNewRate(newStaderRate);
            swellOracle.setNewRate(newSwellRate);

            oracle.updateAll();

            for (uint256 j = 0; j < ILK_COUNT; j++) {
                for (uint256 k = 0; k < LOOK_BACK; k++) {
                    if (k == indexToUpdate) {
                        assertEq(oracle.historicalExchangeRates(k, j), newRates[j] / 10 ** 12);
                    } else {
                        assertEq(oracle.historicalExchangeRates(k, j), ratesBefore[k][j]);
                    }
                }
            }
        }

        // _prettyPrintApys();
        // _prettyPrintRatesMatrix();
    }

    function test_RevertWhen_ExchangeRateIsZero() external {
        vm.warp(block.timestamp + 1 days);

        lidoOracle.setNewRate(0);
        vm.expectRevert(abi.encodeWithSelector(ApyOracle.InvalidExchangeRate.selector, 0));
        oracle.updateAll();
    }

    function test_RevertWhen_NewExchangeRateIsLessThanPrevious() external {
        vm.warp(block.timestamp + 1 days);

        lidoOracle.setNewRate(2 wei);
        vm.expectRevert(abi.encodeWithSelector(ApyOracle.InvalidExchangeRate.selector, 0));
        oracle.updateAll();
    }

    function test_RevertWhen_UpdatingMoreThanOnceADay() external {
        vm.expectRevert(ApyOracle.AlreadyUpdated.selector);
        oracle.updateAll();
    }

    function _prettyPrintApys() internal view {
        for (uint256 i = 0; i < ILK_COUNT; i++) {
            console.log("Ilk: %s", i + 1);
            console.log("APY: %s", oracle.apys(i));
            console.log("");
        }
    }

    function _prettyPrintRatesMatrix() internal view {
        for (uint256 k = 0; k < LOOK_BACK; k++) {
            console.log("Day: %s", k + 1);
            for (uint256 j = 0; j < ILK_COUNT; j++) {
                console.log(oracle.historicalExchangeRates(k, j));
            }
            console.log("");
        }
    }
}
