// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.19;

import { Script, console2 } from "forge-std/Script.sol";
import { safeconsole as console } from "forge-std/safeconsole.sol";
import { ApyOracle, LOOK_BACK, PROVIDER_PRECISION, APY_PRECISION, ILK_COUNT } from "src/APYOracle.sol";
import { SafeCast } from "@openzeppelin/contracts/utils/math/SafeCast.sol";
import { RoundedMath } from "src/math/RoundedMath.sol";
import { stdJson as StdJson } from "forge-std/StdJson.sol";

contract DeployApyOracleScript is Script {
    using RoundedMath for uint256;
    using SafeCast for uint256;
    using StdJson for string;

    string configPath = "./deployment-config/ApyOracle.json";
    string config = vm.readFile(configPath);

    function run() public {
        uint256 scale = 10 ** (PROVIDER_PRECISION - APY_PRECISION);

        string[] memory configKeys = vm.parseJsonKeys(config, ".exchangeRateData");
        assert(configKeys.length == ILK_COUNT);

        uint256[] memory lidoRates = vm.parseJsonUintArray(config, ".exchangeRateData.lido.historicalExchangeRates");
        uint256[] memory staderRates = vm.parseJsonUintArray(config, ".exchangeRateData.stader.historicalExchangeRates");
        uint256[] memory swellRates = vm.parseJsonUintArray(config, ".exchangeRateData.swell.historicalExchangeRates");

        uint32[ILK_COUNT][LOOK_BACK] memory historicalExchangeRates;

        address lidoExchangeRateAddress = vm.parseJsonAddress(config, ".exchangeRateData.lido.address");
        address staderExchangeRateAddress = vm.parseJsonAddress(config, ".exchangeRateData.stader.address");
        address swellExchangeRateAddress = vm.parseJsonAddress(config, ".exchangeRateData.swell.address");

        for (uint256 i = 0; i < LOOK_BACK; i++) {
            uint32 lidoEr = (lidoRates[i] / scale).toUint32();
            uint32 staderEr = (staderRates[i] / scale).toUint32();
            uint32 swellEr = (swellRates[i] / scale).toUint32();

            uint32[ILK_COUNT] memory exchangesRates = [lidoEr, staderEr, swellEr];

            historicalExchangeRates[i] = exchangesRates;
        }
        vm.startBroadcast(vm.envUint("PRIVATE_KEY"));
        ApyOracle oracle = new ApyOracle(historicalExchangeRates, lidoExchangeRateAddress, staderExchangeRateAddress, swellExchangeRateAddress);
        vm.stopBroadcast();
    }

    function configureDeployment() external {
        string[] memory inputs = new string[](3);
        inputs[0] = "bun";
        inputs[1] = "run";
        inputs[2] = "offchain/scrapePastExchangeRates.ts";

        bytes memory res = vm.ffi(inputs);

        if (!vm.exists(configPath)) {
            vm.writeFile(configPath, string(""));
        }
        vm.writeJson(string(res), configPath);
    }
}
