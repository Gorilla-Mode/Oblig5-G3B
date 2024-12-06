# kgcontroller module
import math
import altair as alt
alt.renderers.enable("html")
import numpy as np

from dbexcel import *
from kgmodel import *


# CRUD metoder

# Create
# pd.append, pd.concat eller df.loc[-1] = [1,2] df.index = df.index + 1 df = df.sort_index()
def insert_foresatt(f):
    # Ikke en god praksis å oppdaterer DataFrame ved enhver endring!
    # DataFrame er ikke egnet som en databasesystem for webapplikasjoner.
    # Vanligvis bruker man databaseapplikasjoner som MySql, Postgresql, sqlite3 e.l.
    # 3 fremgangsmåter for å oppdatere DataFrame:
    # (1) df.colums er [['a', 'b']]
    #     df = pd.concat([pd.DataFrame([[1,2]], columns=df.columns), df], ignore_index=True)
    # (2) df = df.append({'a': 1, 'b': 2}, ignore_index=True)
    # (3) df.loc[-1] = [1,2]
    #     df.index = df.index + 1
    #     df = df.sort_index()
    global forelder
    new_id = 0
    if forelder.empty:
        new_id = 1
    else:
        new_id = forelder['foresatt_id'].max() + 1
    
    # skriv kode for å unngå duplikater
    
    forelder = pd.concat([pd.DataFrame([[new_id,
                                        f.foresatt_navn,
                                        f.foresatt_adresse,
                                        f.foresatt_tlfnr,
                                        f.foresatt_pnr]],
                columns=forelder.columns), forelder], ignore_index=True)
    
    
    return forelder

def insert_barn(b):
    global barn
    new_id = 0
    if barn.empty:
        new_id = 1
    else:
        new_id = barn['barn_id'].max() + 1
    
    # burde også sjekke for samme foresatt_pnr for å unngå duplikater
    
    barn = pd.concat([pd.DataFrame([[new_id,
                                    b.barn_pnr]],
                columns=barn.columns), barn], ignore_index=True)
    
    return barn

def insert_soknad(s):
    """[sok_id, foresatt_1, foresatt_2, barn_1, fr_barnevern, fr_sykd_familie,
    fr_sykd_barn, fr_annet, barnehager_prioritert, sosken__i_barnehagen,
    tidspunkt_oppstart, brutto_inntekt]
    """
    global soknad
    new_id = 0
    if soknad.empty:
        new_id = 1
    else:
        new_id = soknad['sok_id'].max() + 1


    # burde også sjekke for duplikater
    
    soknad = pd.concat([pd.DataFrame([[new_id,
                                     s.foresatt_1.foresatt_id,
                                     s.foresatt_2.foresatt_id,
                                     s.barn_1.barn_id,
                                     s.fr_barnevern,
                                     s.fr_sykd_familie,
                                     s.fr_sykd_barn,
                                     s.fr_annet,
                                     s.barnehager_prioritert,
                                     s.sosken__i_barnehagen,
                                     s.tidspunkt_oppstart,
                                     s.brutto_inntekt]],
                columns=soknad.columns), soknad], ignore_index=True)
    return soknad



# ---------------------------
# Read (select)

def select_barnehage_by_id(bh_id, bo_list):
    return list(filter(lambda barnehage_objekter: barnehage_objekter.barnehage_id == bh_id, bo_list))

def select_alle_barnehager():
    """Returnerer en liste med alle barnehager definert i databasen dbexcel."""
    return barnehage.apply(lambda r: Barnehage(r['barnehage_id'],
                             r['barnehage_navn'],
                             r['barnehage_antall_plasser'],
                             r['barnehage_ledige_plasser']),
         axis=1).to_list()


def select_foresatt(f_navn):
    """OBS! Ignorerer duplikater"""
    series = forelder[forelder['foresatt_navn'] == f_navn]['foresatt_id']
    if series.empty:
        return np.nan
    else:
        return series.iloc[0] # returnerer kun det første elementet i series

def select_barn(b_pnr):
    """OBS! Ignorerer duplikater"""
    series = barn[barn['barn_pnr'] == b_pnr]['barn_id']
    if series.empty:
        return np.nan
    else:
        return series.iloc[0] # returnerer kun det første elementet i series
    

# --- Skriv kode for select_soknad her
def select_alle_soknader():
    return soknad.apply(lambda r: Soknad(
                             r['sok_id'],
                             r['foresatt_1'],
                             r['foresatt_2'],
                             r['barn_1'],
                             r['fr_barnevern'],
                             r['fr_sykd_familie'],
                             r['fr_sykd_barn'],
                             r['fr_annet'],
                             r['barnehager_prioritert'],
                             r['sosken__i_barnehagen'],
                             r['tidspunkt_oppstart'],
                             r['brutto_inntekt']),
                             axis=1).to_list()

