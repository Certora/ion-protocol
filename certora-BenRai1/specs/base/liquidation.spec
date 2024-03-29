using ERC20A as underlying;
using ERC20B as underlyingForPool;
using IonPool as IonPool;

/////////////////// METHODS ///////////////////////
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
    function IonPool.underlying() external returns (address) envfree;
    function underlying.balanceOf(address) external returns (uint256) envfree;
    function underlyingForPool.balanceOf(address) external returns (uint256) envfree;
    function MAX_DISCOUNT_0() external returns (uint256) envfree;
    function MAX_DISCOUNT_1() external returns (uint256) envfree;
    function MAX_DISCOUNT_2() external returns (uint256) envfree;
    function LIQUIDATION_THRESHOLD_0() external returns (uint256) envfree;
    function LIQUIDATION_THRESHOLD_1() external returns (uint256) envfree;
    function LIQUIDATION_THRESHOLD_2() external returns (uint256) envfree;
    function TARGET_HEALTH() external returns (uint256) envfree;
    function rayDivUpHarness(uint256 x, uint256 y, uint256 z) external returns (uint256) envfree;
    function getConfigsHarness(uint8 ilkIndex) external returns (Liquidation.Configs) envfree;
    function getRepayAmt(uint8 ilkIndex, address vault) external returns (uint256) envfree;
    function getExchangeRateHarness(address _oracle) external returns (uint256) envfree;
    function getCollateralValueHarness(uint256 collateral, uint256 exchangeRate,uint256 liquidationThreshold) external returns (uint256) envfree;
    function getHealthRatioHarness(uint256 collateralValue, uint256 normalizedDebt, uint256 rate) external returns (uint256) envfree;
    function getDiscountHarness(uint256 healthRatio, uint256 maxDiscount) external returns (uint256) envfree;
}

///////////////// DEFINITIONS /////////////////////

////////////////// FUNCTIONS //////////////////////
function cvlMulDiv(uint x, uint y, uint denominator) returns uint {
    require(denominator != 0);
    return require_uint256(x*y/denominator);
}

///////////////// GHOSTS & HOOKS //////////////////

///////////////// INITIAL PROPERTIES /////////////

///////////////// INVARIANTS /////////////