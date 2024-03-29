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
    function LiquidationHarness.liquidateWithMoreReturn(uint8, address, address) external returns (uint256, uint256, uint256);

    function WEReverveOracle.currentExchangeRate() external returns (uint256) envfree;

    function BASE_DISCOUNT() external returns (uint256) envfree;

    function _._getRepayAmt(uint256 debtValue, uint256 collateralValue, uint256 liquidationThreshold, uint256 discount) internal => checkDiscountValue(discount) expect uint256;
}

// Get calculated discount value out for checking. It should be less than RAY.
// Multiplied by RAY so it can present itself in getRepayAmt output.
function checkDiscountValue(uint256 discount) returns uint256 {
    if (discount > 10 ^ 27) {
        return assert_uint256(10 ^ 54);
    }
    
    return assert_uint256(discount * (10 ^ 27));
}

function cvlMulDiv(uint x, uint y, uint denominator) returns uint {
    require(denominator != 0);
    return require_uint256(x*y/denominator);
}

// spec: calculated discount should not exceed maximum discount
// verified 
rule discountNotExceedingMaximum(uint8 ilkIndex, address vault) {
    env e;
    uint256 discount;
    // _getRepayAmt is summarized to discount * RAY so getRepayAmt output can be discount
    discount = LiquidationHarness.getRepayAmt(e, ilkIndex, vault);
    Liquidation.Configs configs = LiquidationHarness.getConfigs(e, ilkIndex);
    assert discount <= configs.maxDiscount;
}
