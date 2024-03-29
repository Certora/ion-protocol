pragma solidity 0.8.21;

import "../../src/IonPool.sol";
import { WadRayMath, RAY } from "../../src/libraries/math/WadRayMath.sol";
import { SafeCast } from "@openzeppelin/contracts/utils/math/SafeCast.sol";
contract IonPoolHarness is IonPool {
    using WadRayMath for *;
    using SafeCast for *;
    constructor() IonPool(){ }
    function toInt256Exposed(uint256 value) public pure returns (int256) {
        return value.toInt256();
    }

    function calculateRewardAndDebtDistributionForIlk(
        uint8 ilkIndex,
        uint256 totalEthSupply
    )
        public
        view
        returns (
            uint256 supplyFactorIncrease,
            uint256 treasuryMintAmount,
            uint104 newRateIncrease,
            uint256 newDebtIncrease,
            uint48 timestampIncrease
        )
    {
        return super._calculateRewardAndDebtDistributionForIlk(ilkIndex, totalEthSupply);
    }

    function modifyPosition(
        uint8 ilkIndex,
        address u,
        address v,
        address w,
        int256 changeInCollateral,
        int256 changeInNormalizedDebt
    )
        public
        returns (uint104 ilkRate, uint256 newTotalDebt)
    {
        return super._modifyPosition(ilkIndex, u, v, w, changeInCollateral, changeInNormalizedDebt);
    }

    function transferWeth(address user, int256 amount) public {
        super._transferWeth(user, amount);
    }


    // --- Math ---

    // function add(uint256 x, int256 y) public pure returns (uint256 z) {
    //     return super.add(x, y);
    // }

    // function sub(uint256 x, int256 y) public pure returns (uint256 z) {
    //     return super._sub(x, y);
    // }

    // function rpow(uint256 x, uint256 n, uint256 b) public pure returns (uint256 z) {
    //     return super._rpow(x, n, b);
    // }

    // // --- Boolean ---
    function eitherExposed(bool x, bool y) public pure returns (bool z) {
        return super.either(x, y);
    }

    function bothExposed(bool x, bool y) public pure returns (bool z) {
        return super.both(x, y);
    }

    
    // function scaleUpToWad(uint256 value, uint256 scale) public pure returns (uint256) {
    //     return value.scaleUpToWad(scale);
    // }

    function scaleUpToRay(uint256 value, uint256 scale) public pure returns (uint256) {
        return value.scaleUpToRay(scale);
    }

    // function wadMulDown(uint256 value, uint256 scale) public pure returns (uint256) {
    //     return value.wadMulDown(scale);
    // }

    // function rayMulDown(uint256 value, uint256 scale) public pure returns (uint256) {
    //     return value.rayMulDown(scale);
    // }

    function unsafeCastTo48(uint256 x) public pure returns (uint48)  {
        return uint48(x);
    }

    function wethSupplyCap() external view returns (uint256) {
        IonPoolStorage storage $ = _getIonPoolStorage();
        return $.wethSupplyCap;
    }

}