def select_alle_barn():
    return barn.apply(lambda r: Barn(
                             r['barn_id'],
                             r['barn_pnr']),
                             axis=1).to_list()

def select_alle_foresatt():
    return forelder.apply(lambda r: Foresatt(
                             r['foresatt_id'],
                             r['foresatt_navn'],
                             r['foresatt_adresse'],
                             r['foresatt_tlfnr'],
                             r['foresatt_pnr']),
                             axis=1).to_list()

# Importerer data
data = pd.read_excel("ssb-barnehager-2015-2023-alder-1-2-aar.xlsm",
                       sheet_name="KOSandel120000", header=3,
                       names=['kom','y15','y16','y17','y18','y19','y20','y21','y22','y23'],
                       na_values=['.', '..']
                     )
df = pd.DataFrame(data)  # dataframe
df.drop(range(724, 780), inplace = True)  # Fjerner irrelvante rader
df.drop_duplicates(inplace = True)  # Fjerner potensielle duplikaer

#fra janis, endrer navn på strings ved index[0][0], der strings strings mellom første og andre mellomrom beholdes
for coln in ['kom']:
    df[coln] = df[coln].str.split(" ").apply(lambda x: x[1] if len(x) > 1 else "")

#fra Janis, fjerner prosenter over 100
for coln in ['y15','y16','y17','y18','y19','y20','y21','y22','y23']:
    mask_over_100 = (df[coln] > 100)
    df.loc[mask_over_100, coln] = float("nan")

dflist = df.values.tolist()
"""print(ta.tabulate(dflist))"""

cleaned_list = []  # Tom liste der nan verdier bytter med korrespoderene verdier

# Sjekker om elementer allerede er renset
def search_clean_list_exist(search_string):
    for i in range(len(cleaned_list)):
        if search_string in cleaned_list[i][0]:
            return True
    return False

# Funksjonen henter den første mathcen til søket
def extract_match(dataframe):
    """
    list.append(element) -> list:
    range(start, stop, step)
    len(list, string) -> integer
    math.isnan(x) -> Boolean
    """
    for j in range(len(dataframe)):
        if not j <= i:
            if search_key == dataframe[j][0]:
                second_list.append(dataframe[j])

# Legger inn andre mulige duplikate kommunene navn og legger verdiene inn instedenfor nan
for i in range(len(dflist)):
    first_list = dflist[i]
    if not search_clean_list_exist(first_list[0]):
        search_key = first_list[0]
        second_list = []
        clean_row =[]
        extract_match(dflist)
        for k in range(len(first_list)):
            if k == 0:
                clean_row.append(first_list[k])
            else:
                if math.isnan(first_list[k]):
                    if not second_list == []:
                        for j in range(len(second_list)):
                            if not math.isnan(second_list[j][k]):
                                clean_row.append(second_list[j][k])
                                break
                            if j == len(second_list):
                                clean_row.append(None)
                    else:
                        clean_row.append(None)
                else:
                    clean_row.append(first_list[k])
        cleaned_list.append(clean_row)

cleaned_table = pd.DataFrame(cleaned_list, columns = ['kom','y15','y16','y17','y18','y19','y20','y21','y22','y23'])
final_list = cleaned_table.values.tolist() #liste versjon av dataframe, enklere for noen funskjoner

# y23 is index 9
#lager en liste med alle verdiene i en kolonne basert på valgt index i datafram
def make_column_list(table, index: int):
    """
    list.append(element) -> list:
    range(start, stop, step)
    len(list, string) -> integer
    """
    column_list = []
    for i in range(len(table)):
        column_list.append(table[i][index])
    return column_list


# lager et linje diagram med verdiene over årene for en kommune spesifisert av bruker, kjøres kun for å generere PNG
def get_diagram_by_name(dataframe):
    """
    input(prompt) -> String
    range(start, stop, step)
    len(list, string) -> integer
    list.index(element) -> integer
    df.values.tolist(dataframe) -> list
    property DataFrame.loc
    class altair.Chart(data=Undefined, encoding=Undefined, mark=Undefined, width=Undefined, height=Undefined, **kwargs)
    chart.save('chart.html') -> html
    """
    municipality_list = make_column_list(final_list, 0)
    print(f"Kommuner:")
    for i in range(len(municipality_list)):
        municipality_index = municipality_list.index(municipality_list[i])
        municipality_row = dataframe.loc[municipality_index]
        municipality_list_dataframe = municipality_row.values.tolist()
        df = pd.DataFrame({
            'year': ['y15','y16','y17','y18','y19', 'y20', 'y21', 'y22', 'y23'],
            'values': municipality_list_dataframe[1:]})
        chart = (alt.Chart(df).mark_line().encode
                 (x='year', y=alt.Y('values', scale = alt.Scale(type='linear', domain=[65,100]))))
        chart.save(f"E:/_Skole/_UIA/IT/IS-114/Git/Oblig5-privat/barnehage/static/charts/{municipality_list[i].lower()}.png")
        print(f"chart for {municipality_list[i]} is saved")
