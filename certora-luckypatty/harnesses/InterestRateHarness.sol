pragma solidity 0.8.21;

import "../../src/InterestRate.sol";
import { RAY } from "../../src/libraries/math/WadRayMath.sol";

contract InterestRateHarness is InterestRate {
    using WadRayMath for *;

    constructor(IlkData[] memory ilkDataList, IYieldOracle _yieldOracle) InterestRate(ilkDataList, _yieldOracle) { }

    // Get internal state variables
    function unpackCollateralConfig(uint256 index) public view returns (IlkData memory ilkData) {
        return super._unpackCollateralConfig(index);
    }

    function getCollateralCount() public view returns (uint256) {
        return COLLATERAL_COUNT;
    }

    function getRAY() public pure returns (uint256) {
        return RAY;
    }

    // function getWAD() public pure returns (uint256) {
    //     return WAD;
    // }

    // function getRAD() public pure returns (uint256) {
    //     return RAD;
    // }

    // Get access to internal functions in WadRayMath
    function scaleUpToRay(uint256 value, uint256 scale) public pure returns (uint256) {
        return value.scaleUpToRay(scale);
    }

    // Get sum of all reserveFactor values. Assist to set precondition for rule
    function sumOfReserveFactor() public view returns (uint256) {
        uint256 distributionFactorSum = 0;
        for (uint256 i = 0; i < COLLATERAL_COUNT;) {
            distributionFactorSum += unpackCollateralConfig(i).reserveFactor;
            unchecked { ++i; }
        }
        return distributionFactorSum;
    }

}
