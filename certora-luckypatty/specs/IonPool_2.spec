import "erc20.spec";

using IonPoolHarness as IP;

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

    function _._accrueInterest() internal => addNumAcureInterestCall() expect uint256;

}

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

ghost mathint numAcureInterestCall;

function addNumAcureInterestCall() returns uint256 {
    numAcureInterestCall = numAcureInterestCall + 1;
    return 1;
}

// Upon successful borrower or lender operations, the totalETHSupply changes,
// meaning every collateral’s interest rates need to be updated and accumulated
rule accureInterestWhenSupply(address user, uint256 amount, bytes32[] proof) {
    env e;
    mathint numCallBefore = numAcureInterestCall;
    supply(e, user, amount, proof);
    mathint numCallAfter = numAcureInterestCall;
    assert (
        numCallAfter == numCallBefore + 1
    );
}

rule accureInterestWhenWithdraw(address receiverOfUnderlying, uint256 amount) {
    env e;
    mathint numCallBefore = numAcureInterestCall;
    withdraw(e, receiverOfUnderlying, amount);
    mathint numCallAfter = numAcureInterestCall;
    assert (
        numCallAfter == numCallBefore + 1
    );
}

rule accureInterestWhenBorrow(
        uint8 ilkIndex,
        address user,
        address recipient,
        uint256 amountOfNormalizedDebt,
        bytes32[] proof
    ) {
    env e;
    mathint numCallBefore = numAcureInterestCall;
    borrow(e, ilkIndex, user, recipient, amountOfNormalizedDebt, proof);
    mathint numCallAfter = numAcureInterestCall;
    assert (
        numCallAfter == numCallBefore + 1
    );
}

rule accureInterestWhenRepay(
        uint8 ilkIndex,
        address user,
        address payer,
        uint256 amountOfNormalizedDebt
    ) {
    env e;
    mathint numCallBefore = numAcureInterestCall;
    repay(e, ilkIndex, user, payer, amountOfNormalizedDebt);
    mathint numCallAfter = numAcureInterestCall;
    assert (
        numCallAfter == numCallBefore + 1
    );
}

rule accureInterestWhenWithdrawCollateral(
        uint8 ilkIndex,
        address user,
        address recipient,
        uint256 amount
    ) {
    env e;
    calldataarg args;
    mathint numCallBefore = numAcureInterestCall;
    withdrawCollateral(e, ilkIndex, user, recipient, amount);
    mathint numCallAfter = numAcureInterestCall;
    assert (
        numCallAfter == numCallBefore + 1
    );
}

rule accureInterestWhenDepositCollateral(
        uint8 ilkIndex,
        address user,
        address depositor,
        uint256 amount,
        bytes32[] proof
    ) {
    env e;
    mathint numCallBefore = numAcureInterestCall;
    depositCollateral(e, ilkIndex, user, depositor, amount, proof);
    mathint numCallAfter = numAcureInterestCall;
    assert (
        numCallAfter == numCallBefore + 1
    );
}

// When paused, first update the interest rate 
rule accureInterestWhenPause() {
    env e;
    mathint numCallBefore = numAcureInterestCall;
    pause(e);
    mathint numCallAfter = numAcureInterestCall;
    assert (
        numCallAfter == numCallBefore + 1
    );
}

// function whenPaused() returns mathint {
//     env e;
//     pause(e);
//     mathint numCallAfter = numAcureInterestCall;
//     return numCallAfter;
// }

// invariant notAccureInterestWhenPaused()
//     whenPaused() == numAcureInterestCall;

// When paused, no accureInterest call can be made
rule notAccureInterestWhenPaused(method f) {
    env e;
    calldataarg args;
    require paused(e);
    mathint numCallBefore = numAcureInterestCall;
    f@withrevert(e, args);
    mathint numCallAfter = numAcureInterestCall;
    assert (
        numCallAfter == numCallBefore
    );
}

// When paused lastRateUpdate should be updated to current time stamp
rule setLastRateUpdateWhenUnpause(uint8 ilkIndex, env e) {
    unpause(e);
    assert (
        lastRateUpdate(e, ilkIndex) == assert_uint256(IP.unsafeCastTo48(e, e.block.timestamp))
    );
}

