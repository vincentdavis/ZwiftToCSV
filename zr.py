from time import sleep

import pandas as pd
from httpx import Client

CATS = ["Diamond", "Ruby", "Emerald", "Sapphire", "Amethyst", "Platinum", "Gold", "Silver", "Bronze", "Copper"]
SORTBY = [
    "points",
    "rating",
    "finishes",
    "wins",
    "podiums",
    "dnfs",
    "wkg5",
    "wkg15",
    "wkg30",
    "wkg60",
    "wkg120",
    "wkg300",
    "wkg1200",
]


def get_elo(
    all_pages: bool = False,
    cat: str = "Diamond",
    pagesize: int = 500,
    sortby: str = "points",
    sortdirection: str = "desc",
    page: int = 0,
    gender: str = "",
) -> dict:
    """
    Get the ZRL ELO data.
    """
    # https://www.zwiftracing.app/api/riders?gender=M&page=0&pageSize=50&sortBy=points&sortDirection=asc&cat=Copper
    # https://www.zwiftracing.app/api/riders?page=0&pageSize=50&sortBy=points&sortDirection=desc&cat=Diamond
    if gender:
        url = f"https://www.zwiftracing.app/api/riders?gender={gender}page={page}&pageSize={pagesize}&sortBy={sortby}&sortDirection={sortdirection}&cat={cat}"
    else:
        url = f"https://www.zwiftracing.app/api/riders?page={page}&pageSize={pagesize}&sortBy={sortby}&sortDirection={sortdirection}&cat={cat}"
    client = Client(follow_redirects=True)
    response = client.get("https://www.zwiftracing.app")
    if all_pages:
        # {"riders": [], "totalResults": 12345}
        page = 0
        has_data = True
        data = []
        pagesize = 500
        while has_data:
            url = f"https://www.zwiftracing.app/api/riders?page={page}&pageSize={pagesize}&sortBy={sortby}&sortDirection={sortdirection}&cat={cat}"
            response = client.get(url)
            if len(response.json()["riders"]) > 0:
                data += response.json()["riders"]
                page += 1
            else:
                has_data = False
            sleep(1)
    else:
        data = client.get(url).json()["riders"]
    return data


def expand_elo_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expand the elo data into a dataframe.
    """
    for col in df.columns:
        if isinstance(df[col][0], list):
            # print(f"Column name: {col}")
            df_temp = pd.DataFrame(df[col].tolist(), index=df.index)
            df[[f"{col}_{c}" for c in range(len(df_temp.columns))]] = df_temp
            df.drop(col, axis=1, inplace=True)

    for col in df.columns:
        if isinstance(df[col][0], dict):
            # print(f"Column name: {col}")
            df_temp = pd.DataFrame.from_dict(df[col].to_dict()).transpose()
            new_names = {k: f"{col}_{k}" for k in df_temp.columns}
            df_temp.rename(columns=new_names, inplace=True)
            df = pd.concat([df, df_temp], axis=1)
            df.drop(col, axis=1, inplace=True)
    return df


if __name__ == "__main__":
    df = pd.DataFrame(get_elo(all=False))
    expand_elo_columns(df).to_csv("temp_zrl_elo.csv", index=False)
