import "erc20.spec";

using ERC20A as underlying;
using ERC20B as underlyingForPool;
using IonPool as Ion;
using LiquidationHarness as LiquidationHarness;
using WstEthReserveOracle as WEReverveOracle;
using Liquidation as Liquidation;

// use builtin rule sanity;

methods {
    function _.currentExchangeRate() external => DISPATCHER(true);

    // mulDiv summary for better run time
    function _.mulDiv(uint x, uint y, uint denominator) internal => cvlMulDiv(x,y,denominator) expect uint;

    // InterestRate
    // Summarizing this function will improve run time, use NONDET if output doesn't matter
    function _.calculateInterestRate(uint256,uint256,uint256) external => DISPATCHER(true);

    // YieldOracle
    function _.apys(uint256) external => PER_CALLEE_CONSTANT;

    // envfree definitions
    function Ion.underlying() external returns (address) envfree;
    function underlying.balanceOf(address) external returns (uint256) envfree;
    function underlyingForPool.balanceOf(address) external returns (uint256) envfree;

    function LiquidationHarness.scaleUpToRay(uint256, uint256) external returns (uint256) envfree;
    function LiquidationHarness.rayMulDown(uint256, uint256) external returns (uint256) envfree;
    function LiquidationHarness.rayDivDown(uint256, uint256) external returns (uint256) envfree;
    function LiquidationHarness.rayMulUp(uint256, uint256) external returns (uint256) envfree;
    function LiquidationHarness.toInt256(uint256) external returns (int256) envfree;
    function LiquidationHarness.ray() external returns (uint256) envfree;
    function LiquidationHarness.liquidationThreshold(uint8) external returns (uint256) envfree;
    // function LiquidationHarness.maxDiscount(uint8) external returns (uint256) envfree;

    function WEReverveOracle.currentExchangeRate() external returns (uint256) envfree;

    function BASE_DISCOUNT() external returns (uint256) envfree;
}

function cvlMulDiv(uint x, uint y, uint denominator) returns uint {
    require(denominator != 0);
    return require_uint256(x*y/denominator);
}

// liquidate should revert when exchange rate is 0
// Verified.
rule liquidationRevertsWhenExchangeRateIsZero(env e) {
    uint8 ilkIndex; 
    address vault; 
    address kpr;

    uint256 exchangeRate = WEReverveOracle.currentExchangeRate();
    uint256 exchangeRateScaledUp = LiquidationHarness.scaleUpToRay(exchangeRate, 18);

    liquidate@withrevert(e, ilkIndex, vault, kpr);

    assert exchangeRateScaledUp == 0 => lastReverted, "Does not revert when exchange rate is zero";
}

rule liquidationFailsWhenNotLiquidatable(env e) {
    uint8 ilkIndex; 
    address vault; 
    address kpr;

    uint256 exchangeRate = WEReverveOracle.currentExchangeRate();
    uint256 exchangeRateScaledUp = LiquidationHarness.scaleUpToRay(exchangeRate, 18);

    uint256 collateral;
    uint256 normalizedDebt;
    collateral, normalizedDebt = Ion.vault(e, ilkIndex, vault);

    mathint collateralValue = collateral * exchangeRate;
    uint256 collateralValueMulDown = LiquidationHarness.rayMulDown(require_uint256(collateralValue), LiquidationHarness.liquidationThreshold(ilkIndex));

    uint256 rate = Ion.rate(e, ilkIndex);

    mathint roundDownFactor = normalizedDebt * rate;
    uint256 healthRatio = LiquidationHarness.rayDivDown(collateralValueMulDown, require_uint256(roundDownFactor));

    require exchangeRateScaledUp != 0;

    liquidate@withrevert(e, ilkIndex, vault, kpr);

    assert healthRatio >= LiquidationHarness.ray() => lastReverted, "Does not revert when the vault is healthy";
}

