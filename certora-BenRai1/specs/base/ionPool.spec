using Whitelist as whitelist;
using IonPoolHarness as IonPool;
using ERC20A as underlying; //WETH



/////////////////// METHODS ///////////////////////
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

    //IonPoolHarness
    function _._transferWeth(address user, int256 amount) internal => trasferWethHarness(user, amount) expect void;
    

    //envfree
    function getIlkslength() external returns (uint256) envfree;
    function getIlk(uint256 ilkIndex) external returns (IonPool.Ilk memory) envfree;
    function ilkCount() external returns (uint256) envfree;
    function getIlkValues(uint256 ilkIndex) external  returns (uint104 , uint104 ,uint48 ,address ,uint256 ,uint256 ) envfree;
    function gem(uint8 ilkIndex, address user) external returns (uint256) envfree;
    function vault(uint8 ilkIndex, address user) external returns (uint256, uint256) envfree;
    function unbackedDebt(address user) external returns (uint256) envfree;
    function totalUnbackedDebt() external returns (uint256) envfree;
    function whitelist() external returns (address) envfree;
    function getSupplyCap() external returns (uint256) envfree;
    function interestRateModule() external returns (address) envfree;
    function spot(uint8 ilkIndex) external returns (address) envfree;
    function dust(uint8 ilkIndex) external returns (uint256) envfree;
    function debtCeiling(uint8 ilkIndex) external returns (uint256) envfree;
    function isOperator(address user, address operator) external returns (bool) envfree;
    function weth() external returns (uint256) envfree;
    function addressContains(address ilk) external returns (bool) envfree;
    function getIlkIndex(address ilkAddress) external returns (uint8) envfree;
    function totalNormalizedDebt(uint8 ilkIndex) external returns (uint256) envfree;
    function lastRateUpdate(uint8 ilkIndex) external returns (uint256) envfree;
    function underlying() external returns (address) envfree;
    function getIlkAddress(uint256 ilkIndex) external returns (address) envfree;
    function lastRateUpdate(uint8 ilkIndex) external returns (uint256) envfree;
    function collateral(uint8 ilkIndex, address user) external returns (uint256) envfree;
    function normalizedDebt(uint8 ilkIndex, address user) external returns (uint256) envfree;
    function collateral(uint8 ilkIndex, address user) external returns (uint256) envfree;
    function rateUnaccrued(uint8 ilkIndex) external returns (uint256) envfree;
    function addressContains(address ilk) external returns (bool) envfree;
    function debtCeiling(uint8 ilkIndex) external returns (uint256) envfree;
    function isAllowed(address user, address operator) external returns (bool) envfree;
    function debtUnaccrued() external returns (uint256) envfree;
    function trasferWethHarness(address user, int256 amount) external envfree;
    function wethToTransfer(int256 amount) external returns(int256) envfree;
    function underlying.balanceOf(address account) external returns (uint256) envfree;
    function getIlkSpotPrice(uint256 ilkIndex) external returns (uint256) envfree;
    function getWeth() external returns (uint256) envfree;
}

///////////////// DEFINITIONS /////////////////////

////////////////// FUNCTIONS //////////////////////

///////////////// GHOSTS & HOOKS //////////////////

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
        require(isWhitelisted_Ghost[user]);
        return isWhitelisted_Ghost[user];
        
    }

    function getStETHByWstETHCVL(uint256 amount) returns uint256 {
        return getStETHByWstETH_Ghost[amount];
    }

    function mulDivCVL(uint x, uint y, uint denominator) returns uint {
        require(denominator != 0);
        return require_uint256(x*y/denominator);

    //ghost for underluying balance
}


///////////////// INITIAL PROPERTIES /////////////