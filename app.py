# =============================================================================
# 📊 NOMAD SWING TRADE PRO — Streamlit App
# =============================================================================
# Arquivo: app.py
# Deploy: Streamlit Cloud (github.com)
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pytz
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nomad Swing Trade Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stMetric { background: #1e2130; border-radius: 8px; padding: 0.5rem; }
    .header-box {
        background: linear-gradient(135deg, #1a237e, #283593);
        padding: 1.5rem 2rem; border-radius: 10px; margin-bottom: 1rem;
    }
    .header-box h1 { color: white; margin: 0; font-size: 1.6rem; }
    .header-box p  { color: rgba(255,255,255,0.8); margin: 0.3rem 0 0 0; }
    .stDataFrame { border-radius: 8px; }
    div[data-testid="metric-container"] {
        background-color: #1e2130;
        border: 1px solid #2d3250;
        padding: 0.6rem 1rem;
        border-radius: 8px;
    }
    .badge-muito-alta { background:#2e7d32; color:white; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:0.75rem; }
    .badge-alta       { background:#558b2f; color:white; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:0.75rem; }
    .badge-media      { background:#f57f17; color:white; padding:2px 8px; border-radius:4px; font-size:0.75rem; }
    .badge-baixa      { background:#546e7a; color:white; padding:2px 8px; border-radius:4px; font-size:0.75rem; }
    .warning-box {
        background:#fff3e0; border-left:4px solid #ff9800;
        padding:0.8rem 1rem; border-radius:4px; margin:0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# DICIONÁRIO DE AÇÕES NOMAD (~992 tickers)
# =============================================================================
NOMAD_STOCKS = {

    # ══════════════════════════════════════════════════════════════════════════
    # TECNOLOGIA — As 7 Magníficas + Hardware + Infraestrutura
    # ══════════════════════════════════════════════════════════════════════════
    'AAPL':  ('Apple Inc.',                         'Tecnologia'),
    'MSFT':  ('Microsoft Corp.',                    'Tecnologia'),
    'GOOGL': ('Alphabet Inc. (A)',                  'Tecnologia'),
    'GOOG':  ('Alphabet Inc. (C)',                  'Tecnologia'),
    'AMZN':  ('Amazon.com Inc.',                    'Tecnologia'),
    'META':  ('Meta Platforms Inc.',                'Tecnologia'),
    'NVDA':  ('NVIDIA Corp.',                       'Tecnologia'),
    'IBM':   ('IBM Corp.',                          'Tecnologia'),
    'CSCO':  ('Cisco Systems',                      'Tecnologia'),
    'HPQ':   ('HP Inc.',                            'Tecnologia'),
    'HPE':   ('Hewlett Packard Enterprise',         'Tecnologia'),
    'DELL':  ('Dell Technologies',                  'Tecnologia'),
    'STX':   ('Seagate Technology',                 'Tecnologia'),
    'WDC':   ('Western Digital',                    'Tecnologia'),
    'PSTG':  ('Pure Storage Inc.',                  'Tecnologia'),
    'NTAP':  ('NetApp Inc.',                        'Tecnologia'),
    'FFIV':  ('F5 Inc.',                            'Tecnologia'),
    'CDW':   ('CDW Corp.',                          'Tecnologia'),
    'ZBRA':  ('Zebra Technologies',                 'Tecnologia'),
    'TRMB':  ('Trimble Inc.',                       'Tecnologia'),
    'EPAM':  ('EPAM Systems',                       'Tecnologia'),
    'GDDY':  ('GoDaddy Inc.',                       'Tecnologia'),

    # ══════════════════════════════════════════════════════════════════════════
    # SEMICONDUTORES
    # ══════════════════════════════════════════════════════════════════════════
    'AMD':   ('Advanced Micro Devices',             'Semicondutores'),
    'INTC':  ('Intel Corp.',                        'Semicondutores'),
    'AVGO':  ('Broadcom Inc.',                      'Semicondutores'),
    'QCOM':  ('Qualcomm Inc.',                      'Semicondutores'),
    'TXN':   ('Texas Instruments',                  'Semicondutores'),
    'ASML':  ('ASML Holding ADR',                   'Semicondutores'),
    'TSM':   ('Taiwan Semiconductor ADR',           'Semicondutores'),
    'LRCX':  ('Lam Research Corp.',                 'Semicondutores'),
    'KLAC':  ('KLA Corp.',                          'Semicondutores'),
    'AMAT':  ('Applied Materials',                  'Semicondutores'),
    'MRVL':  ('Marvell Technology',                 'Semicondutores'),
    'MU':    ('Micron Technology',                  'Semicondutores'),
    'SMCI':  ('Super Micro Computer',               'Semicondutores'),
    'ARM':   ('ARM Holdings ADR',                   'Semicondutores'),
    'ON':    ('ON Semiconductor',                   'Semicondutores'),
    'SWKS':  ('Skyworks Solutions',                 'Semicondutores'),
    'QRVO':  ('Qorvo Inc.',                         'Semicondutores'),
    'MPWR':  ('Monolithic Power Systems',           'Semicondutores'),
    'WOLF':  ('Wolfspeed Inc.',                     'Semicondutores'),
    'FORM':  ('FormFactor Inc.',                    'Semicondutores'),
    'ACLS':  ('Axcelis Technologies',               'Semicondutores'),
    'COHU':  ('Cohu Inc.',                          'Semicondutores'),
    'ONTO':  ('Onto Innovation',                    'Semicondutores'),
    'UCTT':  ('Ultra Clean Holdings',               'Semicondutores'),

    # ══════════════════════════════════════════════════════════════════════════
    # SOFTWARE / SaaS / NUVEM
    # ══════════════════════════════════════════════════════════════════════════
    'ADBE':  ('Adobe Inc.',                         'Software'),
    'CRM':   ('Salesforce Inc.',                    'Software'),
    'ORCL':  ('Oracle Corp.',                       'Software'),
    'NOW':   ('ServiceNow Inc.',                    'Software'),
    'WDAY':  ('Workday Inc.',                       'Software'),
    'VEEV':  ('Veeva Systems',                      'Software'),
    'HUBS':  ('HubSpot Inc.',                       'Software'),
    'ZM':    ('Zoom Video Comm.',                   'Software'),
    'DDOG':  ('Datadog Inc.',                       'Software'),
    'SNOW':  ('Snowflake Inc.',                     'Software'),
    'MDB':   ('MongoDB Inc.',                       'Software'),
    'ESTC':  ('Elastic NV',                         'Software'),
    'TWLO':  ('Twilio Inc.',                        'Software'),
    'OKTA':  ('Okta Inc.',                          'Software'),
    'ZS':    ('Zscaler Inc.',                       'Software'),
    'CRWD':  ('CrowdStrike Holdings',               'Software'),
    'NET':   ('Cloudflare Inc.',                    'Software'),
    'PATH':  ('UiPath Inc.',                        'Software'),
    'DOCN':  ('DigitalOcean Holdings',              'Software'),
    'BOX':   ('Box Inc.',                           'Software'),
    'GTLB':  ('GitLab Inc.',                        'Software'),
    'BILL':  ('BILL Holdings',                      'Software'),
    'PEGA':  ('Pegasystems Inc.',                   'Software'),
    'APPN':  ('Appian Corp.',                       'Software'),
    'BSY':   ('Bentley Systems',                    'Software'),
    'PCTY':  ('Paylocity Holding',                  'Software'),
    'PAYC':  ('Paycom Software',                    'Software'),
    'PAYX':  ('Paychex Inc.',                       'Software'),
    'ADP':   ('Automatic Data Processing',          'Software'),
    'CDNS':  ('Cadence Design Systems',             'Software'),
    'SNPS':  ('Synopsys Inc.',                      'Software'),
    'PTC':   ('PTC Inc.',                           'Software'),
    'MANH':  ('Manhattan Associates',               'Software'),
    'GWRE':  ('Guidewire Software',                 'Software'),
    'NCNO':  ('nCino Inc.',                         'Software'),
    'CFLT':  ('Confluent Inc.',                     'Software'),
    'SPT':   ('Sprout Social',                      'Software'),
    'BRZE':  ('Braze Inc.',                         'Software'),
    'AMPL':  ('Amplitude Inc.',                     'Software'),
    'TOST':  ('Toast Inc.',                         'Software'),
    'TASK':  ('TaskUs Inc.',                        'Software'),
    'KVYO':  ('Klaviyo Inc.',                       'Software'),
    'RNG':   ('RingCentral Inc.',                   'Software'),
    'FIVN':  ('Five9 Inc.',                         'Software'),
    'NICE':  ('NICE Ltd. ADR',                      'Software'),
    'ALRM':  ('Alarm.com Holdings',                 'Software'),
    'ASAN':  ('Asana Inc.',                         'Software'),

    # ══════════════════════════════════════════════════════════════════════════
    # IA / DADOS / ROBÓTICA
    # ══════════════════════════════════════════════════════════════════════════
    'PLTR':  ('Palantir Technologies',              'IA & Dados'),
    'AI':    ('C3.ai Inc.',                         'IA & Dados'),
    'SOUN':  ('SoundHound AI',                      'IA & Dados'),
    'BBAI':  ('BigBear.ai Holdings',                'IA & Dados'),
    'IONQ':  ('IonQ Inc.',                          'IA & Dados'),
    'QBTS':  ('D-Wave Quantum',                     'IA & Dados'),
    'RGTI':  ('Rigetti Computing',                  'IA & Dados'),
    'ISRG':  ('Intuitive Surgical',                 'IA & Dados'),
    'TNDM':  ('Tandem Diabetes Care',               'IA & Dados'),
    'ACMR':  ('ACM Research',                       'IA & Dados'),

    # ══════════════════════════════════════════════════════════════════════════
    # CIBERSEGURANÇA
    # ══════════════════════════════════════════════════════════════════════════
    'PANW':  ('Palo Alto Networks',                 'Cibersegurança'),
    'FTNT':  ('Fortinet Inc.',                      'Cibersegurança'),
    'S':     ('SentinelOne Inc.',                   'Cibersegurança'),
    'TENB':  ('Tenable Holdings',                   'Cibersegurança'),
    'RPD':   ('Rapid7 Inc.',                        'Cibersegurança'),
    'VRNS':  ('Varonis Systems',                    'Cibersegurança'),
    'QLYS':  ('Qualys Inc.',                        'Cibersegurança'),
    'CHKP':  ('Check Point Software ADR',           'Cibersegurança'),
    'CYBR':  ('CyberArk Software ADR',              'Cibersegurança'),

    # ══════════════════════════════════════════════════════════════════════════
    # E-COMMERCE / PLATAFORMAS DIGITAIS
    # ══════════════════════════════════════════════════════════════════════════
    'SHOP':  ('Shopify Inc.',                       'E-commerce'),
    'MELI':  ('MercadoLibre Inc.',                  'E-commerce'),
    'BABA':  ('Alibaba Group ADR',                  'E-commerce'),
    'JD':    ('JD.com ADR',                         'E-commerce'),
    'PDD':   ('PDD Holdings ADR',                   'E-commerce'),
    'BIDU':  ('Baidu Inc. ADR',                     'E-commerce'),
    'EBAY':  ('eBay Inc.',                          'E-commerce'),
    'ETSY':  ('Etsy Inc.',                          'E-commerce'),
    'W':     ('Wayfair Inc.',                       'E-commerce'),
    'CHWY':  ('Chewy Inc.',                         'E-commerce'),
    'REAL':  ('RealReal Inc.',                      'E-commerce'),

    # ══════════════════════════════════════════════════════════════════════════
    # MOBILIDADE / ENTREGAS / VIAGENS
    # ══════════════════════════════════════════════════════════════════════════
    'UBER':  ('Uber Technologies',                  'Mobilidade'),
    'LYFT':  ('Lyft Inc.',                          'Mobilidade'),
    'ABNB':  ('Airbnb Inc.',                        'Mobilidade'),
    'DASH':  ('DoorDash Inc.',                      'Mobilidade'),
    'GRAB':  ('Grab Holdings',                      'Mobilidade'),
    'DKNG':  ('DraftKings Inc.',                    'Mobilidade'),
    'BKNG':  ('Booking Holdings',                   'Mobilidade'),
    'EXPE':  ('Expedia Group',                      'Mobilidade'),
    'MAR':   ('Marriott International',             'Mobilidade'),
    'HLT':   ('Hilton Worldwide',                   'Mobilidade'),
    'H':     ('Hyatt Hotels Corp.',                 'Mobilidade'),
    'CCL':   ('Carnival Corp.',                     'Mobilidade'),
    'RCL':   ('Royal Caribbean Group',              'Mobilidade'),
    'NCLH':  ('Norwegian Cruise Line',              'Mobilidade'),
    'AAL':   ('American Airlines',                  'Mobilidade'),
    'DAL':   ('Delta Air Lines',                    'Mobilidade'),
    'UAL':   ('United Airlines',                    'Mobilidade'),
    'LUV':   ('Southwest Airlines',                 'Mobilidade'),
    'ALK':   ('Alaska Air Group',                   'Mobilidade'),

    # ══════════════════════════════════════════════════════════════════════════
    # STREAMING / ENTRETENIMENTO / MÍDIA
    # ══════════════════════════════════════════════════════════════════════════
    'NFLX':  ('Netflix Inc.',                       'Entretenimento'),
    'DIS':   ('Walt Disney Co.',                    'Entretenimento'),
    'WBD':   ('Warner Bros. Discovery',             'Entretenimento'),
    'SPOT':  ('Spotify Technology',                 'Entretenimento'),
    'RBLX':  ('Roblox Corp.',                       'Entretenimento'),
    'U':     ('Unity Software',                     'Entretenimento'),
    'TTWO':  ('Take-Two Interactive',               'Entretenimento'),
    'EA':    ('Electronic Arts',                    'Entretenimento'),
    'NTES':  ('NetEase ADR',                        'Entretenimento'),
    'BILI':  ('Bilibili Inc. ADR',                  'Entretenimento'),
    'IMAX':  ('IMAX Corp.',                         'Entretenimento'),
    'FOXA':  ('Fox Corp. A',                        'Entretenimento'),
    'NWSA':  ('News Corp. A',                       'Entretenimento'),
    'NYT':   ('New York Times Co.',                 'Entretenimento'),
    'PINS':  ('Pinterest Inc.',                     'Entretenimento'),
    'SNAP':  ('Snap Inc.',                          'Entretenimento'),
    'RDDT':  ('Reddit Inc.',                        'Entretenimento'),
    'BMBL':  ('Bumble Inc.',                        'Entretenimento'),
    'MTCH':  ('Match Group',                        'Entretenimento'),

    # ══════════════════════════════════════════════════════════════════════════
    # FINTECH / PAGAMENTOS / CRIPTO
    # ══════════════════════════════════════════════════════════════════════════
    'V':     ('Visa Inc.',                          'Fintech'),
    'MA':    ('Mastercard Inc.',                    'Fintech'),
    'AXP':   ('American Express',                   'Fintech'),
    'PYPL':  ('PayPal Holdings',                    'Fintech'),
    'AFRM':  ('Affirm Holdings',                    'Fintech'),
    'UPST':  ('Upstart Holdings',                   'Fintech'),
    'SOFI':  ('SoFi Technologies',                  'Fintech'),
    'COIN':  ('Coinbase Global',                    'Fintech'),
    'HOOD':  ('Robinhood Markets',                  'Fintech'),
    'NU':    ('Nu Holdings (Nubank)',                'Fintech'),
    'PAGS':  ('PagSeguro Digital',                  'Fintech'),
    'STNE':  ('StoneCo Ltd.',                       'Fintech'),
    'INTR':  ('Inter & Co.',                        'Fintech'),
    'GPN':   ('Global Payments Inc.',               'Fintech'),
    'FIS':   ('Fidelity National Info Services',    'Fintech'),
    'FISV':  ('Fiserv Inc.',                        'Fintech'),
    'DLO':   ('dLocal Ltd.',                        'Fintech'),
    'MSTR':  ('MicroStrategy Inc.',                 'Fintech'),
    'CRCL':  ('Circle Internet Group',              'Fintech'),
    'FLUT':  ('Flutter Entertainment',              'Fintech'),
    'LPX':   ('Louisiana-Pacific Corp.',            'Fintech'),
    'WEX':   ('WEX Inc.',                           'Fintech'),
    'FOUR':  ('Shift4 Payments',                    'Fintech'),
    'PRAX':  ('Praxis Precision Medicine',          'Fintech'),
    'RELY':  ('Remitly Global',                     'Fintech'),
    'FLYW':  ('Flywire Corp.',                      'Fintech'),
    'XP':    ('XP Inc.',                            'Fintech'),

    # ══════════════════════════════════════════════════════════════════════════
    # BANCOS / SERVIÇOS FINANCEIROS / SEGUROS
    # ══════════════════════════════════════════════════════════════════════════
    'JPM':   ('JPMorgan Chase',                     'Bancos'),
    'BAC':   ('Bank of America',                    'Bancos'),
    'GS':    ('Goldman Sachs',                      'Bancos'),
    'MS':    ('Morgan Stanley',                     'Bancos'),
    'WFC':   ('Wells Fargo',                        'Bancos'),
    'C':     ('Citigroup Inc.',                     'Bancos'),
    'BLK':   ('BlackRock Inc.',                     'Bancos'),
    'SCHW':  ('Charles Schwab',                     'Bancos'),
    'COF':   ('Capital One Financial',              'Bancos'),
    'BRK-B': ('Berkshire Hathaway B',               'Bancos'),
    'IBKR':  ('Interactive Brokers',                'Bancos'),
    'USB':   ('U.S. Bancorp',                       'Bancos'),
    'PNC':   ('PNC Financial Services',             'Bancos'),
    'TFC':   ('Truist Financial',                   'Bancos'),
    'MTB':   ('M&T Bank Corp.',                     'Bancos'),
    'RF':    ('Regions Financial',                  'Bancos'),
    'CFG':   ('Citizens Financial Group',           'Bancos'),
    'FITB':  ('Fifth Third Bancorp',                'Bancos'),
    'KEY':   ('KeyCorp',                            'Bancos'),
    'HBAN':  ('Huntington Bancshares',              'Bancos'),
    'WBS':   ('Webster Financial',                  'Bancos'),
    'ALLY':  ('Ally Financial',                     'Bancos'),
    'SYF':   ('Synchrony Financial',                'Bancos'),
    'AIG':   ('American International Group',       'Bancos'),
    'MET':   ('MetLife Inc.',                       'Bancos'),
    'PRU':   ('Prudential Financial',               'Bancos'),
    'AFL':   ('Aflac Inc.',                         'Bancos'),
    'PGR':   ('Progressive Corp.',                  'Bancos'),
    'ALL':   ('Allstate Corp.',                     'Bancos'),
    'TRV':   ('Travelers Companies',                'Bancos'),
    'CB':    ('Chubb Ltd.',                         'Bancos'),
    'HIG':   ('Hartford Financial Services',        'Bancos'),
    'MMC':   ('Marsh & McLennan',                   'Bancos'),
    'AON':   ('Aon PLC',                            'Bancos'),
    'AJG':   ('Arthur J. Gallagher',                'Bancos'),
    'ITUB':  ('Itaú Unibanco ADR',                  'Bancos'),
    'BBD':   ('Bradesco ADR',                       'Bancos'),
    'SAN':   ('Banco Santander ADR',                'Bancos'),
    'DB':    ('Deutsche Bank ADR',                  'Bancos'),
    'HSBC':  ('HSBC Holdings ADR',                  'Bancos'),
    'UBS':   ('UBS Group ADR',                      'Bancos'),
    'ING':   ('ING Groep ADR',                      'Bancos'),

    # ══════════════════════════════════════════════════════════════════════════
    # SAÚDE / FARMACÊUTICO / EQUIPAMENTOS MÉDICOS
    # ══════════════════════════════════════════════════════════════════════════
    'JNJ':   ('Johnson & Johnson',                  'Saúde'),
    'UNH':   ('UnitedHealth Group',                 'Saúde'),
    'PFE':   ('Pfizer Inc.',                        'Saúde'),
    'MRNA':  ('Moderna Inc.',                       'Saúde'),
    'ABBV':  ('AbbVie Inc.',                        'Saúde'),
    'LLY':   ('Eli Lilly & Co.',                    'Saúde'),
    'MRK':   ('Merck & Co.',                        'Saúde'),
    'BMY':   ('Bristol-Myers Squibb',               'Saúde'),
    'AMGN':  ('Amgen Inc.',                         'Saúde'),
    'BIIB':  ('Biogen Inc.',                        'Saúde'),
    'REGN':  ('Regeneron Pharmaceuticals',          'Saúde'),
    'GILD':  ('Gilead Sciences',                    'Saúde'),
    'ABT':   ('Abbott Laboratories',                'Saúde'),
    'MDT':   ('Medtronic PLC',                      'Saúde'),
    'TMO':   ('Thermo Fisher Scientific',           'Saúde'),
    'DHR':   ('Danaher Corp.',                      'Saúde'),
    'ELV':   ('Elevance Health',                    'Saúde'),
    'CVS':   ('CVS Health Corp.',                   'Saúde'),
    'HCA':   ('HCA Healthcare',                     'Saúde'),
    'DXCM':  ('DexCom Inc.',                        'Saúde'),
    'PODD':  ('Insulet Corp.',                      'Saúde'),
    'INCY':  ('Incyte Corp.',                       'Saúde'),
    'BAX':   ('Baxter International',               'Saúde'),
    'BSX':   ('Boston Scientific',                  'Saúde'),
    'EW':    ('Edwards Lifesciences',               'Saúde'),
    'SYK':   ('Stryker Corp.',                      'Saúde'),
    'ZBH':   ('Zimmer Biomet Holdings',             'Saúde'),
    'BDX':   ('Becton Dickinson',                   'Saúde'),
    'IQV':   ('IQVIA Holdings',                     'Saúde'),
    'A':     ('Agilent Technologies',               'Saúde'),
    'WAT':   ('Waters Corp.',                       'Saúde'),
    'MTD':   ('Mettler-Toledo International',       'Saúde'),
    'TECH':  ('Bio-Techne Corp.',                   'Saúde'),
    'HOLX':  ('Hologic Inc.',                       'Saúde'),
    'ALGN':  ('Align Technology',                   'Saúde'),
    'HSIC':  ('Henry Schein Inc.',                  'Saúde'),
    'VTRS':  ('Viatris Inc.',                       'Saúde'),
    'JAZZ':  ('Jazz Pharmaceuticals',               'Saúde'),
    'ILMN':  ('Illumina Inc.',                      'Saúde'),
    'IDXX':  ('IDEXX Laboratories',                 'Saúde'),
    'MOH':   ('Molina Healthcare',                  'Saúde'),
    'CNC':   ('Centene Corp.',                      'Saúde'),
    'HUM':   ('Humana Inc.',                        'Saúde'),
    'CI':    ('Cigna Group',                        'Saúde'),
    'DVA':   ('DaVita Inc.',                        'Saúde'),
    'ACAD':  ('Acadia Healthcare',                  'Saúde'),
    'ENSG':  ('The Ensign Group',                   'Saúde'),

    # ══════════════════════════════════════════════════════════════════════════
    # BIOTECNOLOGIA
    # ══════════════════════════════════════════════════════════════════════════
    'VRTX':  ('Vertex Pharmaceuticals',             'Biotech'),
    'MRVI':  ('Maravai LifeSciences',               'Biotech'),
    'CRSP':  ('CRISPR Therapeutics',                'Biotech'),
    'BEAM':  ('Beam Therapeutics',                  'Biotech'),
    'NTLA':  ('Intellia Therapeutics',              'Biotech'),
    'EDIT':  ('Editas Medicine',                    'Biotech'),
    'RXRX':  ('Recursion Pharmaceuticals',          'Biotech'),
    'EXAS':  ('Exact Sciences',                     'Biotech'),
    'FATE':  ('Fate Therapeutics',                  'Biotech'),
    'RVMD':  ('Revolution Medicines',               'Biotech'),
    'FOLD':  ('Amicus Therapeutics',                'Biotech'),
    'RARE':  ('Ultragenyx Pharmaceutical',          'Biotech'),
    'ALNY':  ('Alnylam Pharmaceuticals',            'Biotech'),
    'BMRN':  ('BioMarin Pharmaceutical',            'Biotech'),
    'RCKT':  ('Rocket Pharmaceuticals',             'Biotech'),
    'ARWR':  ('Arrowhead Pharmaceuticals',          'Biotech'),
    'PTGX':  ('Protagonist Therapeutics',           'Biotech'),
    'DNLI':  ('Denali Therapeutics',                'Biotech'),
    'IMVT':  ('Immunovant Inc.',                    'Biotech'),
    'HALO':  ('Halozyme Therapeutics',              'Biotech'),
    'NKTR':  ('Nektar Therapeutics',                'Biotech'),
    'NVAX':  ('Novavax Inc.',                       'Biotech'),
    'SAVA':  ('Cassava Sciences',                   'Biotech'),

    # ══════════════════════════════════════════════════════════════════════════
    # VAREJO / CONSUMO CÍCLICO / RESTAURANTES
    # ══════════════════════════════════════════════════════════════════════════
    'TSLA':  ('Tesla Inc.',                         'Consumo Cíclico'),
    'WMT':   ('Walmart Inc.',                       'Varejo'),
    'COST':  ('Costco Wholesale',                   'Varejo'),
    'TGT':   ('Target Corp.',                       'Varejo'),
    'HD':    ('Home Depot Inc.',                    'Varejo'),
    'LOW':   ("Lowe's Companies",                   'Varejo'),
    'NKE':   ('Nike Inc.',                          'Varejo'),
    'SBUX':  ('Starbucks Corp.',                    'Varejo'),
    'MCD':   ("McDonald's Corp.",                   'Varejo'),
    'CMG':   ('Chipotle Mexican Grill',             'Varejo'),
    'YUM':   ('Yum! Brands',                        'Varejo'),
    'QSR':   ('Restaurant Brands International',    'Varejo'),
    'DPZ':   ("Domino's Pizza",                     'Varejo'),
    'DNUT':  ('Krispy Kreme Inc.',                  'Varejo'),
    'LULU':  ('Lululemon Athletica',                'Varejo'),
    'ROST':  ('Ross Stores',                        'Varejo'),
    'TJX':   ('TJX Companies',                     'Varejo'),
    'DG':    ('Dollar General Corp.',               'Varejo'),
    'DLTR':  ('Dollar Tree Inc.',                   'Varejo'),
    'BBY':   ('Best Buy Co.',                       'Varejo'),
    'ANF':   ('Abercrombie & Fitch',                'Varejo'),
    'AEO':   ('American Eagle Outfitters',          'Varejo'),
    'URBN':  ('Urban Outfitters',                   'Varejo'),
    'PVH':   ('PVH Corp.',                          'Varejo'),
    'RL':    ('Ralph Lauren Corp.',                 'Varejo'),
    'TPR':   ('Tapestry Inc.',                      'Varejo'),
    'CPRI':  ('Capri Holdings',                     'Varejo'),
    'CROX':  ('Crocs Inc.',                         'Varejo'),
    'ONON':  ('On Holding AG ADR',                  'Varejo'),
    'SFM':   ('Sprouts Farmers Market',             'Varejo'),
    'KR':    ('Kroger Co.',                         'Varejo'),
    'ACI':   ('Albertsons Companies',               'Varejo'),
    'SYY':   ('Sysco Corp.',                        'Varejo'),
    'PFGC':  ('Performance Food Group',             'Varejo'),
    'ARMK':  ('Aramark Holdings',                   'Varejo'),
    'EAT':   ('Brinker International',              'Varejo'),
    'TXRH':  ('Texas Roadhouse',                    'Varejo'),
    'SHAK':  ('Shake Shack Inc.',                   'Varejo'),
    'WING':  ('Wingstop Inc.',                      'Varejo'),
    'PLAY':  ("Dave & Buster's",                    'Varejo'),
    'HOG':   ('Harley-Davidson Inc.',               'Varejo'),
    'POOL':  ('Pool Corp.',                         'Varejo'),
    'ORLY':  ("O'Reilly Automotive",                'Varejo'),
    'AZO':   ('AutoZone Inc.',                      'Varejo'),
    'AAP':   ('Advance Auto Parts',                 'Varejo'),
    'CVNA':  ('Carvana Co.',                        'Varejo'),
    'KMX':   ('CarMax Inc.',                        'Varejo'),

    # ══════════════════════════════════════════════════════════════════════════
    # ENERGIA CONVENCIONAL
    # ══════════════════════════════════════════════════════════════════════════
    'XOM':   ('Exxon Mobil Corp.',                  'Energia'),
    'CVX':   ('Chevron Corp.',                      'Energia'),
    'COP':   ('ConocoPhillips',                     'Energia'),
    'SLB':   ('SLB (Schlumberger)',                 'Energia'),
    'EOG':   ('EOG Resources',                      'Energia'),
    'OXY':   ('Occidental Petroleum',               'Energia'),
    'DVN':   ('Devon Energy Corp.',                 'Energia'),
    'HAL':   ('Halliburton Co.',                    'Energia'),
    'MPC':   ('Marathon Petroleum',                 'Energia'),
    'VLO':   ('Valero Energy',                      'Energia'),
    'FANG':  ('Diamondback Energy',                 'Energia'),
    'PSX':   ('Phillips 66',                        'Energia'),
    'BKR':   ('Baker Hughes',                       'Energia'),
    'NOV':   ('NOV Inc.',                           'Energia'),
    'OVV':   ('Ovintiv Inc.',                       'Energia'),
    'APA':   ('APA Corp.',                          'Energia'),
    'PR':    ('Permian Resources',                  'Energia'),
    'SM':    ('SM Energy',                          'Energia'),
    'CIVI':  ('Civitas Resources',                  'Energia'),
    'KMI':   ('Kinder Morgan',                      'Energia'),
    'WMB':   ('Williams Companies',                 'Energia'),
    'OKE':   ('ONEOK Inc.',                         'Energia'),
    'ET':    ('Energy Transfer LP',                 'Energia'),
    'PBR':   ('Petrobras ADR',                      'Energia'),
    'E':     ('Eni SpA ADR',                        'Energia'),
    'BP':    ('BP PLC ADR',                         'Energia'),
    'SHEL':  ('Shell PLC ADR',                      'Energia'),
    'TTE':   ('TotalEnergies ADR',                  'Energia'),
    'EQNR':  ('Equinor ASA ADR',                    'Energia'),

    # ══════════════════════════════════════════════════════════════════════════
    # ENERGIA LIMPA / ESG / UTILITIES
    # ══════════════════════════════════════════════════════════════════════════
    'ENPH':  ('Enphase Energy',                     'Energia Limpa'),
    'SEDG':  ('SolarEdge Technologies',             'Energia Limpa'),
    'FSLR':  ('First Solar Inc.',                   'Energia Limpa'),
    'RUN':   ('Sunrun Inc.',                        'Energia Limpa'),
    'BE':    ('Bloom Energy Corp.',                 'Energia Limpa'),
    'PLUG':  ('Plug Power Inc.',                    'Energia Limpa'),
    'CSIQ':  ('Canadian Solar ADR',                 'Energia Limpa'),
    'JKS':   ('JinkoSolar ADR',                     'Energia Limpa'),
    'ARRY':  ('Array Technologies',                 'Energia Limpa'),
    'SHLS':  ('Shoals Technologies',                'Energia Limpa'),
    'NEE':   ('NextEra Energy',                     'Utilities'),
    'DUK':   ('Duke Energy Corp.',                  'Utilities'),
    'SO':    ('Southern Company',                   'Utilities'),
    'AEP':   ('American Electric Power',            'Utilities'),
    'EXC':   ('Exelon Corp.',                       'Utilities'),
    'PCG':   ('PG&E Corp.',                         'Utilities'),
    'SRE':   ('Sempra Energy',                      'Utilities'),
    'XEL':   ('Xcel Energy',                        'Utilities'),
    'WEC':   ('WEC Energy Group',                   'Utilities'),
    'ES':    ('Eversource Energy',                  'Utilities'),
    'ATO':   ('Atmos Energy',                       'Utilities'),
    'AWK':   ('American Water Works',               'Utilities'),
    'CMS':   ('CMS Energy',                         'Utilities'),

    # ══════════════════════════════════════════════════════════════════════════
    # INDÚSTRIA / AEROESPACIAL / DEFESA / LOGÍSTICA
    # ══════════════════════════════════════════════════════════════════════════
    'BA':    ('Boeing Co.',                         'Indústria'),
    'RTX':   ('RTX Corp.',                          'Indústria'),
    'LMT':   ('Lockheed Martin',                    'Indústria'),
    'NOC':   ('Northrop Grumman',                   'Indústria'),
    'GE':    ('GE Aerospace',                       'Indústria'),
    'CAT':   ('Caterpillar Inc.',                   'Indústria'),
    'DE':    ('Deere & Co.',                        'Indústria'),
    'MMM':   ('3M Co.',                             'Indústria'),
    'HON':   ('Honeywell International',            'Indústria'),
    'UPS':   ('United Parcel Service',              'Indústria'),
    'FDX':   ('FedEx Corp.',                        'Indústria'),
    'GD':    ('General Dynamics',                   'Indústria'),
    'LHX':   ('L3Harris Technologies',              'Indústria'),
    'AXON':  ('Axon Enterprise',                    'Indústria'),
    'LDOS':  ('Leidos Holdings',                    'Indústria'),
    'CARR':  ('Carrier Global',                     'Indústria'),
    'OTIS':  ('Otis Worldwide',                     'Indústria'),
    'TDG':   ('TransDigm Group',                    'Indústria'),
    'HEI':   ('HEICO Corp.',                        'Indústria'),
    'HXL':   ('Hexcel Corp.',                       'Indústria'),
    'TXT':   ('Textron Inc.',                       'Indústria'),
    'KTOS':  ('Kratos Defense & Security',          'Indústria'),
    'CACI':  ('CACI International',                 'Indústria'),
    'SAIC':  ('Science Applications Intl.',         'Indústria'),
    'BAH':   ('Booz Allen Hamilton',                'Indústria'),
    'PRLB':  ('Proto Labs Inc.',                    'Indústria'),
    'ITT':   ('ITT Inc.',                           'Indústria'),
    'AME':   ('AMETEK Inc.',                        'Indústria'),
    'ROP':   ('Roper Technologies',                 'Indústria'),
    'IEX':   ('IDEX Corp.',                         'Indústria'),
    'XYL':   ('Xylem Inc.',                         'Indústria'),
    'GWW':   ('W.W. Grainger',                      'Indústria'),
    'MSC':   ('MSC Industrial Direct',              'Indústria'),
    'FAST':  ('Fastenal Co.',                       'Indústria'),
    'SNA':   ('Snap-on Inc.',                       'Indústria'),
    'PH':    ('Parker-Hannifin Corp.',              'Indústria'),
    'EMR':   ('Emerson Electric',                   'Indústria'),
    'ETN':   ('Eaton Corp.',                        'Indústria'),
    'ROK':   ('Rockwell Automation',                'Indústria'),
    'IR':    ('Ingersoll Rand',                     'Indústria'),
    'NDSN':  ('Nordson Corp.',                      'Indústria'),
    'AGCO':  ('AGCO Corp.',                         'Indústria'),
    'CNH':   ('CNH Industrial ADR',                 'Indústria'),
    'PCAR':  ('PACCAR Inc.',                        'Indústria'),
    'CMI':   ('Cummins Inc.',                       'Indústria'),
    'CSX':   ('CSX Corp.',                          'Indústria'),
    'NSC':   ('Norfolk Southern',                   'Indústria'),
    'UNP':   ('Union Pacific Corp.',                'Indústria'),
    'CP':    ('Canadian Pacific Kansas City',       'Indústria'),
    'CNI':   ('Canadian National Railway',          'Indústria'),
    'WAB':   ('Wabtec Corp.',                       'Indústria'),

    # ══════════════════════════════════════════════════════════════════════════
    # AUTOMOTIVO / EVs / MOBILIDADE
    # ══════════════════════════════════════════════════════════════════════════
    'F':     ('Ford Motor Co.',                     'Automotivo'),
    'GM':    ('General Motors Co.',                 'Automotivo'),
    'RIVN':  ('Rivian Automotive',                  'Automotivo'),
    'LCID':  ('Lucid Group',                        'Automotivo'),
    'NIO':   ('NIO Inc. ADR',                       'Automotivo'),
    'XPEV':  ('XPeng Inc. ADR',                     'Automotivo'),
    'LI':    ('Li Auto ADR',                        'Automotivo'),
    'BWA':   ('BorgWarner Inc.',                    'Automotivo'),
    'LEA':   ('Lear Corp.',                         'Automotivo'),
    'ALV':   ('Autoliv Inc.',                       'Automotivo'),
    'APTV':  ('Aptiv PLC',                          'Automotivo'),
    'DAN':   ('Dana Inc.',                          'Automotivo'),
    'GT':    ('Goodyear Tire & Rubber',             'Automotivo'),
    'SMP':   ('Standard Motor Products',            'Automotivo'),

    # ══════════════════════════════════════════════════════════════════════════
    # TELECOMUNICAÇÕES
    # ══════════════════════════════════════════════════════════════════════════
    'T':     ('AT&T Inc.',                          'Telecom'),
    'VZ':    ('Verizon Communications',             'Telecom'),
    'TMUS':  ('T-Mobile US',                        'Telecom'),
    'LUMN':  ('Lumen Technologies',                 'Telecom'),
    'VOD':   ('Vodafone Group ADR',                 'Telecom'),
    'AMX':   ('América Móvil ADR',                  'Telecom'),
    'TKC':   ('Turkcell ADR',                       'Telecom'),

    # ══════════════════════════════════════════════════════════════════════════
    # BENS DE CONSUMO BÁSICO / ALIMENTOS / BEBIDAS / TABACO
    # ══════════════════════════════════════════════════════════════════════════
    'PG':    ('Procter & Gamble',                   'Consumo Básico'),
    'KO':    ('Coca-Cola Co.',                      'Consumo Básico'),
    'PEP':   ('PepsiCo Inc.',                       'Consumo Básico'),
    'CL':    ('Colgate-Palmolive',                  'Consumo Básico'),
    'MO':    ('Altria Group',                       'Consumo Básico'),
    'PM':    ('Philip Morris International',        'Consumo Básico'),
    'BTI':   ('British American Tobacco ADR',       'Consumo Básico'),
    'KHC':   ('Kraft Heinz Co.',                    'Consumo Básico'),
    'GIS':   ('General Mills',                      'Consumo Básico'),
    'CPB':   ("Campbell's Company",                 'Consumo Básico'),
    'HSY':   ('Hershey Co.',                        'Consumo Básico'),
    'MDLZ':  ('Mondelez International',             'Consumo Básico'),
    'MKC':   ('McCormick & Co.',                    'Consumo Básico'),
    'SJM':   ('J.M. Smucker',                       'Consumo Básico'),
    'HRL':   ('Hormel Foods',                       'Consumo Básico'),
    'TSN':   ('Tyson Foods',                        'Consumo Básico'),
    'CAG':   ('Conagra Brands',                     'Consumo Básico'),
    'BG':    ('Bunge Global',                       'Consumo Básico'),
    'ADM':   ('Archer-Daniels-Midland',             'Consumo Básico'),
    'INGR':  ('Ingredion Inc.',                     'Consumo Básico'),
    'CLX':   ('Clorox Co.',                         'Consumo Básico'),
    'CHD':   ('Church & Dwight',                    'Consumo Básico'),
    'EL':    ('Estée Lauder Companies',             'Consumo Básico'),
    'COTY':  ('Coty Inc.',                          'Consumo Básico'),
    'KVUE':  ('Kenvue Inc.',                        'Consumo Básico'),
    'NVO':   ('Novo Nordisk ADR',                   'Consumo Básico'),
    'DEO':   ('Diageo PLC ADR',                     'Consumo Básico'),
    'STZ':   ('Constellation Brands',               'Consumo Básico'),
    'BUD':   ('AB InBev ADR',                       'Consumo Básico'),
    'TAP':   ('Molson Coors Beverage',              'Consumo Básico'),
    'SAM':   ('Boston Beer Company',                'Consumo Básico'),

    # ══════════════════════════════════════════════════════════════════════════
    # IMOBILIÁRIO (REITs)
    # ══════════════════════════════════════════════════════════════════════════
    'AMT':   ('American Tower Corp.',               'REITs'),
    'PLD':   ('Prologis Inc.',                      'REITs'),
    'EQIX':  ('Equinix Inc.',                       'REITs'),
    'SPG':   ('Simon Property Group',               'REITs'),
    'O':     ('Realty Income Corp.',                'REITs'),
    'VICI':  ('VICI Properties',                    'REITs'),
    'WPC':   ('W. P. Carey Inc.',                   'REITs'),
    'DOC':   ('Healthpeak Properties',              'REITs'),
    'DLR':   ('Digital Realty Trust',               'REITs'),
    'CCI':   ('Crown Castle Inc.',                  'REITs'),
    'SBAC':  ('SBA Communications',                 'REITs'),
    'PSA':   ('Public Storage',                     'REITs'),
    'EXR':   ('Extra Space Storage',                'REITs'),
    'CUBE':  ('CubeSmart',                          'REITs'),
    'NSA':   ('National Storage Affiliates',        'REITs'),
    'EQR':   ('Equity Residential',                 'REITs'),
    'AVB':   ('AvalonBay Communities',              'REITs'),
    'MAA':   ('Mid-America Apartment',              'REITs'),
    'CPT':   ('Camden Property Trust',              'REITs'),
    'UDR':   ('UDR Inc.',                           'REITs'),
    'NNN':   ('NNN REIT Inc.',                      'REITs'),
    'ADC':   ('Agree Realty Corp.',                 'REITs'),
    'EPRT':  ('Essential Properties Realty',        'REITs'),
    'BXP':   ('BXP Inc.',                           'REITs'),
    'ARE':   ('Alexandria Real Estate',             'REITs'),
    'VTR':   ('Ventas Inc.',                        'REITs'),
    'WELL':  ('Welltower Inc.',                     'REITs'),
    'HR':    ('Healthcare Realty Trust',            'REITs'),
    'KIM':   ('Kimco Realty Corp.',                 'REITs'),
    'REG':   ('Regency Centers Corp.',              'REITs'),
    'FRT':   ('Federal Realty Trust',               'REITs'),
    'IIPR':  ('Innovative Industrial Properties',   'REITs'),

    # ══════════════════════════════════════════════════════════════════════════
    # MATERIAIS / MINERAÇÃO / QUÍMICOS
    # ══════════════════════════════════════════════════════════════════════════
    'VALE':  ('Vale SA ADR',                        'Materiais'),
    'FCX':   ('Freeport-McMoRan',                   'Materiais'),
    'NEM':   ('Newmont Corp.',                      'Materiais'),
    'GOLD':  ('Barrick Gold Corp.',                 'Materiais'),
    'AA':    ('Alcoa Corp.',                        'Materiais'),
    'CLF':   ('Cleveland-Cliffs',                   'Materiais'),
    'MP':    ('MP Materials Corp.',                 'Materiais'),
    'LIN':   ('Linde PLC',                          'Materiais'),
    'APD':   ('Air Products & Chemicals',           'Materiais'),
    'ECL':   ('Ecolab Inc.',                        'Materiais'),
    'SHW':   ('Sherwin-Williams',                   'Materiais'),
    'PPG':   ('PPG Industries',                     'Materiais'),
    'RPM':   ('RPM International',                  'Materiais'),
    'ALB':   ('Albemarle Corp.',                    'Materiais'),
    'EMN':   ('Eastman Chemical',                   'Materiais'),
    'CE':    ('Celanese Corp.',                     'Materiais'),
    'HUN':   ('Huntsman Corp.',                     'Materiais'),
    'WLK':   ('Westlake Corp.',                     'Materiais'),
    'CC':    ('Chemours Company',                   'Materiais'),
    'CTVA':  ('Corteva Inc.',                       'Materiais'),
    'FMC':   ('FMC Corp.',                          'Materiais'),
    'MOS':   ('Mosaic Co.',                         'Materiais'),
    'CF':    ('CF Industries Holdings',             'Materiais'),
    'NTR':   ('Nutrien Ltd.',                       'Materiais'),
    'IP':    ('International Paper',                'Materiais'),
    'PKG':   ('Packaging Corp of America',          'Materiais'),
    'SEE':   ('Sealed Air Corp.',                   'Materiais'),
    'BALL':  ('Ball Corp.',                         'Materiais'),
    'ATI':   ('ATI Inc.',                           'Materiais'),
    'CMC':   ('Commercial Metals Co.',              'Materiais'),
    'STLD':  ('Steel Dynamics',                     'Materiais'),
    'NUE':   ('Nucor Corp.',                        'Materiais'),
    'MT':    ('ArcelorMittal ADR',                  'Materiais'),
    'RIO':   ('Rio Tinto ADR',                      'Materiais'),
    'BHP':   ('BHP Group ADR',                      'Materiais'),
    'SCCO':  ('Southern Copper Corp.',              'Materiais'),
    'RS':    ('Reliance Steel & Aluminum',          'Materiais'),

    # ══════════════════════════════════════════════════════════════════════════
    # LATAM / BRASIL / ÁSIA / EUROPA (ADRs listados nos EUA)
    # ══════════════════════════════════════════════════════════════════════════
    'BSAC':  ('Banco Santander Chile ADR',          'LatAm'),
    'BBAR':  ('BBVA Argentina ADR',                 'LatAm'),
    'GGAL':  ('Grupo Financiero Galicia ADR',       'LatAm'),
    'BMA':   ('Banco Macro ADR',                    'LatAm'),
    'PAM':   ('Pampa Energía ADR',                  'LatAm'),
    'YPF':   ('YPF SA ADR',                         'LatAm'),
    'LOMA':  ('Loma Negra ADR',                     'LatAm'),
    'CEPU':  ('Central Puerto ADR',                 'LatAm'),
    'IRS':   ('IRSA Inversiones ADR',               'LatAm'),
    'GLOB':  ('Globant SA',                         'LatAm'),
    'ARCO':  ('Arcos Dorados ADR',                  'LatAm'),
    'GGB':   ('Gerdau SA ADR',                      'LatAm'),
    'SID':   ('Companhia Siderúrgica ADR',          'LatAm'),
    'SUZ':   ('Suzano SA ADR',                      'LatAm'),
    'CIG':   ('Cemig ADR',                          'LatAm'),
    'ELP':   ('Copel ADR',                          'LatAm'),
    'SBS':   ('Sabesp ADR',                         'LatAm'),
    'ENIC':  ('Enel Chile ADR',                     'LatAm'),
    'LTM':   ('LATAM Airlines ADR',                 'LatAm'),
    'VNET':  ('VNET Group ADR',                     'LatAm'),
    'TME':   ('Tencent Music ADR',                  'Ásia'),
    'BEKE':  ('KE Holdings ADR',                    'Ásia'),
    'VIPS':  ('Vipshop Holdings ADR',               'Ásia'),
    'IQ':    ('iQIYI Inc. ADR',                     'Ásia'),
    'SE':    ('Sea Limited ADR',                    'Ásia'),
    'WB':    ('Weibo Corp. ADR',                    'Ásia'),
    'LPSN':  ('LivePerson Inc.',                    'Ásia'),
    'ASIX':  ('AdvanSix Inc.',                      'Ásia'),

    # ══════════════════════════════════════════════════════════════════════════
    # ETFs — Amplos (Mercado, Setoriais, Temáticos, Renda Fixa, Commodities)
    # ══════════════════════════════════════════════════════════════════════════
    # Mercado amplo
    'SPY':   ('SPDR S&P 500 ETF',                   'ETF'),
    'QQQ':   ('Invesco Nasdaq 100 ETF',             'ETF'),
    'IWM':   ('iShares Russell 2000 ETF',           'ETF'),
    'DIA':   ('SPDR Dow Jones ETF',                 'ETF'),
    'VTI':   ('Vanguard Total Stock Market ETF',    'ETF'),
    'VOO':   ('Vanguard S&P 500 ETF',               'ETF'),
    'SCHB':  ('Schwab US Broad Market ETF',         'ETF'),
    'IVV':   ('iShares Core S&P 500 ETF',           'ETF'),
    'VEA':   ('Vanguard FTSE Dev Markets ETF',      'ETF'),
    'VWO':   ('Vanguard FTSE Emerging Markets ETF', 'ETF'),
    'EEM':   ('iShares MSCI Emerging Markets ETF',  'ETF'),
    'EFA':   ('iShares MSCI EAFE ETF',              'ETF'),
    'ACWI':  ('iShares MSCI ACWI ETF',              'ETF'),
    'URTH':  ('iShares MSCI World ETF',             'ETF'),
    'INDA':  ('iShares MSCI India ETF',             'ETF'),
    'EWZ':   ('iShares MSCI Brazil ETF',            'ETF'),
    'FXI':   ('iShares China Large-Cap ETF',        'ETF'),
    'MCHI':  ('iShares MSCI China ETF',             'ETF'),
    'EWT':   ('iShares MSCI Taiwan ETF',            'ETF'),
    'EWJ':   ('iShares MSCI Japan ETF',             'ETF'),
    'EWY':   ('iShares MSCI South Korea ETF',       'ETF'),
    'GXG':   ('Global X MSCI Colombia ETF',         'ETF'),
    'ECH':   ('iShares MSCI Chile ETF',             'ETF'),
    'EWW':   ('iShares MSCI Mexico ETF',            'ETF'),
    'ILF':   ('iShares Latin America 40 ETF',       'ETF'),
    # Setoriais SPDR
    'XLK':   ('Technology Select Sector SPDR',      'ETF'),
    'XLF':   ('Financial Select Sector SPDR',       'ETF'),
    'XLE':   ('Energy Select Sector SPDR',          'ETF'),
    'XLV':   ('Health Care Select Sector SPDR',     'ETF'),
    'XLI':   ('Industrial Select Sector SPDR',      'ETF'),
    'XLB':   ('Materials Select Sector SPDR',       'ETF'),
    'XLY':   ('Consumer Discret. Select SPDR',      'ETF'),
    'XLP':   ('Consumer Staples Select SPDR',       'ETF'),
    'XLRE':  ('Real Estate Select Sector SPDR',     'ETF'),
    'XLU':   ('Utilities Select Sector SPDR',       'ETF'),
    'XLC':   ('Communication Services SPDR',        'ETF'),
    # Temáticos
    'XBI':   ('SPDR Biotech ETF',                   'ETF'),
    'ARKK':  ('ARK Innovation ETF',                 'ETF'),
    'ARKG':  ('ARK Genomic Revolution ETF',         'ETF'),
    'ARKW':  ('ARK Next Gen Internet ETF',          'ETF'),
    'ARKF':  ('ARK Fintech Innovation ETF',         'ETF'),
    'SOXX':  ('iShares Semiconductor ETF',          'ETF'),
    'SMH':   ('VanEck Semiconductor ETF',           'ETF'),
    'CIBR':  ('First Trust Cybersecurity ETF',      'ETF'),
    'BUG':   ('Global X Cybersecurity ETF',         'ETF'),
    'CLOU':  ('Global X Cloud Computing ETF',       'ETF'),
    'BOTZ':  ('Global X Robotics & AI ETF',         'ETF'),
    'ROBO':  ('ROBO Global Robotics ETF',           'ETF'),
    'AIQ':   ('Global X AI & Technology ETF',       'ETF'),
    'DRIV':  ('Global X Autonomous & EV ETF',       'ETF'),
    'LIT':   ('Global X Lithium & Battery ETF',     'ETF'),
    'COPX':  ('Global X Copper Miners ETF',         'ETF'),
    'URA':   ('Global X Uranium ETF',               'ETF'),
    'REMX':  ('VanEck Rare Earth/Strateg. Metals',  'ETF'),
    'ICLN':  ('iShares Global Clean Energy ETF',    'ETF'),
    'TAN':   ('Invesco Solar ETF',                  'ETF'),
    'FAN':   ('First Trust Global Wind Energy ETF', 'ETF'),
    'CNRG':  ('SPDR S&P Kensho Clean Power ETF',   'ETF'),
    'JETS':  ('US Global Jets ETF',                 'ETF'),
    'BETZ':  ('Roundhill Sports Betting ETF',       'ETF'),
    'HERO':  ('Global X Video Games & Esports ETF', 'ETF'),
    'ESPO':  ('VanEck Video Gaming & eSports ETF',  'ETF'),
    'SOCL':  ('Global X Social Media ETF',          'ETF'),
    'FINX':  ('Global X FinTech ETF',               'ETF'),
    'KBWB':  ('Invesco KBW Bank ETF',               'ETF'),
    'KRE':   ('SPDR S&P Regional Banking ETF',      'ETF'),
    'PAVE':  ('Global X US Infrastructure Dev ETF', 'ETF'),
    'INDS':  ('Pacer Industrials & Logistics ETF',  'ETF'),
    'HACK':  ('ETFMG Prime Cyber Security ETF',     'ETF'),
    'WCLD':  ('WisdomTree Cloud Computing ETF',     'ETF'),
    'SKYY':  ('First Trust Cloud Computing ETF',    'ETF'),
    'IPAY':  ('ETFMG Prime Mobile Payments ETF',    'ETF'),
    'PAWZ':  ('ProShares Pet Care ETF',             'ETF'),
    'CTEC':  ('Global X CleanTech ETF',             'ETF'),
    'DIVO':  ('Amplify CWP Enhanced Div Inc ETF',   'ETF'),
    'NOBL':  ('ProShares S&P 500 Div Aristocrats',  'ETF'),
    'SDY':   ('SPDR S&P Dividend ETF',              'ETF'),
    'VIG':   ('Vanguard Div Appreciation ETF',      'ETF'),
    'DVY':   ('iShares Select Dividend ETF',        'ETF'),
    'SCHD':  ('Schwab US Div Equity ETF',           'ETF'),
    'HDV':   ('iShares Core High Div ETF',          'ETF'),
    # Renda Fixa
    'TLT':   ('iShares 20+ Year Treasury ETF',      'ETF'),
    'IEF':   ('iShares 7-10 Year Treasury ETF',     'ETF'),
    'SHY':   ('iShares 1-3 Year Treasury ETF',      'ETF'),
    'SGOV':  ('iShares 0-3 Month Treasury ETF',     'ETF'),
    'BIL':   ('SPDR Bloomberg 1-3 Month T-Bill',    'ETF'),
    'HYG':   ('iShares High Yield Bond ETF',        'ETF'),
    'LQD':   ('iShares Investment Grade Bond ETF',  'ETF'),
    'AGG':   ('iShares Core US Aggregate Bond ETF', 'ETF'),
    'BND':   ('Vanguard Total Bond Market ETF',     'ETF'),
    'TIP':   ('iShares TIPS Bond ETF',              'ETF'),
    'MBB':   ('iShares MBS ETF',                    'ETF'),
    'EMB':   ('iShares JPMorgan EM Bond ETF',       'ETF'),
    # Commodities e Ouro
    'GLD':   ('SPDR Gold Shares ETF',               'ETF'),
    'IAU':   ('iShares Gold Trust ETF',             'ETF'),
    'SLV':   ('iShares Silver Trust ETF',           'ETF'),
    'PDBC':  ('Invesco DB Opt Yield Div Com ETF',   'ETF'),
    'GSG':   ('iShares S&P GSCI Commodity ETF',     'ETF'),
    'USO':   ('United States Oil Fund ETF',         'ETF'),
    'UNG':   ('United States Nat Gas Fund ETF',     'ETF'),
    'CORN':  ('Teucrium Corn Fund ETF',             'ETF'),
    'WEAT':  ('Teucrium Wheat Fund ETF',            'ETF'),
    'SOYB':  ('Teucrium Soybean Fund ETF',          'ETF'),
    # VNQ e REITs ETF
    'VNQ':   ('Vanguard Real Estate ETF',           'ETF'),
    'SCHH':  ('Schwab US REIT ETF',                 'ETF'),
    # Cripto ETFs
    'IBIT':  ('iShares Bitcoin Trust ETF',          'ETF'),
    'BITB':  ('Bitwise Bitcoin ETF',                'ETF'),
    'FBTC':  ('Fidelity Wise Origin Bitcoin ETF',   'ETF'),
    'ARKB':  ('ARK 21Shares Bitcoin ETF',           'ETF'),
    'ETHA':  ('iShares Ethereum Trust ETF',         'ETF'),
    'ETHW':  ('ProShares Ultra Ether ETF',          'ETF'),
    'BITO':  ('ProShares Bitcoin Strategy ETF',     'ETF'),
    'GBTC':  ('Grayscale Bitcoin Trust ETF',        'ETF'),
    # Leveraged / Inverse (populares)
    'TQQQ':  ('ProShares UltraPro QQQ 3x',          'ETF'),
    'SQQQ':  ('ProShares UltraPro Short QQQ 3x',    'ETF'),
    'UPRO':  ('ProShares UltraPro S&P 500 3x',      'ETF'),
    'SPXU':  ('ProShares UltraPro Short S&P 3x',    'ETF'),
    'UVXY':  ('ProShares Ultra VIX Short-Term ETF', 'ETF'),
    'SVXY':  ('ProShares Short VIX Short-Term ETF', 'ETF'),
    'SOXL':  ('Direxion Daily Semicon Bull 3x',     'ETF'),
    'SOXS':  ('Direxion Daily Semicon Bear 3x',     'ETF'),
    'LABU':  ('Direxion Daily Biotech Bull 3x',     'ETF'),
    'TNA':   ('Direxion Daily S&P Small Bull 3x',   'ETF'),
    'SPXL':  ('Direxion Daily S&P 500 Bull 3x',     'ETF'),
    'FAS':   ('Direxion Daily Financial Bull 3x',   'ETF'),
    'TECL':  ('Direxion Daily Tech Bull 3x',        'ETF'),
    'CURE':  ('Direxion Daily Healthcare Bull 3x',  'ETF'),
    'NAIL':  ('Direxion Daily Homebuilders Bull 3x','ETF'),
    'HIBL':  ('Direxion Daily S&P 500 High Beta 3x','ETF'),
    # ══════════════════════════════════════════════════════════════════════════
    # SUBSTITUIÇÕES E CORREÇÕES (tickers anteriores inválidos no yfinance)
    # ══════════════════════════════════════════════════════════════════════════
    # Ticker corrigido: SNE → SONY (Sony relistada com novo ticker 2023)
    'SONY':  ('Sony Group Corp ADR',                'Entretenimento'),
    # Ticker corrigido: TATAMOTORS → TTM (Tata Motors ADR correto)
    'TTM':   ('Tata Motors ADR',                    'Automotivo'),
    # COG virou CTRA (fusão Cabot Oil & Gas + Cimarex Energy 2021)
    'CTRA':  ('Coterra Energy Inc.',                'Energia'),
    # ERJ - Embraer ADR (ticker alternativo EMBR.SA, mas ERJ funciona às vezes)
    # Substituído por outro ADR LatAm válido
    'BRKR':  ('Bruker Corp.',                       'Saúde'),
    # Adicionando tickers válidos para substituir removidos
    'XRAY':  ('Dentsply Sirona',                    'Saúde'),
    'JOBY':  ('Joby Aviation Inc.',                 'Automotivo'),
    'ACHR':  ('Archer Aviation Inc.',               'Automotivo'),
    'GFL':   ('GFL Environmental Inc.',             'Indústria'),
    'TTEK':  ('Tetra Tech Inc.',                    'Indústria'),
    'PSN':   ('Parsons Corp.',                      'Indústria'),
    'DRS':   ('Leonardo DRS Inc.',                  'Indústria'),
    'AOS':   ('A. O. Smith Corp.',                  'Indústria'),
    'GNRC':  ('Generac Holdings Inc.',              'Indústria'),
    'NVT':   ('nVent Electric PLC',                 'Indústria'),
    'LECO':  ('Lincoln Electric Holdings',          'Indústria'),
    'CW':    ('Curtiss-Wright Corp.',               'Indústria'),
    'MSCI':  ('MSCI Inc.',                          'Bancos'),
    'BX':    ('Blackstone Inc.',                    'Bancos'),
    'KKR':   ('KKR & Co.',                          'Bancos'),
    'APO':   ('Apollo Global Management',           'Bancos'),
    'CG':    ('Carlyle Group Inc.',                 'Bancos'),
    'ARES':  ('Ares Management Corp.',              'Bancos'),
    'TPG':   ('TPG Inc.',                           'Bancos'),
    'OWL':   ('Blue Owl Capital Inc.',              'Bancos'),
    'BN':    ('Brookfield Corp.',                   'Bancos'),
    'BAM':   ('Brookfield Asset Management',        'Bancos'),
    'EG':    ('Everest Group Ltd.',                 'Bancos'),
    'RYAN':  ('Ryan Specialty Group',               'Bancos'),
    'FAF':   ('First American Financial',           'Bancos'),
    'FDS':   ('FactSet Research Systems',           'Bancos'),
    'TW':    ('Tradeweb Markets Inc.',              'Bancos'),
    'MCK':   ('McKesson Corp.',                     'Saúde'),
    'COR':   ('Cencora Inc.',                       'Saúde'),
    'CAH':   ('Cardinal Health Inc.',               'Saúde'),
    'RMD':   ('ResMed Inc.',                        'Saúde'),
    'CRL':   ('Charles River Laboratories',         'Saúde'),
    'STE':   ('STERIS PLC',                         'Saúde'),
    'RPRX':  ('Royalty Pharma PLC',                 'Saúde'),
    'GDRX':  ('GoodRx Holdings',                    'Saúde'),
    'DOCS':  ('Doximity Inc.',                      'Saúde'),
    'TDOC':  ('Teladoc Health Inc.',                'Saúde'),
    'HIMS':  ('Hims & Hers Health Inc.',            'Saúde'),
    'SRPT':  ('Sarepta Therapeutics',               'Biotech'),
    'LEGN':  ('Legend Biotech Corp ADR',            'Biotech'),
    'APLS':  ('Apellis Pharmaceuticals',            'Biotech'),
    'PRCT':  ('Procept BioRobotics',                'Biotech'),
    'DHI':   ('D.R. Horton Inc.',                   'Construção'),
    'LEN':   ('Lennar Corp.',                       'Construção'),
    'PHM':   ('PulteGroup Inc.',                    'Construção'),
    'TOL':   ('Toll Brothers Inc.',                 'Construção'),
    'NVR':   ('NVR Inc.',                           'Construção'),
    'MHO':   ('M/I Homes Inc.',                     'Construção'),
    'TMHC':  ('Taylor Morrison Home Corp.',         'Construção'),
    'KBH':   ('KB Home',                            'Construção'),
    'AWI':   ('Armstrong World Industries',         'Construção'),
    'TREX':  ('Trex Company Inc.',                  'Construção'),
    'FBIN':  ('Fortune Brands Innovations',         'Construção'),
    'IBP':   ('Installed Building Products',        'Construção'),
    'BLD':   ('TopBuild Corp.',                     'Construção'),
    'BLDR':  ('Builders FirstSource Inc.',          'Construção'),
    'SKY':   ('Skyline Champion Corp.',             'Construção'),
    'FIVE':  ('Five Below Inc.',                    'Varejo'),
    'ULTA':  ('Ulta Beauty Inc.',                   'Varejo'),
    'DKS':   ("Dick's Sporting Goods",              'Varejo'),
    'WSM':   ('Williams-Sonoma Inc.',               'Varejo'),
    'BOOT':  ('Boot Barn Holdings',                 'Varejo'),
    'CPNG':  ('Coupang Inc.',                       'E-commerce'),
    'FRPT':  ('Freshpet Inc.',                      'Consumo Básico'),
    'VITL':  ('Vital Farms Inc.',                   'Consumo Básico'),
    'LNG':   ('Cheniere Energy Inc.',               'Energia'),
    'EQT':   ('EQT Corp.',                          'Energia'),
    'AR':    ('Antero Resources Corp.',             'Energia'),
    'RRC':   ('Range Resources Corp.',              'Energia'),
    'VST':   ('Vistra Corp.',                       'Energia'),
    'GEV':   ('GE Vernova Inc.',                    'Energia'),
    'CEG':   ('Constellation Energy Corp.',         'Utilities'),
    'NRG':   ('NRG Energy Inc.',                    'Energia'),
    'ODFL':  ('Old Dominion Freight Line',          'Indústria'),
    'EXPD':  ('Expeditors International',           'Indústria'),
    'XPO':   ('XPO Inc.',                           'Indústria'),
    'CHRW':  ('C.H. Robinson Worldwide',            'Indústria'),
    'JBHT':  ('J.B. Hunt Transport Services',       'Indústria'),
    'SAIA':  ('Saia Inc.',                          'Indústria'),
    'TFII':  ('TFI International Inc.',             'Indústria'),
    'GXO':   ('GXO Logistics Inc.',                 'Indústria'),
    'HII':   ('Huntington Ingalls Industries',      'Indústria'),
    'URI':   ('United Rentals Inc.',                'Indústria'),
    'WM':    ('Waste Management Inc.',              'Indústria'),
    'RSG':   ('Republic Services Inc.',             'Indústria'),
    'CWST':  ('Casella Waste Systems',              'Indústria'),
    'CLH':   ('Clean Harbors Inc.',                 'Indústria'),
    'NXPI':  ('NXP Semiconductors ADR',             'Semicondutores'),
    'STM':   ('STMicroelectronics ADR',             'Semicondutores'),
    'MCHP':  ('Microchip Technology Inc.',          'Semicondutores'),
    'TER':   ('Teradyne Inc.',                      'Semicondutores'),
    'ENTG':  ('Entegris Inc.',                      'Semicondutores'),
    'SMTC':  ('Semtech Corp.',                      'Semicondutores'),
    'MTSI':  ('MACOM Technology Solutions',         'Semicondutores'),
    'POWI':  ('Power Integrations Inc.',            'Semicondutores'),
    'MKSI':  ('MKS Instruments Inc.',              'Semicondutores'),
    'IPGP':  ('IPG Photonics Corp.',                'Semicondutores'),
    'CRUS':  ('Cirrus Logic Inc.',                  'Semicondutores'),
    'RMBS':  ('Rambus Inc.',                        'Semicondutores'),
    'SITM':  ('SiTime Corp.',                       'Semicondutores'),
    'ALGM':  ('Allegro MicroSystems Inc.',          'Semicondutores'),
    'IIVI':  ('Coherent Corp.',                     'Semicondutores'),
    'ACN':   ('Accenture PLC',                      'Software'),
    'ADSK':  ('Autodesk Inc.',                      'Software'),
    'G':     ('Gartner Inc.',                       'Software'),
    'DAY':   ('Dayforce Inc.',                      'Software'),
    'ANET':  ('Arista Networks Inc.',               'Tecnologia'),
    'APH':   ('Amphenol Corp.',                     'Tecnologia'),
    'GRMN':  ('Garmin Ltd.',                        'Tecnologia'),
    'VRSN':  ('VeriSign Inc.',                      'Tecnologia'),
    'INFY':  ('Infosys ADR',                        'Software'),
    'WIT':   ('Wipro ADR',                          'Software'),
    'CTSH':  ('Cognizant Technology Solutions',     'Software'),
    'HDB':   ('HDFC Bank ADR',                      'Bancos'),
    'IBN':   ('ICICI Bank ADR',                     'Bancos'),
    'KB':    ('KB Financial Group ADR',             'Bancos'),
    'SHG':   ('Shinhan Financial Group ADR',        'Bancos'),
    'MUFG':  ('Mitsubishi UFJ Financial ADR',       'Bancos'),
    'SMFG':  ('Sumitomo Mitsui Financial ADR',      'Bancos'),
    'MFG':   ('Mizuho Financial Group ADR',         'Bancos'),
    'SAP':   ('SAP SE ADR',                         'Software'),
    'AZN':   ('AstraZeneca PLC ADR',                'Saúde'),
    'NVS':   ('Novartis AG ADR',                    'Saúde'),
    'GSK':   ('GSK PLC ADR',                        'Saúde'),
    'BAYRY': ('Bayer AG ADR',                       'Saúde'),
    'SNY':   ('Sanofi SA ADR',                      'Saúde'),
    'NTDOY': ('Nintendo Co ADR',                    'Entretenimento'),
    'MLM':   ('Martin Marietta Materials',          'Materiais'),
    'VMC':   ('Vulcan Materials Co.',               'Materiais'),
    'EXP':   ('Eagle Materials Inc.',               'Materiais'),
    'UFPI':  ('UFP Industries Inc.',                'Materiais'),
    'WY':    ('Weyerhaeuser Co.',                   'Materiais'),
    'LYB':   ('LyondellBasell Industries',          'Materiais'),
    'SMG':   ('Scotts Miracle-Gro Co.',             'Consumo Básico'),
    'CELH':  ('Celsius Holdings Inc.',              'Consumo Básico'),
    'MNST':  ('Monster Beverage Corp.',             'Consumo Básico'),
    'RKT':   ('Rocket Companies Inc.',              'Fintech'),
    'UWMC':  ('UWM Holdings Corp.',                 'Fintech'),
    'OPEN':  ('Opendoor Technologies',              'Fintech'),
    'Z':     ('Zillow Group Inc.',                  'E-commerce'),
    'CBRE':  ('CBRE Group Inc.',                    'REITs'),
    'JLL':   ('Jones Lang LaSalle Inc.',            'REITs'),
    'IRM':   ('Iron Mountain Inc.',                 'REITs'),
    'GLPI':  ('Gaming and Leisure Properties',      'REITs'),
    'MPW':   ('Medical Properties Trust',           'REITs'),
    'OHI':   ('Omega Healthcare Investors',         'REITs'),
    'CHCT':  ('Community Healthcare Trust',         'REITs'),
    'MGM':   ('MGM Resorts International',          'Entretenimento'),
    'WYNN':  ('Wynn Resorts Ltd.',                  'Entretenimento'),
    'LVS':   ('Las Vegas Sands Corp.',              'Entretenimento'),
    'CZR':   ('Caesars Entertainment Inc.',         'Entretenimento'),
    'PENN':  ('PENN Entertainment Inc.',            'Entretenimento'),
    'LYV':   ('Live Nation Entertainment',          'Entretenimento'),
    'GENI':  ('Genius Sports Ltd.',                 'Entretenimento'),
    'FWONK': ('Formula One Group',                  'Entretenimento'),
    'MAT':   ('Mattel Inc.',                        'Entretenimento'),
    'HAS':   ('Hasbro Inc.',                        'Entretenimento'),
    'PTON':  ('Peloton Interactive Inc.',           'Entretenimento'),
    'CHTR':  ('Charter Communications Inc.',        'Telecom'),
    'CMCSA': ('Comcast Corp.',                      'Telecom'),
    'LBRDA': ('Liberty Broadband Corp A',           'Telecom'),
    'CLSK':  ('CleanSpark Inc.',                    'Fintech'),
    'RIOT':  ('Riot Platforms Inc.',                'Fintech'),
    'MARA':  ('Marathon Digital Holdings',          'Fintech'),
    'HUT':   ('Hut 8 Corp.',                        'Fintech'),
    'CIFR':  ('Cipher Mining Inc.',                 'Fintech'),
    'WGMI':  ('Valkyrie Bitcoin Miners ETF',        'ETF'),
    'BITI':  ('ProShares Short Bitcoin ETF',        'ETF'),
    'AIT':   ('Applied Industrial Technologies',    'Indústria'),

    # ══════════════════════════════════════════════════════════════════════════
    # S&P 500 — EMPRESAS COMPLEMENTARES (cobertura total do índice)
    # ══════════════════════════════════════════════════════════════════════════

    # Consultoria / Serviços Profissionais
    'CSGP':  ('CoStar Group',                       'Software'),
    'TYL':   ('Tyler Technologies',                 'Software'),
    'DT':    ('Dynatrace Inc.',                     'Software'),
    'PRGS':  ('Progress Software',                  'Software'),

    # Semicondutores complementares
    'IFNNY': ('Infineon Technologies ADR',          'Semicondutores'),
    'SLAB':  ('Silicon Laboratories',               'Semicondutores'),
    'DIOD':  ('Diodes Inc.',                        'Semicondutores'),
    'PI':    ('Impinj Inc.',                        'Semicondutores'),

    # Exchanges / Infraestrutura Financeira
    'CME':   ('CME Group Inc.',                     'Bancos'),
    'ICE':   ('Intercontinental Exchange',          'Bancos'),
    'NDAQ':  ('Nasdaq Inc.',                        'Bancos'),
    'CBOE':  ('Cboe Global Markets',                'Bancos'),
    'SPGI':  ('S&P Global Inc.',                    'Bancos'),
    'MCO':   ('Moody\'s Corp.',                     'Bancos'),
    'MKTX':  ('MarketAxess Holdings',               'Bancos'),
    'RJF':   ('Raymond James Financial',            'Bancos'),
    'LPL':   ('LPL Financial Holdings',             'Bancos'),
    'AMP':   ('Ameriprise Financial',               'Bancos'),
    'VOYA':  ('Voya Financial',                     'Bancos'),
    'BEN':   ('Franklin Resources (Templeton)',      'Bancos'),
    'IVZ':   ('Invesco Ltd.',                       'Bancos'),
    'WRB':   ('W. R. Berkley Corp.',                'Bancos'),
    'ACGL':  ('Arch Capital Group',                 'Bancos'),
    'RLI':   ('RLI Corp.',                          'Bancos'),
    'FNF':   ('Fidelity National Financial',        'Bancos'),
    'LPLA':  ('LPL Financial Holdings',             'Bancos'),

    # Saúde complementar / Distribuição
    'COO':   ('Cooper Companies',                   'Saúde'),
    'ZTS':   ('Zoetis Inc.',                        'Saúde'),
    'GEHC':  ('GE HealthCare Technologies',         'Saúde'),
    'UNM':   ('Unum Group',                         'Bancos'),

    # Construção Civil / Homebuilders
    'NX':    ('Quanex Building Products',           'Construção'),

    # Energia — Gás Natural / Infraestrutura
    'CQP':   ('Cheniere Energy Partners LP',        'Energia'),
    'OGE':   ('OGE Energy Corp.',                   'Utilities'),
    'NI':    ('NiSource Inc.',                      'Utilities'),
    'PPL':   ('PPL Corp.',                          'Utilities'),
    'LNT':   ('Alliant Energy Corp.',               'Utilities'),
    'ETR':   ('Entergy Corp.',                      'Utilities'),
    'POR':   ('Portland General Electric',          'Utilities'),
    'IDACORP':('IDACORP Inc.',                      'Utilities'),
    'OGS':   ('ONE Gas Inc.',                       'Utilities'),

    # Indústria — complementar
    'ITW':   ('Illinois Tool Works',                'Indústria'),
    'J':     ('Jacobs Solutions Inc.',              'Indústria'),
    'MTZ':   ('MasTec Inc.',                        'Indústria'),
    'HUBB':  ('Hubbell Inc.',                       'Indústria'),
    'CSL':   ('Carlisle Companies',                 'Indústria'),
    'NPO':   ('Enpro Inc.',                         'Indústria'),
    'WTS':   ('Watts Water Technologies',           'Indústria'),
    'FELE':  ('Franklin Electric',                  'Indústria'),

    # Waste Management / Serviços Ambientais
    'SRCL':  ('Stericycle Inc.',                    'Indústria'),

    # Varejo Complementar / Especialidades
    'RH':    ('RH (Restoration Hardware)',          'Varejo'),
    'BJ':    ('BJ\'s Wholesale Club',              'Varejo'),
    'TSCO':  ('Tractor Supply Co.',                 'Varejo'),
    'CASY':  ('Casey\'s General Stores',           'Varejo'),
    'CHEF':  ('The Chef\'s Warehouse',             'Varejo'),
    'ELF':   ('e.l.f. Beauty Inc.',                 'Varejo'),
    'KDP':   ('Keurig Dr Pepper',                   'Consumo Básico'),
    'RYN':   ('Rayonier Inc.',                      'REITs'),

    # Tecnologia da Saúde / Dados
    'PHR':   ('Phreesia Inc.',                      'Saúde'),

    # Agronegócio / Fertilizantes / Sementes
    'APOG':  ('Apogee Enterprises',                 'Materiais'),

    # Imobiliário / Hipotecas
    'CWK':   ('Cushman & Wakefield',                'REITs'),
    'LTC':   ('LTC Properties',                     'REITs'),
    'NHI':   ('National Health Investors',          'REITs'),

    # Entretenimento / Cassinos / Gaming

    # Telecom + Internet complementar

    # ADRs Europeus Premium
    'ROG':   ('Roche Holding ADR',                  'Saúde'),
    'UCB':   ('UCB SA ADR',                         'Saúde'),
    'LNVGY': ('Lenovo Group ADR',                   'Tecnologia'),
    'SIEGY': ('Siemens AG ADR',                     'Indústria'),
    'MTUAY': ('MTU Aero Engines ADR',               'Indústria'),
    'SBGSY': ('Schneider Electric ADR',             'Indústria'),
    'LVMUY': ('LVMH Moët Hennessy ADR',             'Varejo'),
    'PPRUY': ('Kering SA ADR',                      'Varejo'),
    'CFRUY': ('Compagnie Financière Richemont ADR', 'Varejo'),
    'HESAY': ('Hermès International ADR',           'Varejo'),
    'WPP':   ('WPP PLC ADR',                        'Software'),
    'ABBNY': ('ABB Ltd ADR',                        'Indústria'),
    'ATLCY': ('Atlantia SpA ADR',                   'Indústria'),
    'ENLAY': ('Enel SpA ADR',                       'Utilities'),
    'ISNPY': ('Industrias Bachoco ADR',             'Consumo Básico'),
    'NGLOY': ('Anglo American ADR',                 'Materiais'),

    # ADRs Asiáticos Premium
    'HTHIY': ('Hitachi ADR',                        'Tecnologia'),
    'KYCCF': ('Kyocera Corp ADR',                   'Tecnologia'),
    'CCOEY': ('Canon Inc. ADR',                     'Tecnologia'),
    'TOELF': ('Tokio Marine Holdings ADR',          'Bancos'),
    'WF':    ('Woori Financial Group ADR',          'Bancos'),
    'MIDD':  ('Middleby Corp.',                     'Indústria'),

    # Criptoativos / Web3 / Blockchain listados nos EUA
    'BTBT':  ('Bit Digital Inc.',                   'Fintech'),

    # Russell 1000 — Small/Mid Caps relevantes ausentes
    'GEN':   ('Gen Digital Inc.',                   'Cibersegurança'),
    'DECK':  ('Deckers Outdoor Corp.',              'Varejo'),
    'GTLS':  ('Chart Industries',                   'Indústria'),
    'MWA':   ('Mueller Water Products',             'Indústria'),
    'EAF':   ('GrafTech International',             'Materiais'),
    'SIRI':  ('Sirius XM Holdings',                 'Entretenimento'),
    'IAG':   ('IAG Silver Corp.',                   'Materiais'),
    'PLTK':  ('Playtika Holding',                   'Entretenimento'),
    'FSTR':  ('L.B. Foster Company',                'Indústria'),
    'TRN':   ('Trinity Industries',                 'Indústria'),

    # ── Corrigidos v2.1 (tickers substitutos) ────────────────────────────────
    'COHR':  ('Coherent Corp.',                         'Semicondutores'),
    'IDA':   ('IDACORP Inc.',                           'Utilities'),
    'PHG':   ('Philips NV ADR',                         'Saúde'),
    'TIMB':  ('TIM SA ADR',                             'Telecom'),
    'IAC':   ('IAC Inc.',                               'Entretenimento'),
    'USFD':  ('US Foods Holding Corp.',                 'Varejo'),
    'EXE':   ('Expand Energy Corp.',                    'Energia'),
    'LGFA':  ('Lions Gate Entertainment A',             'Entretenimento'),
}
# Mapa ticker → setor
SETOR_MAP = {tk: v[1] for tk, v in NOMAD_STOCKS.items()}
NOME_MAP  = {tk: v[0] for tk, v in NOMAD_STOCKS.items()}

PERIODO = "1y"

def nome_curto(ticker):
    n = NOME_MAP.get(ticker, ticker)
    return n[:22] + "…" if len(n) > 22 else n


# =============================================================================
# FUNÇÕES DE ANÁLISE TÉCNICA
# =============================================================================

@st.cache_data(ttl=3600, show_spinner=False)
def buscar_dados(tickers_tuple):
    """Download OHLCV via yfinance. Cached por 1 hora."""
    tickers = list(tickers_tuple)
    try:
        df = yf.download(
            tickers,
            period=PERIODO,
            auto_adjust=True,
            progress=False,
            timeout=60,
            threads=True,
        )
        if df.empty:
            return pd.DataFrame()
        if not isinstance(df.columns, pd.MultiIndex):
            df.columns = pd.MultiIndex.from_tuples(
                [(c, tickers[0]) for c in df.columns]
            )
        df = df.dropna(axis=1, how='all')
        return df
    except Exception as e:
        st.error(f"Erro no download: {e}")
        return pd.DataFrame()


def calcular_indicadores(df, progress_bar=None):
    """Calcula RSI, Estocástico, EMAs, Bollinger, MACD."""
    df_calc = df.copy()
    tickers = df_calc.columns.get_level_values(1).unique()
    total = len(tickers)

    for i, ticker in enumerate(tickers):
        try:
            close = df_calc[('Close', ticker)]
            high  = df_calc[('High',  ticker)]
            low   = df_calc[('Low',   ticker)]

            # RSI 14
            delta = close.diff()
            ganho = delta.clip(lower=0).rolling(14).mean()
            perda = -delta.clip(upper=0).rolling(14).mean()
            rs    = ganho / perda.replace(0, np.nan)
            df_calc[('RSI14',    ticker)] = 100 - (100 / (1 + rs))

            # Estocástico %K
            ll = low.rolling(14).min()
            hh = high.rolling(14).max()
            rng = (hh - ll).replace(0, np.nan)
            df_calc[('Stoch_K',  ticker)] = 100 * ((close - ll) / rng)

            # EMAs
            df_calc[('EMA20',    ticker)] = close.ewm(span=20,  adjust=False).mean()
            df_calc[('EMA50',    ticker)] = close.ewm(span=50,  adjust=False).mean()
            df_calc[('EMA200',   ticker)] = close.ewm(span=200, adjust=False).mean()

            # Bollinger
            sma = close.rolling(20).mean()
            std = close.rolling(20).std()
            df_calc[('BB_Lower', ticker)] = sma - 2 * std
            df_calc[('BB_Upper', ticker)] = sma + 2 * std

            # MACD
            ema12 = close.ewm(span=12, adjust=False).mean()
            ema26 = close.ewm(span=26, adjust=False).mean()
            macd  = ema12 - ema26
            sig   = macd.ewm(span=9, adjust=False).mean()
            df_calc[('MACD_Hist', ticker)] = macd - sig

        except Exception:
            continue

        if progress_bar:
            progress_bar.progress((i + 1) / total)

    return df_calc


def calcular_fibonacci(df_ticker):
    try:
        if len(df_ticker) < 50:
            return None
        h = df_ticker['High'].max()
        l = df_ticker['Low'].min()
        return {'61.8%': l + (h - l) * 0.618}
    except Exception:
        return None


def classificar_score_tecnico(s):
    if s >= 4: return "Muito Alta"
    if s >= 2: return "Alta"
    if s >= 1: return "Média"
    return "Baixa"


def gerar_sinal(row, df_ticker):
    sinais, explicacoes, score = [], [], 0
    try:
        close    = row.get('Close')
        rsi      = row.get('RSI14')
        stoch    = row.get('Stoch_K')
        macd_h   = row.get('MACD_Hist')
        bb_lower = row.get('BB_Lower')
        ema200   = row.get('EMA200')

        if pd.notna(rsi):
            if rsi < 30:
                sinais.append("RSI Oversold"); score += 3
                explicacoes.append(f"📉 RSI {rsi:.1f} (<30): Forte sobrevenda")
            elif rsi < 40:
                sinais.append("RSI Baixo"); score += 1
                explicacoes.append(f"📊 RSI {rsi:.1f} (<40): Sobrevenda moderada")

        if pd.notna(stoch):
            if stoch < 20:
                sinais.append("Stoch. Fundo"); score += 2
                explicacoes.append(f"📉 Estoc. {stoch:.1f} (<20): Muito sobrevendido")
            elif stoch < 30:
                sinais.append("Stoch. Baixo"); score += 1
                explicacoes.append(f"📊 Estoc. {stoch:.1f} (<30): Sobrevendido")

        if pd.notna(close) and pd.notna(ema200) and close > ema200:
            sinais.append("Acima EMA200"); score += 2
            explicacoes.append("📈 Preço acima da EMA200: Tendência de alta")

        if pd.notna(macd_h) and macd_h > 0:
            sinais.append("MACD Virando"); score += 1
            explicacoes.append("🔄 MACD positivo: Momentum de alta começando")

        if pd.notna(close) and pd.notna(bb_lower):
            if close < bb_lower:
                sinais.append("Abaixo BB"); score += 2
                explicacoes.append("⚠️ Abaixo da Banda Inferior: Sobrevenda extrema")
            elif close < bb_lower * 1.02:
                sinais.append("Suporte BB"); score += 1
                explicacoes.append("🎯 Próximo da Banda Inferior: Zona de suporte")

        fibo = calcular_fibonacci(df_ticker)
        if fibo and pd.notna(close):
            f618 = fibo['61.8%']
            if f618 * 0.99 <= close <= f618 * 1.01:
                sinais.append("Fibo 61.8%"); score += 2
                explicacoes.append("⭐ Zona de Ouro Fibonacci (61.8%): Reversão provável!")

    except Exception:
        pass
    return sinais, score, classificar_score_tecnico(score), explicacoes


def calcular_liquidez(df_ticker, n=20):
    try:
        n = min(n, len(df_ticker))
        vol = df_ticker['Volume'].tail(n)
        vm  = vol.mean()
        if pd.isna(vm): vm = 0

        n_gaps = sum(
            1 for i in range(1, min(n + 1, len(df_ticker)))
            if df_ticker['Close'].iloc[-i-1] > 0 and
               abs((df_ticker['Open'].iloc[-i] - df_ticker['Close'].iloc[-i-1])
                   / df_ticker['Close'].iloc[-i-1]) * 100 > 1
        )
        consist = sum(1 for v in vol if pd.notna(v) and v >= vm * 0.8) / n if n > 0 else 0

        liq = 0
        if   vm > 50_000_000:  liq += 40
        elif vm > 10_000_000:  liq += 35
        elif vm >  5_000_000:  liq += 30
        elif vm >  1_000_000:  liq += 25
        elif vm >    500_000:  liq += 20
        elif vm >    100_000:  liq += 15
        else:                   liq += 5

        thresholds = [0, 1, 3, 6, 9, 13, 99]
        pts_gaps   = [30, 25, 20, 15, 10, 5, 5]
        for t, p in zip(thresholds, pts_gaps):
            if n_gaps <= t:
                liq += p
                break

        if   consist >= 0.75: liq += 30
        elif consist >= 0.50: liq += 20
        elif consist >= 0.25: liq += 10
        else:                  liq += 5

        return max(0, min(10, round(liq / 10)))
    except Exception:
        return 1


def analisar_oportunidades(df_calc, progress_bar=None):
    """Varre todos os tickers e retorna lista de oportunidades (em queda com sinais de reversão)."""
    resultados = []
    tickers = df_calc.columns.get_level_values(1).unique()
    total = len(tickers)

    for i, ticker in enumerate(tickers):
        try:
            df_t = df_calc.xs(ticker, axis=1, level=1).dropna()
            if len(df_t) < 50:
                continue

            last   = df_t.iloc[-1]
            ant    = df_t.iloc[-2]
            preco  = last.get('Close')
            p_ant  = ant.get('Close')
            p_open = last.get('Open')
            volume = last.get('Volume')

            if pd.isna(preco) or pd.isna(p_ant):
                continue

            queda_dia = (preco - p_ant) / p_ant * 100
            gap       = (p_open - p_ant) / p_ant * 100 if pd.notna(p_open) else 0

            if queda_dia >= 0:
                continue

            sinais, score_tec, potencial, explicacoes = gerar_sinal(last, df_t)

            rsi   = last.get('RSI14', 50)
            stoch = last.get('Stoch_K', 50)
            rsi   = 50.0 if pd.isna(rsi)   else float(rsi)
            stoch = 50.0 if pd.isna(stoch) else float(stoch)
            is_index = ((100 - rsi) + (100 - stoch)) / 2
            liq   = calcular_liquidez(df_t)

            resultados.append({
                'Ticker':      ticker,
                'Empresa':     nome_curto(ticker),
                'Setor':       SETOR_MAP.get(ticker, 'Outro'),
                'Preco':       round(preco, 2),
                'Volume':      volume,
                'Queda_Dia':   round(queda_dia, 2),
                'Gap':         round(gap, 2),
                'IS':          round(is_index, 1),
                'RSI14':       round(rsi, 1),
                'Stoch':       round(stoch, 1),
                'Potencial':   potencial,
                'Score_Tec':   score_tec,
                'Sinais':      ", ".join(sinais) if sinais else "—",
                'Explicacoes': explicacoes,
                'Liquidez':    liq,
                'Score_Fund':  None,
                'Classe_Fund': '—',
                'Score_Total': None,
            })
        except Exception:
            continue

        if progress_bar:
            progress_bar.progress((i + 1) / total)

    resultados.sort(key=lambda x: x['Queda_Dia'])
    return resultados


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_fundamentalista_cached(ticker):
    """Busca dados fundamentalistas para um ticker. Cached 1h."""
    try:
        stock = yf.Ticker(ticker)
        info  = stock.info
        if not info or len(info) < 5:
            return None

        score = 0
        detalhes = {}

        pe = info.get('trailingPE') or info.get('forwardPE')
        if pe and isinstance(pe, (int, float)):
            if   pe < 15:              score += 15
            elif pe < 25:              score += 10
            elif pe < 35:              score += 5
            elif pe > 60:              score -= 10
            detalhes['pe'] = round(pe, 2)

        dy = info.get('dividendYield')
        if dy and isinstance(dy, (int, float)):
            if   dy > 0.05: score += 10
            elif dy > 0.02: score += 7
            elif dy > 0:    score += 3
            detalhes['dy'] = round(dy * 100, 2)

        rg = info.get('revenueGrowth')
        if rg and isinstance(rg, (int, float)):
            if   rg > 0.20: score += 15
            elif rg > 0.10: score += 10
            elif rg > 0.05: score += 5
            elif rg < -0.10: score -= 10
            detalhes['rg'] = round(rg * 100, 1)

        rec = info.get('recommendationKey', '')
        pts_rec = {'strong_buy': 10, 'buy': 5, 'hold': 0, 'sell': -5, 'strong_sell': -10}
        score += pts_rec.get(rec, 0)
        detalhes['rec'] = rec.replace('_', ' ').title() if rec else 'N/A'

        mc = info.get('marketCap')
        if mc and isinstance(mc, (int, float)):
            if   mc > 1e12:   score += 10
            elif mc > 100e9:  score += 5
            detalhes['mc'] = mc

        score = max(0, min(100, score))
        if   score >= 80: classe = '🌟'
        elif score >= 65: classe = '✅'
        elif score >= 50: classe = '⚖️'
        elif score >= 35: classe = '⚠️'
        else:             classe = '🔴'

        return {
            'score':  score,
            'classe': classe,
            'detalhes': detalhes,
            'setor':  info.get('sector', ''),
        }
    except Exception:
        return None


def enriquecer_fundamentalista(oportunidades, top_n=25, progress_bar=None):
    """Busca dados fundamentalistas para os top_n por IS."""
    top = sorted(oportunidades, key=lambda x: x['IS'], reverse=True)[:top_n]
    tickers_top = [o['Ticker'] for o in top]
    fund_cache = {}

    for i, ticker in enumerate(tickers_top):
        fd = buscar_fundamentalista_cached(ticker)
        fund_cache[ticker] = fd
        if progress_bar:
            progress_bar.progress((i + 1) / len(tickers_top))

    for opp in oportunidades:
        tk = opp['Ticker']
        fd = fund_cache.get(tk)
        if fd:
            opp['Score_Fund']  = fd['score']
            opp['Classe_Fund'] = fd['classe']
            score_tec_norm     = min(100, opp['Score_Tec'] * 15)
            opp['Score_Total'] = round(score_tec_norm * 0.60 + fd['score'] * 0.40, 1)
        else:
            opp['Score_Total'] = round(min(100, opp['Score_Tec'] * 15) * 0.60, 1)

    return oportunidades, fund_cache


# =============================================================================
# FILTROS
# =============================================================================

def aplicar_filtros(oportunidades, df_calc,
                    ema20=False, ema50=False, ema200=False,
                    setor=None, potencial_min=None,
                    is_min=0, liq_min=0):
    ordens = {'Baixa': 0, 'Média': 1, 'Alta': 2, 'Muito Alta': 3}
    filtradas = []
    for opp in oportunidades:
        tk = opp['Ticker']

        if setor and setor != 'Todos' and opp['Setor'] != setor:
            continue
        if potencial_min and potencial_min != 'Todos':
            if ordens.get(opp['Potencial'], -1) < ordens.get(potencial_min, 0):
                continue
        if is_min > 0 and opp['IS'] < is_min:
            continue
        if liq_min > 0 and opp.get('Liquidez', 0) < liq_min:
            continue

        if (ema20 or ema50 or ema200) and df_calc is not None:
            try:
                df_t  = df_calc.xs(tk, axis=1, level=1).dropna()
                preco = df_t['Close'].iloc[-1]
                ok = True
                if ema20  and (preco <= df_t.get('EMA20',  pd.Series([0])).iloc[-1]): ok = False
                if ema50  and ok and (preco <= df_t.get('EMA50',  pd.Series([0])).iloc[-1]): ok = False
                if ema200 and ok and (preco <= df_t.get('EMA200', pd.Series([0])).iloc[-1]): ok = False
                if not ok:
                    continue
            except Exception:
                continue

        filtradas.append(opp)
    return filtradas


# =============================================================================
# GRÁFICO PLOTLY
# =============================================================================

def plotar_grafico_plotly(df_ticker, ticker, fund_data=None):
    empresa = NOME_MAP.get(ticker, ticker)
    setor   = SETOR_MAP.get(ticker, '')

    close  = df_ticker['Close']
    ema20  = df_ticker.get('EMA20')
    ema50  = df_ticker.get('EMA50')
    ema200 = df_ticker.get('EMA200')
    bb_low = df_ticker.get('BB_Lower')
    bb_up  = df_ticker.get('BB_Upper')
    rsi_s  = df_ticker.get('RSI14')
    stoch_s= df_ticker.get('Stoch_K')

    # Fibonacci
    h = df_ticker['High'].max()
    l = df_ticker['Low'].min()
    d = h - l
    fibs = {
        '0%':    h,
        '23.6%': h - d * 0.236,
        '38.2%': h - d * 0.382,
        '50%':   h - d * 0.5,
        '61.8%': h - d * 0.618,
        '78.6%': h - d * 0.786,
        '100%':  l,
    }
    fib_cores = {
        '0%':    '#ef5350', '23.6%': '#ff7043', '38.2%': '#ffa726',
        '50%':   '#42a5f5', '61.8%': '#66bb6a', '78.6%': '#26a69a', '100%': '#ab47bc'
    }

    fund_str = ""
    if fund_data:
        fund_str = f" | Fundamentalista: {fund_data['classe']} {fund_data['score']:.0f}/100"

    fig = make_subplots(
        rows=3, cols=1,
        row_heights=[0.6, 0.2, 0.2],
        shared_xaxes=True,
        vertical_spacing=0.04,
        subplot_titles=[
            f"📈 {ticker} — {empresa} [{setor}]{fund_str}",
            "RSI 14",
            "Estocástico %K",
        ]
    )

    # ── Candlestick ───────────────────────────────────────────────────────────
    if 'Open' in df_ticker.columns and 'High' in df_ticker.columns and 'Low' in df_ticker.columns:
        fig.add_trace(go.Candlestick(
            x=df_ticker.index,
            open=df_ticker['Open'], high=df_ticker['High'],
            low=df_ticker['Low'],   close=close,
            name='OHLC',
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350',
            showlegend=False,
        ), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(x=close.index, y=close, name='Fechamento',
                                  line=dict(color='#90caf9', width=1.5)), row=1, col=1)

    # ── Bollinger ─────────────────────────────────────────────────────────────
    if bb_low is not None and bb_up is not None:
        fig.add_trace(go.Scatter(
            x=bb_up.index, y=bb_up, name='BB Superior',
            line=dict(color='rgba(120,144,156,0.6)', width=1, dash='dot'),
            showlegend=False,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=bb_low.index, y=bb_low, name='BB Inferior',
            line=dict(color='rgba(120,144,156,0.6)', width=1, dash='dot'),
            fill='tonexty', fillcolor='rgba(120,144,156,0.06)',
            showlegend=False,
        ), row=1, col=1)

    # ── EMAs ──────────────────────────────────────────────────────────────────
    if ema20  is not None:
        fig.add_trace(go.Scatter(x=ema20.index,  y=ema20,  name='EMA20',
                                  line=dict(color='#42a5f5', width=1.3)), row=1, col=1)
    if ema50  is not None:
        fig.add_trace(go.Scatter(x=ema50.index,  y=ema50,  name='EMA50',
                                  line=dict(color='#ff7043', width=1.3)), row=1, col=1)
    if ema200 is not None:
        fig.add_trace(go.Scatter(x=ema200.index, y=ema200, name='EMA200',
                                  line=dict(color='#66bb6a', width=2.0)), row=1, col=1)

    # ── Fibonacci levels ──────────────────────────────────────────────────────
    for nivel, pf in fibs.items():
        cor = fib_cores[nivel]
        fig.add_hline(y=pf, line_dash="dot", line_color=cor, line_width=0.8,
                      annotation_text=f" {nivel}", annotation_position="right",
                      annotation_font_color=cor, annotation_font_size=10, row=1, col=1)

    # ── RSI ───────────────────────────────────────────────────────────────────
    if rsi_s is not None:
        fig.add_trace(go.Scatter(x=rsi_s.index, y=rsi_s, name='RSI14',
                                  line=dict(color='#ff8f00', width=1.5)), row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#ef5350", line_width=1, row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="#66bb6a", line_width=1, row=2, col=1)
        fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(239,83,80,0.08)",  row=2, col=1)
        fig.add_hrect(y0=70, y1=100, fillcolor="rgba(102,187,106,0.08)", row=2, col=1)

    # ── Estocástico ───────────────────────────────────────────────────────────
    if stoch_s is not None:
        fig.add_trace(go.Scatter(x=stoch_s.index, y=stoch_s, name='Stoch %K',
                                  line=dict(color='#ce93d8', width=1.5)), row=3, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="#ef5350", line_width=1, row=3, col=1)
        fig.add_hline(y=80, line_dash="dash", line_color="#66bb6a", line_width=1, row=3, col=1)
        fig.add_hrect(y0=0,  y1=20,  fillcolor="rgba(239,83,80,0.08)",  row=3, col=1)
        fig.add_hrect(y0=80, y1=100, fillcolor="rgba(102,187,106,0.08)", row=3, col=1)

    fig.update_layout(
        height=650,
        template='plotly_dark',
        paper_bgcolor='#0e1117',
        plot_bgcolor='#0e1117',
        legend=dict(orientation='h', y=1.05, x=0),
        margin=dict(l=40, r=40, t=60, b=20),
        xaxis_rangeslider_visible=False,
    )
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')

    return fig

# =============================================================================
# INTERFACE STREAMLIT — HELPERS
# =============================================================================

def cor_is(val):
    if val >= 75: return "🔴"
    if val >= 60: return "🟠"
    if val >= 45: return "🟡"
    return "⚪"

def formatar_volume(v):
    if pd.isna(v) or v is None: return "—"
    v = float(v)
    if v >= 1e9:  return f"{v/1e9:.1f}B"
    if v >= 1e6:  return f"{v/1e6:.1f}M"
    if v >= 1e3:  return f"{v/1e3:.0f}K"
    return str(int(v))


# =============================================================================
# STREAMLIT MAIN
# =============================================================================

def main():
    import plotly.express as px

    fuso  = pytz.timezone("America/Sao_Paulo")
    agora = datetime.now(fuso)
    dias_pt = {
        "Monday":"Segunda","Tuesday":"Terça","Wednesday":"Quarta",
        "Thursday":"Quinta","Friday":"Sexta","Saturday":"Sábado","Sunday":"Domingo"
    }
    dia_pt = dias_pt.get(agora.strftime("%A"), agora.strftime("%A"))
    data_str = agora.strftime("%d/%m/%Y às %H:%M")

    st.markdown(
        f'<div class="header-box"><h1>📊 Monitor de Ações Nomad — Swing Trade Pro</h1>'
        f'<p>{dia_pt}, {data_str} (Brasília) &nbsp;|&nbsp; ~992 tickers · NYSE + Nasdaq · ETFs · ADRs</p></div>',
        unsafe_allow_html=True
    )

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## ⚙️ Configurações")
        st.markdown("### 🔍 Varredura")

        todos_setores = sorted(set(SETOR_MAP.values()))
        setores_sel = st.multiselect(
            "Setores (vazio = todos)", options=todos_setores, default=[],
            help="Deixe em branco para varrer todos os ~992 tickers"
        )
        n_tickers_placeholder = st.empty()

        st.markdown("---")
        st.markdown("### 🎯 Filtros de Resultado")
        col1, col2 = st.columns(2)
        with col1:
            is_min = st.slider("I.S. mínimo", 0, 100, 0, 5,
                               help="0=sem filtro | 75+=extremo")
        with col2:
            liq_min = st.slider("Liquidez mín.", 0, 10, 0)

        potencial_min = st.selectbox("Potencial mínimo",
                                     ["Todos", "Média", "Alta", "Muito Alta"])

        st.markdown("### 📈 EMAs (tendência de alta)")
        ema20_on  = st.checkbox("Acima da EMA20  (curto prazo)")
        ema50_on  = st.checkbox("Acima da EMA50  (médio prazo)")
        ema200_on = st.checkbox("Acima da EMA200 (longo prazo)")

        st.markdown("---")
        st.markdown("### 💼 Fundamentalista")
        top_n_fund = st.slider("Top N análise fundamentalista", 5, 50, 25, 5)

        st.markdown("---")
        executar = st.button("🚀 Executar Varredura", type="primary",
                             use_container_width=True)

        st.markdown("---")
        st.caption("⚠️ Apenas fins educacionais. Não constitui recomendação de investimento.")

    # ── Seleciona tickers ─────────────────────────────────────────────────────
    if setores_sel:
        tickers_filtro = [tk for tk, v in NOMAD_STOCKS.items() if v[1] in setores_sel]
    else:
        tickers_filtro = list(NOMAD_STOCKS.keys())

    n_tickers_placeholder.caption(f"🔢 {len(tickers_filtro)} tickers na varredura")

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_dash, tab_grafico, tab_sobre = st.tabs(
        ["📊 Dashboard", "📈 Gráfico Técnico", "ℹ️ Sobre"]
    )

    # =========================================================================
    # TAB DASHBOARD
    # =========================================================================
    with tab_dash:
        if not executar and "oportunidades" not in st.session_state:
            st.info("👈 Configure os filtros na barra lateral e clique em **🚀 Executar Varredura**.")
            st.markdown("""
### Como usar
1. **Setores** — filtre por setor ou deixe em branco para varrer tudo (~992 tickers)  
2. **I.S.** — Índice de Sobrevenda: soma de RSI e Estocástico invertidos; quanto maior, mais sobrevendido  
3. **EMAs** — exige que o preço esteja acima das médias (busca correções em tendência de alta)  
4. **Potencial** — classificação baseada no número de sinais técnicos detectados  
5. Selecione um ticker na tabela para ver o **gráfico na aba ao lado**

### Indicadores calculados
- **RSI 14** — Relative Strength Index
- **Estocástico %K** — Momentum sobrecomprado/sobrevendido
- **EMA 20 / 50 / 200** — Médias móveis exponenciais
- **Bandas de Bollinger** — Volatilidade e reversão
- **MACD** — Momentum e virada
- **Fibonacci 61.8%** — Zona dourada de reversão
            """)
            return

        if executar:
            st.markdown("#### ⬇️ Baixando dados de mercado...")
            pb1 = st.progress(0, text="Conectando ao Yahoo Finance...")
            with st.spinner(f"Baixando {len(tickers_filtro)} tickers (1 ano)..."):
                df = buscar_dados(tuple(sorted(tickers_filtro)))
            pb1.progress(100, text="✅ Download concluído")

            if df.empty:
                st.error("❌ Falha no download. Verifique a conexão.")
                return

            n_ok = len(df.columns.get_level_values(1).unique())
            st.success(f"✅ {df.shape[0]} dias históricos | {n_ok} tickers válidos")

            st.markdown("#### 🔢 Calculando indicadores técnicos...")
            pb2 = st.progress(0, text="RSI, EMAs, Bollinger, MACD...")
            df_calc = calcular_indicadores(df, pb2)
            pb2.progress(100, text="✅ Indicadores prontos")

            st.markdown("#### 🔍 Varrendo oportunidades...")
            pb3 = st.progress(0, text="Detectando quedas com sinais de reversão...")
            oportunidades = analisar_oportunidades(df_calc, pb3)
            pb3.progress(100, text=f"✅ {len(oportunidades)} oportunidades detectadas")

            if oportunidades:
                st.markdown(f"#### 💼 Análise fundamentalista (top {top_n_fund})...")
                pb4 = st.progress(0, text="Buscando dados fundamentalistas...")
                oportunidades, fund_cache = enriquecer_fundamentalista(
                    oportunidades, top_n=top_n_fund, progress_bar=pb4)
                pb4.progress(100, text="✅ Fundamentalista concluído")

                st.session_state["oportunidades"] = oportunidades
                st.session_state["df_calc"]       = df_calc
                st.session_state["fund_cache"]    = fund_cache
            else:
                st.warning("Nenhuma oportunidade detectada.")
                return

        oportunidades = st.session_state.get("oportunidades", [])
        df_calc       = st.session_state.get("df_calc")
        fund_cache    = st.session_state.get("fund_cache", {})

        if not oportunidades:
            return

        # Aplica filtros
        filtradas = aplicar_filtros(
            oportunidades, df_calc,
            ema20=ema20_on, ema50=ema50_on, ema200=ema200_on,
            setor=None,
            potencial_min=potencial_min if potencial_min != "Todos" else None,
            is_min=is_min, liq_min=liq_min,
        )

        # Métricas de topo
        st.markdown("---")
        df_opp = pd.DataFrame(oportunidades)
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("🔍 Total encontradas", len(oportunidades))
        c2.metric("✅ Após filtros",       len(filtradas))
        c3.metric("🔥 I.S. médio",         f"{df_opp['IS'].mean():.1f}")
        c4.metric("📉 Maior queda",
                  f"{df_opp['Queda_Dia'].min():.2f}%", delta_color="inverse")
        c5.metric("🌟 Potencial Muito Alta",
                  len([o for o in oportunidades if o["Potencial"] == "Muito Alta"]))

        st.markdown("---")
        if not filtradas:
            st.warning("⚠️ Nenhum resultado após os filtros.")
            return

        df_fil = pd.DataFrame(filtradas)

        # Top highlights
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("#### 🔥 Top 5 — Mais Sobrevendidos (I.S.)")
            for o in sorted(filtradas, key=lambda x: x["IS"], reverse=True)[:5]:
                st.markdown(
                    f"**{o['Ticker']}** `{o['Empresa']}`  "
                    f"IS={cor_is(o['IS'])} **{o['IS']:.0f}**  "
                    f"Queda: 🔴 **{o['Queda_Dia']:.2f}%**  `{o['Setor']}`"
                )
        with col_r:
            st.markdown("#### 📉 Top 5 — Maiores Quedas do Dia")
            for o in sorted(filtradas, key=lambda x: x["Queda_Dia"])[:5]:
                st.markdown(
                    f"**{o['Ticker']}** `{o['Empresa']}`  "
                    f"**{o['Queda_Dia']:.2f}%**  IS={o['IS']:.0f}  `{o['Setor']}`"
                )

        # Top Score Total
        df_score = df_fil[df_fil["Score_Total"].notna()].nlargest(5, "Score_Total")
        if not df_score.empty:
            st.markdown("#### 🌟 Top 5 — Score Total (Técnico + Fundamentalista)")
            sc_cols = st.columns(min(5, len(df_score)))
            for col, (_, r) in zip(sc_cols, df_score.iterrows()):
                col.metric(
                    label=f"{r['Ticker']} {r['Classe_Fund']}",
                    value=f"Score {r['Score_Total']:.0f}",
                    delta=f"{r['Queda_Dia']:.2f}%",
                    delta_color="inverse"
                )

        # Gráfico por setor
        st.markdown("---")
        st.markdown("#### 📊 Oportunidades por Setor")
        sc_df = df_fil["Setor"].value_counts().reset_index()
        sc_df.columns = ["Setor", "Qtd"]
        fig_bar = px.bar(sc_df, x="Setor", y="Qtd",
                         color="Qtd", color_continuous_scale="Blues",
                         template="plotly_dark", height=300)
        fig_bar.update_layout(
            paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
            margin=dict(l=10, r=10, t=10, b=80),
            coloraxis_showscale=False, xaxis_tickangle=-45
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # Tabela
        st.markdown("---")
        st.markdown(f"#### 📋 Tabela de Oportunidades — {len(filtradas)} ativos")

        cols_show = ["Ticker","Empresa","Setor","Preco","Queda_Dia","IS",
                     "RSI14","Stoch","Potencial","Score_Tec","Classe_Fund",
                     "Score_Total","Sinais","Liquidez"]
        df_show = df_fil[cols_show].copy()
        df_show = df_show.rename(columns={
            "Preco":"Preço(USD)","Queda_Dia":"Queda%","IS":"I.S.",
            "Stoch":"Stoch%K","Score_Tec":"Sc.Tec",
            "Classe_Fund":"Fund.","Score_Total":"Sc.Total"
        })
        df_show["Preço(USD)"] = df_show["Preço(USD)"].map(lambda x: f"${x:.2f}")
        df_show["Queda%"]     = df_show["Queda%"].map(lambda x: f"{x:.2f}%")
        df_show["I.S."]       = df_show["I.S."].map(lambda x: f"{x:.1f}")
        df_show["RSI14"]      = df_show["RSI14"].map(lambda x: f"{x:.1f}")
        df_show["Stoch%K"]    = df_show["Stoch%K"].map(lambda x: f"{x:.1f}")
        df_show["Sc.Total"]   = df_show["Sc.Total"].map(
            lambda x: f"{x:.0f}" if x is not None else "—")

        def highlight_rows(row):
            styles = [""] * len(row)
            idx = list(row.index)
            try:
                is_v = float(row["I.S."])
                if is_v >= 75:
                    styles[idx.index("I.S.")] = "background-color:#b71c1c;color:white;font-weight:bold"
                elif is_v >= 60:
                    styles[idx.index("I.S.")] = "background-color:#e65100;color:white"
            except Exception: pass
            try:
                pot_map = {
                    "Muito Alta": "background-color:#1b5e20;color:white;font-weight:bold",
                    "Alta":       "background-color:#33691e;color:white;font-weight:bold",
                    "Média":      "background-color:#bf360c;color:white",
                    "Baixa":      "background-color:#37474f;color:#ccc",
                }
                styles[idx.index("Potencial")] = pot_map.get(row["Potencial"], "")
            except Exception: pass
            return styles

        styled = df_show.reset_index(drop=True).style.apply(highlight_rows, axis=1)
        st.dataframe(styled, use_container_width=True, height=480)

        # Download CSV
        csv_data = df_fil.drop(columns=["Explicacoes"], errors="ignore").to_csv(index=False)
        st.download_button(
            label="⬇️ Baixar CSV",
            data=csv_data,
            file_name=f"nomad_{agora.strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )

        # Seletor para gráfico
        st.markdown("---")
        st.markdown("#### 📈 Selecione um ticker para o gráfico detalhado")
        tickers_disp = [o["Ticker"] for o in filtradas]
        ticker_sel = st.selectbox(
            "Ticker",
            tickers_disp,
            format_func=lambda t: f"{t} — {nome_curto(t)} ({SETOR_MAP.get(t,'')})"
        )
        if ticker_sel:
            st.session_state["ticker_grafico"] = ticker_sel
            st.info(f"✅ **{ticker_sel}** selecionado. Vá para a aba **📈 Gráfico Técnico**.")

    # =========================================================================
    # TAB GRÁFICO
    # =========================================================================
    with tab_grafico:
        st.markdown("### 📈 Análise Técnica Detalhada")

        df_calc    = st.session_state.get("df_calc")
        fund_cache = st.session_state.get("fund_cache", {})

        ticker_input = st.text_input(
            "Digite o ticker (ex: AAPL, NVDA, MELI)",
            value=st.session_state.get("ticker_grafico", "NVDA"),
            max_chars=10,
        ).upper().strip()

        gerar_btn = st.button("📊 Gerar Gráfico", type="primary")

        if gerar_btn or (df_calc is not None and ticker_input):
            if df_calc is None:
                st.warning("⚠️ Execute a varredura primeiro na aba **📊 Dashboard**.")
            else:
                tickers_ok = df_calc.columns.get_level_values(1).unique()
                if ticker_input not in tickers_ok:
                    st.error(f"Ticker '{ticker_input}' não encontrado. Execute a varredura incluindo o setor correspondente.")
                else:
                    try:
                        df_t = df_calc.xs(ticker_input, axis=1, level=1).dropna()
                        fd   = fund_cache.get(ticker_input)

                        last  = df_t.iloc[-1]
                        rsi_v = float(last.get("RSI14", 50))
                        st_v  = float(last.get("Stoch_K", 50))
                        is_v  = ((100 - rsi_v) + (100 - st_v)) / 2

                        gc1, gc2, gc3, gc4, gc5 = st.columns(5)
                        gc1.metric("Ticker",    ticker_input)
                        gc2.metric("Preço",     f"${last.get('Close',0):.2f}")
                        gc3.metric("RSI 14",    f"{rsi_v:.1f}")
                        gc4.metric("Estoc. %K", f"{st_v:.1f}")
                        gc5.metric("I.S.",      f"{is_v:.1f}")

                        fig = plotar_grafico_plotly(df_t, ticker_input, fd)
                        st.plotly_chart(fig, use_container_width=True)

                        sinais, _, _, explicacoes = gerar_sinal(last, df_t)
                        if explicacoes:
                            st.markdown("#### 📋 Sinais Detectados")
                            for exp in explicacoes:
                                st.markdown(f"- {exp}")

                        # Fundamentalista
                        if not fd:
                            with st.spinner(f"Buscando dados fundamentalistas para {ticker_input}..."):
                                fd = buscar_fundamentalista_cached(ticker_input)

                        if fd:
                            det = fd.get("detalhes", {})
                            st.markdown("---")
                            st.markdown("#### 💼 Análise Fundamentalista")
                            fc1, fc2, fc3, fc4, fc5 = st.columns(5)
                            fc1.metric("Score Fund.",  f"{fd['score']:.0f}/100 {fd['classe']}")
                            fc2.metric("P/E Ratio",    str(det.get("pe", "N/A")))
                            fc3.metric("Dividend %",   f"{det.get('dy',0):.2f}%" if "dy" in det else "N/A")
                            fc4.metric("Rev. Growth",  f"{det.get('rg',0):.1f}%" if "rg" in det else "N/A")
                            fc5.metric("Recomendação", det.get("rec", "N/A"))

                    except Exception as e:
                        st.error(f"Erro ao gerar gráfico: {e}")

    # =========================================================================
    # TAB SOBRE
    # =========================================================================
    with tab_sobre:
        st.markdown("""
## 📊 Nomad Swing Trade Pro

Scanner de oportunidades de swing trade para investidores brasileiros que operam
ações e ETFs no mercado americano via **conta Nomad**.

### Como funciona
1. **Download** de dados históricos (1 ano) via Yahoo Finance para ~992 tickers
2. **Cálculo** de indicadores técnicos: RSI, Estocástico, EMA20/50/200, Bollinger, MACD, Fibonacci
3. **Detecção** de ativos em queda no dia com sinais de reversão técnica
4. **Análise fundamentalista** para os ativos mais sobrevendidos (P/E, dividend yield, crescimento de receita, recomendação de analistas, market cap)
5. **Score combinado** = 60% técnico + 40% fundamentalista

### Índice de Sobrevenda (I.S.)
```
I.S. = ((100 - RSI14) + (100 - Stoch%K)) / 2
```
- **≥ 75** → Sobrevenda extrema 🔴
- **60–74** → Sobrevenda forte 🟠
- **45–59** → Moderada 🟡
- **< 45**  → Normal ⚪

### Potencial Técnico
- **Muito Alta** → 4+ sinais simultâneos
- **Alta** → 2–3 sinais
- **Média** → 1 sinal
- **Baixa** → 0 sinais

### Universo de ativos (~992 tickers)
ETFs, Tecnologia, Semicondutores, Software, IA & Dados, Cibersegurança,
E-commerce, Fintech, Bancos, Saúde, Biotech, Varejo, Energia, Utilities,
Indústria, Automotivo, REITs, Materiais, Telecom, LatAm, Ásia e muito mais.

---
⚠️ **Aviso Legal**: Este aplicativo é para fins **exclusivamente educacionais**.
Não constitui recomendação de investimento. Rentabilidade passada não garante resultados futuros.
        """)
        st.caption("Versão 2.2 · Dados: Yahoo Finance (yfinance) · Deploy: Streamlit Cloud")


# =============================================================================
# ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    main()