// The discount used in calculation is not larger than the maximum allowed value.
// verified.
// rule discountNotExceedingMaximum(env e) {
//     uint8 ilkIndex;
//     address vault; 
//     address kpr;

//     uint256 exchangeRate = WEReverveOracle.currentExchangeRate();
//     uint256 exchangeRateScaledUp = LiquidationHarness.scaleUpToRay(exchangeRate, 18);

//     uint256 collateral;
//     uint256 normalizedDebt;
//     collateral, normalizedDebt = Ion.vault(e, ilkIndex, vault);

//     mathint collateralValue = collateral * exchangeRate;
//     uint256 collateralValueMulDown = LiquidationHarness.rayMulDown(require_uint256(collateralValue), LiquidationHarness.liquidationThreshold(ilkIndex));

//     uint256 rate = Ion.rate(e, ilkIndex);

//     mathint roundDownFactor = normalizedDebt * rate;
//     uint256 healthRatio = LiquidationHarness.rayDivDown(collateralValueMulDown, require_uint256(roundDownFactor));

//     uint256 ray = LiquidationHarness.ray();
//     uint256 mDiscount = LiquidationHarness.maxDiscount(ilkIndex);

//     require exchangeRateScaledUp != 0 && healthRatio < ray && mDiscount < ray;

//     uint256 returnedRepay;
//     uint256 returnedGemOut;
//     returnedRepay, returnedGemOut = LiquidationHarness.liquidate@withrevert(e, ilkIndex, vault, kpr);

//     assert !lastReverted, "Discount is larger than maximum.";
// }

// function isRevertLiquidate() returns bool {
//     env e;
//     uint8 ilkIndex;
//     address vault; 
//     address kpr;
//     LiquidationHarness.liquidate@withrevert(e, ilkIndex, vault, kpr);
//     return lastReverted;
// }

// invariant liquidateNotRevert()
//     isRevertLiquidate();

// Correct balance change during dust liquidation
// Timed out.
// rule correctBalanceChangeWhenDustLiquidation(env e) {
//     uint8 ilkIndex; 
//     address vault; 
//     address kpr;

//     uint256 exchangeRate = WEReverveOracle.currentExchangeRate();
//     uint256 exchangeRateScaledUp = LiquidationHarness.scaleUpToRay(exchangeRate, 18);

//     uint256 collateral;
//     uint256 normalizedDebt;
//     collateral, normalizedDebt = Ion.vault(e, ilkIndex, vault);

//     mathint collateralValue = collateral * exchangeRate;
//     uint256 collateralValueMulDown = LiquidationHarness.rayMulDown(require_uint256(collateralValue), LiquidationHarness.liquidationThreshold(ilkIndex));

//     uint256 rate = Ion.rate(e, ilkIndex);

//     mathint roundDownFactor = normalizedDebt * rate;
//     uint256 healthRatio = LiquidationHarness.rayDivDown(collateralValueMulDown, require_uint256(roundDownFactor));

    // mathint discount = BASE_DISCOUNT() + (LiquidationHarness.ray() - healthRatio);
    // mathint adjustedDiscount = require_uint256(discount) <= LiquidationHarness.maxDiscount(ilkIndex) ? require_uint256(discount) : LiquidationHarness.maxDiscount(ilkIndex);
    // mathint debtValue = normalizedDebt * rate;
    // mathint rayDiscountDiff = LiquidationHarness.ray() - require_uint256(adjustedDiscount);
    // uint256 price = LiquidationHarness.rayMulUp(exchangeRateScaledUp, require_uint256(rayDiscountDiff));
//     uint256 repay = LiquidationHarness.getRepayAmt(require_uint256(debtValue), collateralValueMulDown, LiquidationHarness.liquidationThreshold(ilkIndex), require_uint256(adjustedDiscount));
    
//     require repay <= require_uint256(debtValue);
//     require exchangeRateScaledUp != 0;
//     require exchangeRateScaledUp != 0 && healthRatio < LiquidationHarness.ray();