"""get_diagram_by_name(cleaned_table"""




# ------------------
# Update


# ------------------
# Delete


# ----- Persistent lagring ------
def commit_all():
    """Skriver alle dataframes til excel"""
    with pd.ExcelWriter('kgdata.xlsx', mode='a', if_sheet_exists='replace') as writer:  
        forelder.to_excel(writer, sheet_name='foresatt')
        barnehage.to_excel(writer, sheet_name='barnehage')
        barn.to_excel(writer, sheet_name='barn')
        soknad.to_excel(writer, sheet_name='soknad')
        
# --- Diverse hjelpefunksjoner ---
def form_to_object_soknad(sd):
    """sd - formdata for soknad, type: ImmutableMultiDict fra werkzeug.datastructures
Eksempel:
ImmutableMultiDict([('navn_forelder_1', 'asdf'),
('navn_forelder_2', ''),
('adresse_forelder_1', 'adf'),
('adresse_forelder_2', 'adf'),
('tlf_nr_forelder_1', 'asdfsaf'),
('tlf_nr_forelder_2', ''),
('personnummer_forelder_1', ''),
('personnummer_forelder_2', ''),
('personnummer_barnet_1', '234341334'),
('personnummer_barnet_2', ''),
('fortrinnsrett_barnevern', 'on'),
('fortrinnsrett_sykdom_i_familien', 'on'),
('fortrinnsrett_sykdome_paa_barnet', 'on'),
('fortrinssrett_annet', ''),
('liste_over_barnehager_prioritert_5', ''),
('tidspunkt_for_oppstart', ''),
('brutto_inntekt_husholdning', '')])
    """
    # Lagring i hurtigminne av informasjon om foreldrene (OBS! takler ikke flere foresatte)
    foresatt_1 = Foresatt(0,
                          sd.get('navn_forelder_1'),
                          sd.get('adresse_forelder_1'),
                          sd.get('tlf_nr_forelder_1'),
                          sd.get('personnummer_forelder_1'))
    insert_foresatt(foresatt_1)
    foresatt_2 = Foresatt(0,
                          sd.get('navn_forelder_2'),
                          sd.get('adresse_forelder_2'),
                          sd.get('tlf_nr_forelder_2'),
                          sd.get('personnummer_forelder_2'))
    insert_foresatt(foresatt_2) 
    
    # Dette er ikke elegang; kunne returnert den nye id-en fra insert_ metodene?
    foresatt_1.foresatt_id = select_foresatt(sd.get('navn_forelder_1'))
    foresatt_2.foresatt_id = select_foresatt(sd.get('navn_forelder_2'))
    
    # Lagring i hurtigminne av informasjon om barn (OBS! kun ett barn blir lagret)
    barn_1 = Barn(0, sd.get('personnummer_barnet_1'))
    insert_barn(barn_1)
    barn_1.barn_id = select_barn(sd.get('personnummer_barnet_1'))
    
    # Lagring i hurtigminne av all informasjon for en søknad (OBS! ingen feilsjekk / alternativer)
        
    sok_1 = Soknad(0,
                   foresatt_1,
                   foresatt_2,
                   barn_1,
                   sd.get('fortrinnsrett_barnevern'),
                   sd.get('fortrinnsrett_sykdom_i_familien'),
                   sd.get('fortrinnsrett_sykdome_paa_barnet'),
                   sd.get('fortrinssrett_annet'),
                   sd.get('liste_over_barnehager_prioritert_5'),
                   sd.get('har_sosken_som_gaar_i_barnehagen'),
                   sd.get('tidspunkt_for_oppstart'),
                   sd.get('brutto_inntekt_husholdning'))
    
    return sok_1

# Testing
def test_df_to_object_list():
    assert barnehage.apply(lambda r: Barnehage(r['barnehage_id'],
                             r['barnehage_navn'],
                             r['barnehage_antall_plasser'],
                             r['barnehage_ledige_plasser']),
         axis=1).to_list()[0].barnehage_navn == "Sunshine Preschool"
