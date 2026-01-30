import pandas as pd
import altair as alt

# for readable
DATA_FILE = "hw1/data/global-temperature-anomalies-by-month.csv"
CODE = 'Code'
YEAR = 'Year'
TA = 'Temperature anomaly'  #[T]emperature [A]nomaly
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
    _20_cent_std = (df_clean[(df_clean[YEAR] >= 1900) &
                             (df_clean[YEAR] <= 1999)])[TA].std()
    print(f"avg = {_20_cent_avg}, std = {_20_cent_std}")

    # print(df_clean.info)

    # delta = {TA - avg }, make it ezier to encode into color
    # TODO: use normalization ?
    df_clean["delta_n"] = (df_clean[TA] - _20_cent_avg) # / _20_cent_std

    # draw a line to connect all points
    # the line itself won't reflect the diff between TA and avg
    line = alt.Chart(df_clean).mark_line(color='gray', opacity=0.5).encode(
        x=f'{DATE}:T',
        y=f'{TA}:Q'
    )

    #Instead, let the point do that...
    points = alt.Chart(df_clean).mark_point(filled=True).encode(
        x=f'{DATE}:T',
        y=f'{TA}:Q',
        color=alt.Color("delta_n:Q", scale=alt.Scale(scheme="redblue", reverse=True),
                        legend=alt.Legend(title=f"vs 20c avg (~{round(_20_cent_avg, 2)}°C)"),)
    )

    chart = line + points

    #because of the nature of alt, i have to export as chart.html; afterwards,
    # I will use browser to download it as pdf or png.
    chart.save("hw1/report/chart.html")

    # print(columns)
    # print(df['Entity'])