//     uint256 dart = 0;
//     mathint gemOut = 0;
//     bool dustLiquidationCondition = require_uint256(require_uint256(debtValue) - repay) < Ion.dust(e, ilkIndex);
//     uint256 repayToSend = repay;
//     if (dustLiquidationCondition) {
//         repayToSend = require_uint256(debtValue);
//         dart = normalizedDebt; // pay off all debt including dust
//         gemOut = debtValue / price;
//     }

//     mathint transferAmt = (repayToSend / LiquidationHarness.ray());
//     mathint transferAmtToSend = transferAmt;
//     if (repayToSend % LiquidationHarness.ray() > 0) 
//         transferAmtToSend = transferAmt + 1;

//     uint256 underlyingBalanceBefore = underlying.balanceOf(currentContract);

//     liquidate@withrevert(e, ilkIndex, vault, kpr);
//     bool reverted = lastReverted;

//     uint256 underlyingBalanceAfter = underlying.balanceOf(currentContract);

//     assert dustLiquidationCondition && !reverted => underlyingBalanceAfter == 
//         assert_uint256(underlyingBalanceBefore - transferAmtToSend + repayToSend), "Does not revert when the vault is healthy";
// }

// Balance should stay the same when it's partial liquidation
// Timed out.
// rule balanceDoNotChangeWhenPartialLiquidation(env e) {
//     uint8 ilkIndex; 
//     address vault; 
//     address kpr;

//     uint256 exchangeRate = WEReverveOracle.currentExchangeRate();
//     require exchangeRate > 0;
//     uint256 exchangeRateScaledUp = LiquidationHarness.scaleUpToRay(exchangeRate, 18);

//     uint256 collateral;
//     uint256 normalizedDebt;
//     collateral, normalizedDebt = Ion.vault(e, ilkIndex, vault);

//     mathint collateralValue = collateral * exchangeRate;
//     uint256 collateralValueMulDown = LiquidationHarness.rayMulDown(require_uint256(collateralValue), LiquidationHarness.liquidationThreshold(ilkIndex));

//     uint256 rate = Ion.rate(e, ilkIndex);

//     mathint roundDownFactor = normalizedDebt * rate;
//     uint256 healthRatio = LiquidationHarness.rayDivDown(collateralValueMulDown, require_uint256(roundDownFactor));

//     mathint discount = BASE_DISCOUNT() + (LiquidationHarness.ray() - healthRatio);
//     mathint adjustedDiscount = require_uint256(discount) <= LiquidationHarness.maxDiscount(ilkIndex) ? require_uint256(discount) : LiquidationHarness.maxDiscount(ilkIndex);
//     mathint debtValue = normalizedDebt * rate;
//     mathint rayDiscountDiff = LiquidationHarness.ray() - require_uint256(adjustedDiscount);
//     uint256 price = LiquidationHarness.rayMulUp(exchangeRateScaledUp, require_uint256(rayDiscountDiff));
//     uint256 repay = LiquidationHarness.getRepayAmt(require_uint256(debtValue), collateralValueMulDown, LiquidationHarness.liquidationThreshold(ilkIndex), require_uint256(adjustedDiscount));
    
//     uint256 dart = 0;
//     mathint gemOut = 0;
//     bool protocolLiquidationCondition = repay > require_uint256(debtValue);

//     require exchangeRateScaledUp != 0 && healthRatio < LiquidationHarness.ray();

//     uint256 underlyingBalanceBefore = underlying.balanceOf(currentContract);

//     uint256 repayReturn;
//     uint256 gemOutReturn;
//     repayReturn, gemOutReturn = liquidate@withrevert(e, ilkIndex, vault, kpr);
//     bool reverted = lastReverted;

//     uint256 underlyingBalanceAfter = underlying.balanceOf(currentContract);

//     assert protocolLiquidationCondition && !reverted => 
//         underlyingBalanceAfter == underlyingBalanceBefore && repayReturn == 0 && gemOutReturn == 0, "Does not revert when the vault is healthy";
// }
