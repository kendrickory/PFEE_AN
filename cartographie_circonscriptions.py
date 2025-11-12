import geopandas as panda
import folium
import random
import pandas as pd
from folium.plugins import Geocoder

from folium.features import GeoJsonTooltip, GeoJsonPopup

circo = panda.read_file("C:\\Users\\kendr\\Downloads\\circonscriptions-legislatives-p10.geojson")

foreign = panda.read_file("C:\\Users\\kendr\\Downloads\\world-administrative-boundaries\\world-administrative-boundaries.shp")[["name", "iso3", "geometry"]]


foreign_circo = {
    "1": ["USA", "CAN"],
    "2": ["MEX","ARG","BRA","CHL","COL","PER","VEN","URY","PRY","ECU","FLK","CRI","PAN","CUB","DOM","HTI","JAM","BHS","TTO","BLZ","GTM","HDN","NIC","SLV","BOL","GUY","SUR","ATG","BRB","DMA","GRD","LCA","VCT","KNA","HND"], 
    "3": ["GBR","IRL","ISL","NOR","SWE","FIN","DNK","EST","LVA","LTU","GRL"],
    "4": ["BEL","NLD","LUX"],
    "5": ["AND","ESP","MCO","PRT"],
    "6": ["CHE","LIE"],
    "7": ["DEU","ALB","AUT","BIH","BGR","HRV","HUN","MKD","POL","ROU","SRB","MNE","SVN","CZE","SVK"],
    "8": ["ITA","MLT","SMR","VAT","CYP","GRC","TUR","ISR"],
    "9": ["DZA","MAR","LBY","TUN","BFA","MLI","NER","MRT","CPV","GMB","GNB","GIN","SEN","SLE","CIV","LBR","ESH"],
    "10": ["ZAF","BWA","LSO","MWI","MOZ","NAM","SWZ","ZMB","ZWE","COM","MDG","MUS","SYC","EGY","SDN","DJI","ERI","ETH","SOM","BDI","KEN","UGA","RWA","TZA","BEN","GHA","NGA","TGO","CMR","CAF","TCD","GAB","GNQ","STP","AGO","COG","COD","IRQ","JOR","LBN","SYR","SAU","BHR","ARE","KWT","OMN","QAT","YEM","SSD"],
    "11": ["ARM","BTN","TWN","PRK","AZE","BLR","GEO","KAZ","KGZ","MDA","UZB","RUS","TJK","TKM","UKR","AFG","BGD","IND","IRN","MDV","NPL","PAK","LKA","CHN","KOR","JPN","MNG","MMR","BRN","KHM","IDN","LAO","MYS","PLW","PHL","SGP","THA","TLS","VNM","AUS","FJI","KIR","MHL","FSM","NRU","NZL","PNG","SLB","WSM","TON","TUV","VUT"]
}

circonscriptions = []

for circ, countries in foreign_circo.items():
    subset = foreign[foreign["iso3"].isin(countries)]
    geom = subset.union_all()
    circonscriptions.append({"NUM_CIRC": circ, "geometry": geom})

df = panda.GeoDataFrame(circonscriptions, geometry="geometry", crs=foreign.crs)


df.to_file("C:\\Users\\kendr\\OneDrive\\Documents\\circonscriptions_etrangeres.geojson", driver="GeoJSON")
etr = panda.read_file("C:\\Users\\kendr\\OneDrive\\Documents\\circonscriptions_etrangeres.geojson").to_crs(epsg=4326)

full = panda.GeoDataFrame(pd.concat([circo, etr], ignore_index=True), crs=circo.crs)

etranger_labels = {
    "1": "Amérique du Nord",
    "2": "Amérique latine et Caraïbes",
    "3": "Europe du Nord",
    "4": "Benelux et péninsule Ibérique",
    "5": "Europe centrale et orientale",
    "6": "Suisse et Liechtenstein",
    "7": "Europe de l’Est, Asie et Océanie",
    "8": "Afrique du Nord et Moyen-Orient",
    "9": "Afrique de l’Ouest",
    "10": "Afrique centrale, australe et orientale",
    "11": "Europe du Sud-Est et Asie de l’Ouest"
}


