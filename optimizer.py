from collections import defaultdict

class Bond:
    def __init__(self, isin, ticker, maturity_bucket, rating_score, yield_level):
       self.isin = isin 
       self.ticker = ticker 
       self.maturity_bucket = maturity_bucket 
       self.rating_score = rating_score 
       self.yield_level = yield_level 

class Position:
    def __init__(self, size: float, bond: Bond):
        self.size = size
        self.bond = bond
        
    def market_value(self):
        return self.size * self.bond.price_level
        
    def __str__(self):
        return f"<{self.bond.ticker} | {self.size}mm>"
    
    def __repr__(self):
        return self.__str__()

class Portfolio:
    def __init__(self, position_list, ticker_cap, bond_cap, tenor_limits, minimum_rating):
        self.position_list = position_list
        self.ticker_cap = ticker_cap
        self.bond_cap = bond_cap
        self.tenor_limits = tenor_limits
        self.minimum_rating = minimum_rating
    
    def calculate_average_yield(self):
        yield_sum = 0.0
        notional = 0.0
        for position in self.position_list:
            yield_sum += (position.size * position.bond.yield_level)
            notional += position.size
        return yield_sum / notional
    
    def tenor_buckets(self):
        buckets = defaultdict(float)
        for position in self.position_list:
            buckets[position.bond.maturity_bucket] += position.size
        return buckets
    
    def ticker_buckets(self):
        buckets = defaultdict(float)
        for position in self.position_list:
            buckets[position.bond.ticker] += position.size
        return buckets
    
    def positions_by_tenor(self):
        buckets = defaultdict(list)
        for position in self.position_list:
            buckets[position.bond.maturity_bucket].append(position)
        return buckets
    
    def market_value(self):
        mv = 0.0
        for position in self.position_list:
            mv += position.market_value()
        return mv / 100
    
    def average_rating(self):
        rating_score_sum = 0.0
        notional = 0.0
        for position in self.position_list:
            rating_score_sum += (position.size * position.bond.rating_score)
            notional += position.size
        return rating_score_sum / notional
    
    def average_rating_by_tenor(self):
        positions_by_tenor = self.positions_by_tenor()
        buckets = defaultdict(float)
        for tenor in positions_by_tenor:
            rating_score_sum = 0.0
            notional = 0.0
            for position in positions_by_tenor[tenor]:
                rating_score_sum += (position.size * position.bond.rating_score)
                notional += position.size
            buckets[tenor] = rating_score_sum / notional
        return buckets
    
    def get_violations(self):
        violations = []
        ticker_buckets = self.ticker_buckets()
        for ticker in ticker_buckets:
            if ticker not in self.ticker_cap:
                violations.append(f"No ticker cap for ticker: {ticker}")
            elif ticker_buckets[ticker] > self.ticker_cap[ticker]:
                violations.append(f"Ticker exceeds limit: {ticker}")
        for position in self.position_list:
            if position.size > self.bond_cap[position.bond.ticker]:
                violations.append(f"Position size exceeds limit: {position.bond.ticker}")
        
        tenor_buckets = self.tenor_buckets()
        for tenor in tenor_buckets:
            if tenor not in self.tenor_limits:
                violations.append(f"Tenor not in tenor_limits: {tenor}")
            if tenor_buckets[tenor] > self.tenor_limits[tenor]:
                violations.append(f"Tenor size exceeds limit: {tenor}")
        
        average_rating = self.average_rating()
        if self.average_rating() > self.minimum_rating:
            violations.append(f"Average rating is {average_rating}, below min rating {self.minimum_rating}")
        return violations