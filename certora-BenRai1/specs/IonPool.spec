import "erc20.spec";
import "./base/ionPool.spec";


use builtin rule sanity;



//---------------------------- RULES TEST ----------------------------------

//------------------------------RULES OK --------------------------------------

    // initializeIlk works as it should 
    rule initializeIlkIntegraty(){
        env e;
        address ilkAddress;
        uint256 ilkCountBefore = ilkCount();
        require(ilkCountBefore < 255);
        bool inEnumerableSetBefore = addressContains(ilkAddress);


        initializeIlk@withrevert(e, ilkAddress);
        bool lastFReverted = lastReverted;

        mathint ilkCountAfter = ilkCount();
       
        bool inEnumerableSetAfter = addressContains(ilkAddress);


        //--- ok ---
        assert(ilkCountBefore >= 255 => lastFReverted, "initializeIlk does not revert when there are already 256 ilks");
        assert(inEnumerableSetBefore == true => lastFReverted, "initializeIlk does not revert when the new address is already part of the enumerableSet");
        assert(lastFReverted == false => ilkCountAfter == ilkCountBefore + 1, "initializeIlk does not increase the ilkCount propperly");
        assert(ilkAddress == 0 => lastFReverted, "initializeIlk does not revert when the new address is 0");

    }

    // _modifyPosition works as it should (with revert)
    rule _modifyPositionIntegraty(env e) {
        uint8 ilkIndex;
        address user; //u
        address otherUser;
        require(user != otherUser);
        address collateralRecipient; //v
        address otherCollateralRecipient;
        require(collateralRecipient != otherCollateralRecipient);
        address underlyingRecipient; //w
        address otherUnderlyingRecipient;
        require(underlyingRecipient != otherUnderlyingRecipient);
        int256 changeInCollateral;
        int256 changeInNormalizedDebt;
        //currentSupply ETH 120 Million *1e18 => mimit at 100x of current ETH supply
        require(-120 * 10^6 * 10^18 * 100 < changeInNormalizedDebt && changeInNormalizedDebt < 120 * 10^6 * 10^18 * 100);
        

        //------------------BEFORE VALUES------------------
            //ilk before
            mathint ilkRateUnaccruedBefore = rateUnaccrued(ilkIndex);
            //ensure that the change in debt is not bigger than the max_int
            require(ilkRateUnaccruedBefore < ((max_uint / 2) - 1)/(120 * 10^6 * 10^18 * 100));
            mathint ilkDebtCeilingBefore = debtCeiling(ilkIndex);
            mathint ilkTotalNormalizedDebtBefore = totalNormalizedDebt(ilkIndex);
            mathint ilkSpotPrice = getIlkSpotPrice(ilkIndex);

            //collateral in vault before
            mathint collateralUserBefore = collateral(ilkIndex, user);
            mathint collateralOtherUserBefore = collateral(ilkIndex, otherUser);

            //normalizedDeb in vault and protocol before
            mathint normalizedDebtUserBefore = normalizedDebt(ilkIndex, user);
            mathint normalizedDebtOtherUserBefore = normalizedDebt(ilkIndex, otherUser);
            mathint totalNormalizedDebtBefore = totalNormalizedDebt(ilkIndex);

            //total debt before
            mathint debtProtocoldebtUnaccruedBefore = debtUnaccrued();

            //allowances before
            bool msgSenderIsAllowedByUser = isAllowed(user, e.msg.sender);
            bool msgSenderIsAllowedByCollateralSource = isAllowed(collateralRecipient, e.msg.sender);
            bool msgSenderIsAllowedByUnderlyingRecipient = isAllowed(underlyingRecipient, e.msg.sender);

            //others before
            mathint ilkDust = dust(ilkIndex);
            mathint gemsCollateralRecipientBefore = gem(ilkIndex, collateralRecipient);
            mathint gemsOtherCollateralRecipientBefore = gem(ilkIndex, otherCollateralRecipient);

            mathint changeInDebt = ilkRateUnaccruedBefore * changeInNormalizedDebt;
            require(ilkRateUnaccruedBefore * changeInNormalizedDebt < (max_uint/2)-1);

            //weth before
            // mathint balanceUnderlyingRecipientBefore = underlying.balanceOf(e, underlyingRecipient);
            // require(balanceUnderlyingRecipientBefore + changeInDebt < max_uint);
            // mathint balanceOtherUnderlyingRecipientBefore = underlying.balanceOf(e, otherUnderlyingRecipient);
            // mathint balanceUnderlyingPoolBefore = underlying.balanceOf(e, currentContract);
            // require(balanceUnderlyingPoolBefore - changeInDebt < max_uint);
            // require(e.msg.sender == currentContract);
            // mathint wethBefore = weth();
            // mathint wethToTransfer = wethToTransfer(assert_int256(changeInDebt));


        //------------------CALL------------------
            modifyPositionHarness@withrevert(e, ilkIndex, user, collateralRecipient, underlyingRecipient, changeInCollateral, changeInNormalizedDebt);
            bool lastFReverted = lastReverted;
        //------------------CALL------------------

        //------------------AFTER VALUES------------------
        
            //ilk after
            mathint ilkRateUnaccruedAfter = rateUnaccrued(ilkIndex);
            mathint ilkDebtCeilingAfter = debtCeiling(ilkIndex);
            mathint ilkTotalNormalizedDebtAfter = totalNormalizedDebt(ilkIndex);

            //collateral in vault after
            mathint collateralUserAfter = collateral(ilkIndex, user);
            mathint collateralOtherUserAfter = collateral(ilkIndex, otherUser);

            //normalizedDeb in vault and protocol after
            mathint normalizedDebtUserAfter = normalizedDebt(ilkIndex, user);
            mathint normalizedDebtOtherUserAfter = normalizedDebt(ilkIndex, otherUser);
            mathint totalNormalizedDebtAfter = totalNormalizedDebt(ilkIndex);

            //total debt after
            mathint debtProtocoldebtUnaccruedAfter = debtUnaccrued();

            //others after
            mathint newTotalDebtUser = ilkRateUnaccruedBefore * normalizedDebtUserAfter;
            mathint newTotalDebtProtocol = ilkRateUnaccruedBefore * totalNormalizedDebtAfter;
            mathint gemsCollateralRecipientAfter = gem(ilkIndex, collateralRecipient);
            mathint gemsOtherCollateralRecipientAfter = gem(ilkIndex, otherCollateralRecipient);


            //weth after
            // mathint balanceUnderlyingRecipientAfter = underlying.balanceOf(e, underlyingRecipient);
            // mathint balanceOtherUnderlyingRecipientAfter = underlying.balanceOf(e, otherUnderlyingRecipient);
            // mathint balanceUnderlyingPoolAfter = underlying.balanceOf(e, currentContract);
            // mathint wethAfter = weth();
            

        
        //------------------Checks------------------

        //---------------------CHECKS OK ---------------------

            //ilk checks    
            assert(ilkRateUnaccruedBefore == 0 => lastFReverted, "modifiePosition does not revert if the ilk rate is 0");
            assert(ilkRateUnaccruedBefore == ilkRateUnaccruedAfter, "modifiePosition should not change the ilkRateUnaccrued");
            assert(ilkDebtCeilingBefore == ilkDebtCeilingAfter, "modifiePosition should not change the ilkDebtCeiling");
            assert(lastFReverted == false => ilkTotalNormalizedDebtBefore + changeInNormalizedDebt == ilkTotalNormalizedDebtAfter, "modifiePosition does not change the totalNormalizedDebt of the ilk propperly");

            //collateral checks
            assert(lastFReverted == false =>collateralUserBefore + changeInCollateral == collateralUserAfter, "modifiePosition does not change the collateral propperly");
            assert(collateralOtherUserBefore == collateralOtherUserAfter, "modifiePosition should not change the collateral of the other user");
            
            //normalizedDebt changes
            assert(lastFReverted == false =>normalizedDebtUserBefore + changeInNormalizedDebt == normalizedDebtUserAfter, "modifiePosition does not change the normalizedDebt propperly");
            assert(normalizedDebtOtherUserBefore == normalizedDebtOtherUserAfter, "modifiePosition should not change the normalizedDebt of the other user");
            assert(normalizedDebtUserAfter != 0 && newTotalDebtUser < ilkDust => lastFReverted, "modifiePosition should revert if the normalizedDebt of the user is not 0 and the new newTotalDebtUser is smaller than the ilkDust");
            assert(lastFReverted == false => totalNormalizedDebtBefore + changeInNormalizedDebt == totalNormalizedDebtAfter, "modifiePosition does not change the totalNormalizedDebt propperly");

            //total debt changes
            assert(changeInNormalizedDebt > 0 && newTotalDebtProtocol > ilkDebtCeilingBefore => lastFReverted, "modifiePosition should revert if the totalNormalizedDebt * ilkRateUnaccrued is bigger than the ilkDebtCeiling"); 
            assert(lastFReverted == false => debtProtocoldebtUnaccruedBefore + changeInDebt == debtProtocoldebtUnaccruedAfter, "modifiePosition does not change the debtUnaccrued propperly");

            //allowances checks
            assert((changeInNormalizedDebt > 0 || changeInCollateral < 0) && msgSenderIsAllowedByUser == false => lastFReverted, "modifiePosition should revert if the msg.sender is not allowed by user");
            assert(changeInCollateral > 0 && msgSenderIsAllowedByCollateralSource == false => lastFReverted, "modifiePosition should revert if the msg.sender is not allowed by the collateral source");
            assert(changeInNormalizedDebt < 0 && msgSenderIsAllowedByUnderlyingRecipient == false => lastFReverted, "modifiePosition should revert if the msg.sender is not allowed by the underlying recipient");

            //not allocated yet
            assert(lastFReverted == false => gemsCollateralRecipientBefore - changeInCollateral == gemsCollateralRecipientAfter, "modifiePosition does not change the gem of the underlyingRecipient propperly");
            assert(gemsOtherCollateralRecipientBefore == gemsOtherCollateralRecipientAfter, "modifiePosition should not change the gem of the other underlyingRecipient"); 
            assert((changeInNormalizedDebt > 0 || changeInCollateral < 0) && newTotalDebtUser > collateralUserAfter * ilkSpotPrice => lastFReverted, "modifiePosition should revert if the newTotalDebtUser is bigger than the collateralUserAfter * ilkSpotPrice"); 

            // // balance of weth 
            // assert(!lastFReverted => balanceUnderlyingRecipientBefore + wethToTransfer == balanceUnderlyingRecipientAfter, "modifiePosition does not change the balance of the underlyingRecipient propperly");
            // assert(!lastFReverted => balanceOtherUnderlyingRecipientBefore == balanceOtherUnderlyingRecipientAfter, "modifiePosition should not change the balance of the other user");
            // assert(!lastFReverted => balanceUnderlyingPoolBefore - wethToTransfer == balanceUnderlyingPoolAfter, "modifiePosition does not change the balance of the pool propperly");

            // //wethamount in pool storage
            // assert(lastFReverted == false => wethBefore + wethToTransfer == wethAfter, "modifiePosition does not change the weth propperly"); //@audit ok to test
        
        


    }

    //only specific functions can change Whitelist
    rule whitelistCanOnlyBeChangedBySpecificFunctions(method f) filtered{f ->!f.isView}{
        env e;
        calldataarg arg;

        address valueBefore = whitelist();
        
        f(e, arg);
        
        address valueAfter = whitelist();

        assert(valueBefore != valueAfter =>
            f.selector == sig:initialize(address,address,uint8,string,string,address,address,address).selector ||
            f.selector == sig:updateWhitelist(address).selector ,
        "Function should not be able to change whitelist");
    }
   
    //only specific functions can change interestrateModule
    rule interestrateModuleCanOnlyBeChangedBySpecificFunctions(method f) filtered{f ->!f.isView}{
        env e;
        calldataarg arg;

        address valueBefore = interestRateModule();
        
        f(e, arg);
        
        address valueAfter = interestRateModule();

        assert(valueBefore != valueAfter =>
            f.selector == sig:initialize(address,address,uint8,string,string,address,address,address).selector ||
            f.selector == sig:updateInterestRateModule(address).selector ,
        "Function should not be able to change interestRateModule");
    }

    //only specific functions can change wethSupplyCap
    rule wethSupplyCapCanOnlyBeChangedBySpecificFunctions(method f) filtered{f ->!f.isView}{
        env e;
        calldataarg arg;

        uint256 valueBefore = getSupplyCap();
        
        f(e, arg);
        
        uint256 valueAfter = getSupplyCap();

        assert(valueBefore != valueAfter =>
            f.selector == sig:updateSupplyCap(uint256).selector ,
        "Function should not be able to change weth");
    }

    //only specific functions can change weth
    rule wethCanOnlyBeChangedBySpecificFunctions(method f) filtered{f ->!f.isView}{
        env e;
        calldataarg arg;

        uint256 valueBefore = weth();
        
        f(e, arg);
        
        uint256 valueAfter = weth();

        assert(valueBefore != valueAfter =>
            f.selector == sig:borrow(uint8,address,address,uint256,bytes32[]).selector ||
            f.selector == sig:depositCollateral(uint8,address,address,uint256,bytes32[]).selector ||
            f.selector == sig:repay(uint8,address,address,uint256).selector ||
            f.selector == sig:repayBadDebt(address,uint256).selector ||
            f.selector == sig:supply(address,uint256,bytes32[]).selector ||
            f.selector == sig:withdraw(address,uint256).selector ||
            f.selector == sig:withdrawCollateral(uint8,address,address,uint256).selector,
        "Function should not be able to change weth");
    }

    //removeOperator works as it should 
    rule removeOperatorIntegraty(){
        env e;
        address operator;

        removeOperator(e, operator);

        bool valueAfter = isOperator(e.msg.sender, operator);

        assert(valueAfter == false, "removeOperator does not set the operator propperly");
    }


    //addOperator works as it should 
    rule addOperatorIntegraty(){
        env e;
        address operator;

        addOperator(e, operator);

        bool valueAfter = isOperator(e.msg.sender, operator);

        assert(valueAfter == true, "addOperator does not set the operator propperly");
    }

    //updateIlkDebtCeiling works as it should
    rule updateIlkDebtCeilingIntegraty(){
        env e;
        uint8 ilkIndex;
        uint256 newCeiling;

        updateIlkDebtCeiling(e, ilkIndex, newCeiling);

        uint256 valueAfter = debtCeiling(ilkIndex);

        assert(newCeiling == valueAfter, "updateIlkDebtCeiling does not set the newCeiling propperly");
    }

    //updateIlkDust works as it should
    rule updateIlkDustIntegraty(){
        env e;
        uint8 ilkIndex;
        uint256 newDust;

        updateIlkDust(e, ilkIndex, newDust);

        uint256 valueAfter = dust(ilkIndex);

        assert(newDust == valueAfter, "updateIlkDust does not set the new dustValue propperly");
    }


    //updateIlkSpot works as it should
    rule updateIlkSpotIntegraty(){
        env e;
        uint8 ilkIndex;
        address newSpot;

        updateIlkSpot(e, ilkIndex, newSpot);

        address valueAfter = spot(ilkIndex);

        assert(newSpot == valueAfter, "updateIlkSpot does not set the newSpot propperly");
    }

    //updateSupplyCap works as it should
    rule updateSupplyCapIntegraty(){
        env e;
        uint256 newValue;

        updateSupplyCap(e, newValue);

        uint256 valueAfter = getSupplyCap();

        assert(newValue == valueAfter, "updateSupplyCap does not set the new supplyCap propperly");
    }

    //updateWhitelist works as it should
    rule updateWhitelistIntegraty(){
        env e;
        address newValue;
        address valueBefore = whitelist();

        updateWhitelist@withrevert(e, newValue);
        bool lastFReverted = lastReverted;

        address valueAfter = whitelist();

        assert(newValue == 0 => lastFReverted, "updateWhitelist does not revert when the new address is 0");
        assert(lastFReverted == false => newValue == valueAfter, "updateWhitelist does not set the new whitelist propperly");
    }


    //only specific functions can change total bad debt
    rule totalBedDebtCanOnlyBeChangedBySpecificFunctions(method f) filtered{f ->!f.isView}{
        env e;
        calldataarg arg;

        uint256 valueBefore = totalUnbackedDebt();
        
        f(e, arg);
        
        uint256 valueAfter = totalUnbackedDebt();

        assert(valueBefore != valueAfter =>
            f.selector == sig:confiscateVault(uint8,address,address,address,int256,int256).selector ||
            f.selector == sig:repayBadDebt(address,uint256).selector,
        "Function should not be able to change total bad debt");
    }

    //only specific functions can change users bad debt
    rule userBedDebtCanOnlyBeChangedBySpecificFunctions(method f) filtered{f ->!f.isView}{
        env e;
        calldataarg arg;
        address user;

        uint256 badDebtBefore = unbackedDebt(user);
        
        f(e, arg);
        
        uint256 badDebtAfter = unbackedDebt(user);

        assert(badDebtBefore != badDebtAfter =>
            f.selector == sig:confiscateVault(uint8,address,address,address,int256,int256).selector ||
            f.selector == sig:repayBadDebt(address,uint256).selector,
        "Function should not be able to change users bad debt");
    }

    //only specific functions can change vaults
    rule vaultsCanOnlyBeChangedBySpecificFunctions(method f) filtered{f ->!f.isView}{
        env e;
        calldataarg arg;
        uint8 ilkIndex;
        address user;
        uint256 collateralBefore;
        uint256 collateralAfter;
        uint256 normalizedDebtBefore;
        uint256 normalizedDebtAfter;

        collateralBefore, normalizedDebtBefore  = vault(ilkIndex, user);
        
        f(e, arg);
        
        collateralAfter, normalizedDebtAfter = vault(ilkIndex, user);

        assert(collateralBefore != collateralAfter || 
            normalizedDebtBefore != normalizedDebtAfter =>
            f.selector == sig:borrow(uint8,address,address,uint256,bytes32[]).selector ||
            f.selector == sig:confiscateVault(uint8,address,address,address,int256,int256).selector ||
            f.selector == sig:depositCollateral(uint8,address,address,uint256,bytes32[]).selector ||
            f.selector == sig:repay(uint8,address,address,uint256).selector ||
            f.selector == sig:withdrawCollateral(uint8,address,address,uint256).selector,
        "Function should not be able to change vaults");
    }

    //only specific functions can change gems
    rule gemsCanOnlyBeChangedBySpecificFunctions(method f) filtered{f ->!f.isView}{
        env e;
        calldataarg arg;
        uint8 ilkIndex;
        address user;
        uint256 gemBefore = gem(ilkIndex, user);
        
        f(e, arg);
        
        uint256 gemAfter  = gem(ilkIndex, user);

        assert(gemBefore != gemAfter =>
            f.selector == sig:borrow(uint8,address,address,uint256,bytes32[]).selector ||
            f.selector == sig:confiscateVault(uint8,address,address,address,int256,int256).selector ||
            f.selector == sig:depositCollateral(uint8,address,address,uint256,bytes32[]).selector ||
            f.selector == sig:mintAndBurnGem(uint8,address,int256).selector ||
            f.selector == sig:repay(uint8,address,address,uint256).selector ||
            f.selector == sig:transferGem(uint8,address,address,uint256).selector ||
            f.selector == sig:unpause().selector ||
            f.selector == sig:withdrawCollateral(uint8,address,address,uint256).selector,
        "Function should not be able to change gems");
    }

    //only specific functions can change totalNormalizedDebt, rate and lastRateUpdate of ilks
    rule variablesOfIlksCanOnlyBeChangedBySpecificFunctions(method f) filtered{f ->!f.isView}{
        env e;
        calldataarg arg;
        uint256 ilkIndex; 
        uint104 totalNormalizedDebtBefore; 
        uint104 rateBefore; 
        uint48 lastRateUpdateBefore; 
        address spotBefore; 
        uint256 debtCeilingBefore; 
        uint256 dustBefore; 

        uint104 totalNormalizedDebtAfter; 
        uint104 rateAfter; 
        uint48 lastRateUpdateAfter; 
        address spotAfter; 
        uint256 debtCeilingAfter; 
        uint256 dustAfter; 


        totalNormalizedDebtBefore, rateBefore, lastRateUpdateBefore, spotBefore, debtCeilingBefore, dustBefore = getIlkValues(ilkIndex);

        f(e, arg);

        totalNormalizedDebtAfter, rateAfter, lastRateUpdateAfter, spotAfter, debtCeilingAfter, dustAfter = getIlkValues(ilkIndex);

        assert((
        totalNormalizedDebtBefore != totalNormalizedDebtAfter ||
        rateBefore != rateAfter ||
        lastRateUpdateBefore != lastRateUpdateAfter
        )=> 
            f.selector == sig:accrueInterest().selector ||
            f.selector == sig:borrow(uint8,address,address,uint256,bytes32[]).selector ||
            f.selector == sig:confiscateVault(uint8,address,address,address,int256,int256).selector ||
            f.selector == sig:depositCollateral(uint8,address,address,uint256,bytes32[]).selector ||
            f.selector == sig:initializeIlk(address).selector ||
            f.selector == sig:pause().selector ||
            f.selector == sig:repay(uint8,address,address,uint256).selector ||
            f.selector == sig:repayBadDebt(address,uint256).selector ||
            f.selector == sig:supply(address,uint256,bytes32[]).selector ||
            f.selector == sig:unpause().selector ||
            f.selector == sig:withdraw(address,uint256).selector ||
            f.selector == sig:withdrawCollateral(uint8,address,address,uint256).selector,
        "Function should not be able to change `variable` values in the ilks array");
    }
    
    //only initializeIlk changes the length of ilks array
    rule changeLengthOfIlkAddresses(){

        method f;
        env e;
        calldataarg arg;

        uint256 ilksLengthBefore = ilkCount();

        f(e, arg);

        uint256 ilksLengthAfter = ilkCount();


        assert(ilksLengthBefore != ilksLengthAfter => f.selector == sig:initializeIlk(address).selector, "Function should not be abel to change the length of ilks array");

    }

    // only whitelisted borrowers can borrow
    rule onlyWhitelistedBorrowerCanBorrow(){
        env e;
        uint8 ilkIndex;
        address user;
        address recipient;
        uint256 amountOfNormalizedDebt;
        bytes32[] proof;

        borrow(e, ilkIndex, user, recipient, amountOfNormalizedDebt, proof);

        assert(getWhitelistCVL(user), "Caller is not whitelisted as borrower");
    }

    // only whitelisted borrowers can depositCollateral
    rule onlyWhitelistedBorrowerCanDepositCollateral(){
        env e;
        uint8 ilkIndex;
        address user;
        address recipient;
        uint256 amountOfNormalizedDebt;
        bytes32[] proof;

        depositCollateral(e, ilkIndex, user, recipient, amountOfNormalizedDebt, proof);

        assert(getWhitelistCVL(user), "Caller is not whitelisted as borrower");

    }

    // only whitelisted Lenders are able to call supply
    rule onlyWhitelistedLendersCanSupply(){
        env e;
        address user;
        uint256 amount;
        bytes32[] proof;

        supply(e, user, amount, proof);

        assert(getWhitelistCVL(user), "Caller is not whitelisted as Lender");

    }

    // only LIQUIDATOR_ROLE role can call this functions
    rule onlyLIQUIDATOR_ROLE(method f) filtered{ f ->
        f.selector == sig:confiscateVault(uint8,address,address,address,int256,int256).selector 
        }{
        env e;
        calldataarg arg;

        f(e, arg);

        assert(hasRole(e,LIQUIDATOR_ROLE(e), e.msg.sender), "Caller does not have the LIQUIDATOR_ROLE");
    }

        // only GEM_JOIN_ROLE role can call this functions
    rule onlyGEM_JOIN_ROLE(method f) filtered{ f ->
        f.selector == sig:mintAndBurnGem(uint8,address,int256).selector 
        }{
        env e;
        calldataarg arg;

        f(e, arg);

        assert(hasRole(e,GEM_JOIN_ROLE(e), e.msg.sender), "Caller does not have the LIQUIDATOR_ROLE");
    }

    // only ION role can call this functions
    rule onlyIonRole(method f) filtered{ f ->
        f.selector == sig:initializeIlk(address).selector ||
        f.selector == sig:pause().selector ||
        f.selector == sig:unpause().selector ||
        f.selector == sig:updateIlkDebtCeiling(uint8,uint256).selector ||
        f.selector == sig:updateIlkDust(uint8,uint256).selector ||
        f.selector == sig:updateIlkSpot(uint8,address).selector ||
        f.selector == sig:updateInterestRateModule(address).selector ||
        f.selector == sig:updateSupplyCap(uint256).selector ||
        f.selector == sig:updateWhitelist(address).selector
        }{
        env e;
        calldataarg arg;

        f(e, arg);

        assert(hasRole(e,ION(e), e.msg.sender), "Caller does not have the ION role");


    }

    //this functions can not be called when paused
    rule notCallableWhenPause(method f) filtered{f->
        f.selector == sig:accrueInterest().selector ||
        f.selector == sig:borrow(uint8,address,address,uint256,bytes32[]).selector ||
        f.selector == sig:depositCollateral(uint8,address,address,uint256,bytes32[]).selector ||
        f.selector == sig:repay(uint8,address,address,uint256).selector ||
        f.selector == sig:repayBadDebt(address,uint256).selector ||
        f.selector == sig:supply(address,uint256,bytes32[]).selector ||
        f.selector == sig:withdraw(address,uint256).selector ||
        f.selector == sig:confiscateVault(uint8,address,address,address,int256,int256).selector ||
        f.selector == sig:withdrawCollateral(uint8,address,address,uint256).selector

     }{
        env e;
        calldataarg arg;

        require(paused(e));

        f@withrevert(e,arg);
        assert(lastReverted, "Function can be called even if the contract is paused");
    }

//------------------------- INVARIENTS -----------------------------

    //totalBadDebt is the sum of all users bad debt
    invariant totalBadDebtInvariant(address alice, address bob, address carol)
        (alice != bob && bob != carol && alice != carol) =>
        unbackedDebt(alice) + unbackedDebt(bob) + unbackedDebt(carol) == to_mathint(totalUnbackedDebt())
        { 
            preserved confiscateVault(uint8 ilkIndex, address u, address v, address w, int256 changeInCollateral, int256 changeInNormalizedDebt) with(env e){
            require w == alice || w == bob || w == carol;
            }

            preserved repayBadDebt(address user, uint256 rad) with(env e){
            require user == alice || user == bob || user == carol;
            }

    }

    //bad dabed of a user is always smaller or equal to the total bad debt
    invariant userBadDebtInvariant(address a) unbackedDebt(a) <= totalUnbackedDebt()
    { 
        preserved confiscateVault(uint8 ilkIndex, address u, address v, address w, int256 changeInCollateral, int256 changeInNormalizedDebt) with(env e){
        require w == a;
        }

        preserved repayBadDebt(address user, uint256 rad) with(env e){
        require user == a;
        }

    }

    
   