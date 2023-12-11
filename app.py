import streamlit as st
import requests

# Function to fetch pools from the API
def fetch_pools():
    url = "https://api.prismafinance.com/api/v1/pools"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['data']['pools']
    else:
        st.error("Failed to fetch pools from the API")
        return {}

# Process pools to get a list of "type: name"
def process_pools(pools_data):
    return [f"{pool_info['poolName']}" for pool_id, pool_info in pools_data.items()]

# Function to calculate boost (Placeholder for actual logic)
def calculate_boost(deposits, tokens_locked, lock_in_period):
    # Implement the actual boost calculation logic here
    # This is just a placeholder calculation
    boost = sum(deposits.values()) * tokens_locked * lock_in_period
    return boost

def total_lockweight():
    url = "https://api.prismafinance.com/api/v1/systemState"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['data']['totalLockWeight']
    else:
        st.error("Failed to fetch pools from the API")
        return {}
    
def current_week():
    url= "https://api.prismafinance.com/api/v1/systemState"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['data']['week']
    else:
        st.error("Failed to fetch pools from the API")
        return {}
    
def current_week_emissions():
    week = current_week()
    url=f'https://api.prismafinance.com/api/v1/emissionVotes?week={week}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['data']['weeklyEmissions']
    else:
        st.error("Failed to fetch pools from the API")
        return {}

def tvl_usd(poolname):
    for values in pools_data.values():
        if(values["poolName"] == poolname):
            return values["tvlUSD"]


def fetch_emissions():
    week = current_week()
    url=f'https://api.prismafinance.com/api/v1/emissionVotes?week={week}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['data']['receiverToWeights']
    else:
        st.error("Failed to fetch pools from the API")
        return {}

def pool_emissions(poolname):
    for values in emission_data.values():
        if(values["name"] == poolname):
            return values["totalEmissions"]



def calculate_prisma_pool(poolname,inputusd):
    tvl = tvl_usd(poolname)
    prisma_emission = pool_emissions(poolname)
    return prisma_emission * inputusd / tvl

def calculate_total_prisma():
    totalprisma = 0
    for key in deposits.keys():
        totalprisma = totalprisma + calculate_prisma_pool(key,deposits[key])
    return totalprisma

def adjusted_boosted_amount(amount):
    prevAmount = 0
    weeklyEmissions = current_week_emissions()
    pct = 100 * prisma_tokens_locked * lock_in_period / total_lockweight()
    total = amount + prevAmount
    maxBoostable = weeklyEmissions * pct / 100
    fullDecay = maxBoostable * 2
    adjustedAmount = 0
    if (maxBoostable >= total):
        return amount
    if (fullDecay <= prevAmount):
        return amount / 2
    if(prevAmount < maxBoostable):
        adjustedAmount = maxBoostable - prevAmount
        amount -= adjustedAmount
        prevAmount = maxBoostable
    if(total > fullDecay):
        adjustedAmount += (total - fullDecay) / 2
        amount -= (total - fullDecay)
    if(amount == maxBoostable):
        return adjustedAmount + ((maxBoostable * 3) / 4)
    finalBoosted = amount - (amount * (prevAmount + amount - maxBoostable)) / maxBoostable / 2
    adjustedAmount += finalBoosted
    initialBoosted = amount - (amount * (prevAmount - maxBoostable)) / maxBoostable / 2
    adjustedAmount += (initialBoosted - finalBoosted) / 2
    return adjustedAmount
        



# Fetch and process pool data
pools_data = fetch_pools()
all_pools = process_pools(pools_data)
emission_data = fetch_emissions()

# Streamlit app
st.title('Prisma Finance Boost Calculator')

# Multi-select widget for pools
selected_pools = st.multiselect('Select the pools you have deposits in', all_pools)

# Dictionary to hold deposit inputs
deposits = {}

# Create input fields for each selected pool
for pool in selected_pools:
    deposit = st.number_input(f'Enter deposits for {pool} (In USD)', min_value=0.0, format='%f')
    deposits[pool] = deposit

# Input for Prisma tokens locked
prisma_tokens_locked = st.number_input('Prisma Tokens To Lock', min_value=0.0, format='%f')

# Slider for selecting lock-in period
lock_in_period = st.slider('Select Lock-in Period (weeks)', 1, 52, 1)

# Calculate boost
if st.button('Calculate Boost'):
    boost = calculate_boost(deposits, prisma_tokens_locked, lock_in_period)
    total_lock_weight = total_lockweight()
    lock_weight = prisma_tokens_locked * lock_in_period
    week = current_week()
    current_emissions = current_week_emissions()
    totalprisma = calculate_total_prisma()
    adjustedPrisma = adjusted_boosted_amount(totalprisma)
    st.write(f'Your Lock Weight  is: {lock_weight}')
    st.write(f'Total Lock Weight  is: {total_lock_weight}')
    st.write(f'Your Share is: {100 * lock_weight / total_lock_weight} %')
    st.write(f'Current Week : {week}')
    st.write(f'Current Weeks Emission : {current_emissions} PRISMA')
    st.write(f'Boosted Rewards :  {adjustedPrisma} PRISMA')
    st.write(f'Unboosted Rewards (If you wont lock any prisma token): {totalprisma / 2} PRISMA')
    st.write(f'On {week + 1}th week You will likely to receive {adjustedPrisma / (totalprisma / 2)} X times more rewards (compared to unboosted rewards) if you lock {prisma_tokens_locked} prisma tokens for {lock_in_period} weeks ')
    


