import pandas as pd


def cg14_18(stockdata,data22):
    # "Material group 1.1" sütunundaki değerleri dönüştürün
    data22['Material group 1.1'] = data22['Material group 1.1'].astype(str)

    # Başında sıfır olanları kaldırın ve metin içeren değerleri atlayın
    #data22['Material group 1'] = data22['Material group 1'].apply(lambda x: x.lstrip('0') if x.isdigit() else None)

    # None olanları (metin içerenleri) atlayın
    data22 = data22.dropna(subset=['Material group 1'])

    # Dönüşüm sonucunu integer'a çevirin
    #data22['Material group 1'] = data22['Material group 1'].astype(float)

    data22 = data22[~data22['Sales document'].astype(str).str.startswith(('6001', '7'))]

    data22 = data22[~data22['Material'].str.startswith(('PD'))]

    data22 = data22[data22["Sales Organization"]== 1000]

    data22 = data22[data22["Distribution Channel"]== 10]

    data22 = data22[data22["Entity"]== "Turkey"]

    data22 = data22[data22["Plant"]== "TR02"]

    unique_materials = stockdata['Material'].unique()

    data22 = data22[data22['Material'].isin(unique_materials)]

    df = data22
    df = df[(df["Entity"] == 'Turkey')]
    df = df[(df["Plant"] == 'TR02')]
    df = df[(df["Customer Group"] == 14) | (df["Customer Group"] == 15)|(df["Customer Group"] == 16)|(df["Customer Group"] == 17)|(df["Customer Group"] == 18)|
            (df["Customer Group"] == "14") | (df["Customer Group"] == "15")|(df["Customer Group"] == "16")|(df["Customer Group"] == "17")|(df["Customer Group"] == "18")]
    df = df.reset_index()
    df = df.drop(['index'], axis=1)

    #quantity için cum_TRY 2'li grupları olusturma

    cum_TRY2 = (df.groupby(["Customer Name", "Material group 1.1"])["Order Qty In SU"]
              .sum().unstack().reset_index().fillna(0)
              .set_index("Customer Name"))

    cum_TRY3 = (df.groupby(["Customer Name", "Original Activity Code"])["Order Qty In SU"]
              .sum().unstack().reset_index().fillna(0)
              .set_index("Customer Name"))

    #quantity corr for groups 14 and 15

    corr_TRY2 = cum_TRY2.corr()
    s2 = corr_TRY2.unstack()
    so2 = s2.sort_values(kind="quicksort")
    so2= pd.DataFrame(so2,columns=["Correlation coefficient"])
    so12= so2[(so2.iloc[:,0] >=0) & (so2.iloc[:,0]!=1)]
    so22 = so2.drop_duplicates()
    corr_TRY2=corr_TRY2.reset_index()
    corr_matrix2 = cum_TRY2.corr()

    corr_TRY3 = cum_TRY3.corr()
    s3 = corr_TRY3.unstack()
    so3 = s3.sort_values(kind="quicksort")
    so3= pd.DataFrame(so3,columns=["Correlation coefficient"])
    so13= so3[(so3.iloc[:,0] >=0) & (so3.iloc[:,0]!=1)]
    so33 = so3.drop_duplicates()
    corr_TRY3=corr_TRY3.reset_index()
    corr_matrix3 = cum_TRY3.corr()

    corr_TRY2.to_excel("material_group_corr.xlsx")
    corr_TRY3.to_excel("CG14_15_16_17_18.xlsx")
    return corr_TRY2


