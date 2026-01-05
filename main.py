import bets
import trading
import time
import datetime

def run_trading_cycle():
    try:
        print(f"\n{'='*50}")
        print(f"Checking at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        
        # Get current market data
        nba_markets = bets.get_nba_markets()
        print(f"Found {len(nba_markets)} NBA markets today")
        
        # Get current positions
        open_positions = trading.get_open_positions()
        print(f"Current open positions: {len(open_positions)}")
        if open_positions:
            print(f"  Positions: {list(open_positions)}")
        
        # Check for buy opportunities
        bet_tickers = bets.get_valid_bet_tickers(nba_markets)
        
        new_buy_tickers = [t for t in bet_tickers if t not in open_positions]
        skipped_tickers = [t for t in bet_tickers if t in open_positions]
        
        if skipped_tickers:
            print(f"\nSkipping {len(skipped_tickers)} tickers (already owned):")
            for ticker in skipped_tickers:
                print(f"  - {ticker}")
        
        if new_buy_tickers:
            print(f"\nNew buy opportunities: {len(new_buy_tickers)}")
            for ticker in new_buy_tickers:
                print(f"  - {ticker}")
            buys = trading.place_bet(new_buy_tickers, open_positions)
            print(f"Buys executed: {buys}")
        else:
            if not skipped_tickers:
                print("\nNo buy opportunities found")
        
        # Check for sell opportunities
        # Don't need this section if odds flip and other teams Yes contract is purchased
        # sell_tickers = bets.get_valid_sell_tickers(nba_markets, open_positions)
        # if sell_tickers:
        #     print(f"\nSell opportunities: {len(sell_tickers)}")
        #     for ticker in sell_tickers:
        #         # Find the current price for this ticker
        #         price = next((g['yes_ask'] for g in nba_markets if g['ticker'] == ticker), None)
        #         print(f"  - {ticker} (current price: {price})")
        #     sells = trading.place_sells(sell_tickers)
        #     print(f"Sells executed: {sells}")
        # else:
        #     print("\nNo sell opportunities found")
            
    except Exception as e:
        print(f"Error in trading cycle: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("Starting trading bot...")
    print("Press Ctrl+C to stop")
    
    cycle_count = 0
    
    try:
        while True:
            cycle_count += 1
            print(f"\n--- Cycle {cycle_count} ---")
            
            run_trading_cycle()
            
            print(f"\nWaiting 30 seconds until next check...")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        print(f"Total cycles completed: {cycle_count}")
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()