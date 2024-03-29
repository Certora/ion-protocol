## Table of contents

- [**Overview**](#overview)
    - [**About Certora**](#about-certora)
    - [**About Ion Protocol**](#about-ion-protocol)
    - [**About Hats Finance**](#about-hats-finance)
    - [**Summary**](#summary)
- [**Low Findings (5)**](#low-findings)
    - [**L-01**](#l-01-permanent-pause-of-gemjoin-contract-will-break-contracts-functionality)
    - [**L-02**](#l-02-unhandled-chainlink-revert-would-lock-price-oracle-access-in-ethxspotoraclesolgetprice)
    - [**L-03**](#l-03-reservefactor-validation-check-cannot-revert-in-case-of-invalid-value-assignment)
    - [**L-04**](#l-04-payable-modifier-on-function-without-use-of-native-currency-can-lead-to-locked-eth)
    - [**L-05**](#l-05-exchange-rate-aggregation-can-lead-to-lower-pricing-and-opens-to-vulnerability-for-the-protocol-and-users)
- [**Mutations**](#mutations)
    - [InterestRate](#interestrate)
    - [IonPool](#ionpool)
    - [Liquidation](#liquidation)
- [**Notable Properties**](#notable-properties)
    - [InterestRate](#interestrate-1)
    - [IonPool](#ionpool-1)
    - [Liquidation](#liquidation-1)
- [**Disclaimer**](#disclaimer)

# Overview

This report compiles the bugs found and properties proven in the Ion Protocol contest in collaboration with Hats Finance. 

## Competition Details

- **Duration**: Jan 22 to Feb 5 2024
- **Maximum Reward**: $40,000
- **Submissions**: 49
- **Findings**: 5 Low
- **Total Payout**: $12,500 distributed among 13 participants

## About Ion Protocol

Ion Protocol is a price-agnostic lending platform built to support staked and restaked assets. It allows users to participate in lending markets of all kinds, ranging from leveraged staking yields to points multiplier pools and more. Ion focuses on bringing staking-based mechanisms to DeFi, creating an enhanced lending and borrowing experience for users to earn more while risking less.

## About Hats Finance

Hats Finance builds autonomous security infrastructure for integration with major DeFi protocols to secure users' assets. Hats Audit Competitions revolutionize web3 project security through decentralized, competition-based bug hunting, rewarding only auditors who identify vulnerabilities. This approach efficiently uses budgets by paying for results, and attracts top talent by prioritizing the first submitter of a vulnerability, setting a new standard in decentralized web3 security.

## About Certora

Certora is a Web3 security company that provides industry-leading formal verification tools and smart contract audits. Certora’s flagship security product, Certora Prover, is a unique SaaS product which locates hard-to-find bugs in smart contracts or mathematically proves their absence. A formal verification contest is a competition where members of the community mathematically validate the accuracy of smart contracts, in return for a reward offered by the sponsor based on the participants' findings and property coverage.

## Summary 

In the formal verification contest detailed here, contenders formally verified IonPool smart contracts. Mutations are used to evaluate the quality of the specification. The mutations are described below and were made available at the end of the contest, you can find them [here](https://github.com/Certora/ion-protocol/blob/master/certora/mutations). Additionally, the top specifications have been added to the [contest repo](https://github.com/Certora/ion-protocol/blob/master) and some specific properties have been included in this report as good examples. You can find the final results for the competition [here](https://docs.google.com/spreadsheets/d/1fiNkz2oucJer0zjV0x4_xlgo6o9HMFlviVQ2Zb5K-CA/edit#gid=1970712821).

# Low Findings

## [L-01](https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/issues/35) Permanent pause of `GemJoin` contract will break contracts functionality

_Submitted by 0xRizwan_

### Description

`GemJoin.sol` is one of the core contract and it is extensively used in Ion protocol contracts and it allows users to convert their ERC20 tokens into internal gem balance inside the IonPool which can then be collateralized and borrowed against it.

`GemJoin.sol` can be paused by owner which is pauser and it can call pause() to pause the contract. After pausing the contract, if the owner renounces its ownership then the pause state of contract will be permanent, there would be no way to reverse this action or unless contract redeployment happens.

Functions like `GemJoin.join()` and `GemJoin.exit()` can only be called when the contract is not paused due to presense of `whenNotPaused` on these functions.

This should not be considered as centralization risk considering the overall impact produces by the owner action, however a simple below recommendation is fixing this permanent failure from happenning and also this issue is not submitted by openzeppelin audit report.

The issue is identified as low severity as there is no fund loss and only contract functionality is affected.

### Impact
Whole contracts functionality is permanently broken the owner renounces as the ownership after pausing the contracts.

### Recommendation to fix
Recommend to disable the renounce ownership function in contract.

For example:

```
    function renounceOwnership() public override onlyOwner {
        revert (" can 't renounceOwnership here ");
    }
```

## [L-02](https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/issues/36) Unhandled Chainlink revert would lock price oracle access in `EthXSpotOracle.sol.getPrice()`

_Submitted by 0xRizwan_

### Description

In `EthXSpotOracle.sol.getPrice()`,

```
    function getPrice() public view override returns (uint256 ethPerEthX) {

        (, int256 answer,,,) = REDSTONE_ETHX_PRICE_FEED.latestRoundData();

        uint256 usdPerEthX = uint256(answer).scaleUpToWad(REDSTONE_DECIMALS);

        (, int256 _usdPerEth,,,) = USD_PER_ETH_CHAINLINK.latestRoundData(); 

        uint256 usdPerEth = uint256(_usdPerEth).scaleUpToWad(CHAINLINK_DECIMALS); 

        ethPerEthX = usdPerEthX.wadDivDown(usdPerEth);
    }
```

`getPrice()` makes use of Chainlink's `latestRoundData()` to get the latest price. However, there is no fallback logic to be executed when the access to the Chainlink data feed is denied by Chainlink's multisigs. Chainlink's multisigs can immediately block access to price feeds at will. Therefore, to prevent denial of service scenarios, it is recommended to query Chainlink price feeds using a defensive approach with Solidity’s try/catch structure. In this way, if the call to the price feed fails, the caller contract is still in control and can handle any errors safely and explicitly.

Referring Chainlink documentation on how Chainlink services are updated. Please note Chainlink multisig holds the power of Chainlink’s multisigs can immediately block access to price feeds at will.

Onchain updates take place at the smart contract level, where a multi-signature safe (multisig) is used to modify onchain parameters relating to a Chainlink service. This can include replacing faulty nodes on a specific oracle network, introducing new features such as Offchain Reporting, or resolving a smart contract logic error. The multisig-coordinated upgradability of Chainlink services involves time-tested processes that balance collusion-resistance with the flexibility required to implement improvements and adjust parameters. Reference link

This issue is very much possible here as the price feeds passed in constructor are immutable.

```
    IRedstonePriceFeed public immutable REDSTONE_ETHX_PRICE_FEED;
    IChainlink public immutable USD_PER_ETH_CHAINLINK;
```

There is no setter function if the address of feeds from Chainlink is changed in future and with current implementation the functions could be permanently in DOS if price feeds reverts.

### Impact

Call to latestRoundData could potentially revert and make it impossible to query any prices. This could lead to permanent denial of service.

### Recommendation to fix
Surround the call to `latestRoundData()` with try/catch instead of calling it directly. In a scenario where the call reverts, the catch block can be used to call a fallback oracle or handle the error in any other suitable way.

For example:

```
function getPrice(address priceFeedAddress) external view returns (int256) {
        try AggregatorV3Interface(priceFeedAddress).latestRoundData() returns (
            uint80,         // roundID
            int256 price,   // price
            uint256,        // startedAt
            uint256,        // timestamp
            uint80          // answeredInRound
        ) {
            return price;
        } catch Error(string memory) {            
            // handle failure here:
            // revert, call propietary fallback oracle, fetch from another 3rd-party oracle, etc.
        }
    }
```

References

Openzeppelin reference: Refer to https://blog.openzeppelin.com/secure-smart-contract-guidelines-the-dangers-of-price-oracles/ for more information regarding potential risks to account for when relying on external price feed providers.

Reference news article: https://cryptonews.net/news/defi/20502745/

## [L-03](https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/issues/39) `reserveFactor` validation check cannot revert in case of invalid value assignment

_Submitted by rokinot_

### Description

In [InterestRate.sol](https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/blob/bdfcb2aeb948d5c658f61636f8674459cd538c26/src/InterestRate.sol#L159-L162), some checks are done in order to ensure variables were assigned with valid inputs. `reserveFactor` is one of them, which is an `uint16` type. This value is then checked against `RAY` as shown in the link. The issue is, since `RAY` is equal to `1e27`, an amount much higher than what the uint16 type allows for, the revert section is unreachable regardless of inputed value.

Now that the check will always pass, the interest rate module can be updated with any reserve factor. In [IonPool.sol](https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/blob/bdfcb2aeb948d5c658f61636f8674459cd538c26/src/IonPool.sol#L514), when interest has to be accrued, it calls `_calculateRewardAndDebtDistributionForIlk()` where it runs a subtraction of `RAY - reserveFactor.scaledUpToRay(4)`. This scale up is equivalent to multiplying the reserve factor by `10**23`.

If the interest rate module is updated with a new `reserveFactor` of amount higher than 10000, `_accrueInterest()` will always revert due to underflow, and as a consequence so will `pause()`, `supply()`, `withdraw()`, `depositCollateral()`, `withdrawCollateral()`, `borrow()`, `repay()` and `confiscateVault()`, freezing all operations that can move the funds of a pool.

### Proof of Concept (PoC)

Run the test below under `IonPool.t.sol`
```
    function test_InvalidReserveFactorIsSet() external {
        uint256 collateralDepositAmount = 1e18;
        uint256 normalizedBorrowAmount = 1e18;

        uint8 i = 0; //we'll use the first index

        //simulate a borrow
        vm.prank(borrower1);
        ionPool.depositCollateral(i, borrower1, borrower1, collateralDepositAmount, new bytes32[](0));

        vm.prank(borrower1);
        ionPool.borrow(i, borrower1, borrower1, normalizedBorrowAmount, new bytes32[](0));

        ilkConfigs[i].reserveFactor = 10_001; //any value above 10_000 will cause it to revert

        InterestRate newInterestRateModule = new InterestRate(ilkConfigs, apyOracle);

        ionPool.updateInterestRateModule(newInterestRateModule);

        vm.warp(block.timestamp + 12); //since accrueInterest() was already called, it won't be updated in this block anymore.
        //So we have to let a block pass in order to update it again

        vm.expectRevert();
        ionPool.accrueInterest();
    }
```

### Recommendation to fix

In `InterestRate.sol`, instead of checking against the raw value of reverse factor, do so against the scaled up version, as shown below:

```
    if ((ilkDataList[i].reserveFactor).scaleUpToRay(4) > RAY) { 
        revert InvalidReserveFactor(ilkDataList[i].reserveFactor);
    }
```

## [L-04](https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/issues/40) `payable` modifier on function without use of native currency can lead to locked ETH

_Submitted by rokinot_

### Description
As described by the [OpenZeppelin's report](https://blog.openzeppelin.com/ion-protocol-audit#locked-eth-in-contract), `payable` functions with no use of ether can lead to locked funds. However, the report, as well as the fix commit, missed a function: `flashLeverageWethAndSwap()` at `UniswapFlashloanBalancerSwapHandler.sol`, which can be found [here](https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/blob/bdfcb2aeb948d5c658f61636f8674459cd538c26/src/flash/handlers/base/UniswapFlashloanBalancerSwapHandler.sol#L91).

The functions in the aforementioned report have the unnecessary payable modifiers, which were subsequently patched in a commit, but the main branch still includes the modifier in them as well as the competition's version of the code. I'm pointing this out as to make sure the developers are aware of this version control ambiguity.

### Recommendation to fix
Remove the modifier. Running the unit and fuzz tests will show the system still works as intended.

```
    function flashLeverageWethAndSwap(
        uint256 initialDeposit,
        uint256 resultingAdditionalCollateral,
        uint256 maxResultingAdditionalDebt,
        uint256 deadline,
        bytes32[] calldata proof
    )
        external
        checkDeadline(deadline)
        onlyWhitelistedBorrowers(proof)
    { ... }
```

## [L-05](https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/issues/46) Exchange Rate aggregation can lead to lower pricing and opens to vulnerability for the protocol and users

_Submitted by ravikiranweb3_

### Description

Describe the context and the effect of the vulnerability. ReserveOracle refers to three feeds in addtion to the protocol feed for underlying asset type. The reserveFeed is manually maintained by the owner of a contract that sets the exchange rate for each collateral type for each feeds.

The reserve Oracle also has a quorum mechanism under which the the exchange from the manual feeds is aggregated based the configured quorum. Refer to the below function for how the aggregation is being done in the aggregate function.

Refer to issueFunctions.txt.

The problem happens in the above aggregate function where aggregate value is computed as below

`val = ((feed0ExchangeRate + feed1ExchangeRate) / uint256(QUORUM));`

So, for example, ETH rate from the two feeds for quorum 2 is as below

`val = (2000 + 2002)/2 = 4002/2 = 2001`

`val = 2001`

now, let say, feed2 was not configured for ETH rate, but the quorum is still 2 in which case, the aggregate value for exchange rate will be

`val = (2000 + 0)/2 = 1000`

So, instead of 2000 range, the value drops to half in the case of quorum two and 1/3 incase the case of quorum 3 and only 1 feed has the rate configured for the collateral.

The risk here is that, feed contract stores data in a map with exchange rates as below.

`mapping(uint8 ilkIndex => uint256 exchangeRate) public exchangeRates;`

Since the map for all collaterals will default to 0, this is a silent error.

hence, the rate is default to 0 and that have huge implications in the protocol. This is a silent error that will not be noticed as it starts from inititalization of rates and will stay there. The _maxChange guard also does not offer protection.

Impact on spot exchange rate:

Even bigger problem is that, in the SpotOracle, getSpot() function will give preference to exchangeRate becoz of the Math.min function and effectively apply this rate to both reserve and spot.


Attack Scenario:

1. add three feeds to a collateral.

2. set quorum to 3

3. dont configure the collateral asset rate in two of the feeds.

### Proof of Concept (PoC):
Note how the aggregate exchange is computed without checking for exchange rate from the feed to be greater than 0.

This leads to lower exchange rate.

```
if (QUORUM == 0) {
            return type(uint256).max;
        } else if (QUORUM == 1) {
            val = FEED0.getExchangeRate(_ILK_INDEX);
        } else if (QUORUM == 2) {
            // @assuming that all feeds have exchangeRate for ild_index
            uint256 feed0ExchangeRate = FEED0.getExchangeRate(_ILK_INDEX);
            uint256 feed1ExchangeRate = FEED1.getExchangeRate(_ILK_INDEX);
            val = ((feed0ExchangeRate + feed1ExchangeRate) / uint256(QUORUM));
        } else if (QUORUM == 3) {
            uint256 feed0ExchangeRate = FEED0.getExchangeRate(_ILK_INDEX);
            uint256 feed1ExchangeRate = FEED1.getExchangeRate(_ILK_INDEX);
            uint256 feed2ExchangeRate = FEED2.getExchangeRate(_ILK_INDEX);
            val = ((feed0ExchangeRate + feed1ExchangeRate + feed2ExchangeRate) / uint256(QUORUM));
        }
```

Refer to how the min of price from external source and exchange rate from reserver is taken. In the reserve exchange as the exchange rate could be 1/2 or 1/3 if not configured, the reserve rate will be lower than external source price and hence exchange rate take precedence due to min of the two prices as in the function below.

hence this function impacts the spot exchange rates and makes it difficult to notice and could adversely impact the users and the protocol.

```
function getSpot() external view returns (uint256 spot) {
        uint256 price = getPrice(); // must be [wad]
        uint256 exchangeRate = RESERVE_ORACLE.currentExchangeRate();

        // Min the price with reserve oracle before multiplying by ltv
        uint256 min = Math.min(price, exchangeRate); // [wad]

        spot = LTV.wadMulDown(min); 
}
```
issue functions.txt

### Recommendation to fix

The solution is to check the price returned for each of the feeds in the quorum and based on the valid number of prices returned, revise the aggregation logic or revert to let the owner know and configure the exchange rate across the feeds.

The second option is illustrated as below.

```
function _aggregate(uint8 _ILK_INDEX) internal view returns (uint256 val) {
        if (QUORUM == 0) {
            return type(uint256).max;
        } else if (QUORUM == 1) {
            val = FEED0.getExchangeRate(_ILK_INDEX);
            require(val > 0,"Incorrect exchange rate");
        } else if (QUORUM == 2) {
            // @assuming that all feeds have exchangeRate for ild_index
            uint256 feed0ExchangeRate = FEED0.getExchangeRate(_ILK_INDEX);
            require(feed0ExchangeRate > 0,"Incorrect exchange rate0");
            uint256 feed1ExchangeRate = FEED1.getExchangeRate(_ILK_INDEX);
            require(feed1ExchangeRate > 0,"Incorrect exchange rate1");
            val = ((feed0ExchangeRate + feed1ExchangeRate) / uint256(QUORUM));
        } else if (QUORUM == 3) {
            uint256 feed0ExchangeRate = FEED0.getExchangeRate(_ILK_INDEX);
            require(feed0ExchangeRate > 0,"Incorrect exchange rate0");
            uint256 feed1ExchangeRate = FEED1.getExchangeRate(_ILK_INDEX);
            require(feed1ExchangeRate > 0,"Incorrect exchange rate1");
            uint256 feed2ExchangeRate = FEED2.getExchangeRate(_ILK_INDEX);
            require(feed2ExchangeRate > 0,"Incorrect exchange rate2");
            val = ((feed0ExchangeRate + feed1ExchangeRate + feed2ExchangeRate) / uint256(QUORUM));
        }
}
```

solution2.txt

Files:

Issue functions.txt (https://hats-backend-prod.herokuapp.com/v1/files/QmPurhvHSVDZ9wL9Pcgvt5F9yFtu3yecyerUcSKH2TKPAZ)
Issue2.txt (https://hats-backend-prod.herokuapp.com/v1/files/Qma8fN8sVLyTtcHWPyaS5X4kYWNiK7DnfqwXjHHF3BvSxp)
solution2.txt (https://hats-backend-prod.herokuapp.com/v1/files/QmPErRVfny3dUQan1TAeThETqNrdDJrfPAZoLr1e1k3Ds9)

# Mutations

## InterestRate

[**InterstRate_0.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/InterestRate/InterestRate_0.sol): In `calculateInterestRate`, replace `rayMulDown` with `rayDivUp`.

[**InterstRate_1.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/InterestRate/InterestRate_1.sol): Initialize `COLLATERAL_COUNT` to 1.

[**InterstRate_2.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/InterestRate/InterestRate_2.sol): In `calculateInterestRate`, replace `utilizationRate` calculation with 1.

[**InterstRate_3.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/InterestRate/InterestRate_3.sol): In `calculateInterestRate`, initialize `ilkData` as empty instead of calling `_unpackCollateralConfig`.

[**InterstRate_4.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/InterestRate/InterestRate_4.sol): In `calculateInterestRate`, when calculating `slopeNumerator`, switch `collateralApyRayInSeconds` with `ilkData.adjustedProfitMargin`.

[**InterstRate_5.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/InterestRate/InterestRate_5.sol): In `calculateInterestRate`, always return the minimum interest rate.

[**InterstRate_P.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/InterestRate/InterestRate_P.sol): In `calculateInterestRate`, return `minimumKindRate` when `distributionFactor >= 0` instead of `distributionFactor == 0`.

## IonPool

[**IonPool_0.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/IonPool/IonPool_0.sol): In `_accrueInterest`, fail to increase `ilk.rate`. 

[**IonPool_1.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/IonPool/IonPool_1.sol): In `repayBadDebt`, replace `_msgSender()` with `address(0)`.

[**IonPool_2.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/IonPool/IonPool_2.sol): In `borrow`, fail to call `_accrueInterest()`. 

[**IonPool_3.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/IonPool/IonPool_3.sol): In `depositCollateral`, fail to check that the contract is not paused.

[**IonPool_4.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/IonPool/IonPool_4.sol): In `supply`, replace `user` with `address(this)`.

[**IonPool_5.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/IonPool/IonPool_5.sol): In `confiscateVault`, switch `_add` calls with `_sub` calls.

[**IonPool_6.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/IonPool/IonPool_6.sol): In `repay`, replace `user` with `address(this)`.

[**IonPool_7.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/IonPool/IonPool_7.sol): In `onlyWhitelistedBorrowers` modifier, fail to check that `msg.sender` is a whitelisted borrower.

[**IonPool_8.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/IonPool/IonPool_8.sol): In `mintAndBurnGem`, fail to check that the caller has `GEM_JOIN_ROLE`.

[**IonPool_9.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/IonPool/IonPool_9.sol): In `_accrueInterest`, replace `totalTreasuryMintAmount` with `totalTreasuryMintAmount / ilksLength` when calculating `debt`.

[**IonPool_P.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/IonPool/IonPool_P.sol): In `_modifyPosition`, update `w`'s position instead of `v`'s.

## Liquidation

[**Liquidation_0.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/Liquidation/Liquidation_0.sol): In `_getRepayAmt`, replace `rayDivUp` with `rayMulUp` when calculating `repay`.

[**Liquidation_1.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/Liquidation/Liquidation_1.sol): In `liquidate`, revert when healthRatio is too high instead of too low.

[**Liquidation_2.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/Liquidation/Liquidation_2.sol): In `liquidate`, call `confiscateVault` with fixed `1 ether` value instead of `gemOut` and `dart`.

[**Liquidation_3.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/Liquidation/Liquidation_3.sol): In `liquidate`, replace `<` with `>`, assuming remaining debt will be dust and paying it all.

[**Liquidation_4.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/Liquidation/Liquidation_4.sol): In `liquidate`, define `gemOut` to `collateral` instead of `normalizedDebt * rate / liquidateArgs.price`.

[**Liquidation_5.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/Liquidation/Liquidation_5.sol): When calling `confiscateVault` in `liquidate`, switch `kpr` and `vault`.

[**Liquidation_6.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/Liquidation/Liquidation_6.sol): In `liquidate`, instead of transferring from `msg.sender` to `address(this)`, do the opposite.

[**Liquidation_7.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/Liquidation/Liquidation_7.sol): In `liquidate`, when calling `confiscateVault`, replace `kpr` with `address(this)`.

[**Liquidation_8.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/Liquidation/Liquidation_8.sol): In `liquidate`, when calling `confiscateVault`, fail to negate `dart`.

[**Liquidation_9.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/Liquidation/Liquidation_9.sol): In `liquidate`, revert when healthRatio is too high instead of too low.

[**Liquidation_10.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/Liquidation/Liquidation_10.sol): In `liquidate`, always repay 0 debt.

[**Liquidation_P.sol**](https://github.com/Certora/ion-protocol/blob/master/certora/mutations/Liquidation/Liquidation_P.sol): In `getRepayAmt`, replace `<=` with `>=`, effectively making `maxDiscount` the minimum discount.

# Notable Properties

## InterstRate

### If `distributionFactor` is equal to zero then `borrowRate` must be equal to `minimumKinkRate`.

*Author:* [luckypatty](https://github.com/Certora/ion-protocol/blob/master/certora-luckypatty/specs/InterestRate.spec#L40-L58)

```
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
```

---

### For all `ilk`, if `distributionFactor` is nonzero then `borrowRate` must be greater than the larger of `adjustedBaseRate` and `minimumBaseRate`.

*Author:* [luckypatty](https://github.com/Certora/ion-protocol/blob/master/certora-luckypatty/specs/InterestRate.spec#L62-L88)

```
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
```

---

### `_unpackCollateralConfig` must preserve all input validations in constructor.

*Author:* [luckypatty](https://github.com/Certora/ion-protocol/blob/master/certora-luckypatty/specs/InterestRate.spec#L106-L112)

```
invariant unPackCorrect(uint256 ilkIndex)
    InterestRateHarness.unpackCollateralConfig(ilkIndex).minimumKinkRate >= InterestRateHarness.unpackCollateralConfig(ilkIndex).minimumBaseRate
    && InterestRateHarness.unpackCollateralConfig(ilkIndex).optimalUtilizationRate != 0
    && assert_uint256(InterestRateHarness.unpackCollateralConfig(ilkIndex).reserveFactor) <= InterestRateHarness.getRAY()
    && ilkIndex <= 8;
```

## IonPool

### `totalBadDebt` must be the sum of all users' bad debt.

*Author:* [BenRai1](https://github.com/Certora/ion-protocol/blob/master/certora-BenRai1/specs/IonPool.spec#L615-L627)

```
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
```

---

### `borrow` must accrue interest when called. 

Note: This rule should be generalized to balance debt changing functions.

*Author:* [luckypatty](https://github.com/Certora/ion-protocol/blob/master/certora-luckypatty/specs/InterestRate.spec#L91-L105)

```
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
    assert numCallAfter == numCallBefore + 1;
}
```

## Liquidation

### `liquidate` must not liquidate healthy accounts. 

*Author:* [luckypatty](https://github.com/Certora/ion-protocol/blob/master/certora-luckypatty/specs/Liquidation_2.spec#L64-L89)

```
rule liquidationFailsWhenNotLiquidatable(env e, uint8 ilkIndex, address vault, address kpr) {
    uint256 exchangeRate = WEReverveOracle.currentExchangeRate();
    uint256 exchangeRateScaledUp = LiquidationHarness.scaleUpToRay(exchangeRate, 18);

    uint256 collateral;
    uint256 normalizedDebt;
    collateral, normalizedDebt = Ion.vault(e, ilkIndex, vault);

    mathint collateralValue = collateral * exchangeRate;
    uint256 collateralValueMulDown = LiquidationHarness.rayMulDown(require_uint256(collateralValue), LiquidationHarness.liquidationThreshold(ilkIndex));

    uint256 rate = Ion.rate(e, ilkIndex);

    mathint roundDownFactor = normalizedDebt * rate;
    uint256 healthRatio = LiquidationHarness.rayDivDown(collateralValueMulDown, require_uint256(roundDownFactor));

    require exchangeRateScaledUp != 0;

    liquidate@withrevert(e, ilkIndex, vault, kpr);

    assert healthRatio >= LiquidationHarness.ray() => lastReverted, "Does not revert when the vault is healthy";
}
```

# Disclaimer

The Certora Prover takes a contract and a specification as input and formally proves that the contract satisfies the specification in all scenarios. Notably, the guarantees of the Certora Prover are scoped to the provided specification and the Certora Prover does not check any cases not covered by the specification. 

Certora does not provide a warranty of any kind, explicit or implied. The contents of this report should not be construed as a complete guarantee that the contract is secure in all dimensions. In no event shall Certora or any of its employees or community participants be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the results reported here. All smart contract software should be used at the sole risk and responsibility of users.

