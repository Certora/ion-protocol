// Created a harness to help write rules
using InterestRateHarness as InterestRateHarness;

// Declare envfree methods
methods
{
    function calculateInterestRate(uint256, uint256, uint256) external returns(uint256, uint256) envfree;
    function InterestRateHarness.unpackCollateralConfig(uint256) external returns(InterestRateHarness.IlkData) envfree;
    function InterestRateHarness.scaleUpToRay(uint256, uint256) external returns(uint256) envfree;
    function InterestRateHarness.getCollateralCount() external returns(uint256) envfree;
    function InterestRateHarness.getRAY() external returns(uint256) envfree;
    // function InterestRateHarness.getRAD() external returns(uint256) envfree;
    // function InterestRateHarness.getWAD() external returns(uint256) envfree;
    function InterestRateHarness.sumOfReserveFactor() external returns(uint256) envfree;
}

// ReserveFactor should always be ilkData.reserveFactor.scaleUpToRay(4)
// Verified
rule calculateCorrectReserveFactor(
        uint256 ilkIndex,
        uint256 totalIlkDebt,
        uint256 totalEthSupply
     ) 
{
    InterestRateHarness.IlkData ilkData = InterestRateHarness.unpackCollateralConfig(ilkIndex);
    uint16 reserveFactorInput = ilkData.reserveFactor;
    uint256 reserveFactorInputScaleUp = InterestRateHarness.scaleUpToRay(reserveFactorInput, 4);
    
    uint256 borrowRate;
    uint256 reserveFactor;
    
    borrowRate, reserveFactor = InterestRateHarness.calculateInterestRate(ilkIndex, totalIlkDebt, totalEthSupply);

    // Always be ilkData.reserveFactor.scaleUpToRay(4)
    assert reserveFactor == reserveFactorInputScaleUp;
}

// If distributionFactor == 0 then borrowRate == minimumKinkRate
// Verified
rule calculateCorrectBorrowRateZeroDistributionFactor(
        uint256 ilkIndex,
        uint256 totalIlkDebt,
        uint256 totalEthSupply
     ) 
{
    InterestRateHarness.IlkData ilkData = InterestRateHarness.unpackCollateralConfig(ilkIndex);
    uint16 distributionFactor = ilkData.distributionFactor;
    uint96 minimumKinkRate = ilkData.minimumKinkRate;

    require distributionFactor == 0;
    
    uint256 borrowRate;
    uint256 reserveFactor;
    
    borrowRate, reserveFactor = InterestRateHarness.calculateInterestRate(ilkIndex, totalIlkDebt, totalEthSupply);

    assert assert_uint256(minimumKinkRate) == borrowRate;
}

// If ilkData.distributionFactor != 0, then borrowRate >= max(adjustedBaseRate, minimumBaseRate)
// Verified
rule calculateCorrectBorrowRateLargerThanBase(
        uint256 ilkIndex,
        uint256 totalIlkDebt,
        uint256 totalEthSupply
     ) 
{
    InterestRateHarness.IlkData ilkData = InterestRateHarness.unpackCollateralConfig(ilkIndex);
    uint16 distributionFactor = ilkData.distributionFactor;
    uint96 adjustedBaseRate = ilkData.adjustedBaseRate;
    uint96 minimumBaseRate = ilkData.minimumBaseRate;
    uint96 maxBaseRate;

    if (minimumBaseRate > adjustedBaseRate) {
        maxBaseRate = minimumBaseRate;
    } else {
        maxBaseRate = adjustedBaseRate;
    }

    require distributionFactor != 0;
    
    uint256 borrowRate;
    uint256 reserveFactor;
    
    borrowRate, reserveFactor = InterestRateHarness.calculateInterestRate(ilkIndex, totalIlkDebt, totalEthSupply);
    
    assert borrowRate >= assert_uint256(maxBaseRate);
}

