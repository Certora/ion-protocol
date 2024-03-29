import "erc20.spec";
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

/// @title The user's valut can only be updated through borrow, repay, depositCollateral, and withdrawCollateral OR confiscateVault.
rule vaultChangesFromCertainFunctions(method f, uint8 ilkIndex, address user){
    env e;
    calldataarg args;
    uint256 collateralBefore = collateral(ilkIndex, user);
    uint256 normalizedDebtBefore = normalizedDebt(ilkIndex, user);

    f(e, args);

    uint256 collateralAfter = collateral(ilkIndex, user);
    uint256 normalizedDebtAfter = normalizedDebt(ilkIndex, user);


    assert (
        (collateralBefore != collateralAfter || normalizedDebtBefore != normalizedDebtAfter) => 
                (
                f.selector == sig:borrow(uint8,address,address,uint256,bytes32[] memory).selector ||
                f.selector == sig:repay(uint8,address,address,uint256).selector ||
                f.selector == sig:depositCollateral(uint8,address,address,uint256,bytes32[] calldata).selector ||
                f.selector == sig:withdrawCollateral(uint8,address,address,uint256).selector ||
                f.selector == sig:confiscateVault(uint8,address,address,address,int256,int256).selector
                )
            ),
        "user's valut changed as a result function other than borrow(), repay(), depositCollateral(),  withdrawCollateral(), or confiscateVault().";
}

// inconclusive
// rule incrementLastRateUpdate(method f, uint8 ilkIndex){
//     env e;
//     calldataarg args;

//     uint256 rateBefore = lastRateUpdate(e, ilkIndex);
//     f(e, args);
//     uint256 rateAfter = lastRateUpdate(e, ilkIndex);

//     assert(rateBefore <= rateAfter),
//     "lastRateUpdate must ever increase.";
// }

// @title withdraw update balance correctly.
rule withdrawCorrectUpdateLiquidity(address receiver, uint256 amount){
    env e;
    require receiver != e.msg.sender;

    uint256 ethBefore = weth();

    withdraw(e, receiver, amount);

    uint256 ethAfter = weth();

    assert(assert_uint256(ethAfter + amount) == ethBefore), "eth update incorrect.";
}

// Invariant: user has vault

invariant sanityRate(env e, uint8 ilkIndex) 
    0 < rate(e, ilkIndex) && 
        rate(e, ilkIndex) <= 0xFFFFFFFFFFFFFFFFFFFFFFFFFF;

invariant sanityRateCal(env e, uint8 ilkIndex, mathint tmp) 
    0 < assert_uint256(rate(e, ilkIndex) * tmp) && 
        assert_uint256(rate(e, ilkIndex) * tmp) <= debtCeiling(ilkIndex);

invariant sanityDebtCelling(uint8 ilkIndex) 
    0 <= debtCeiling(ilkIndex) 
        && debtCeiling(ilkIndex) <= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF;


rule correctTransferCollateralAndGem(env e, 
                        uint8 ilkIndex,
                        address user,
                        address recipient,
                        uint256 amount){
    require nonzerosender(e);
    require amount != 0;

    uint256 collateralBefore = collateral(ilkIndex, user);
    uint256 gemRecipientBefore = gem(ilkIndex, recipient);

    require collateralBefore > amount;
    require gemRecipientBefore + amount < 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff;

    withdrawCollateral@withrevert(e, ilkIndex, user, recipient, amount);
    bool success = !lastReverted;
    uint256 collateralAfter = collateral(ilkIndex, user);
    uint256 gemRecipientAfter = gem(ilkIndex, recipient);

    assert success => 
        assert_uint256(collateralBefore - amount) == collateralAfter, "collateral transfer error.";
        
    assert success =>
        assert_uint256(gemRecipientBefore + amount) == gemRecipientAfter, "gem transfer error.";
}


// inconclusive
// @title borrow behavior and side effects
// NOTE: user borrow debt for recipient
// rule borrow(env e, 
//             uint8 ilkIndex,
//             address user,
//             address recipient,
//             uint256 amountOfNormalizedDebt,
//             bytes32[] proof)
// {
//     require nonzerosender(e);
//     require amountOfNormalizedDebt != 0;

//     uint8 otherIlkIndex;
//     address otherAccount;

//     uint256 normalizedDebtBefore = normalizedDebt(ilkIndex, user);
//     // uint256 normalizedDebtRecipientBefore = normalizedDebt(ilkIndex, recipient);
//     uint256 normalizedDebtOtherBefore = normalizedDebt(ilkIndex, otherAccount);

//     uint256 totalNormalizedDebtBefore = totalNormalizedDebt(ilkIndex);
//     uint256 totalNormalizedDebtOtherBefore = totalNormalizedDebt(otherIlkIndex);

//     uint256 debtBefore = debtUnaccrued();