for col in ["nomDepartement", "nomCirconscription"]:
    if col not in full.columns:
        full[col] = None


mask_etranger = full["NUM_CIRC"].astype(str).isin(etranger_labels.keys())

full.loc[mask_etranger, "nomDepartement"] = "Hors France"
full.loc[mask_etranger, "nomCirconscription"] = (
    full.loc[mask_etranger, "NUM_CIRC"]
    .astype(str)
    .map(lambda x: f"{etranger_labels[x]}")
)
if "NUM_CIRC" in full.columns and "codeCirconscription" not in full.columns:
    full = full.rename(columns={"NUM_CIRC": "codeCirconscription"})
elif "NUM_CIRC" in full.columns and "codeCirconscription" in full.columns:
    full["codeCirconscription"] = full["codeCirconscription"].fillna(full["NUM_CIRC"].astype(str))
    full = full.drop(columns=["NUM_CIRC"])
full.to_file("C:\\Users\\kendr\\OneDrive\\Documents\\circonscriptions_france_complete.geojson", driver="GeoJSON")
all_circo = panda.read_file("C:\\Users\\kendr\\OneDrive\\Documents\\circonscriptions_france_complete.geojson")


m = folium.Map(location=[46.6, 2.4], zoom_start=6, tiles=None
               , max_bounds=True,)

folium.TileLayer(
    'CartoDB positron',
    name='Fond de carte',
    no_wrap=True,      
).add_to(m)
all_circo["risque_institutionel"] = [random.randint(0, 100) for _ in range(len(all_circo))]

all_circo["risque_des_ressources"] = [random.randint(0, 100) for _ in range(len(all_circo))]
all_circo["risque_infrastructurel"] = [random.randint(0, 100) for _ in range(len(all_circo))]


  


all_circo["risque_total"] = (
    0.3 * (all_circo["risque_institutionel"] / all_circo["risque_institutionel"].max()) +
    0.3 * (all_circo["risque_des_ressources"] / all_circo["risque_des_ressources"].max()) +
    0.3 * (all_circo["risque_infrastructurel"] / all_circo["risque_infrastructurel"].max())
)


all_circo["risque_total"] = 100 * (all_circo["risque_total"] - all_circo["risque_total"].min()) / (all_circo["risque_total"].max() - all_circo["risque_total"].min())


geojson_layer= folium.GeoJson(
    all_circo,
    no_wrap = True,
    name="Circonscriptions législatives 2022",
    
    highlight_function=lambda feature: {
        "fillColor": "#ffff00",  
        "color": "white",
        "weight": 3,
        "fillOpacity": 0.6,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["nomDepartement", "nomCirconscription","risque_total"],
        aliases=["Département :","Circonscription :","Risque combiné :"]
    ),
    style_function=lambda x: {"fillOpacity": 0.01, "color": "black", "weight": 0.7},
    popup=folium.GeoJsonPopup(
        fields=["nomDepartement","nomCirconscription", "risque_institutionel", "risque_des_ressources", "risque_infrastructurel"],
        aliases=["Département","Circonscription :", "Risque institutionel :", "Risque des ressources :", "Risque infrastructurel:"],
        localize=True,
       labels=True,
       style="background-color: white; font-size: 12px;"
    )
).add_to(m)




