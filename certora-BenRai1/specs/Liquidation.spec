import "erc20.spec";
import "./base/liquidation.spec";

use builtin rule sanity;

//------------------------------RULES OK --------------------------------------


///////////////// INVARIANTS OK /////////////
    
    
    //_targetHealth >= RAY
    invariant targetHealthInvariant2() TARGET_HEALTH() >= 10^27;
    
    //invariants _maxDiscounts < RAY (10^27)
    invariant maxDiscountInvariant() MAX_DISCOUNT_0() < 10^27 && MAX_DISCOUNT_1() < 10^27 && MAX_DISCOUNT_2() < 10^27;

    //_liquidationThresholds != 0
    invariant liquidationThresholdsInvariant() LIQUIDATION_THRESHOLD_0() != 0 && LIQUIDATION_THRESHOLD_1() != 0 && LIQUIDATION_THRESHOLD_2() != 0;




//--------------- OLD RULES -----------------------------