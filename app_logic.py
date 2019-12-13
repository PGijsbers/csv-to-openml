import csv
import io
import re

import pandas as pd
import openml
from openml.datasets.functions import create_dataset
from openml.datasets import OpenMLDataset


def infer_categorical_variables_in_place(df: pd.DataFrame):
    """ Infers which columns of the DataFrame are categorical, and casts them as such. """
    # infer which variables are categorical
    MAX_UNIQUE_VALUES = 10
    for column in df.columns:
        if df[column].nunique() <= MAX_UNIQUE_VALUES:
            df[column] = df[column].astype('category')


def csv_bytes_to_dataframe(csv_bytes: bytes) -> pd.DataFrame:
    """ Converts a `bytes` object that represents a csv to a pandas dataframe. """
    file_content = io.StringIO(csv_bytes.decode())

    has_header = csv.Sniffer().has_header(file_content.read(1024))
    file_content.seek(0)

    df = pd.read_csv(file_content, header=0 if has_header else None)

    if not has_header:
        # If no header is provided, column names are integer, which is inconvenient later, change to str;
        df.columns = df.columns.astype(str)

    infer_categorical_variables_in_place(df)
    return df


def create_openml_dataset(df: pd.DataFrame, da: 'DataAnnotation') -> OpenMLDataset:
    collection_date = None if da.collection_date is None else da.collection_date.strftime("%d-%m-%Y")

    for column in df.columns:
        if df[column].dtype.name == 'category':
            # OpenML Python requires categorical values to be strings.
            df[column] = df[column].astype(str).astype('category')

    return create_dataset(
        name=da.name,
        description=da.description,
        creator=da.creator or None,
        contributor=da.contributor or None,
        collection_date=collection_date,
        language=da.language or None,
        licence=da.licence or None,
        default_target_attribute=da.target_column or None,
        row_id_attribute=da.id_column or None,
        citation=da.citation or None,
        ignore_attribute=da.ignore_columns or None,
        attributes='auto',
        data=df,
        # version_label
        original_data_url=da.data_url or None,
        paper_url=da.paper_url or None
    )


def set_openml_apikey(key):
    """ Tests if the string is 32-length hex string, if so, set as openml api key. """
    looks_like_key = re.fullmatch('[a-f0-9]{32}', key)
    if looks_like_key:
        openml.config.apikey = key
    return looks_like_key