"""cp_combiné=folium.Choropleth(
    geo_data=all_circo,
   data=all_circo,
    name="Risque combiné",
    columns=["codeCirconscription","risque_total"],
    key_on="feature.properties.codeCirconscription",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.8,
    line_weight=2,
    line_color="Black",
    legend_name="Risque combiné",
    style_function=lambda feature: {
        "fillColor": "transparent",
        "color": "black",
        "weight": 0.8,
        "fillOpacity": 0.3,
    },
    highlight_function=lambda feature: {
        "fillColor": "#ffff00",
        "color": "white",
        "weight": 3,
        "fillOpacity": 0.6,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["nomDepartement", "nomCirconscription", "risque_total"],
        aliases=["Département :", "Circonscription :", "Risque combiné :"],
        sticky=True,
        localize=True,
    ),
    popup=folium.GeoJsonPopup(
        fields=["nomDepartement", "nomCirconscription", 
                "risque_institutionel", "risque_des_ressources", "risque_infrastructurel"],
        aliases=["Département :", "Circonscription :", 
                 "Risque institutionel :", "Risque des ressources :", "Risque infrastructurel :"],
        localize=True,
        labels=True,
        style="background-color: white; font-size: 12px;"
    )
  
).add_to(m)


cp_institut=layer_institu=folium.Choropleth(
    geo_data=all_circo,
    data=all_circo,
    name="Risque institutionel",
    columns=["codeCirconscription", "risque_institutionel"],
    key_on="feature.properties.codeCirconscription",
    fill_color="Reds",
    fill_opacity=0.7,
    line_opacity=0.8,
    line_weight=2,
    line_color="Black",
    legend_name="Risque institutionel",
    style_function=lambda f: {"fillOpacity": 0, "color": "black", "weight": 0.8},
    highlight_function=lambda f: {"fillColor": "#ffcccc", "color": "white", "weight": 3, "fillOpacity": 0.6},
    tooltip=folium.GeoJsonTooltip(
        fields=["nomDepartement", "nomCirconscription", "risque_institutionel"],
        aliases=["Département :", "Circonscription :", "Risque institutionnel :"],
        sticky=True,
        localize=True,
    ),
    popup=folium.GeoJsonPopup(
        fields=["nomDepartement", "nomCirconscription", "risque_institutionel"],
        aliases=["Département :", "Circonscription :", "Risque institutionnel :"],
        localize=True,
        labels=True,
        style="background-color: white; font-size: 12px;"
    ),
   
).geojson

cp_ressources=layer_ressoures=folium.Choropleth(
    geo_data=all_circo,
    data=all_circo,
    name="Risque des ressources",
    columns=["codeCirconscription", "risque_des_ressources"],
    key_on="feature.properties.codeCirconscription",
    fill_color="Blues",
    fill_opacity=0.7,
    line_opacity=0.8,
    line_weight=2,
    line_color="Black",
    legend_name="Risque des ressouces",
    style_function=lambda f: {"fillOpacity": 0, "color": "black", "weight": 0.8},
    highlight_function=lambda f: {"fillColor": "#cce5ff", "color": "white", "weight": 3, "fillOpacity": 0.6},
    tooltip=folium.GeoJsonTooltip(
        fields=["nomDepartement", "nomCirconscription", "risque_des_ressources"],
        aliases=["Département :", "Circonscription :", "Risque des ressources :"],
        sticky=True,
        localize=True,
    ),
    popup=folium.GeoJsonPopup(
        fields=["nomDepartement", "nomCirconscription", "risque_des_ressources"],
        aliases=["Département :", "Circonscription :", "Risque des ressources :"],
        localize=True,
        labels=True,
        style="background-color: white; font-size: 12px;"
    ),
).geojson

cp_infrastruture=layer_infrastructure=folium.Choropleth(
    geo_data=all_circo,
    data=all_circo,
    name="Risque infrastructurel",
    columns=["codeCirconscription", "risque_infrastructurel"],
    key_on="feature.properties.codeCirconscription",
    fill_color="Greens",
    fill_opacity=0.7,
    line_opacity=0.8,
    line_weight=2,
    line_color="Black",
    legend_name="Risque infrastructurel",
    style_function=lambda f: {"fillOpacity": 0, "color": "black", "weight": 0.8},
    highlight_function=lambda f: {"fillColor": "#ccffcc", "color": "white", "weight": 3, "fillOpacity": 0.6},
    tooltip=folium.GeoJsonTooltip(
        fields=["nomDepartement", "nomCirconscription", "risque_infrastructurel"],
        aliases=["Département :", "Circonscription :", "Risque infrastructurel :"],
        sticky=True,
        localize=True,
    ),
    popup=folium.GeoJsonPopup(
        fields=["nomDepartement", "nomCirconscription", "risque_infrastructurel"],
        aliases=["Département :", "Circonscription :", "Risque infrastructurel :"],
        localize=True,
        labels=True,
        style="background-color: white; font-size: 12px;"
    ),
    
).geojson

popup_compiné=folium.GeoJsonPopup(
       fields=["nomDepartement","nomCirconscription", "risque_institutionel", "risque_des_ressources", "risque_infrastructurel"],
        aliases=["Département","Circonscription :", "Risque institutionel :", "Risque des ressources :", "Risque infrastructurel:"],
        localize=True,
        labels=True,
        style="background-color: white; font-size: 12px;"
    ).add_to(cp_combiné.geojson)

popup_institutionel=folium.GeoJsonPopup(
        fields=["nomDepartement","nomCirconscription", "risque_institutionel"],
        aliases=["Département","Circonscription :", "Risque institutionel :"],
        localize=True,
        labels=True,
        style="background-color: white; font-size: 12px;").add_to(cp_institut)
popup_ressources=folium.GeoJsonPopup(
        fields=["nomDepartement","nomCirconscription",  "risque_des_ressources"],
        aliases=["Département","Circonscription :", "Risque des ressources :"],
        localize=True,
       labels=True,
        style="background-color: white; font-size: 12px;").add_to(cp_ressources)

popup_infrastructure=folium.GeoJsonPopup(
        fields=["nomDepartement","nomCirconscription", "risque_infrastructurel"],
        aliases=["Département","Circonscription :",  "Risque infrastructurel:"],
        localize=True,
        labels=True,
        style="background-color: white; font-size: 12px;"
    ).add_to(cp_infrastruture)
folium.FeatureGroup(name="Risque infrastructure", show=False).add_child(layer_infrastructure).add_to(m)
folium.FeatureGroup(name="Risque institue", show=False).add_child(layer_institu).add_to(m)
folium.FeatureGroup(name="Risque des ressources", show=False).add_child(layer_ressoures).add_to(m)

folium.GeoJson(
    data=cp_combiné.geojson.data,
    style_function=lambda x: {'weight': 1, 'color': 'transparent', 'fillOpacity': 0.7},
    highlight_function=lambda x: {'weight': 3, 'color': 'white', 'fillOpacity': 0.3},
).add_to(m)"""

