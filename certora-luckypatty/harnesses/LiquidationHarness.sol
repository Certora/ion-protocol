pragma solidity 0.8.21;

import "../../src/Liquidation.sol";
import { WadRayMath, RAY } from "../../src/libraries/math/WadRayMath.sol";
import { Math } from "@openzeppelin/contracts/utils/math/Math.sol";
import { SafeCast } from "@openzeppelin/contracts/utils/math/SafeCast.sol";
import { IERC20 } from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import { SafeERC20 } from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract LiquidationHarness is Liquidation {
    using WadRayMath for *;
    using SafeERC20 for IERC20;
    using Math for uint256;
    using SafeCast for uint256;

    constructor(
        address _ionPool,
        address _protocol,
        address[] memory _reserveOracles,
        uint256[] memory _liquidationThresholds,
        uint256 _targetHealth,
        uint256 _reserveFactor,
        uint256[] memory _maxDiscounts
    ) Liquidation(_ionPool, _protocol, _reserveOracles, _liquidationThresholds, _targetHealth, _reserveFactor, _maxDiscounts) { }

    function scaleUpToRay(uint256 value, uint256 scale) public pure returns (uint256) {
        return value.scaleUpToRay(scale);
    }

    function rayMulDown(uint256 a, uint256 b) public pure returns (uint256) {
        return a.mulDiv(b, RAY);
    }

    function rayDivDown(uint256 a, uint256 b) public pure returns (uint256) {
        return a.mulDiv(RAY, b);
    }

    function rayMulUp(uint256 a, uint256 b) public pure returns (uint256) {
        return a.mulDiv(b, RAY, Math.Rounding.Ceil);
    }

    function ray() public pure returns (uint256) {
        return RAY;
    }

    function liquidationThreshold(uint8 ilkIndex) public view returns (uint256 threshold) {
        if (ilkIndex == 0) {
            return LIQUIDATION_THRESHOLD_0;
        } else if (ilkIndex == 1) {
            return LIQUIDATION_THRESHOLD_1;
        } else if (ilkIndex == 2) {
            return LIQUIDATION_THRESHOLD_2;
        }
    }

    function toInt256(uint256 value) public pure returns (int256) {
        // Note: Unsafe cast below is okay because `type(int256).max` is guaranteed to be positive
        if (value > uint256(type(int256).max)) {
            revert SafeCast.SafeCastOverflowedUintToInt(value);
        }
        return int256(value);
    }

    function getConfigs(uint8 ilkIndex)
        public
        view
        returns (Configs memory configs)
    {
        return super._getConfigs(ilkIndex);
    }

}