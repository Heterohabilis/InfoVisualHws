import pandas as pd
import altair as alt

# for readable
DATA_FILE = "hw1/data/global-temperature-anomalies-by-month.csv"
CODE = 'Code'
YEAR = 'Year'
TA = 'Temperature anomaly'
ENTITY = 'Entity'
DATE = 'Date'


# calc upper bound and lower bound, to eliminate outliers
def upper_lower_bound_handler(df):
    QT1 = df[TA].quantile(.25)
    QT3 = df[TA].quantile(.75)
    IQR = QT3 - QT1

    upper = QT3 + 1.5 * IQR
    lower = QT1 - 1.5 * IQR
    return upper, lower


if __name__ == "__main__":
    df = pd.read_csv(DATA_FILE)
    columns = df.columns.tolist()

    # concact year & entity, and -> datetime objects
    df[DATE] = pd.to_datetime(df[ENTITY] + ', ' + df[YEAR].astype(str),
                    format='%B, %Y')

    # set the newly added row as the index of the df.
    df = df.set_index(DATE).sort_index()

    # findout qt1 and qt3
    upper, lower = upper_lower_bound_handler(df)

    # We remove outliers BY ROW, thus we need to recover the removed rows
    df_clean = df[(df[TA] >= lower) &
                  (df[TA] <= upper)]

    print(f'removed {len(df) - len(df_clean)} rows')

    # Add the removed row back
    # we reassign a value to these removed outlier
    # rows along with the originally NaN rows
    date_range = pd.date_range(start=df.index.min(),
                                    end=df.index.max(), freq='MS')

    df_clean = df_clean.reindex(date_range)

    assert len(df_clean) == len(df)

    df_clean[TA] = df_clean[TA].interpolate(method = 'linear')

    # to plot it conveniently, reset the index to a normal column as 'Date'
    df_clean = df_clean.reset_index().rename(columns={'index': 'Date'})

    # calculate 20th century avg:
    _20_cent_avg = (df_clean[(df_clean[YEAR] >= 1900) &
                             (df_clean[YEAR] <= 1999)])[TA].mean()
    print(_20_cent_avg)

    # print(df_clean.info)

    # delta = {TA - avg}
    df_clean["delta"] = df_clean["Temperature anomaly"] - _20_cent_avg


    # plot it
    # To achieve the color changing on the LINE, I choose to render the line by segments
    # each segment has its own color
    segments = (
        alt.Chart(df_clean[[DATE, TA, "delta"]])
        .transform_window(
            sort=[{"field": DATE, "order": "ascending"}],   #early->late
            next_date=f"lead({DATE})",
            next_ta=f"lead({TA})",
            next_delta="lead(delta)",
        )
        .transform_calculate(seg_delta="(datum.delta + datum.next_delta) / 2")
        .mark_rule(strokeWidth=2)
        .encode(
            x=alt.X(f"{DATE}:T", title="Year"),
            x2="next_date:T",
            y=alt.Y(f"{TA}:Q", title="Temperature Anomaly"),
            y2="next_ta:Q",
            color=alt.Color(
                "seg_delta:Q",
                #higher->more red, lower ->more blue
                scale=alt.Scale(scheme="redblue", reverse=True),
                legend=alt.Legend(title=f"vs 20c avg ({_20_cent_avg:.2f} °C)"),
            ),
        )
        .properties(title="Temperature Anomalies", width=600, height=400)
    )


    # this is the 20century avg line
    rule = alt.Chart(pd.DataFrame({'y': [_20_cent_avg]})).mark_rule(
        color='black', strokeDash=[5, 5],
    ).encode(y='y:Q')

    #combine the components
    (segments + rule).save('hw1/report/chart.html')

    # print(columns)
    # print(df['Entity'])