"""def style_function(feature):
    return {
        "weight": 0.5,
        "color": "transparent",
        "fillOpacity": 0,
    }

def highlight_function(feature):
    return {
        "weight": 3,
        "color": "white",
        "fillOpacity": 0.3,
    }"""


"""folium.GeoJson(
        data=all_circo,
        name="combined_interactif",
        style_function=lambda f: {
            "weight": 0.8,
            "color": "transparent",
            "fillOpacity": 0
        },
        highlight_function=lambda f: {
            "weight": 3,
            "color": "white",
            "fillOpacity": 0.3
        },
        popup=popup_compiné
    ).add_to(m)
interactive_combined = folium.GeoJson(
    #geo_data=all_circo,
    data=all_circo,
    name="Risque combiné",
    columns=["codeCirconscription","risque_total"],
    key_on="feature.properties.codeCirconscription",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.8,
    line_weight=2,
    line_color="Black",
    legend_name="Risque combiné",
    style_function=lambda feature: {
        "fillOpacity": 0,  # transparent
        "color": "transparent",
        "weight": 0.5,
    },
    highlight_function=lambda feature: {
        "color": "white",
        "weight": 3,
        "fillColor": "#ffff99",
        "fillOpacity": 0.5,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["nomDepartement", "nomCirconscription", "risque_total"],
        aliases=["Département :", "Circonscription :", "Risque combiné :"],
        sticky=True,
        localize=True,
    ),
    popup=folium.GeoJsonPopup(
        fields=["nomDepartement","nomCirconscription", "risque_institutionel", 
                "risque_des_ressources", "risque_infrastructurel"],
        aliases=["Département","Circonscription :", 
                 "Risque institutionel :", "Risque des ressources :", "Risque infrastructurel :"],
        localize=True,
        labels=True,
        style="background-color: white; font-size: 12px;"
    )
)
interactive_combined.add_to(m)

interactive_institutionnel = folium.GeoJson(
    data=all_circo,
    name="Risque institutionnel (interactif)",
    style_function=lambda f: {"fillOpacity": 0, "color": "transparent", "weight": 0.5},
    highlight_function=lambda f: {"color": "white", "weight": 3, "fillColor": "#ff9999", "fillOpacity": 0.5},
    tooltip=folium.GeoJsonTooltip(
        fields=["nomDepartement", "nomCirconscription", "risque_institutionel"],
        aliases=["Département :", "Circonscription :", "Risque institutionnel :"],
        sticky=True,
        localize=True,
    ),
    popup=folium.GeoJsonPopup(
        fields=["nomDepartement","nomCirconscription","risque_institutionel"],
        aliases=["Département","Circonscription :","Risque institutionnel :"],
        localize=True,
        labels=True,
        style="background-color: white; font-size: 12px;"
    )
)
interactive_institutionnel.add_to(m)

interactive_ressources = folium.GeoJson(
    data=all_circo,
    name="Risque des ressources (interactif)",
    style_function=lambda f: {"fillOpacity": 0, "color": "transparent", "weight": 0.5},
    highlight_function=lambda f: {"color": "white", "weight": 3, "fillColor": "#99ccff", "fillOpacity": 0.5},
    tooltip=folium.GeoJsonTooltip(
        fields=["nomDepartement", "nomCirconscription", "risque_des_ressources"],
        aliases=["Département :", "Circonscription :", "Risque des ressources :"],
        sticky=True,
        localize=True,
    ),
    popup=folium.GeoJsonPopup(
        fields=["nomDepartement","nomCirconscription","risque_des_ressources"],
        aliases=["Département","Circonscription :","Risque des ressources :"],
        localize=True,
        labels=True,
        style="background-color: white; font-size: 12px;"
    )
)
interactive_ressources.add_to(m)

interactive_infra = folium.GeoJson(
    data=all_circo,
    name="Risque infrastructurel (interactif)",
    style_function=lambda f: {"fillOpacity": 0, "color": "transparent", "weight": 0.5},
    highlight_function=lambda f: {"color": "white", "weight": 3, "fillColor": "#99ff99", "fillOpacity": 0.5},
    tooltip=folium.GeoJsonTooltip(
        fields=["nomDepartement", "nomCirconscription", "risque_infrastructurel"],
        aliases=["Département :", "Circonscription :", "Risque infrastructurel :"],
        sticky=True,
        localize=True,
    ),
    popup=folium.GeoJsonPopup(
        fields=["nomDepartement","nomCirconscription","risque_infrastructurel"],
        aliases=["Département","Circonscription :","Risque infrastructurel :"],
        localize=True,
        labels=True,
        style="background-color: white; font-size: 12px;"
    )
)
interactive_infra.add_to(m)"""

