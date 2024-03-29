// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity 0.8.21;

import "../../src/InterestRate.sol";
import { WadRayMath, RAY } from "../../src/libraries/math/WadRayMath.sol";



contract InterestRateHarness is InterestRate {

    using WadRayMath for *;
    constructor(IlkData[] memory ilkDataList, IYieldOracle _yieldOracle) InterestRate(ilkDataList, _yieldOracle){ }


    function unpackCollateralConfig(uint256 ilkIndex) external view returns (IlkData memory ilkData){
        ilkData = _unpackCollateralConfig(ilkIndex);
    }

    function getAdjustedProfitMargin(uint256 ilkIndex) external view returns (uint96){
        IlkData memory ilkData = _unpackCollateralConfig(ilkIndex);
        return ilkData.adjustedProfitMargin;
    }
    function getMinimumKinkRate(uint256 ilkIndex) external view returns (uint96){
        IlkData memory ilkData = _unpackCollateralConfig(ilkIndex);
        return ilkData.minimumKinkRate;
    }

    function getReserveFactor(uint256 ilkIndex) external view returns (uint16){
        IlkData memory ilkData = _unpackCollateralConfig(ilkIndex);
        return ilkData.reserveFactor;
    }

    function getAdjustedBaseRate(uint256 ilkIndex) external view returns (uint96){
        IlkData memory ilkData = _unpackCollateralConfig(ilkIndex);
        return ilkData.adjustedBaseRate;
    }
    
    function getMinimumBaseRate(uint256 ilkIndex) external view returns (uint96){
        IlkData memory ilkData = _unpackCollateralConfig(ilkIndex);
        return ilkData.minimumBaseRate;
    }
    function getOptimalUtilizationRate(uint256 ilkIndex) external view returns (uint16){
        IlkData memory ilkData = _unpackCollateralConfig(ilkIndex);
        return ilkData.optimalUtilizationRate;
    }

    function getDistributionFactor(uint256 ilkIndex) external view returns (uint16){
        IlkData memory ilkData = _unpackCollateralConfig(ilkIndex);
        return ilkData.distributionFactor;
    }

    function getAdjustedAboveKinkSlope(uint256 ilkIndex) external view returns (uint96){
        IlkData memory ilkData = _unpackCollateralConfig(ilkIndex);
        return ilkData.adjustedAboveKinkSlope;
    }

    function getMinimumAboveKinkSlope(uint256 ilkIndex) external view returns (uint96){
        IlkData memory ilkData = _unpackCollateralConfig(ilkIndex);
        return ilkData.minimumAboveKinkSlope;
    }

    function getUtilizationRate(uint256 totalEthSupply, uint256 totalIlkDebt, uint256 ilkIndex) public view returns (uint256){
        IlkData memory ilkData = _unpackCollateralConfig(ilkIndex);
        uint256 distributionFactor = ilkData.distributionFactor;
        
        
         return(totalEthSupply == 0 ? 0 : totalIlkDebt / (totalEthSupply.wadMulDown(distributionFactor* 10^16)));
    }

    function getCollateralApyRayInSeconds(uint256 ilkIndex) public view returns (uint256 collateralApyRayInSeconds){
        collateralApyRayInSeconds = YIELD_ORACLE.apys(ilkIndex).scaleUpToRay(8) / SECONDS_IN_A_YEAR;
    }

    function getAdjustedBelowKinkSlope(uint256 ilkIndex) public view returns (uint256 adjustedBelowKinkSlope){
        IlkData memory ilkData = _unpackCollateralConfig(ilkIndex);
        uint256 collateralApyRayInSeconds = getCollateralApyRayInSeconds(ilkIndex);
        uint256 slopeNumerator;
        unchecked {
                slopeNumerator = collateralApyRayInSeconds - ilkData.adjustedProfitMargin - ilkData.adjustedBaseRate;
            }

            // Underflow occured
            // If underflow occured, then the Apy was too low or the profitMargin was too high and
            // we would want to switch to minimum borrow rate. Set slopeNumerator to zero such
            // that adjusted borrow rate is below the minimum borrow rate.
            if (slopeNumerator > collateralApyRayInSeconds) {
                slopeNumerator = 0;
            }

            adjustedBelowKinkSlope = slopeNumerator.rayDivDown(ilkData.optimalUtilizationRate *10^23);
    }

    function utilRateBelowOptimum (uint256 ilkIndex, uint256 utilisationRate) external view returns (uint256, uint256){
            IlkData memory ilkData = _unpackCollateralConfig(ilkIndex);
            uint256 adjustedBelowKinkSlope = getAdjustedBelowKinkSlope(ilkIndex);
            uint256 minimumBelowKinkSlope =
            (ilkData.minimumKinkRate - ilkData.minimumBaseRate).rayDivDown(ilkData.optimalUtilizationRate*10^23);

            uint256 adjustedBorrowRate = adjustedBelowKinkSlope.rayMulDown(utilisationRate) + ilkData.adjustedBaseRate;
            uint256 minimumBorrowRate = minimumBelowKinkSlope.rayMulDown(utilisationRate) + ilkData.minimumBaseRate;

            if (adjustedBorrowRate < minimumBorrowRate) {
                return (minimumBorrowRate, ilkData.reserveFactor.scaleUpToRay(4));
            } else {
                return (adjustedBorrowRate, ilkData.reserveFactor.scaleUpToRay(4));
            }
        }
    


 


}