// calculateInterestRate function should always revert when ilkIndex >= collateralCount
// Verified
rule calculateRevert(
        uint256 ilkIndex,
        uint256 totalIlkDebt,
        uint256 totalEthSupply
     ) 
{
    InterestRateHarness.IlkData ilkData = InterestRateHarness.unpackCollateralConfig(ilkIndex);
    uint256 collateralCount = InterestRateHarness.getCollateralCount();
    require ilkIndex >= collateralCount;
    InterestRateHarness.calculateInterestRate@withrevert(ilkIndex, totalIlkDebt, totalEthSupply);
    assert lastReverted;
}

// Spec: _unpackCollateralConfig preserve all input validations in constructor
invariant unPackCorrect(
        uint256 ilkIndex
)
    InterestRateHarness.unpackCollateralConfig(ilkIndex).minimumKinkRate >= InterestRateHarness.unpackCollateralConfig(ilkIndex).minimumBaseRate
    && InterestRateHarness.unpackCollateralConfig(ilkIndex).optimalUtilizationRate != 0
    && assert_uint256(InterestRateHarness.unpackCollateralConfig(ilkIndex).reserveFactor) <= InterestRateHarness.getRAY()
    && ilkIndex <= 8;

// calculateInterestRate function should not revert when inputs are allowed by constructor checks
// Violated. Reverted unexpectedly
// rule calculateNotRevert(
//         uint256 ilkIndex,
//         uint256 totalIlkDebt,
//         uint256 totalEthSupply
//      ) 
// {
//     InterestRateHarness.IlkData ilkData = InterestRateHarness.unpackCollateralConfig(ilkIndex);
//     uint256 collateralCount = InterestRateHarness.getCollateralCount();
//     // Same validations as the ones in constructor of InterestRate contract
//     require ilkData.minimumKinkRate >= ilkData.minimumBaseRate;
//     require ilkData.optimalUtilizationRate != 0;
//     require assert_uint256(ilkData.reserveFactor) <= 10000;
//     require InterestRateHarness.sumOfReserveFactor() == 10000;
//     require ilkIndex < collateralCount && collateralCount <= 8;

//     require totalIlkDebt <= InterestRateHarness.getRAD();
//     require totalEthSupply <= InterestRateHarness.getWAD();

//     InterestRateHarness.calculateInterestRate@withrevert(ilkIndex, totalIlkDebt, totalEthSupply);
//     assert !lastReverted;
// }

// function isRevertCalculateInterestRate(
//         uint256 ilkIndex,
//         uint256 totalIlkDebt,
//         uint256 totalEthSupply
// ) returns bool {
//     uint256 collateralCount = InterestRateHarness.getCollateralCount();
//     require ilkIndex < collateralCount && collateralCount <= 8;
//     InterestRateHarness.calculateInterestRate@withrevert(ilkIndex, totalIlkDebt, totalEthSupply);
//     return lastReverted;
// }

// invariant calculateNotRevertInv(
//         uint256 ilkIndex,
//         uint256 totalIlkDebt,
//         uint256 totalEthSupply
// )
//     !isRevertCalculateInterestRate(ilkIndex, totalIlkDebt, totalEthSupply);

// Spec: reserveFactor output of calculateInterestRate should be <= 1 RAY (1e27)
// Violated 
invariant calculateReserveFactorLessThan1RAY(
        uint256 ilkIndex,
        uint256 totalIlkDebt,
        uint256 totalEthSupply
)
    getCalculatedReserveFactor(ilkIndex, totalIlkDebt, totalEthSupply) <= InterestRateHarness.getRAY();

// Get reserveFactor out of calculateInterestRate output
function getCalculatedReserveFactor(
        uint256 ilkIndex,
        uint256 totalIlkDebt,
        uint256 totalEthSupply
) returns uint256 {
    uint256 borrowRate;
    uint256 reserveFactor;
    
    borrowRate, reserveFactor = InterestRateHarness.calculateInterestRate(ilkIndex, totalIlkDebt, totalEthSupply);
    return reserveFactor;
}
