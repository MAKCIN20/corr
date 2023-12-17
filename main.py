
import pandas as pd
#Import datasets
stockdata = pd.read_csv("dataset/supermarket_sales - Sheet1.csv")
stockdata = stockdata[stockdata["Dikkate Alınacaklar"]== "X"]


data22 = pd.read_csv("Datasets/22order.csv",low_memory=False)
policy=pd.read_excel("Datasets/Commercial Policy Dist_rev.xlsx",sheet_name="unique_list")

corr14_18=CG_14_15_16_17_18.cg14_18(stockdata,data22)
corr80=CG80.cg80(stockdata,data22)
#filtering groups
data22=data22[(data22["Customer Group"]==14) | (data22["Customer Group"]==15) | (data22["Customer Group"]==16) | (data22["Customer Group"]==17) | (data22["Customer Group"]==18) | (data22["Customer Group"]=="14") | (data22["Customer Group"]=="15") | (data22["Customer Group"]=="16") | (data22["Customer Group"]=="17") | (data22["Customer Group"]=="18")]
policy["Customer Group"]=policy["Customer Group"].astype("str")
polcy=policy.groupby(["Customer Group"],as_index=False)["Activity Code"].apply(list)

df=data22.groupby(["Customer Name","Material group 1.1","Customer Group"],as_index=False)["Order Qty In SU"].sum()
df.reset_index(inplace=True)
stockdata=stockdata.groupby(["Material Description"],as_index=False)["FreeStock Qty"].sum()

#14-18 Arası olanlar için corr dictionary formatına getirmek için
corr_dict_14_18={}
for column in range(1,len(corr14_18)):
    corr_list=[]
    for row in range(1,len(corr14_18)):
        if (corr14_18.iloc[row,column]>0.3 and corr14_18.iloc[row,column]<1):
            corr_list.append(corr14_18.loc[row,"Material group 1.1"])
    corr_dict_14_18[corr14_18.columns[column]]=corr_list
#80 grubu için korelasyon dictionary
corr_dict_80={}
for column in range(1,len(corr80)):
    corr_list=[]
    for row in range(1,len(corr80)):
        if (corr80.iloc[row,column]>0.3 and corr80.iloc[row,column]<1):
            corr_list.append(corr80.loc[row,"Material group 1.1"])
    corr_dict_80[corr80.columns[column]]=corr_list





def action_list(df,corr_dict,policy,stockdata):
    #Customer ve Activity Code bazında tüm alımları görmek için oluşturulan df
    customer_activity_grouped = df.groupby(["Customer Name"], as_index=False)["Material group 1.1"].apply(list)
    #Material group kodlarını çekme!!
    material_group = data22[["Material group 1", "Material group 1.1"]]
    material_group.drop_duplicates(inplace=True)
    material_group.reset_index(inplace=True)
    # Tüm rowları incelemek için bir for döngüsü
    for i in range(len(df)):
        #Müşteri önce filtreleniyor sonra grubu öğrenilerek policy list buna göre güncellenerek bu aktivite kodları kullanıyor
        filtered_customer_df=df[df["Customer Name"]==df.loc[i,"Customer Name"]]
        customer_group = df.loc[i, "Customer Group"]
        new_pol=policy[policy["Customer Group"]==customer_group]
        policy_list=new_pol.loc[:,"Activity Code"]
        #Getting related correlated list
        corr_list=corr_dict.get(df.loc[i,"Material group 1.1"])
        buyed_recommandation=[]
        #Corr list boş ise otomatik boş dönüyor
        if corr_list!= None:
            #Burda halihazırda satın alınan ve satın alınmamış correle olan activite kodlarını listeliyoruz
            already_buyed_act=[]
            not_buyed_act=[]
            customer_activity_code=list(customer_activity_grouped[customer_activity_grouped["Customer Name"]==df.loc[i,"Customer Name"]]["Material group 1.1"])[0]
            #correlation ve müşterinin aldığı aktivite kodlarının karşılaştırımlası
            for j in range(len(corr_list)):
                for k in range(len(customer_activity_code)):
                    if corr_list[j]==customer_activity_code[k]:
                        already_buyed_act.append(corr_list[j])
            #Müşterinin aldığı ve korelasyonda bulunanları bulduktan sonra bu grupta olmayanları not buyed olarak aldım.
            not_buyed_act=set(corr_list)-set(already_buyed_act)
            #Alınanlar arasında eğer ürün adet olarak %80 oranını tutturmuyorsa bu üründe önerilmeli diye ekledim.
            for j in range(len(already_buyed_act)-1):
                main_activity=filtered_customer_df[filtered_customer_df["Material group 1.1"]==already_buyed_act[j]]
                main_activity.reset_index(inplace=True)
                correlated_activity=filtered_customer_df[filtered_customer_df["Material group 1.1"]==already_buyed_act[j+1]]
                correlated_activity.reset_index(inplace=True)
                main_activity_quantity=main_activity.loc[0,"Order Qty In SU"]
                correlated_activity_quantity = correlated_activity.loc[0, "Order Qty In SU"]
                if 0.8<(main_activity_quantity/correlated_activity_quantity)<1.25 :
                    continue
                else:
                    buyed_recommandation.append(already_buyed_act[j])
            #not_buyed_act=set(not_buyed_act).intersection(set(policy_list))
            #buyed_recommandation=set(buyed_recommandation).intersection(set(policy_list))
            for j in range(len(material_group)):
                if df.loc[i, "Material group 1.1"] == material_group.loc[j, "Material group 1.1"]:
                    df.loc[i, "Material group 1"] = material_group.loc[j, "Material group 1"]
            stock_value_not_buyed=[]
            for j in range(len(not_buyed_act)):
                not_buyed=list(not_buyed_act)
                stock=stockdata[stockdata["Material Description"]==not_buyed[j]]
                stock.reset_index(inplace=True)
                if stock.loc[0,"Material Description"]==[]:
                    stock_value_not_buyed.append("0")
                else:
                    stock_value_not_buyed.append(stock.loc[0,"FreeStock Qty"])
            stock_value_buyed=[]
            for j in range(len(already_buyed_act)):
                buyed = list(already_buyed_act)
                stock = stockdata[stockdata["Material Description"] == buyed[j]]
                stock.reset_index(inplace=True)
                if stock.loc[0, "Material Description"] == None:
                    stock_value_buyed.append("0")
                else:
                    stock_value_buyed.append(stock.loc[0, "FreeStock Qty"])
            df.loc[i,"First Buy"]=str(list(not_buyed_act))
            df.loc[i,"Correlation Recommandation"]=str(list(buyed_recommandation))
            df.loc[i,"Stock First Buy"]=str(list(stock_value_not_buyed))
            df.loc[i, "Stock Correlation Recommendation"] = str(list(stock_value_buyed))

    return df





#functionın aktifleştirilmesi
corr_df_14_18=action_list(df,corr_dict_14_18,policy,stockdata)
corr80_df=action_list(df,corr_dict_80,policy,stockdata)




#Correlation exceli olarak output olarak çıkması.
with pd.ExcelWriter("Correlation.xlsx") as writer:
    corr_df_14_18.to_excel(writer,sheet_name="Correlation of 14-18")
    corr80_df.to_excel(writer,sheet_name="Correlation of 80 ")

#Mehmet Emin Akçin, Eren Fidan, ve sayın yönetici Mervenur Gülel Hayratıdır Kana kana kullanabilirsiniz. :)

