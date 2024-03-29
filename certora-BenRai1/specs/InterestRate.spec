import "./base/interestRate.spec";

use builtin rule sanity;


// -----------------------------INVARIANTS OK --------------------------

    // minimumKinkRate > minimumBaseRate for all Ils
    invariant minimumKinkRateBaseRateInvariant(uint256 a) getMinimumKinkRate(a) >= getMinimumBaseRate(a);

    // reserveFactor <= RAY (1e27) for all Ils
    invariant reserveFactorInvariant(uint256 a) getReserveFactor(a) <= 2^16-1;

    // optimalUtilizationRate != 0 in the beginning for all Ils
    invariant optimalUtilizationRateInvariant(uint256 a) getOptimalUtilizationRate(a) != 0;

    // distributionFactor for each Il is between 0 and 10000
    invariant individualDistributionFactorInvariant(uint256 a) getDistributionFactor(a) <= 10000;

    // sum of distributionFactor for all Ils is 10000
    invariant sumDistributionFactorInvariant(uint256 a) a <= 7 => 
    getDistributionFactor(0) + getDistributionFactor(1) + getDistributionFactor(2) + getDistributionFactor(3) + getDistributionFactor(4) + getDistributionFactor(5) + getDistributionFactor(6) + getDistributionFactor(6) == 10000;
