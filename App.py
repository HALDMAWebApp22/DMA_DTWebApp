import folium
from folium.plugins import HeatMap
import pandas as pd
import geopandas as gpd
from pyproj import CRS
import webbrowser
from folium.plugins import MarkerCluster
from folium.plugins import HeatMapWithTime
import streamlit as st
from streamlit_folium import folium_static
import leafmap.foliumap as leafmap
import hydralit_components as hc
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict, OrderedDict
from PIL import Image
import streamlit_authenticator as stauth
import xml.etree.ElementTree as ET
import plotly.express as px
import requests
from datetime import datetime
import xml
import csv
import numpy as np
from plotly import graph_objects as go
from plotly.subplots import make_subplots
import branca
import streamlit.components.v1 as components
import time
from datetime import datetime
import streamlit as st
from utilis import db

st.set_page_config(layout="wide")
image = Image.open('Data\HAL.png')
add_image = st.sidebar.image(image, width=250)
names = ['Glyn Addicott','Hussein Gulamhusein','Nick Jansen','Fakher Raza', 'Malcolm Russell', 'Soruban Sarvananther','Gary Watts']
usernames = ['Glyn','Hussein','Nick','Fakher', 'Malcolm', 'Soruban', 'Gary']
passwords = ['HAL01','HAL02','SSL01','SSL02','MWS01','MWS02','MWS03']
hashed_passwords = stauth.hasher(passwords).generate()
authenticator = stauth.authenticate(names,usernames,hashed_passwords,'a','b',cookie_expiry_days=0.0001)
name, authentication_status = authenticator.login('Login')

if authentication_status == False:
    st.error('Username/Password is incorrect, please try again')
    
elif authentication_status == None:
    st.warning('Please enter your username and password')
    
elif st.session_state['authentication_status'] == True:

    st.header('Thames Water - RIVERSIDE & ISLE OF DOGS DMA Digital Twins')
    image2 = Image.open(r'Data\tw.png')
    add_image2 = st.sidebar.image(image2, width=250)
    st.sidebar.write('Welcome %s' % (name))


    pages = st.sidebar.radio("NAVIGATION PAGES", ('POI GEO MAP', 'LEAK GEO MAP', 'ZRIVSE PRESSURE LOGGER DATA', 'DM FLOW DATA'))

    if pages == "POI GEO MAP":

        df1 = pd.read_csv(r"Data\DELTA.csv")
        df2 = pd.read_csv(r"Data\HWM Acoustic Loggers.csv")
        df4 = pd.read_csv(r"Data\Projects\Level_Spread_Data.csv")
        df9 = pd.read_csv(r"Data\Projects\HWM Daily.csv")
        
        C1, C2, C3, C4 = st.columns((1,1,1,1))

        with C1:
            fig1 = go.Figure()

            fig1.add_trace(go.Indicator(
                mode = "number+delta",
                value = df1['Delta'].unique().mean(),
                number={"font":{"size":40}},        
                delta={"position": "top", "reference": 1}))
            fig1.update_layout(paper_bgcolor="#E3E3E3", autosize=False, title= "Average Pressure Delta (Bar)",width=300,height=100, margin=dict(l=10,r=10,t=40,b=10,pad=0))
            st.plotly_chart(fig1)

        with C2:   
            fig2 = go.Figure()

            fig2.add_trace(go.Indicator(
                mode = "number+delta",
                value = len(df1[df1['Delta'] >= 0.3]),
                number={"font":{"size":40}},
                delta={"position": "top", "reference": 10}))
            fig2.update_layout(paper_bgcolor="#E3E3E3", autosize=False, title= "Pressure Loggers in Alarm",width=300,height=100, margin=dict(l=10,r=10,t=40,b=10,pad=0))
            st.plotly_chart(fig2)

        with C3:   
            fig3 = go.Figure()

            fig3.add_trace(go.Indicator(
                mode = "number+delta",
                value = len(df9[df9['Leak Status '] == 1]),
                number={"font":{"size":40}},
                delta={"position": "top", "reference": 69}))
            fig3.update_layout(paper_bgcolor="#E3E3E3",autosize=False, title= "Acoustic Loggers in Alarm",width=300,height=100, margin=dict(l=10,r=10,t=40,b=10,pad=0))
            st.plotly_chart(fig3)

        with C4:   
            fig4 = go.Figure()

            fig4.add_trace(go.Indicator(
                mode = "gauge+number",
                value = 3.690,
                delta={"position": "top", "reference": 3.9}))
            fig4.update_layout(paper_bgcolor="#E3E3E3", autosize=False, title= "Max Network Pressure",width=300,height=100, margin=dict(l=10,r=10,t=40,b=10,pad=0))
            st.plotly_chart(fig4) 

        m = leafmap.Map(location=[51.4756, -0.0111], zoom_start=14,tiles='Stamen Toner')
        pipe1 = gpd.read_file(r"Shapefiles\ZRIVSE Pipes.shp")
        pipe2 = gpd.read_file(r"Shapefiles\ZFINSB Pipes.shp")
        folium.GeoJson(data=pipe1["geometry"],style_function=lambda x:{'fillColor': '#000080', 'color': '#000080','weight':4}).add_to(folium.FeatureGroup(name='ZRIVSE Pipes',show=True).add_to(m))
        folium.GeoJson(data=pipe2["geometry"],style_function=lambda x:{'fillColor': '#FACC2E', 'color': '#FACC2E','weight':4}).add_to(folium.FeatureGroup(name='ZFINSB Pipes',show=True).add_to(m))

        def color(delta):
            if delta in range(0,1500):
                col = 'green'
            elif delta in range(1501,3000):
                col = 'orange'
            elif delta in range(3001,6000):
                col='red'
            else:
                col='lightgray'
            return col

        def color2(l):
            if l in range(-20,20):
                col = 'green'
            elif l in range(21,28):
                col = 'orange'
            elif l in range(29,100):
                col='red'
            else:
                col='lightgray'
            return col

        marker_cluster = MarkerCluster().add_to(folium.FeatureGroup(name='Pressure Logger Alarms',show=False).add_to(m))
        for lat,lon,delta in zip(df1['lat '],df1['lon'],df1['delta2']):
            folium.Marker(location=[lat,lon],popup = delta, icon= folium.Icon(color=color(delta),icon_color='white',icon = 'signal')).add_to(marker_cluster)

        Site_ID=[]
        Level=[]
        Spread=[]
        marker_cluster2 = MarkerCluster().add_to(folium.FeatureGroup(name='Acoustic Logger Alarms',show=False).add_to(m))

        for lat,lon,id_,l,s,a in zip(df9['Lat'],df9['Lon'],df9['ID'],df9['Level'],df9['Spread'],df9['A']):
            Site_ID.append(id_)
            Level.append(l)
            Spread.append(s)
            popup = folium.Popup(min_width=300, max_width=300)
            folium.Marker(location=[lat,lon],popup ="Site:{}, Level:{}, Spread:{}".format(id_,l,s),icon= folium.Icon(color=color2(l),icon_color='white',icon = 'signal')).add_to(marker_cluster2)

        index1 = []
        for x in df4['Date '].unique():
            datemap = x
            index1.append(datemap)

        df4_date_list = []
        for date in df4['Date '].sort_values().unique():
            df4_date_list.append(df4.loc[df4['Date '] == date, ['Lat', 'Lon', 'A']].groupby(['Lat', 'Lon']).sum().reset_index().values.tolist())
        HeatMapWithTime(df4_date_list,radius=40,index=index1,gradient={0.5: 'blue', 0.6: 'lime', 0.7:'orange', 0.8: 'red'}, min_opacity=0.2, max_opacity=0.8, position='bottomright',use_local_extrema=True,name='HWM Acoustic Noise Timelapse',show=False).add_to(m)

        folium.Circle(radius=150,location=[51.4755670,-0.0180303],popup='POI01 ZRIVSE03',color='blue',fill=True,fill_color='#3186cc').add_to(folium.FeatureGroup(name='POI01 ZRIVSE03',show=False).add_to(m))
        folium.Circle(radius=150,location=[51.4815247,-0.0139478],popup='POI01 ZRIVSE03',color='black',fill=True,fill_color='#3186cc').add_to(folium.FeatureGroup(name='POI02 ZRIVSE03',show=False).add_to(m))
        folium.Circle(radius=150,location=[51.4891361,0.0062603],popup='POI01 ZRIVSE04',color='black',fill=True,fill_color='#3186cc').add_to(folium.FeatureGroup(name='POI01 ZRIVSE04',show=False).add_to(m))
        folium.Circle(radius=150,location=[51.4705292,-0.0167784],popup='POI01 ZRIVSE02',color='black',fill=True,fill_color='#3186cc').add_to(folium.FeatureGroup(name='POI01 ZRIVSE02',show=False).add_to(m))
        folium.Circle(radius=150,location=[51.4948761,-0.0187323],popup='POI01 ZFINSB26',color='blue',fill=True,fill_color='#3186cc').add_to(folium.FeatureGroup(name='POI01 ZFINSB26',show=False).add_to(m))
        folium.Circle(radius=150,location=[51.5003456,-0.0175156],popup='POI02 ZFINSB26',color='black',fill=True,fill_color='#3186cc').add_to(folium.FeatureGroup(name='POI02 ZFINSB26',show=False).add_to(m))

        folium.TileLayer('openstreetmap').add_to(m)
        folium.TileLayer(tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',attr = 'Esri',name = 'Esri Satellite',overlay = False,control = True).add_to(m)
        folium.TileLayer('stamenterrain').add_to(m)
        folium.LayerControl(collapsed=True).add_to(m)
        m.to_streamlit(width=800, height=800)

        COMMENT_TEMPLATE_MD = """{}  - {}- {}
        > {}"""

        def space(num_lines=1):
            """Adds empty lines to the Streamlit app."""
            for _ in range(num_lines):
                st.write("")

        conn = db.connect()
        comments = db.collect(conn)

        with st.expander("Open Site Team Comments 💬"):

           st.write("**Site Team Findings:**")

           for index, entry in enumerate(comments.itertuples()):
               st.markdown(COMMENT_TEMPLATE_MD.format(entry.Name, entry.DMA, entry.Date, entry.Findings))

               is_last = index == len(comments) - 1
               is_new = "just_posted" in st.session_state and is_last
               if is_new:
                   st.success("☝️ Your comment was successfully posted.")

           space(2)

    # Insert comment

           st.write("**Add your own comment:**")
           form = st.form("comment")
           Name = form.text_input("Name")
           DMA = form.text_input("DMA")
           Findings = form.text_area("Findings")
           submit = form.form_submit_button("Submit")

           if submit:
               Date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
               db.insert(conn, [[Name, DMA, Date, Findings]])
               if "just_posted" not in st.session_state:
                   st.session_state["just_posted"] = True
##           st.experimental_rerun()

    elif pages == "LEAK GEO MAP":

        m = leafmap.Map(location=[51.4756, -0.0111], zoom_start=14,tiles='Stamen Toner')
        pipe1 = gpd.read_file(r"Shapefiles\ZRIVSE Pipes.shp")
        pipe2 = gpd.read_file(r"Shapefiles\ZFINSB Pipes.shp")
        folium.GeoJson(data=pipe1["geometry"],style_function=lambda x:{'fillColor': '#000080', 'color': '#000080','weight':4}).add_to(folium.FeatureGroup(name='ZRIVSE Pipes',show=True).add_to(m))
        folium.GeoJson(data=pipe2["geometry"],style_function=lambda x:{'fillColor': '#FACC2E', 'color': '#FACC2E','weight':4}).add_to(folium.FeatureGroup(name='ZFINSB Pipes',show=True).add_to(m))

        folium.TileLayer('openstreetmap').add_to(m)
        folium.TileLayer(tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',attr = 'Esri',name = 'Esri Satellite',overlay = False,control = True).add_to(m)
        folium.TileLayer('stamenterrain').add_to(m)
        folium.LayerControl(collapsed=False).add_to(m)
        m.to_streamlit(width=800, height=800)


    elif pages == "ZRIVSE PRESSURE LOGGER DATA":

        df5 = pd.read_csv(r"Data\Logger_25.csv")
        fig4 = px.line(df5, x="Time", y=df5.columns,title='Thames water - RIVERSIDE - Pressure Logger Data',width=1000, height=800)
##        fig4.update_layout(hovermode='x')
##        fig4.update_traces(mode="lines", hovertemplate=None)
##        fig4.update_layout(hovermode="x unified")
        fig4.update_layout(yaxis_title="Pressure (m)",legend_title="Pressure Loggers")
        fig4.update_layout(xaxis=dict(rangeselector=dict(buttons=list([dict(count=1,label="1hour",step="hour",stepmode="backward"),dict(count=1,label="1day",step="day",stepmode="backward"),dict(count=3,label="3day",step="day",stepmode="backward"),dict(count=1,label="1month",step="month",stepmode="backward"),dict(count=1,label="1year",step="year",stepmode="backward"),dict(step="all")])),rangeslider=dict(visible=True),type="date"))
        fig4.update_xaxes(rangeslider_thickness = 0.05)

        # add vertical line indicating specific date (e.g. today)

        today = datetime.now()
        fig4.update_layout(shapes=[
        dict(type='line',yref='paper', y0=0, y1=1,xref='x', x0=today, x1=today)])
        st.plotly_chart(fig4,use_container_width=False)

    elif pages == "DM FLOW DATA":
        
        df6 = pd.read_csv(r"Data\ZRIVSE02.csv")
        fig = px.line(df6, x="Date", y=df6.columns)
        fig.update_layout(height=800)
        fig.update_xaxes(rangeslider_thickness = 0.05)
        st.plotly_chart(fig,use_container_width=True)

        df7 = pd.read_csv(r"Data\ZRIVSE03.csv")
        fig2 = px.line(df7, x="Date", y=df7.columns)
        fig2.update_layout(height=800)
        fig2.update_xaxes(rangeslider_thickness = 0.05)
        st.plotly_chart(fig2,use_container_width=True)

        df8 = pd.read_csv(r"Data\ZRIVSE04.csv")
        fig3 = px.line(df8, x="Date", y=df8.columns)
        fig3.update_layout(height=800)
        fig3.update_xaxes(rangeslider_thickness = 0.05)
        st.plotly_chart(fig3,use_container_width=True)

