from collections import namedtuple
import pandas as pd
import numpy as np
from ast import literal_eval


text_collection = namedtuple(
    "text_collection", ['abstract','snippet', "lead_para", "headline"]
    )



def gen_full_text(
    abstract,
    snippet,
    lead_para,
    headline
):
    def clean_text(text):
        if text != "":
            if isinstance(text, str):
                if text.strip().endswith("."):
                    return text + " "
                else:
                    return text.strip() +". "
            else:
                return ""
        else:
            return ""
    
    info = text_collection(
        clean_text(abstract), 
        clean_text(snippet), 
        clean_text(lead_para), 
        clean_text(headline)
        )
    return info.headline + info.abstract + info.snippet + info.lead_para.strip()


def gen_full_text_df(
    df,
    new_col_name = "full_text",
    keep_all_cols = False
):
    
    if not np.all([col in df.columns for col in ("snippet",'lead_paragraph','headline', "abstract")]):
        raise ValueError("DataFrame must have abstact, snippet, lead_paragraph, and headline columns")

    df_new = df.copy()
    df_new[new_col_name] = df_new.apply(
        lambda x: gen_full_text(
            x.abstract,
            x.snippet,
            x.lead_paragraph,
            x.headline
            ),
        axis=1
        )
    if keep_all_cols:
        return df_new
    else:
        return df_new.drop(['abstract','snippet','lead_paragraph','headline'], axis=1)



def clean_df(df):
    """Cleans a raw dataframe generated from the gather_article_set function"""
    
    df_new = df.copy()
    
    df_new.pub_date = pd.to_datetime(df_new.pub_date)
    df_new['arguments'] = df_new['meta.arguments'].apply(
        lambda x: literal_eval(x) if isinstance(x, str) else x 
    )
    
    
    df_new['article_type'] = df_new['meta.article_type'].replace({
        'general_mkt':"general market article",
        'stock': "stock article"
    })
    df_new = df_new.rename({'meta.api': "api"}, axis = 1)
    df_new.drop(['meta.arguments','meta.article_type'], axis=1, inplace=True)
    return df_new


def combine_text_args(
    full_text: str,
    text_type: str,
    arguments: tuple
):
    arg_string = " Article Arguments: " + ", ".join(arguments) + ". "
    type_string = "Article Type: " + text_type + "."
    return full_text + arg_string + type_string

def combine_text_args_df(
    df,
    new_col_name='combined_text',
    keep_all_cols=True
):
    if not np.all([col in df.columns for col in ("full_text",'article_type','arguments')]):
        raise ValueError("DataFrame must have full_text, article_type, and arguments columns")
    
    new_df = df.copy()
    new_df[new_col_name] = new_df.apply(
        lambda x: combine_text_args(
            full_text=x.full_text,
            text_type=x.article_type,
            arguments=x.arguments
            ),
        axis=1
        )
    if keep_all_cols:
        return new_df
    else:
        return new_df.drop(['article_type','arguments'], axis=1)