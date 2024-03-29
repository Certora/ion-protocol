/////////////////// METHODS ///////////////////////
methods{
    //envfree
    function getAdjustedProfitMargin(uint256 ilkIndex) external returns (uint96) envfree;
    function getMinimumKinkRate(uint256 ilkIndex) external returns (uint96) envfree;
    function getReserveFactor(uint256 ilkIndex) external returns (uint16) envfree;
    function getAdjustedBaseRate(uint256 ilkIndex) external returns (uint96) envfree;
    function getMinimumBaseRate(uint256 ilkIndex) external returns (uint96) envfree;
    function getOptimalUtilizationRate(uint256 ilkIndex) external returns (uint16) envfree;
    function getDistributionFactor(uint256 ilkIndex) external returns(uint16) envfree;
    function getAdjustedAboveKinkSlope(uint256 ilkIndex) external returns (uint96) envfree;
    function getMinimumAboveKinkSlope(uint256 ilkIndex) external returns (uint96) envfree;
    function calculateInterestRate(uint256 ilkIndex, uint256 totalIlkDebt, uint256 totalEthSupply) external returns (uint256, uint256) envfree;
    function getUtilizationRate(uint256 totalEthSupply, uint256 totalIlkDebt, uint256 ilkIndex) external returns (uint256) envfree;
    function utilRateBelowOptimum (uint256 ilkIndex, uint256 utilisationRate) external returns (uint256, uint256) envfree;
    
}

///////////////// DEFINITIONS /////////////////////

////////////////// FUNCTIONS //////////////////////

///////////////// GHOSTS & HOOKS //////////////////

///////////////// INITIAL PROPERTIES /////////////

///////////////// INVARIANTS /////////////



