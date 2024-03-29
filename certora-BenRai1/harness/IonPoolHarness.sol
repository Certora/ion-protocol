// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity 0.8.21;

import "../../src/IonPool.sol";

contract IonPoolHarness is IonPool {
    using SafeERC20 for IERC20;
    using SafeCast for *;
    using WadRayMath for *;
    using Math for uint256;
    using EnumerableSet for EnumerableSet.AddressSet;

    IERC20 public underlyingHarness;



    function getIlkValues(uint256 ilkIndex) external view returns (uint104 totalNormalizedDebt, uint104 rate,uint48 lastRateUpdate,address spot,uint256 debtCeiling,uint256 dust){
        IonPoolStorage storage $ = _getIonPoolStorage();
        totalNormalizedDebt = $.ilks[ilkIndex].totalNormalizedDebt;
        rate = $.ilks[ilkIndex].rate;
        lastRateUpdate = $.ilks[ilkIndex].lastRateUpdate;
        spot = address($.ilks[ilkIndex].spot);
        debtCeiling = $.ilks[ilkIndex].debtCeiling;
        dust = $.ilks[ilkIndex].dust;
    }

    function getIlkslength() external view returns (uint256) {
        IonPoolStorage storage $ = _getIonPoolStorage();
        uint256 ilksLength = $.ilks.length;

        return ilksLength;
    }


    function getIlk(uint256 ilkIndex) external view returns (Ilk memory){
        IonPoolStorage storage $ = _getIonPoolStorage();
        return $.ilks[ilkIndex];
    }

    function getIlkSpotPrice(uint256 ilkIndex) external view returns (uint256 spotPrice){
        IonPoolStorage storage $ = _getIonPoolStorage();
         spotPrice = $.ilks[ilkIndex].spot.getSpot();
    }

    function getSupplyCap() external view returns (uint256){
        IonPoolStorage storage $ = _getIonPoolStorage();
        return $.wethSupplyCap;
    }

    function getWeth() external view returns (uint256){
        IonPoolStorage storage $ = _getIonPoolStorage();
        return $.weth; 
    }

    function calculateRewardAndDebtDistributionForIlkHarness(uint8 ilkIndex, uint256 rewardAmount) external view {
        _calculateRewardAndDebtDistributionForIlk(ilkIndex, rewardAmount);
    }

    function modifyPositionHarness(
        uint8 ilkIndex,
        address user,
        address collateralRecipient,
        address underlyingRecipient,
        int256 changeInCollateral,
        int256 changeInNormalizedDebt
    ) external {
        _modifyPosition(ilkIndex, user, collateralRecipient, underlyingRecipient, changeInCollateral, changeInNormalizedDebt);
    }

    //functions for underlying (WETH is underlying)
    // _burn => withdraw
    // _mint => supply + accrueInterest
    // _transferWeth
    //amount has 45 decimals
    function trasferWethHarness(address user, int256 amount) external {
        if (amount == 0) return;
        IonPoolStorage storage $ = _getIonPoolStorage();

        //i: repaymnet
        if (amount < 0) {
            uint256 amountUint = uint256(-amount);
            uint256 amountWad = amountUint / RAY;
            if (amountUint % RAY > 0) ++amountWad;

            $.weth += amountWad;
            underlyingHarness.safeTransferFrom(user, address(this), amountWad);
        } else {
            // Round down in protocol's favor
            uint256 amountWad = uint256(amount) / RAY;

            $.weth -= amountWad;

            underlyingHarness.safeTransfer(user, amountWad);
        }

    }

    function wethToTransfer(int256 amount) external pure returns(int256 amountWad) {
        if (amount < 0) {
            amountWad = amount / (10^27);
            if ((amount % (10^27)) > 0) {amountWad = amountWad + 1;} //@audit-issue why doe this not increase the value by 1?

        } else {
            // Round down in protocol's favor
             amountWad = amount / (10^27);
        }
    }

    function test_transferWethSum(address user, int256 amount) external {
       _transferWeth( user,  amount); 
    }




}