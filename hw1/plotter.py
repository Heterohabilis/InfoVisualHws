import pandas as pd
from matplotlib import pyplot as plt

# for readable code
DATA_FILE = "hw1/data/global-temperature-anomalies-by-month.csv"
CODE = 'Code'
YEAR = 'Year'
TA = 'Temperature anomaly'
ENTITY = 'Entity'
DATE = 'Date'


if __name__ == "__main__":
    df = pd.read_csv(DATA_FILE)
    columns = df.columns.tolist()

    # concact year & entity, and -> datetime objects
    df[DATE] = pd.to_datetime(df[ENTITY] + ', ' + df[YEAR].astype(str),
                    format='%B, %Y')

    # set the newly added row as the index of the df.
    df = df.set_index(DATE).sort_index()

    # findout qt1 and qt3
    QT1 = df[TA].quantile(0.25)
    QT3 = df[TA].quantile(0.75)
    IQR = QT3 - QT1

    upper = QT3 + 1.5 * IQR
    lower = QT1 - 1.5 * IQR

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

    df_clean = df_clean.sort_index()

    # calculate 20th century avg:
    _20_cent_avg = (df_clean[(df_clean[YEAR] >= 1900) &
                             (df_clean[YEAR] <= 1999)])[TA].mean()
    print(_20_cent_avg)

    # print(df_clean.info)

    plt.figure()
    plt.plot(df_clean.index, df_clean[TA],
             color='gray', linewidth=0.5, alpha=0.5)

    # red: > than avg
    plt.fill_between(df_clean.index, df_clean[TA], _20_cent_avg,
                     where=(df_clean[TA] >= _20_cent_avg),
                     color='red', interpolate=True, label='Above Average', alpha = .5)

    # blue: < than avg
    plt.fill_between(df_clean.index, df_clean[TA], _20_cent_avg,
                     where=(df_clean[TA] <= _20_cent_avg),
                     color='blue',interpolate=True, label='Below Average', alpha = .5)

    plt.axhline(y=_20_cent_avg, color='black', linestyle='--', linewidth=1, label='20th Century Avg')
    plt.title('Global Temperature Anomalies')
    plt.ylabel('Temperature Anomaly')
    plt.xlabel('Year')
    plt.legend()

    plt.show()

    # print(columns)
    # print(df['Entity'])