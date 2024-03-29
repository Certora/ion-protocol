// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity 0.8.21;

import "../../src/Liquidation.sol";
import { WadRayMath, RAY } from "./../../src/libraries/math/WadRayMath.sol";

contract LiquidationHarness is Liquidation {
     using WadRayMath for uint256;

    constructor(
        address _ionPool,
        address _protocol,
        address[] memory _reserveOracles,
        uint256[] memory _liquidationThresholds,
        uint256 _targetHealth,
        uint256 _reserveFactor,
        uint256[] memory _maxDiscounts
    ) Liquidation(_ionPool, _protocol, _reserveOracles, _liquidationThresholds, _targetHealth, _reserveFactor, _maxDiscounts) {}

    function rayDivUpHarness(uint256 x, uint256 y, uint256 z) external pure returns (uint256) {
        return x.rayDivUp(y-z);
    }

   function getConfigsHarness(uint8 ilkIndex) external view returns (Configs memory configs){
    configs = _getConfigs(ilkIndex);
   }

   function getExchangeRateHarness(address _oracle) external view returns (uint256) {
       return ReserveOracle(_oracle).currentExchangeRate();
   }

   function getCollateralValueHarness(uint256 collateral, uint256 exchangeRate,uint256 liquidationThreshold) external pure returns (uint256) {
       return (collateral * exchangeRate).rayMulDown(liquidationThreshold);
   }

   function getHealthRatioHarness(uint256 collateralValue, uint256 normalizedDebt, uint256 rate) external pure returns (uint256) {
       return collateralValue.rayDivDown(normalizedDebt * rate);
   }

   function getDiscountHarness(uint256 healthRatio, uint256 maxDiscount) external view returns (uint256 discount) {
       discount = BASE_DISCOUNT + (RAY - healthRatio); 
        discount = discount <= maxDiscount ? discount : maxDiscount; 
   }

   function getRepayAmtHarness(uint256 debt, uint256 collateralValue, uint256 liquidationThreshold, uint256 discount) external view returns (uint256 repay) {
        uint256 repayRad = _getRepayAmt(debt, collateralValue, liquidationThreshold, discount);
        repay = (repayRad / RAY);
        if (repayRad % RAY > 0) ++repay;
   }

}