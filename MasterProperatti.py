#!/usr/bin/env python
# coding: utf-8

# In[22]:


import numpy as np
import pandas as pd
import locale
import pickle
import streamlit as st


# In[2]:


path="C:/Users/nesma/Documents/Consultora/SitioWeb/Demos/DataScience/"
model = pickle.load(open("properattiModel.sav", 'rb'))
# In[3]:


data = pd.read_excel(path+"ciudades.xlsx",usecols=["provincia","ciudad"])
data.drop_duplicates(inplace=True,ignore_index=True)


# #### Streamlit

# In[4]:


# [theme]
primaryColor="#F63366"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F0F2F6"
textColor="#262730"
font="sans serif"


# In[5]:


st.header("Tazador de propiedades")

st.subheader("Características de la propiedad")
col1, col2 = st.columns(2)

    
with col1:
    provincias = tuple(data['provincia'].sort_values().unique())
    provincia = st.selectbox('Provincia',provincias)
    propiedadesDic= { "Casa":"house","Departamento":"apartment", "Propiedad horizontal (PH)": "PH","Negocio":"store"}
    propiedad = st.selectbox('Tipo de propiedad',tuple(propiedadesDic.keys()))  
    
    ambientes = st.number_input("Ambientes", min_value=1, max_value=8)


    estrenar = st.checkbox('A estrenar')
    balcon = st.checkbox('Balcón')
    pileta = st.checkbox('Pileta')
    calefaccion = st.checkbox('Calefacción centralizada')
    
with col2:
    maskCiudades=data['provincia']==provincia
    ciudades = tuple(data.loc[maskCiudades, 'ciudad'].sort_values().unique())
    ciudad = st.selectbox('Ciudad / Barrio',ciudades)   
    
    superficie = st.number_input("Superficie total (metros cuadrados)", min_value=30, max_value=600)
    banos = st.number_input("Cantidad de baños", min_value=1, max_value=9)   
    # estadoDic= ("A estrenar", "Buen estado", "A reciclar")
    # propiedad = st.selectbox('Estado de propiedad',estadoDic)    
    
    cochera = st.checkbox('Cochera')    
    Jardin = st.checkbox('Jardín')
    Quincho = st.checkbox('Quincho')
    Jacuzzi = st.checkbox('Jacuzzi')


# #### Model

# In[41]:


def predict():
    
    newInput= {'const':1,
           'surface_total_in_m2_clean': int(superficie),
           'property_type':propiedadesDic[propiedad],
           'provincia':provincia, 
           'ciudad':ciudad, 
           'rooms_clean': int(ambientes),
           'banos': int(banos), 
           'pileta':pileta, 
           'cochera':cochera, 
           'Jacuzzi':Jacuzzi, 
           'Quincho':Quincho, 
           'balcon':balcon, 
           'estrenar':estrenar, 
           'calefaccion':calefaccion,
           'Jardin':Jardin
          }
    
    data_modelo = pd.DataFrame(newInput,columns=newInput.keys(),index=[0])
    
    data_modelo.replace(False,0,inplace=True)
    data_modelo.replace(True,1,inplace=True)
    data_modelo = pd.get_dummies(data = data_modelo, columns = [ "property_type"])
    data_modelo["localidad_"+data_modelo['ciudad'][0]+data_modelo['provincia'][0]] = 1
    data_modelo['rooms_x_banos'] = data_modelo['rooms_clean'] * data_modelo['banos']
    data_modelo['surface_total_in_m2_clean_squared'] = data_modelo['surface_total_in_m2_clean']**2
    
    if newInput['property_type']=="house":
        data_modelo['house_mas_pileta'] = data_modelo['property_type_house'] * data_modelo['pileta']

    if newInput['property_type']=="apartment":    
        data_modelo['apartment_mas_cochera'] = data_modelo['property_type_apartment'] * data_modelo['cochera']

    if newInput['property_type']=="PH":      
        data_modelo['ph_mas_pileta'] = data_modelo['property_type_PH'] * data_modelo['pileta']
        data_modelo['ph_mas_cochera'] = data_modelo['property_type_PH'] * data_modelo['cochera']


    Xtest_empty = pd.read_excel(path+"Xtest_empty.xlsx")

    Xtest = pd.concat([Xtest_empty,data_modelo], join="inner")
    Xtest = pd.concat([Xtest_empty,Xtest])

    Xtest.fillna(0,inplace=True)
    
    # model = pickle.load(open(path+"properattiModel.sav", 'rb'))
    prediction_sm = model.predict(Xtest)
    
    result=prediction_sm*newInput['surface_total_in_m2_clean']
    
    result = int(result[0]/1000)*1000
    
    locale.setlocale(locale.LC_ALL, 'es_AR')
    result = locale.currency(result, symbol=True, grouping=True, international=False)[:-3]

    
    return result


# In[46]:


if st.button("Tazar propiedad"):
        st.balloons()
        st.success(f"El valor de la propiedad es de {predict()}")


# In[ ]:




