#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 16:42:43 2022

@author: jeremyalexander
"""

from dash import Dash
from dash import dcc
from dash import html
import pandas as pd
#import geoplot as gplt
import json
import geopandas as gpd
#import geoplot.crs as gcrs
import numpy as np
import plotly.express as px

aus_bound = gpd.read_file('/Volumes/ElementsSE/Reef_Authority/shp_boundaries/Boundary_Australia/Australia_Boundary.shp')
aus_bound = aus_bound.to_crs("EPSG:4326")

# gbr boundary
gbr_boundary = gpd.read_file('/Volumes/ElementsSE/Reef_Authority/shp_boundaries/Boundary_GBRMPA/Great_Barrier_Reef_Marine_Park_Boundary.shp')
gbr_boundary = gbr_boundary.to_crs("EPSG:4326")

# emc boundary
emc_bound = gpd.read_file('/Volumes/ElementsSE/Reef_Authority/shp_boundaries/emc_no_mgmt.shp')
emc_bound = emc_bound.to_crs("EPSG:4326")

# tumra boundary
tumra = gpd.read_file('/Volumes/ElementsSE/Reef_Authority/shp_boundaries/Boundary_TUMRA/Traditional_Use_of_Marine_Resources_Agreement_areas.shp')
tumra = tumra.to_crs("EPSG:4326")

# shipping lanes
shipping_boundary = gpd.read_file('/Volumes/ElementsSE/Reef_Authority/shp_boundaries/shipping_boundary/Designated_Shipping_Areas_of_the_GBRMP.shp')
shipping_boundary = shipping_boundary.to_crs("EPSG:4326")

# shipping lanes
gbr_features = gpd.read_file('/Volumes/ElementsSE/Reef_Authority/shp_boundaries/gbr_features_no_mainland.shp')
gbr_features = gbr_features.to_crs("EPSG:4326")

# gbr zoning
gbr_zoning = gpd.read_file('/Volumes/ElementsSE/Reef_Authority/shp_boundaries/Boundary_GBRMPA_Zoning/Great_Barrier_Reef_Marine_Park_Zoning.shp')
gbr_zoning = gbr_zoning.to_crs("EPSG:4326")

gbr_zoning_green = gbr_zoning[gbr_zoning['ALT_ZONE'].isin(['Green Zone'])]
gbr_zoning_pink = gbr_zoning[gbr_zoning['ALT_ZONE'].isin(['Pink Zone'])]
gbr_zoning_yellow = gbr_zoning[gbr_zoning['ALT_ZONE'].isin(['Yellow Zone'])]
gbr_zoning_darkblue = gbr_zoning[gbr_zoning['ALT_ZONE'].isin(['Dark Blue Zone'])]
gbr_zoning_olivegreen = gbr_zoning[gbr_zoning['ALT_ZONE'].isin(['Olive Zone'])]
gbr_zoning_orange = gbr_zoning[gbr_zoning['ALT_ZONE'].isin(['Orange Zone'])]
gbr_zoning_lightblue = gbr_zoning[gbr_zoning['ALT_ZONE'].isin(['Light Blue Zone'])]

data = pd.read_csv('vesselTracking_2021_Dec.csv')

data = data.dropna(subset = ['TIMESTAMP'])
        
data['TIMESTAMP'] = pd.to_datetime(data['TIMESTAMP'], dayfirst = True).sort_values()

# round time to nearest min
data['TIMESTAMP'] = data['TIMESTAMP'].dt.floor('1min')
    
# split dates and times into separate columns
data['DATE'], data['TIME'] = zip(*[(d.date(), d.time()) for d in data['TIMESTAMP']])

# drop days outside month
#df = df[df['DATE'] != datetime.date(2022, 1, 1)]

# convert to datetime
data['DATE'] = pd.to_datetime(data['DATE'])
    
# return year as separate column 
data['YEAR'] = data['DATE'].dt.year

# sort values
data = data.sort_values(by = 'DATE')
#data.sort_values('Date', inplace = True)

data = data.dropna(subset = ['VESSEL_CATEGORY'])

data['VESSEL_CATEGORY'] = data['VESSEL_CATEGORY'].replace(np.nan, '', regex = True)

data['VESSEL_CATEGORY'] = np.where(data.TYPE.str.contains("Tanker"), "Shipping",
                            np.where(data.TYPE.str.contains("Cargo"), "Shipping",
                            np.where(data.TYPE.str.contains("Tug"), "Shipping", 
                            np.where(data.TYPE.str.contains("Passenger"), "Passenger", 
                            np.where(data.TYPE.str.contains("Sailing"), "Sailing", 
                            np.where(data.TYPE.str.contains("Pleasure craft"), "Pleasure Craft",                               
                            np.where(data.TYPE.str.contains("Other"), "Other", 
                            np.where(data.TYPE.str.contains("Towing"), "Shipping", 
                            np.where(data.TYPE.str.contains("unknown"), "Unknown",                                   
                            np.where(data.TYPE.str.contains("Port tender"), "Works", 
                            np.where(data.TYPE.str.contains("Pilot vessel"), "Works", 
                            np.where(data.TYPE.str.contains("Fishing"), "Fishing",                                
                            np.where(data.TYPE.str.contains("Engaged in diving operations"), "Works", 
                            np.where(data.TYPE.str.contains("Reserved"), "Reserved",                            
                            np.where(data.TYPE.str.contains("Law enforcement"), "Government", 
                            np.where(data.TYPE.str.contains("HSC"), "High Speed Craft",                                   
                            np.where(data.TYPE.str.contains("SAR"), "Search and Rescue",                              
                            np.where(data.TYPE.str.contains("Engaged in dredging"), "Works",                                   
                            np.where(data.TYPE.str.contains("Engaged in military"), "Military", 
                            np.where(data.TYPE.str.contains("Vessel with anti-pollution"), "Works",     
                            np.where(data.TYPE.str.contains("Local"), "Local",                                   
                            np.where(data.TYPE.str.contains("WIG"), "Wing in Ground", np.nan)
                            )))))))))))))))))))))
    
# assign unique color to vessel category
data['Color'] = data['VESSEL_CATEGORY'].map(dict(zip(data['VESSEL_CATEGORY'].unique(),
                                       px.colors.qualitative.Alphabet[:len(data['VESSEL_CATEGORY'].unique())])))

# scatter mapbox
vessel_scatter = px.scatter_mapbox(data_frame=data, 
                                   lat = 'LAT', 
                                   lon = 'LON',
                                   color = 'VESSEL_CATEGORY',
                                   opacity = 0.5,
                                   zoom = 5,
                                   mapbox_style = 'carto-positron', 
                                   hover_name = 'VESSEL_CATEGORY',
                                   )

vessel_scatter.update_layout(height = 800, width = 800, margin = dict(l = 10, r = 10, t = 30, b = 10))

vessel_scatter.update_layout(mapbox={
            #"zoom": 8.5,
            "layers": [
                {"source": json.loads(gbr_boundary.geometry.to_json()),
                    "below": "traces",
                    "type": "fill",
                    "color": "black",
                    "opacity" : 0.01,
                    "line": {"width": 1}
                },
                {"source": json.loads(tumra.geometry.to_json()),
                    "below": "traces",
                    "type": "fill",
                    "color": "purple",
                    "opacity" : 0.2,
                    "line": {"width": 0.2}
                },
                {"source": json.loads(gbr_features.geometry.to_json()),
                    "below": "traces",
                    "type": "fill",
                    "opacity" : 0.2,
                    "color": "olive", 
                    "line": {"width": 0.1}
                },
                {"source": json.loads(shipping_boundary.geometry.to_json()),
                    "below": "traces",
                    "type": "fill",
                    "color": "black",
                    "opacity" : 0.1,
                    "line": {"width": 10}
                },
                {"source": json.loads(gbr_zoning_green.geometry.to_json()),
                    "below": "traces",
                    "type": "fill",
                    "opacity" : 0.05,
                    "color": "green", 
                    "line": {"width": 0.1}
               },
                {"source": json.loads(gbr_zoning_lightblue.geometry.to_json()),
                    "below": "traces",
                    "type": "fill",
                    "opacity" : 0.05,
                    "color": "lightblue", 
                    "line": {"width": 0.1}
                },
                {"source": json.loads(gbr_zoning_pink.geometry.to_json()),
                    "below": "traces",
                    "type": "fill",
                    "opacity" : 0.05,
                    "color": "pink", 
                    "line": {"width": 0.1}
                },
                {"source": json.loads(gbr_zoning_yellow.geometry.to_json()),
                    "below": "traces",
                    "type": "fill",
                    "opacity" : 0.05,
                    "color": "yellow", 
                    "line": {"width": 0.1}
                },
                {"source": json.loads(gbr_zoning_darkblue.geometry.to_json()),
                    "below": "traces",
                    "type": "fill",
                    "opacity" : 0.05,
                    "color": "darkblue", 
                    "line": {"width": 0.1}
                },
                {"source": json.loads(gbr_zoning_olivegreen.geometry.to_json()),
                    "below": "traces",
                    "type": "fill",
                    "opacity" : 0.05,
                    "color": "olive", 
                    "line": {"width": 0.1}
                },
                {"source": json.loads(gbr_zoning_orange.geometry.to_json()),
                    "below": "traces",
                    "type": "fill",
                    "opacity" : 0.05,
                    "color": "orange", 
                    "line": {"width": 0.1}
                },
            ],
        },
)

app = Dash(__name__)

# Set up the layout with a single graph
app.layout = html.Div(children = 
   [html.H1('Vessel Location'),
    dcc.Graph(id = 'scatter mapbox', figure = vessel_scatter)
    ])

if __name__ == "__main__":
    app.run_server(debug=True)
    
    