//     // must remain unchanged
//     uint256 ilkRateBefore = rate(e, ilkIndex);
//     // uint256 ilkRateOtherBefore = rate(e, otherIlkIndex);
//     uint256 collateralBefore = collateral(ilkIndex, user);
//     uint256 collateralRecipientBefore = collateral(ilkIndex, recipient);
//     uint256 gemBefore = gem(ilkIndex, user);
//     uint256 gemZeroAddrBefore = gem(ilkIndex, 0);

//     uint256 debtCeiling = debtCeiling(ilkIndex);

//     borrow@withrevert(e, ilkIndex, user, recipient, amountOfNormalizedDebt, proof);
//     bool success = !lastReverted;

//     // liveness
//     assert success <=> (
//         // 1. _modifyPosition's check
//         //  1.1 ilk has been initialised
//         ilkRateBefore != 0 
//         &&
//         // TODO 1.2 either debt has decreased, or debt ceilings are not exceeded
//                 //    both(
//                 //     changeInNormalizedDebt > 0,
//                 //     uint256(_totalNormalizedDebt) * uint256(ilkRate) > $.ilks[ilkIndex].debtCeiling
//                 //    )
//         assert_uint256((totalNormalizedDebtBefore + amountOfNormalizedDebt) * ilkRateBefore) <= debtCeiling
//         //  1.3 vault is either less risky than before, or it is safe
//         // &&
//         //             newTotalDebtInVault <= _vault.collateral * ilkSpot
//         //  1.4 vault is either more safe, or the owner consents
//         //  1.5 collateral src consents(Only used in `withdraw(deposit)Collateral`)
//         //  1.6 debt dst consents
//         //  1.7 vault has no debt, or a non-dusty amount
//         // 2. user can borrow amount debt, overflow-free ?
        
//     );

//     // effect
//     assert success => (
//         // 1. correct update vault.
//         assert_uint256(normalizedDebtBefore + amountOfNormalizedDebt) == normalizedDebt(ilkIndex, user)
//         &&
//         collateralBefore == collateral(ilkIndex, user)
//         &&
//         // 2. correct update gem.
//         gemZeroAddrBefore  == gem(ilkIndex, 0)
//         &&
//         // 3. correct update totalNormalizedDebt.
//         totalNormalizedDebtBefore < totalNormalizedDebt(ilkIndex)
//         &&
//         // 4. correct update debt.
//         debtBefore < debtUnaccrued()
//         // &&
//         // // 5. correct transfer weth
//         // //  5.1 check $.weth
//         // //  5.2 check recipient's underlying balance

//     );

//     // no side effect
//     assert normalizedDebt(ilkIndex, otherAccount) != normalizedDebtOtherBefore
//         => (otherAccount == user);
//     assert totalNormalizedDebt(otherIlkIndex) != totalNormalizedDebtOtherBefore
//         => (otherIlkIndex == ilkIndex);
// }

// inconclusive
// @title withdrawCollateral behavior and side effects
// NOTE: withdraw user's collateral then add to recipient's gem.
// rule withdrawCollateral(env e, 
//                         uint8 ilkIndex,
//                         address user,
//                         address recipient,
//                         uint256 amount)
// {
//     require nonzerosender(e);
//     require amount != 0;

//     uint8 otherIlkIndex;
//     address otherAccount;
//     uint256 otherAmount;

//     // ilk.rate = uint104(RAY);
//     requireInvariant sanityRate(e, ilkIndex);

//     uint256 ilkRateBefore = rate(e, ilkIndex);
//     // uint256 ilkRateOtherBefore = rate(e, otherIlkIndex);

//     // must remain unchanged
//     uint256 normalizedDebtBefore = normalizedDebt(ilkIndex, user);
//     uint256 normalizedDebtRecipientBefore = normalizedDebt(ilkIndex, recipient);
//     // uint256 normalizedDebtOtherBefore = normalizedDebt(ilkIndex, otherAccount);

//     uint256 totalNormalizedDebtBefore = totalNormalizedDebt(ilkIndex);
//     // uint256 totalNormalizedDebtOtherBefore = totalNormalizedDebt(otherIlkIndex);

//     uint256 collateralBefore = collateral(ilkIndex, user);
//     uint256 collateralRecipientBefore = collateral(ilkIndex, recipient);
//     uint256 collateralOtherBefore = collateral(ilkIndex, otherAccount);

//     uint256 gemBefore = gem(ilkIndex, user);
//     uint256 gemRecipientBefore = gem(ilkIndex, recipient);
//     uint256 gemOtherBefore = gem(ilkIndex, otherAccount);

//     uint256 debtBefore = debtUnaccrued();

//     // updateIlkDebtCeiling(e, ilkIndex, 0xffffffffffffffffffffffffffffffff);
//     // uint256 debtCeiling = debtCeiling(ilkIndex);

