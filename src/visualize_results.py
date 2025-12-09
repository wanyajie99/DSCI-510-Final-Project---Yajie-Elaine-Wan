import matplotlib.pyplot as plt
import seaborn as sns

# execute run_analysis.py once and import df, quarterly_avg, route_stats, carrier_stats into this file
from run_analysis import df, quarterly_avg, route_stats, carrier_stats
 
# concatenate more intuitive x-axis labels (e.g., "2023 Q1")
quarterly_avg["year_quarter"] = (quarterly_avg["YEAR"].astype(str) + " Q" + quarterly_avg["QUARTER"].astype(str))
quarterly_avg = quarterly_avg.sort_values(["YEAR", "QUARTER"])

# sort routes and carriers by average fare
route_stats_sorted = route_stats.sort_values("avg_fare")
routes_ordered = route_stats_sorted["route"].tolist()
carrier_stats_sorted = carrier_stats.sort_values("avg_fare")
carriers_ordered = carrier_stats_sorted["CARRIER"].tolist()


### --------- [Question 1] visualizations --------- ###
plt.figure(figsize=(10,7))
sns.lineplot(
    data=quarterly_avg,
    x="year_quarter",
    y="avg_fare",
    hue="route",
    marker="."
    )
plt.title("Quarterly Average Ticket Fare by Route")
plt.xlabel("Quarter")
plt.ylabel("Average Market Fare (USD)")
plt.xticks(rotation=45)
plt.legend(title="Route", bbox_to_anchor=(1,1)) # display the legend to show the names of top 10 routes
plt.grid()
plt.show()

### --------- [Question 2] visualizations --------- ###

# 2a. Route-level visualizations

# Bar plot: average fare per route
plt.figure(figsize=(10,7))
sns.barplot(
    data=route_stats_sorted,
    x="route",
    y="avg_fare",
    palette="Oranges_d"
    )
plt.title("Average Ticket Fare by Route")
plt.xlabel("Route (ORIGIN–DEST)")
plt.ylabel("Average Market Fare (USD)")
plt.xticks(rotation=45)
plt.show()

# Boxplot: fare distribution per route
plt.figure(figsize=(10,7))
sns.boxplot(
    data=df,
    x="route",
    y="MARKET_FARE",
    order=routes_ordered
    )
plt.title("Ticket Fare Distribution by Route")
plt.xlabel("Route (ORIGIN–DEST)")
plt.ylabel("Market Fare (USD)")
plt.xticks(rotation=45)
plt.show()

# 2b. Carrier-level visualizations

# Bar plot: average fare per carrier
plt.figure(figsize=(10,7))
sns.barplot(
    data=carrier_stats_sorted,
    x="CARRIER",
    y="avg_fare",
    order=carriers_ordered,
    palette="tab10"
    )
plt.title("Average Ticket Fare by Carrier Code")
plt.xlabel("Carrier Code")
plt.ylabel("Average Market Fare (USD)")
plt.show()

# Boxplot: fare distribution per carrier
plt.figure(figsize=(10,7))
sns.boxplot(
    data=df[df["CARRIER"].isin(carriers_ordered)],
    x="CARRIER",
    y="MARKET_FARE",
    order=carriers_ordered
    )
plt.title("Ticket Fare Distribution by Carrier")
plt.xlabel("Carrier Code")
plt.ylabel("Market Fare (USD)")
plt.show()