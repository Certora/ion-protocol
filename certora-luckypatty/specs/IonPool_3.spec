import "erc20.spec";

// use builtin rule sanity;
using IonPoolHarness as IonPoolHarness;
methods {
    // Interest rate model
    function _.calculateInterestRate(uint256, uint256, uint256) external => DISPATCHER(true);
    function _.COLLATERAL_COUNT() external => DISPATCHER(true);

    // Spot oracle
    function _.getSpot() external => getSpotCVL() expect uint256;

    // Whitelist
    function _.isWhitelistedBorrower(uint8 ilkIndex, address poolCaller, address addr, bytes32[] proof) external => getWhitelistCVL(poolCaller) expect bool;
    function _.isWhitelistedLender(address poolCaller, address addr, bytes32[] proof) external => getWhitelistCVL(poolCaller) expect bool;

    // Chainlink
    function _.latestRoundData() external => latestRoundDataCVL() expect (uint80, int256, uint256, uint256, uint80);

    function _.getStETHByWstETH(uint256 amount) external => getStETHByWstETHCVL(amount) expect (uint256);

    // mulDiv summary for better run time
    function _.mulDiv(uint x, uint y, uint denominator) internal => mulDivCVL(x,y,denominator) expect uint;
    
    // getters
    function ilkCount() external returns (uint256) envfree;

    function getIlkIndex(address ilkAddress) external returns (uint8) envfree;

    function getIlkAddress(uint256 ilkIndex) external returns (address) envfree;

    function addressContains(address ilk) external returns (bool) envfree;

    function totalNormalizedDebt(uint8 ilkIndex) external returns (uint256) envfree;

    function rateUnaccrued(uint8 ilkIndex) external returns (uint256) envfree;

    function rate(uint8 ilkIndex) external returns (uint256);

    function lastRateUpdate(uint8 ilkIndex) external returns (uint256) envfree;

    //function spot(uint8 ilkIndex) external returns (SpotOracle) envfree;

    function debtCeiling(uint8 ilkIndex) external returns (uint256) envfree;

    function dust(uint8 ilkIndex) external returns (uint256) envfree;

    function collateral(uint8 ilkIndex, address user) external returns (uint256) envfree;

    function normalizedDebt(uint8 ilkIndex, address user) external returns (uint256) envfree;

    function vault(uint8 ilkIndex, address user) external returns (uint256, uint256) envfree;

    function gem(uint8 ilkIndex, address user) external returns (uint256) envfree;

    function unbackedDebt(address user) external returns (uint256) envfree;

    function isOperator(address user, address operator) external returns (bool) envfree;

    function isAllowed(address user, address operator) external returns (bool) envfree;

    function debtUnaccrued() external returns (uint256) envfree;

    function debt() external returns (uint256) envfree;

    function totalUnbackedDebt() external returns (uint256) envfree;

    function interestRateModule() external returns (address) envfree;

    function whitelist() external returns (address) envfree;

    function weth() external returns (uint256) envfree;

    function getCurrentBorrowRate(uint8 ilkIndex) external returns (uint256, uint256) envfree;

    function implementation() external returns (address) envfree;


    //
    function updateIlkDebtCeiling(uint8 ilkIndex, uint256 newCeiling) external;
    function withdraw(address receiverOfUnderlying, uint256 amount) external;
        function supply(
        address user,
        uint256 amount,
        bytes32[] calldata proof
    )
        external;
    function borrow(uint8,address,address,uint256,bytes32[]) external;
    function repay(
        uint8 ilkIndex,
        address user,
        address payer,
        uint256 amountOfNormalizedDebt
    )
        external;
    function withdrawCollateral(
        uint8 ilkIndex,
        address user,
        address recipient,
        uint256 amount
    )
        external;
    function depositCollateral(
        uint8 ilkIndex,
        address user,
        address depositor,
        uint256 amount,
        bytes32[] calldata proof
    )
        external;

    // harness
    function IonPoolHarness.toInt256Exposed(uint256 value) external returns (int256) envfree;
    function IonPoolHarness.eitherExposed(bool x, bool y) external returns (bool) envfree;
    function IonPoolHarness.bothExposed(bool x, bool y) external returns (bool) envfree;
    function IonPoolHarness.wethSupplyCap() external returns (uint256) envfree;
}

// ---- Helpers ------------------------------------------------------------------

definition nonzerosender(env e) returns bool = e.msg.sender != 0;

ghost uint80 roundId;
ghost int256 answer;
ghost uint256 startedAt;
ghost uint256 updatedAt;
ghost uint80 answeredInRound;

function latestRoundDataCVL() returns (uint80, int256, uint256, uint256, uint80) {
    return (roundId, answer, startedAt, updatedAt, answeredInRound);
}

ghost uint256 spot;

function getSpotCVL() returns uint256 {
    return spot;
}

ghost mapping(uint256 => uint256) getStETHByWstETH_Ghost;

ghost mapping(address => bool) isWhitelisted_Ghost;

function getWhitelistCVL(address user) returns bool {
    return isWhitelisted_Ghost[user];
}

function getStETHByWstETHCVL(uint256 amount) returns uint256 {
    return getStETHByWstETH_Ghost[amount];
}

function mulDivCVL(uint x, uint y, uint denominator) returns uint {
    require(denominator != 0);
    return require_uint256(x*y/denominator);
}

// ---- Rules ------------------------------------------------------------------
// inconclusive
// rule withdrawCorrectlyUpdateBalance(env e, address receiverOfUnderlying, uint256 amount) {
//     require nonzerosender(e);
//     require receiverOfUnderlying != e.msg.sender;
    
//     uint256 receiverBalanceBefore = IonPoolHarness.balanceOf(e, receiverOfUnderlying);

//     withdraw@withrevert(e, receiverOfUnderlying, amount);

//     uint256 receiverBalanceAfter = IonPoolHarness.balanceOf(e, receiverOfUnderlying);

//     bool success = !lastReverted;
//     assert success => receiverBalanceAfter == require_uint256(receiverBalanceBefore + amount), "withdraw does not change balance correctly";
// }

rule supplyCorrectUpdateLiquidity(env e, address user, uint256 amount, bytes32[] proof) {
    require nonzerosender(e);
    require user != e.msg.sender;

    uint256 ethBefore = weth();

    supply(e, user, amount, proof);

    uint256 ethAfter = weth();

    assert(assert_uint256(ethAfter - amount) == ethBefore), "eth update incorrect.";
}

// inconclusive
// rule supplyRevertsWhenSupplyCapExceeded(env e, address user, uint256 amount, bytes32[] proof) {
//     require nonzerosender(e);
//     require user != e.msg.sender;

//     uint256 supplyCap = IonPoolHarness.wethSupplyCap();
//     uint256 totalSupply = IonPoolHarness.totalSupply(e);
    
//     supply@withrevert(e, user, amount, proof);

//     assert(totalSupply > supplyCap => lastReverted), "Did not reverts when supply cap exceeded.";
// }