// only lenders themself can redeem their interest-bearing position for the
// underlying asset.
// 1. One lender cannot redeem others' position
rule lenderNotRedeemOtherPosition(address receiverOfUnderlying, uint256 amount, env e) {
    address otherAddr;
    require e.msg.sender != otherAddr;
    uint256 beforeBalance = normalizedBalanceOf(e, otherAddr);
    withdraw(e, receiverOfUnderlying, amount);
    uint256 afterBalance = normalizedBalanceOf(e, otherAddr);
    assert (
        beforeBalance == afterBalance
    );
}

// 2. Lenders can redeem their own positions
rule lenderRedeemOwnPosition(address receiverOfUnderlying, uint256 amount, env e) {
    require amount != 0;
    uint256 beforeTotalWeth = weth(e);
    uint256 beforeBalance = normalizedBalanceOf(e, e.msg.sender);
    withdraw(e, receiverOfUnderlying, amount);
    uint256 afterTotalWeth = weth(e);
    uint256 afterBalance = normalizedBalanceOf(e, e.msg.sender);
    assert (
        beforeBalance > afterBalance && beforeTotalWeth > afterTotalWeth
    );
}

// Lenders can deposit their underlying asset for others.
rule lenderDepositForOthers(address user, uint256 amount, bytes32[] proof, env e) {
    require amount != 0;
    uint256 beforeTotalWeth = weth(e);
    uint256 beforeOtherBalance = normalizedBalanceOf(e, user);
    supply(e, user, amount, proof);
    uint256 afterTotalWeth = weth(e);
    uint256 afterOtherBalance = normalizedBalanceOf(e, user);
    assert (
        beforeOtherBalance < afterOtherBalance && beforeTotalWeth < afterTotalWeth
    );
}

// rule notAccureInterestWhenPausedWithdraw(address receiverOfUnderlying, uint256 amount) {
//     env e;
//     require paused(e);
//     mathint numCallBefore = numAcureInterestCall;
//     withdraw@withrevert(e, receiverOfUnderlying, amount);
//     mathint numCallAfter = numAcureInterestCall;
//     assert (
//         lastReverted && numCallAfter == numCallBefore
//     );
// }

// rule notAccureInterestWhenPausedBorrow(
//         uint8 ilkIndex,
//         address user,
//         address recipient,
//         uint256 amountOfNormalizedDebt,
//         bytes32[] proof
//     ) {
//     env e;
//     require paused(e);
//     mathint numCallBefore = numAcureInterestCall;
//     borrow@withrevert(e, ilkIndex, user, recipient, amountOfNormalizedDebt, proof);
//     mathint numCallAfter = numAcureInterestCall;
//     assert (
//         lastReverted && numCallAfter == numCallBefore
//     );
// }

// rule notAccureInterestWhenPausedRepay(
//         uint8 ilkIndex,
//         address user,
//         address payer,
//         uint256 amountOfNormalizedDebt
//     ) {
//     env e;
//     require paused(e);
//     mathint numCallBefore = numAcureInterestCall;
//     repay@withrevert(e, ilkIndex, user, payer, amountOfNormalizedDebt);
//     mathint numCallAfter = numAcureInterestCall;
//     assert (
//         lastReverted && numCallAfter == numCallBefore
//     );
// }

// rule notAccureInterestWhenPausedWithdrawCollateral(
//         uint8 ilkIndex,
//         address user,
//         address recipient,
//         uint256 amount
//     ) {
//     env e;
//     require paused(e);
//     mathint numCallBefore = numAcureInterestCall;
//     withdrawCollateral@withrevert(e, ilkIndex, user, recipient, amount);
//     mathint numCallAfter = numAcureInterestCall;
//     assert (
//         lastReverted && numCallAfter == numCallBefore
//     );
// }

// rule notAccureInterestWhenPausedDepositCollateral(
//         uint8 ilkIndex,
//         address user,
//         address depositor,
//         uint256 amount,
//         bytes32[] proof
//     ) {
//     env e;
//     require paused(e);
//     mathint numCallBefore = numAcureInterestCall;
//     depositCollateral@withrevert(e, ilkIndex, user, depositor, amount, proof);
//     mathint numCallAfter = numAcureInterestCall;
//     assert (
//         lastReverted && numCallAfter == numCallBefore
//     );
// }

