
import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table

# Cargar datos
df = pd.read_excel(
    "Condiciones Nivel de Automatización Producto y Feature_Actualizado_Perplexity.xlsx",
    sheet_name="Condiciones Nivel de Automatiza"
)

productos_unicos = df["PRODUCT_NAME_EXT"].dropna().unique()

color_principal = '#004481'
color_secundario = '#1973B8'
color_fondo = '#F7F9FC'

app = Dash(__name__)

app.layout = html.Div(
    style={'backgroundColor': color_fondo, 'padding': '20px', 'fontFamily': 'Arial'},
    children=[
        html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}, children=[
            html.H1("Dashboard de Automatización de Productos", style={'color': color_principal}),
            html.Img(src=app.get_asset_url("BBVA_logo.png"), style={'height': '60px'}),
        ]),

        html.Div(style={'marginTop': '40px'}, children=[
            html.Label("Selecciona un Producto:", style={'color': color_principal, 'fontWeight': 'bold'}),
            dcc.Dropdown(id='dropdown_producto', options=[{'label': p, 'value': p} for p in productos_unicos], clearable=False),
        ]),

        html.Div(id='div_nivel', style={'marginTop': '40px'}, children=[
            html.Label("Selecciona el Nivel de Automatización:", style={'color': color_principal, 'fontWeight': 'bold'}),
            dcc.Dropdown(id='dropdown_nivel', clearable=False),
        ]),

        html.Div(id='descripcion_producto', style={
            'marginTop': '40px', 'padding': '15px', 'backgroundColor': '#e1efff',
            'borderLeft': f'5px solid {color_secundario}', 'fontWeight': 'bold', 'display': 'none'
        }),

        html.Div(id='div_configuracion', style={'marginTop': '40px'}, children=[
            html.Label("Selecciona una Configuración:", style={'color': color_principal, 'fontWeight': 'bold'}),
            dcc.Dropdown(id='dropdown_configuracion', clearable=False),
        ]),

        html.Div(id='div_tablas', style={'marginTop': '40px', 'display': 'none'}, children=[
            html.H3("Campos y Valores", style={'color': color_secundario}),
            dash_table.DataTable(id='tabla_campos_valores',
                                 columns=[{"name": c, "id": c} for c in ["Campo", "Valor"]],
                                 style_header={'backgroundColor': color_principal, 'color': 'white'},
                                 style_cell={'textAlign': 'left'}),

            html.Div(id='tabla_features_div', style={'marginTop': '40px'}, children=[
                html.H3("Features que provocan Nivel MANUAL", style={'color': color_secundario}),
                dash_table.DataTable(id='tabla_features',
                                     columns=[{"name": c, "id": c} for c in ["Feature Campo", "Feature Valor"]],
                                     style_header={'backgroundColor': color_principal, 'color': 'white'},
                                     style_cell={'textAlign': 'left'}),
            ])
        ])
    ]
)

@app.callback(
    Output('dropdown_nivel', 'options'),
    Output('dropdown_nivel', 'value'),
    Input('dropdown_producto', 'value')
)
def actualizar_niveles(producto):
    niveles = df[df["PRODUCT_NAME_EXT"] == producto]["NIVEL PRODUCTO"].unique()
    opciones = [{'label': n, 'value': n} for n in niveles]
    return opciones, niveles[0] if len(niveles) > 0 else None

@app.callback(
    Output('descripcion_producto', 'children'),
    Output('descripcion_producto', 'style'),
    Output('dropdown_configuracion', 'options'),
    Output('dropdown_configuracion', 'value'),
    Input('dropdown_producto', 'value'),
    Input('dropdown_nivel', 'value')
)
def actualizar_config(producto, nivel):
    niveles_posibles = df[df["PRODUCT_NAME_EXT"] == producto]["NIVEL PRODUCTO"].unique()
    descripcion = f"El producto {producto} puede alcanzar niveles: {', '.join(niveles_posibles)}."

    configs = df[(df["PRODUCT_NAME_EXT"] == producto) & (df["NIVEL PRODUCTO"] == nivel)]["MAPPINGS_LOGIC"].unique()
    opciones = [{'label': f"Configuración {i+1}", 'value': c} for i, c in enumerate(configs)]
    valor = configs[0] if len(configs) > 0 else None

    return descripcion, {'display': 'block', 'marginTop':'40px', 'padding': '15px', 'backgroundColor': '#e1efff', 'borderLeft': f'5px solid {color_secundario}'}, opciones, valor

@app.callback(
    Output('div_tablas', 'style'),
    Output('tabla_campos_valores', 'data'),
    Output('tabla_features', 'data'),
    Output('tabla_features_div', 'style'),
    Input('dropdown_configuracion', 'value'),
    Input('dropdown_nivel', 'value'),
    Input('dropdown_producto', 'value')
)
def mostrar_tablas(config, nivel, producto):
    if config and producto:
        # Filtra por configuración seleccionada
        fila = df[(df["PRODUCT_NAME_EXT"] == producto) & (df["MAPPINGS_LOGIC"] == config)].iloc[0]

        campos_valores = [{"Campo": fila[f"Campo {i}"], "Valor": fila[f"Valor {i}"]}
                          for i in range(1, 8)
                          if pd.notna(fila.get(f"Campo {i}")) and pd.notna(fila.get(f"Valor {i}"))]

        features_data, display = [], {'display': 'none'}

        # Ahora la lógica precisa para features que provocan MANUAL partiendo desde AUTO
        if nivel == "MANUAL":
            # Obtenemos las features únicas para este producto, que tienen un ID_FEATURE válido
            df_features = df[(df["PRODUCT_NAME_EXT"] == producto) & (df["NIVEL FEATURE"] == "MANUAL") & pd.notna(df["ID_FEATURE"])]

            features_unicas = set()
            features_list = []

            for _, row in df_features.iterrows():
                for i in range(1, 8):
                    campo_feature = row.get(f"Feature Campo {i}")
                    valor_feature = row.get(f"Feature Valor {i}")
                    if pd.notna(campo_feature) and pd.notna(valor_feature):
                        feature = (campo_feature, valor_feature)
                        if feature not in features_unicas:
                            features_unicas.add(feature)
                            features_list.append({"Feature Campo": campo_feature, "Feature Valor": valor_feature})

            features_data = features_list
            display = {'display': 'block'}

        return {'display': 'block'}, campos_valores, features_data, display

    return {'display': 'none'}, [], [], {'display': 'none'}


if __name__ == "__main__":
    app.run(debug=True)
