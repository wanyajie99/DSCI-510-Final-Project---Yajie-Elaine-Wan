import pandas as pd
import statsmodels.api as sm

df = pd.read_csv("../data/processed/cleaned_data.csv") # load cleaned data
df = df[df["MARKET_FARE"] > 0] # only keep rows with non-zero ticket fare
selected_carriers = ["F9", "NK", "WN", "HA", "AS", "B6", "DL", "AA", "UA"] # select well-known carriers
df = df[df["CARRIER"].isin(selected_carriers)] # only keep rows of selected carriers
df["route"] = df["ORIGIN"] + "-" + df["DEST"] # create a new column of route identifier "ORIGIN-DEST"

# create a numeric time index column for regression
min_year = df["YEAR"].min()
df["quarter_index"] = (df["YEAR"] - min_year) * 4 + (df["QUARTER"] - 1) # year diff * 4(num of quarters per year) + quarter diff

### --------- [Question 1]: Long-term fare trends over time (by route) --------- ###

## 1. Quarterly average fare for each route
quarterly_avg = (df.groupby(["route", "YEAR", "QUARTER"], as_index=False)["MARKET_FARE"].mean()
                 .rename(columns={"MARKET_FARE": "avg_fare"})
                 )

print("--------- Quarterly Average Fare by Route ---------")
print(quarterly_avg)

## 2. Fit a linear regression model for overall long-term fare trend across all routes
##    model: MARKET_FARE = β0 + β1 * quarter_index + ε
X = sm.add_constant(df["quarter_index"])
y = df["MARKET_FARE"]
lin_model = sm.OLS(y, X).fit()

print("\n\n--------- Overall Long-Term Fare Trend across All Routes ---------")
print(lin_model.summary())


### --------- [Question 2]: Which routes and carriers are more expensive? --------- ###

## 1. Route-level statistics
route_stats = (
    df.groupby("route")["MARKET_FARE"].agg(
    avg_fare="mean",
    median_fare="median",
    min_fare="min",
    max_fare="max",
    std_fare="std",
    num_observ="count",
    ).reset_index()
    )

# calculate percentage fare difference between all top 10 routes and the cheapest route (by avg_fare)
min_route_avg = route_stats["avg_fare"].min() # find the route with minimum average ticket fare
route_stats["pct_difference_route"] = (
    ((route_stats["avg_fare"] - min_route_avg) / min_route_avg) * 100
    )

print("\n\n--------- Route-Level Ticket Fare Summary ---------")
print(route_stats.sort_values("avg_fare"))


## 2. Carrier-level statistics (across all top 10 routes)
carrier_stats = (
    df.groupby("CARRIER")["MARKET_FARE"].agg(
    avg_fare="mean",
    median_fare="median",
    min_fare="min",
    max_fare="max",
    std_fare="std",
    num_observ="count",
    ).reset_index()
    )

# calculate percentage fare difference between all carriers and the cheapest carrier (by avg_fare)
min_carrier_avg = carrier_stats["avg_fare"].min() # find the carrier with minimum average ticket fare
carrier_stats["pct_difference_carrier"] = (
    ((carrier_stats["avg_fare"] - min_carrier_avg) / min_carrier_avg) * 100
    )

print("\n\n--------- Carrier-Level Ticket Fare Summary ---------")
print(carrier_stats.sort_values("avg_fare"))

## 3. Route-Carrier-level statistics
route_carrier_stats = (
    df.groupby(["route", "CARRIER"])["MARKET_FARE"].agg(
        avg_fare="mean",
        median_fare="median",
        min_fare="min",
        max_fare="max",
        std_fare="std",
        num_observ="count"
        ).reset_index()
        )

# identify the carrier with highest average fare per route
most_expensive_carrier_per_route = (
    route_carrier_stats.sort_values(["route", "avg_fare"], ascending=[True, False]).groupby("route").head(1)
    )
# create a label column to specify that it's showing the carrier with most expensive price for this route
most_expensive_carrier_per_route["price_rank"] = "most_expensive"

# identify the carrier with lowest average fare per route
cheapest_carrier_per_route = (
    route_carrier_stats.sort_values(["route", "avg_fare"], ascending=True).groupby("route").head(1)
    )
# create a label column to specify that it's showing the carrier with cheapest price for this route
cheapest_carrier_per_route["price_rank"] = "cheapest"

# concatenate the two dataframes into one
route_price_long = pd.concat(
    [cheapest_carrier_per_route, most_expensive_carrier_per_route], ignore_index=True
    ).sort_values("route") # sort by route names so that the info for each route are shown together

route_price_long = route_price_long[["route", "CARRIER", "avg_fare", "price_rank"]]

print("\n\n--------- Route-Carrier-Level Ticket Fare Summary ---------")
print(route_price_long)