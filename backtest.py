"""
NBA Compounding Strategy Backtest
Strategy: Buy favorites at 70-85 cents (Optimized Range)
- Win: Take Profit at 99 cents (Optimized)
- Lose: Stop-loss at 40 cents (Optimized)
- Sizing: Dynamic 15% of bankroll per trade
"""

import random
import statistics

# Strategy parameters (Optimized)
ENTRY_MIN = 70
ENTRY_MAX = 85
STOP_LOSS_EXIT = 40
TAKE_PROFIT_EXIT = 99

# Historical NBA win rates by implied probability range
NBA_WIN_RATES = {
    (70, 74): 0.70,
    (75, 79): 0.73,
    (80, 84): 0.79,
    (85, 89): 0.84,
}

def get_actual_win_rate(entry_price):
    for (min_p, max_p), win_rate in NBA_WIN_RATES.items():
        if min_p <= entry_price <= max_p:
            return win_rate
    return entry_price / 100

# Simulation Parameters
FEE_PER_CONTRACT = 0.02  # $0.02 fee per contract (typical exchange fee)
SLIPPAGE_PCT = 0.01      # 1% slippage on large orders

def calculate_fees(contracts, price_cents):
    """Estimate exchange fees."""
    # Simplified: Kalshi fees approx 2 cents/contract or variable
    # We'll use a conservative 2 cents per contract flat fee
    total_fee = contracts * FEE_PER_CONTRACT
    return total_fee

def calculate_slippage(contracts):
    """Estimate price slippage for larger orders."""
    # If ordering > 1000 contracts, price gets worse
    if contracts > 1000:
        return 1.0  # 1 cent/contract worse price
    elif contracts > 500:
        return 0.5
    return 0.0

def run_compounding_simulation(start_balance=500, pct_risk=0.15, num_trades=100):
    balance = start_balance
    history = [balance]
    
    # Track stats
    wins = 0
    losses = 0
    total_fees = 0
    
    for _ in range(num_trades):
        entry_price = random.uniform(ENTRY_MIN, ENTRY_MAX)
        win_rate = get_actual_win_rate(entry_price)
        won = random.random() < win_rate
        
        # Calculate Position Size (Dynamic 15%)
        risk_capital = balance * pct_risk
        
        # Apply slippage to entry price
        contracts = int((risk_capital * 100) / entry_price)
        slip = calculate_slippage(contracts)
        real_entry_price = entry_price + slip
        
        if contracts < 1: contracts = 1
        
        cost = contracts * (real_entry_price / 100)
        entry_fees = calculate_fees(contracts, real_entry_price)
        
        if won:
            # Settle at TP (99c) - potential exit fees
            revenue = contracts * (TAKE_PROFIT_EXIT / 100)
            exit_fees = calculate_fees(contracts, TAKE_PROFIT_EXIT)
            wins += 1
        else:
            # Stop loss at 40c - realistic fill might be worse (35c?)
            # Let's assume worse fill (38c) + slippage
            exit_price = STOP_LOSS_EXIT - slip - 2 
            revenue = contracts * (exit_price / 100)
            exit_fees = calculate_fees(contracts, exit_price)
            losses += 1
            
        profit = revenue - cost - entry_fees - exit_fees
        total_fees += (entry_fees + exit_fees)
        
        balance += profit
        
        # Bank-roll protection (can't go below 0)
        if balance < 0: balance = 0
        
        history.append(balance)
        
    return balance, history, wins, losses

def run_monte_carlo(sims=1000, trades=150):
    """Run multiple simulations to see range of outcomes."""
    final_balances = []
    
    print(f"\nRunning {sims} simulations of {trades} trades each...")
    print(f"Start: $500| Risk: 15% per trade | Strategy: Entry {ENTRY_MIN}-{ENTRY_MAX}c, TP {TAKE_PROFIT_EXIT}, SL {STOP_LOSS_EXIT}")
    
    for _ in range(sims):
        end_bal, _, _, _ = run_compounding_simulation(num_trades=trades)
        final_balances.append(end_bal)
    
    # Analysis
    median_bal = statistics.median(final_balances)
    avg_bal = statistics.mean(final_balances)
    min_bal = min(final_balances)
    max_bal = max(final_balances)
    
    # Sort to find percentiles
    sorted_bal = sorted(final_balances)
    p10 = sorted_bal[int(sims * 0.1)]
    p90 = sorted_bal[int(sims * 0.9)]
    
    print("\n" + "="*50)
    print("COMPOUNDING RESULTS (After ~1 Year / 150 trades)")
    print("="*50)
    print(f"Median Balance:    ${median_bal:,.2f}")
    print(f"Average Balance:   ${avg_bal:,.2f} (skewed by big winners)")
    print(f"Worst Case:        ${min_bal:,.2f}")
    print(f"Best Case:         ${max_bal:,.2f}")
    print(f"\nLikely Range (10th-90th percentile):")
    print(f"${p10:,.2f}  <--->  ${p90:,.2f}")
    print("="*50)

if __name__ == "__main__":
    run_monte_carlo(trades=150) # Approx 1 NBA season of betting
