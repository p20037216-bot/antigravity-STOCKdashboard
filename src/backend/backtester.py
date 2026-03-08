import backtrader as bt
import pandas as pd
from datetime import datetime

class MovingAverageRsiStrategy(bt.Strategy):
    """
    Backtesting strategy based on SMA Golden Cross and RSI.
    Buy Signal: SMA(50) > SMA(200) AND RSI(14) < 70 (not overbought).
    Sell Signal: SMA(50) < SMA(200) OR RSI(14) > 70 (overbought exit).
    """
    params = (
        ('sma_fast', 50),
        ('sma_slow', 200),
        ('rsi_period', 14),
        ('rsi_overbought', 70),
        ('rsi_oversold', 30),
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        # print('%s, %s' % (dt.isoformat(), txt))
        pass

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        
        # Add Technical Indicators
        self.sma_fast = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.sma_fast)
        self.sma_slow = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.sma_slow)
        
        # Crossover indicator (1 if fast > slow, -1 if fast < slow, 0 otherwise)
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)
        
        self.rsi = bt.indicators.RSI(self.datas[0], period=self.params.rsi_period)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status in [order.Completed]:
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            
        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # We are not in the market, look for a buy signal
            if self.crossover > 0 and self.rsi < self.params.rsi_overbought:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
        else:
            # We are already in the market, look for a sell signal
            if self.crossover < 0 or self.rsi > self.params.rsi_overbought:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()


def run_backtest(df: pd.DataFrame, initial_cash: float = 10000.0) -> dict:
    """
    Run backtesting strategy on historical dataframe.
    Returns standard performance metrics like win rate and total return.
    """
    if df.empty:
        return {"error": "Empty dataframe provided"}
        
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MovingAverageRsiStrategy)
    
    # Prepare data feed
    data = bt.feeds.PandasData(
        dataname=df,
        open='open',
        high='high',
        low='low',
        close='close',
        volume='volume',
        openinterest=None
    )
    
    cerebro.adddata(data)
    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=0.001) # 0.1% commission
    
    # Add analyzers for metrics
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="tradeAnalyzer")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returnsAnalyzer")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawDownAnalyzer")
    
    try:
        results = cerebro.run()
        strat = results[0]
        
        # Extract Analytics
        final_value = cerebro.broker.getvalue()
        total_return = ((final_value - initial_cash) / initial_cash) * 100
        
        trade_analysis = strat.analyzers.tradeAnalyzer.get_analysis()
        trades_total = trade_analysis.total.closed if "total" in trade_analysis and "closed" in trade_analysis.total else 0
        trades_won = trade_analysis.won.total if "won" in trade_analysis and "total" in trade_analysis.won else 0
        
        win_rate = (trades_won / trades_total * 100) if trades_total > 0 else 0
        dd_analysis = strat.analyzers.drawDownAnalyzer.get_analysis()
        mdd = dd_analysis.max.drawdown if "max" in dd_analysis else 0
        
        return {
            "initial_cash": initial_cash,
            "final_value": final_value,
            "total_return_pct": total_return,
            "win_rate_pct": win_rate,
            "total_trades": trades_total,
            "max_drawdown_pct": mdd
        }
    except Exception as e:
        return {"error": f"Backtesting failed: {str(e)}"}