def get_color_instit(value):
    if value is None:
        return "#cccccc"
    elif value < 20:
        return "#deebf7"
    elif value < 40:
        return "#9ecae1"
    elif value < 60:
        return "#6baed6"
    elif value < 80:
        return "#3182bd"
    else:
        return "#08519c"

def get_color_ress(value):
    if value is None:
        return "#cccccc"
    elif value < 20:
        return "#edf8e9"
    elif value < 40:
        return "#bae4b3"
    elif value < 60:
        return "#74c476"
    elif value < 80:
        return "#31a354"
    else:
        return "#006d2c"

def get_color_infra(value):
    if value is None:
        return "#cccccc"
    elif value < 20:
        return "#feedde"
    elif value < 40:
        return "#fdd0a2"
    elif value < 60:
        return "#fdae6b"
    elif value < 80:
        return "#fd8d3c"
    else:
        return "#e6550d"

def get_color_total(value):
    if value is None:
        return "#cccccc"
    elif value < 20:
        return "#fff7bc"
    elif value < 40:
        return "#fec44f"
    elif value < 60:
        return "#fe9929"
    elif value < 80:
        return "#d95f0e"
    else:
        return "#993404"



def make_style_function(risk_col, color_func):
    def style_function(feature):
        value = feature["properties"].get(risk_col)
        return {
            "fillColor": color_func(value),
            "color": "black",
            "weight": 0.7,
            "fillOpacity": 0.7,
        }
    return style_function