//     withdrawCollateral@withrevert(e, ilkIndex, user, recipient, amount);
//     bool success = !lastReverted;

//     // liveness
//     assert success <=> (
//         // // 1. _modifyPosition's check
//         // //   1.1 ilk has been initialised
//         // ilkRateBefore != 0 
//         // &&
//         // 3. user has sufficient collateral for withdrawal
//         collateralBefore >= amount
//     );

//     // effect
//     assert success => (
//         // 1. correct update vault.
//         normalizedDebtBefore == normalizedDebt(ilkIndex, user)
//         &&
//         assert_uint256(collateralBefore - amount) == collateral(ilkIndex, user)
//         &&
//         // 2. correct update gem.
//         assert_uint256(gemRecipientBefore + amount) == gem(ilkIndex, recipient)
//         &&
//         // 3. correct update totalNormalizedDebt.
//         totalNormalizedDebtBefore == totalNormalizedDebt(ilkIndex)
//         &&
//         // 4. correct update debt.
//         debtBefore == debtUnaccrued()
//     );

//     // no side effect

//     // NOTE: rate will ONLY update in withdraw/supply
//     // assert rate(e, otherIlkIndex) != ilkRateOtherBefore 
//     //     => (otherIlkIndex == ilkIndex);

//     // NOTE: normalizedDebt ONLY update in borrow/repay  
//     // assert normalizedDebt(ilkIndex, otherAccount) != normalizedDebtOtherBefore 
//     //     => (otherAccount == user || otherAccount == recipient);

//     // assert totalNormalizedDebt(otherIlkIndex) != totalNormalizedDebtOtherBefore
//     //     => (otherIlkIndex == ilkIndex);

//     assert collateral(ilkIndex, otherAccount) != collateralOtherBefore
//         => (otherAccount == user);

//     assert gem(ilkIndex, otherAccount) != gemOtherBefore
//         => (otherAccount == recipient);
// }

// inconclusive
// Rule problems vacuity check timeout
// @title depositCollateral behavior and side effects
// NOTE: Moves collateral from depositor `gem` balances to user `vault.collateral`
//  need checking onlyWhitelistedBorrowers(ilkIndex, user, proof)
// rule depositCollateral(env e, 
//                     uint8 ilkIndex,
//                     address user,
//                     address depositor,
//                     uint256 amount,
//                     bytes32[] proof)
// {
//     require nonzerosender(e);
//     require amount != 0;

//     uint8 otherIlkIndex;
//     address otherAccount;
//     uint256 otherAmount;

//     // ilk.rate = uint104(RAY);
//     requireInvariant sanityRate(e, ilkIndex);

//     uint256 ilkRateBefore = rate(e, ilkIndex);
//     // uint256 ilkRateOtherBefore = rate(e, otherIlkIndex);

//     // must remain unchanged
//     uint256 normalizedDebtBefore = normalizedDebt(ilkIndex, user);
//     uint256 normalizedDebtDepositorBefore = normalizedDebt(ilkIndex, depositor);

//     uint256 totalNormalizedDebtBefore = totalNormalizedDebt(ilkIndex);

//     uint256 collateralBefore = collateral(ilkIndex, user);
//     uint256 collateralDepositorBefore = collateral(ilkIndex, depositor);
//     uint256 collateralOtherBefore = collateral(ilkIndex, otherAccount);

//     uint256 gemBefore = gem(ilkIndex, user);
//     uint256 gemDepositorBefore = gem(ilkIndex, depositor);
//     uint256 gemOtherBefore = gem(ilkIndex, otherAccount);

//     uint256 debtBefore = debtUnaccrued();

//     depositCollateral@withrevert(e, ilkIndex, user, depositor, amount, proof);
//     bool success = !lastReverted;

//     // liveness
//     assert success <=> (
//         // // 1. _modifyPosition's check
//         // //   1.1 ilk has been initialised
//         // ilkRateBefore != 0 
//         // &&
//         // 3. depositor has sufficient gem to deposit
//         gemDepositorBefore >= amount
//     );

//     // effect
//     assert success => (
//         // 1. correct update vault.
//         normalizedDebtBefore == normalizedDebt(ilkIndex, user)
//         &&
//         assert_uint256(collateralBefore + amount) == collateral(ilkIndex, user)
//         &&
//         // 2. correct update gem.
//         assert_uint256(gemDepositorBefore - amount) == gem(ilkIndex, depositor)
//         &&
//         // 3. correct update totalNormalizedDebt.
//         totalNormalizedDebtBefore == totalNormalizedDebt(ilkIndex)
//         &&
//         // 4. correct update debt.
//         debtBefore == debtUnaccrued()
//     );

//     // no side effect
//     assert collateral(ilkIndex, otherAccount) != collateralOtherBefore
//         => (otherAccount == user);
//     assert gem(ilkIndex, otherAccount) != gemOtherBefore
//         => (otherAccount == depositor);
// }