highlight_style = lambda feat: {
    "weight": 3,
    "color": "white",
    "fillOpacity": 0.8,
}



def make_layer(name, risk_col, color_func, popup_fields, popup_aliases):
    if name!="Risque combiné":
        return folium.GeoJson(
            data=all_circo.__geo_interface__,
            name=name,
            style_function=make_style_function(risk_col, color_func),
            highlight_function=highlight_style,
            show=False,
            popup=GeoJsonPopup(
                fields=popup_fields,
                aliases=popup_aliases,
                localize=True,
                labels=True,
                style="background-color: white; font-size: 12px;"
            ),
    
        )
    else:
         return folium.GeoJson(
            data=all_circo.__geo_interface__,
            name=name,
            style_function=make_style_function(risk_col, color_func),
            highlight_function=highlight_style,

            popup=folium.GeoJsonPopup(
                fields=["nomDepartement","nomCirconscription", "risque_institutionel", 
                "risque_des_ressources", "risque_infrastructurel"],
                aliases=["Département","Circonscription :", 
                 "Risque institutionel :", "Risque des ressources :", "Risque infrastructurel :"],
                localize=True,
                labels=True,
                style="background-color: white; font-size: 12px;"
            )
    
        )



layer_instit = make_layer(
    "Risque institutionnel",
    "risque_institutionel",
    get_color_instit,
    ["nomDepartement", "nomCirconscription", "risque_institutionel"],
    ["Département :", "Circonscription :", "Risque institutionnel :"]
)

layer_ress = make_layer(
    "Risque des ressources",
    "risque_des_ressources",
    get_color_ress,
    ["nomDepartement", "nomCirconscription", "risque_des_ressources"],
    ["Département :", "Circonscription :", "Risque des ressources :"]
)

layer_infra = make_layer(
    "Risque infrastructurel",
    "risque_infrastructurel",
    get_color_infra,
    ["nomDepartement", "nomCirconscription", "risque_infrastructurel"],
    ["Département :", "Circonscription :", "Risque infrastructurel :"]
)

layer_total = make_layer(
    "Risque combiné",
    "risque_total",
    get_color_total,
    ["nomDepartement", "nomCirconscription", "risque_total"],
    ["Département :", "Circonscription :", "Risque combiné :"]
)



layer_total.add_to(m)  
layer_instit.add_to(m)
layer_ress.add_to(m)
layer_infra.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

Geocoder(geocoder_options={'countrycodes': 'fr'},  
    collapsed=False,                        
    add_marker=True  ).add_to(m)


m.save("C:\\Users\\kendr\\OneDrive\\Documents\\carte_france_circonscriptions.html")

