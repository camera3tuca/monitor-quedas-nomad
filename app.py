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

st.set_page_config(
    page_title="Nomad Swing Trade Pro",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
    /* ── Cabeçalho ── */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-title {
        color: white; font-size: 2.2rem; font-weight: 700;
        margin: 0; text-align: center;
    }
    .main-subtitle {
        color: rgba(255,255,255,0.9); font-size: 1rem;
        text-align: center; margin-top: 0.5rem;
    }

    /* ── Botões ── */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important; font-weight: 600 !important;
        border: none !important; padding: 0.75rem 2rem !important;
        border-radius: 8px !important; transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102,126,234,0.4) !important;
    }

    /* ── Seções ── */
    .section-header {
        color: #667eea; font-size: 1.4rem; font-weight: 600;
        margin-top: 1.5rem; margin-bottom: 0.75rem;
        padding-bottom: 0.4rem; border-bottom: 2px solid #667eea;
    }

    /* ── Caixas de dica ── */
    .tip-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 0.85rem 1rem; border-radius: 8px; margin-bottom: 1rem;
    }
    .tip-box p { margin: 0; color: #334155; font-size: 0.9rem; }

    /* ── Prompt de seleção ── */
    .select-prompt {
        background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
        padding: 1.75rem 2rem; border-radius: 8px;
        text-align: center; margin: 1.5rem 0;
    }
    .select-prompt p { margin: 0; color: #3730a3; font-size: 1rem; font-weight: 500; }

    /* ── Métricas ── */
    div[data-testid="metric-container"] {
        background: white; border: 1px solid #e2e8f0;
        padding: 0.8rem 1rem; border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    /* ── Checkboxes ── */
    .stCheckbox { background: white; padding: 0.75rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }

    /* ── Alertas ── */
    .stAlert { border-radius: 8px; }

    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


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

SETOR_MAP = {tk: v[1] for tk, v in NOMAD_STOCKS.items()}
NOME_MAP  = {tk: v[0] for tk, v in NOMAD_STOCKS.items()}
PERIODO   = "1y"

def nome_curto(ticker, maxlen=26):
    n = NOME_MAP.get(ticker, ticker)
    return n[:maxlen] + "…" if len(n) > maxlen else n

# =============================================================================
# FUNÇÕES DE ANÁLISE TÉCNICA
# =============================================================================

@st.cache_data(ttl=3600, show_spinner=False)
def buscar_dados(tickers_tuple):
    tickers = list(tickers_tuple)
    try:
        df = yf.download(tickers, period=PERIODO, auto_adjust=True,
                         progress=False, timeout=60, threads=True)
        if df.empty:
            return pd.DataFrame()
        if not isinstance(df.columns, pd.MultiIndex):
            df.columns = pd.MultiIndex.from_tuples([(c, tickers[0]) for c in df.columns])
        return df.dropna(axis=1, how='all')
    except Exception as e:
        st.error(f"Erro no download: {e}")
        return pd.DataFrame()


def calcular_indicadores(df):
    df_calc = df.copy()
    tickers = df_calc.columns.get_level_values(1).unique()
    pb = st.progress(0, text="Calculando indicadores…")
    for i, ticker in enumerate(tickers):
        try:
            close = df_calc[('Close', ticker)]
            high  = df_calc[('High',  ticker)]
            low   = df_calc[('Low',   ticker)]
            delta = close.diff()
            g = delta.clip(lower=0).rolling(14).mean()
            p = (-delta.clip(upper=0)).rolling(14).mean().replace(0, np.nan)
            df_calc[('RSI14',    ticker)] = 100 - (100 / (1 + g / p))
            ll = low.rolling(14).min(); hh = high.rolling(14).max()
            df_calc[('Stoch_K',  ticker)] = 100 * ((close - ll) / (hh - ll).replace(0, np.nan))
            df_calc[('EMA20',    ticker)] = close.ewm(span=20,  adjust=False).mean()
            df_calc[('EMA50',    ticker)] = close.ewm(span=50,  adjust=False).mean()
            df_calc[('EMA200',   ticker)] = close.ewm(span=200, adjust=False).mean()
            sma = close.rolling(20).mean(); std = close.rolling(20).std()
            df_calc[('BB_Lower', ticker)] = sma - 2 * std
            df_calc[('BB_Upper', ticker)] = sma + 2 * std
            e12 = close.ewm(span=12, adjust=False).mean()
            e26 = close.ewm(span=26, adjust=False).mean()
            macd = e12 - e26
            df_calc[('MACD_Hist', ticker)] = macd - macd.ewm(span=9, adjust=False).mean()
        except Exception:
            pass
        pb.progress((i + 1) / len(tickers))
    pb.empty()
    return df_calc


def calcular_fibonacci(df_t):
    try:
        h = df_t['High'].max(); l = df_t['Low'].min()
        return {'61.8%': l + (h - l) * 0.618}
    except Exception:
        return None


def classificar(s):
    if s >= 4: return "Muito Alta"
    if s >= 2: return "Alta"
    if s >= 1: return "Média"
    return "Baixa"


def gerar_sinal(row, df_t):
    sinais, explicacoes, score = [], [], 0
    try:
        close  = row.get('Close');  rsi    = row.get('RSI14'); stoch  = row.get('Stoch_K')
        macd_h = row.get('MACD_Hist'); bb_low = row.get('BB_Lower'); ema200 = row.get('EMA200')
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
        if pd.notna(close) and pd.notna(bb_low):
            if close < bb_low:
                sinais.append("Abaixo BB"); score += 2
                explicacoes.append("⚠️ Abaixo da Banda Inferior: Sobrevenda extrema")
            elif close < bb_low * 1.02:
                sinais.append("Suporte BB"); score += 1
                explicacoes.append("🎯 Próximo da Banda Inferior: Zona de suporte")
        fibo = calcular_fibonacci(df_t)
        if fibo and pd.notna(close):
            f618 = fibo['61.8%']
            if f618 * 0.99 <= close <= f618 * 1.01:
                sinais.append("Fibo 61.8%"); score += 2
                explicacoes.append("⭐ Zona de Ouro Fibonacci 61.8%: Reversão provável!")
    except Exception:
        pass
    return sinais, score, classificar(score), explicacoes


def calcular_liquidez(df_t, n=20):
    try:
        n = min(n, len(df_t))
        vol = df_t['Volume'].tail(n); vm = vol.mean()
        if pd.isna(vm): vm = 0
        n_gaps = sum(1 for i in range(1, min(n+1, len(df_t)))
                     if df_t['Close'].iloc[-i-1] > 0 and
                     abs((df_t['Open'].iloc[-i] - df_t['Close'].iloc[-i-1])
                         / df_t['Close'].iloc[-i-1]) * 100 > 1)
        consist = sum(1 for v in vol if pd.notna(v) and v >= vm * 0.8) / n if n > 0 else 0
        liq = (40 if vm > 50e6 else 35 if vm > 10e6 else 30 if vm > 5e6 else
               25 if vm > 1e6 else 20 if vm > 500e3 else 15 if vm > 100e3 else 5)
        for t, p in zip([0, 1, 3, 6, 9, 13, 99], [30, 25, 20, 15, 10, 5, 5]):
            if n_gaps <= t: liq += p; break
        liq += 30 if consist >= 0.75 else 20 if consist >= 0.50 else 10 if consist >= 0.25 else 5
        return max(0, min(10, round(liq / 10)))
    except Exception:
        return 1


def analisar_oportunidades(df_calc):
    resultados = []
    tickers = df_calc.columns.get_level_values(1).unique()
    pb = st.progress(0, text="Varrendo oportunidades…")
    for i, ticker in enumerate(tickers):
        try:
            df_t = df_calc.xs(ticker, axis=1, level=1).dropna()
            if len(df_t) < 50: continue
            last = df_t.iloc[-1]; ant = df_t.iloc[-2]
            preco = last.get('Close'); p_ant = ant.get('Close')
            if pd.isna(preco) or pd.isna(p_ant): continue
            queda = (preco - p_ant) / p_ant * 100
            if queda >= 0: continue
            p_open = last.get('Open')
            gap = (p_open - p_ant) / p_ant * 100 if pd.notna(p_open) else 0
            sinais, score_tec, potencial, explicacoes = gerar_sinal(last, df_t)
            rsi   = float(last.get('RSI14',   50) or 50)
            stoch = float(last.get('Stoch_K', 50) or 50)
            is_index = ((100 - rsi) + (100 - stoch)) / 2
            liq = calcular_liquidez(df_t)
            resultados.append({
                'Ticker':      ticker,
                'Empresa':     nome_curto(ticker),
                'Setor':       SETOR_MAP.get(ticker, 'Outro'),
                'Liquidez':    liq,
                'Preco':       round(preco, 2),
                'Queda_Dia':   round(queda, 2),
                'IS':          round(is_index, 1),
                'Volume':      int(last.get('Volume', 0) or 0),
                'Gap':         round(gap, 2),
                'Potencial':   potencial,
                'Score':       score_tec,
                'RSI14':       round(rsi, 1),
                'Stoch':       round(stoch, 1),
                'Sinais':      ", ".join(sinais) if sinais else "—",
                'Explicacoes': explicacoes,
            })
        except Exception:
            pass
        pb.progress((i + 1) / len(tickers))
    pb.empty()
    resultados.sort(key=lambda x: x['Queda_Dia'])
    return resultados


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_fundamentalista(ticker):
    try:
        info = yf.Ticker(ticker).info
        if not info or len(info) < 5: return None
        score = 50; det = {}
        pe = info.get('trailingPE') or info.get('forwardPE')
        if pe and isinstance(pe, (int, float)):
            det['pe'] = round(pe, 2)
            if 10 <= pe <= 25:   score += 15; det['pe_pts'] = '+15'; det['pe_av'] = 'Ótimo (10-25)'
            elif pe <= 35:       score += 10; det['pe_pts'] = '+10'; det['pe_av'] = 'Bom (25-35)'
            elif pe > 50:        score -= 10; det['pe_pts'] = '-10'; det['pe_av'] = 'Muito alto (>50)'
            else:                             det['pe_pts'] = '+0';  det['pe_av'] = 'Regular (35-50)'
        dy = info.get('dividendYield')
        if dy and isinstance(dy, (int, float)):
            det['dy'] = round(dy * 100, 2)
            if dy > 0.04:   score += 10; det['dy_pts'] = '+10'; det['dy_av'] = 'Excelente (>4%)'
            elif dy > 0.02: score += 5;  det['dy_pts'] = '+5';  det['dy_av'] = 'Bom (>2%)'
            else:                        det['dy_pts'] = '+3';  det['dy_av'] = 'Baixo (<2%)'
        rg = info.get('revenueGrowth')
        if rg and isinstance(rg, (int, float)):
            det['rg'] = round(rg * 100, 1)
            if rg > 0.20:    score += 15; det['rg_pts'] = '+15'; det['rg_av'] = 'Excelente (>20%)'
            elif rg > 0.10:  score += 10; det['rg_pts'] = '+10'; det['rg_av'] = 'Muito bom (>10%)'
            elif rg > 0.05:  score += 5;  det['rg_pts'] = '+5';  det['rg_av'] = 'Bom (>5%)'
            elif rg < -0.10: score -= 10; det['rg_pts'] = '-10'; det['rg_av'] = 'Negativo (<-10%)'
            else:                         det['rg_pts'] = '+0';  det['rg_av'] = 'Estável'
        rec = info.get('recommendationKey', '')
        pts_rec = {'strong_buy': 10, 'buy': 5, 'hold': 0, 'sell': -5, 'strong_sell': -10}
        lab_rec = {'strong_buy': '🟢 Compra Forte', 'buy': '🟢 Compra', 'hold': '🟡 Manter',
                   'sell': '🔴 Venda', 'strong_sell': '🔴 Venda Forte'}
        score += pts_rec.get(rec, 0)
        det['rec']     = lab_rec.get(rec, rec.replace('_', ' ').title() if rec else 'N/A')
        det['rec_raw'] = rec
        mc = info.get('marketCap')
        if mc and isinstance(mc, (int, float)):
            det['mc'] = mc
            if mc > 1e12:    score += 10; det['mc_av'] = 'Mega Cap (>$1T)'
            elif mc > 100e9: score += 5;  det['mc_av'] = 'Large Cap (>$100B)'
            elif mc > 10e9:               det['mc_av'] = 'Mid Cap (>$10B)'
            else:                         det['mc_av'] = 'Small Cap (<$10B)'
        score = max(0, min(100, score))
        if   score >= 80: classe = '🌟'; label = 'EXCELENTE'; grad = 'linear-gradient(135deg,#d4fc79,#96e6a1)'; tc = '#166534'
        elif score >= 65: classe = '✅'; label = 'BOM';       grad = 'linear-gradient(135deg,#a7f3d0,#6ee7b7)'; tc = '#065f46'
        elif score >= 50: classe = '⚖️'; label = 'NEUTRO';   grad = 'linear-gradient(135deg,#fde047,#fbbf24)'; tc = '#92400e'
        elif score >= 35: classe = '⚠️'; label = 'ATENÇÃO';  grad = 'linear-gradient(135deg,#fdcb6e,#ff7043)'; tc = '#7c3626'
        else:             classe = '🔴'; label = 'EVITAR';   grad = 'linear-gradient(135deg,#ef5350,#c62828)'; tc = 'white'
        return {'score': score, 'classe': classe, 'label': label, 'grad': grad, 'tc': tc,
                'det': det, 'setor': info.get('sector', '')}
    except Exception:
        return None


# =============================================================================
# ESTILOS DA TABELA
# =============================================================================
COR_LIQ = {0:'#c62828', 1:'#e53935', 2:'#ef5350', 3:'#ff7043', 4:'#ffa726',
           5:'#fdd835', 6:'#d4e157', 7:'#9ccc65', 8:'#66bb6a', 9:'#2e7d32', 10:'#1b5e20'}

def estilizar_is(val):
    if val >= 75: return 'background-color:#d32f2f;color:white;font-weight:bold'
    if val >= 60: return 'background-color:#ffa726;color:black;font-weight:bold'
    return 'color:#888888'

def estilizar_potencial(val):
    if val == 'Muito Alta': return 'background-color:#2e7d32;color:white;font-weight:bold'
    if val == 'Alta':       return 'background-color:#66bb6a;color:black;font-weight:bold'
    if val == 'Média':      return 'background-color:#ffa726;color:black'
    return 'background-color:#e0e0e0;color:#555555'

def estilizar_liquidez(val):
    bg = COR_LIQ.get(int(val), '#9e9e9e')
    fg = 'black' if int(val) in [4, 5, 6, 7] else 'white'
    return f'background-color:{bg};color:{fg};font-weight:bold'

def estilizar_queda(val):
    return 'color:#c62828;font-weight:bold'


# =============================================================================
# GRÁFICO TÉCNICO (Plotly)
# =============================================================================
def plotar_grafico(df_t, ticker, empresa):
    close  = df_t['Close']
    ema20  = df_t.get('EMA20');  ema50  = df_t.get('EMA50'); ema200 = df_t.get('EMA200')
    bb_low = df_t.get('BB_Lower'); bb_up = df_t.get('BB_Upper')
    rsi_s  = df_t.get('RSI14');  st_s   = df_t.get('Stoch_K')
    h = df_t['High'].max(); l = df_t['Low'].min(); d = h - l
    fibs = {'0%':h, '23.6%':h-d*.236, '38.2%':h-d*.382, '50%':h-d*.5,
            '61.8%':h-d*.618, '78.6%':h-d*.786, '100%':l}
    fib_cores = {'0%':'#ef5350','23.6%':'#ff7043','38.2%':'#ffa726',
                 '50%':'#42a5f5','61.8%':'#2ecc71','78.6%':'#26a69a','100%':'#ab47bc'}

    fig = make_subplots(
        rows=3, cols=1, row_heights=[0.6, 0.2, 0.2], shared_xaxes=True,
        vertical_spacing=0.04,
        subplot_titles=[f"📈 {ticker} — {empresa}", "RSI 14", "Estocástico %K"],
    )

    # Candlestick / linha
    if 'Open' in df_t.columns and 'High' in df_t.columns:
        fig.add_trace(go.Candlestick(
            x=df_t.index, open=df_t['Open'], high=df_t['High'],
            low=df_t['Low'], close=close, name='OHLC', showlegend=False,
            increasing_line_color='#26a69a', decreasing_line_color='#ef5350'), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(x=close.index, y=close, name='Close',
                                 line=dict(color='#1E1E1E', width=2)), row=1, col=1)

    # Bollinger
    if bb_low is not None and bb_up is not None:
        fig.add_trace(go.Scatter(x=bb_up.index, y=bb_up,
                                 line=dict(color='rgba(120,144,156,0.5)', width=1, dash='dot'),
                                 showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=bb_low.index, y=bb_low,
                                 line=dict(color='rgba(120,144,156,0.5)', width=1, dash='dot'),
                                 fill='tonexty', fillcolor='rgba(120,144,156,0.06)',
                                 showlegend=False), row=1, col=1)

    # EMAs
    if ema20  is not None: fig.add_trace(go.Scatter(x=ema20.index,  y=ema20,  name='EMA20',  line=dict(color='#2962FF', width=1.4)), row=1, col=1)
    if ema50  is not None: fig.add_trace(go.Scatter(x=ema50.index,  y=ema50,  name='EMA50',  line=dict(color='#FF6D00', width=1.4)), row=1, col=1)
    if ema200 is not None: fig.add_trace(go.Scatter(x=ema200.index, y=ema200, name='EMA200', line=dict(color='#00695C', width=2.0)), row=1, col=1)

    # Fibonacci
    for nivel, pf in fibs.items():
        cor = fib_cores[nivel]
        fig.add_hline(y=pf, line_dash="dot", line_color=cor, line_width=0.9,
                      annotation_text=f" {nivel}", annotation_position="right",
                      annotation_font_color=cor, annotation_font_size=9, row=1, col=1)
    # Golden zone
    f382 = fibs['38.2%']; f618 = fibs['61.8%']
    fig.add_hrect(y0=min(f382, f618), y1=max(f382, f618),
                  fillcolor='rgba(46,204,113,0.08)', row=1, col=1)

    # RSI
    if rsi_s is not None:
        fig.add_trace(go.Scatter(x=rsi_s.index, y=rsi_s, name='RSI14',
                                 line=dict(color='#FF6F00', width=1.5)), row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#F44336", line_width=1, row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="#4CAF50", line_width=1, row=2, col=1)
        fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(244,67,54,0.12)",  row=2, col=1)
        fig.add_hrect(y0=70, y1=100, fillcolor="rgba(76,175,80,0.12)",  row=2, col=1)

    # Estocástico
    if st_s is not None:
        fig.add_trace(go.Scatter(x=st_s.index, y=st_s, name='Stoch %K',
                                 line=dict(color='#9C27B0', width=1.5)), row=3, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="#F44336", line_width=1, row=3, col=1)
        fig.add_hline(y=80, line_dash="dash", line_color="#4CAF50", line_width=1, row=3, col=1)
        fig.add_hrect(y0=0,  y1=20,  fillcolor="rgba(244,67,54,0.12)",  row=3, col=1)
        fig.add_hrect(y0=80, y1=100, fillcolor="rgba(76,175,80,0.12)",  row=3, col=1)

    fig.update_layout(
        height=620, template='plotly_dark', paper_bgcolor='#0e1117', plot_bgcolor='#0e1117',
        legend=dict(orientation='h', y=1.07, x=0, font=dict(size=11)),
        margin=dict(l=40, r=70, t=60, b=20), xaxis_rangeslider_visible=False,
    )
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    return fig


# =============================================================================
# SIDEBAR — só varredura
# =============================================================================
with st.sidebar:
    st.markdown("## ⚙️ Varredura")
    setores_todos = sorted(set(SETOR_MAP.values()))
    setores_sel = st.multiselect(
        "Setores (vazio = todos)",
        options=setores_todos, default=[],
        placeholder="Todos os setores",
    )
    tickers_analise = (
        [tk for tk, (_, s) in NOMAD_STOCKS.items() if s in setores_sel]
        if setores_sel else list(NOMAD_STOCKS.keys())
    )
    st.info(f"🗂️ **{len(tickers_analise)} tickers** selecionados")

    st.divider()
    if st.button("🔄 Atualizar Análise", type="primary"):
        st.session_state['run'] = True
        for k in ['oportunidades', 'df_calc', 'fund_cache', 'n_ok']:
            st.session_state.pop(k, None)

    if st.button("🗑️ Limpar Cache"):
        st.cache_data.clear()
        st.session_state.clear()
        st.success("Cache limpo!")

    st.divider()
    st.markdown("""
    <div style="text-align:center;font-size:0.72rem;color:#888;">
        ⚠️ Apenas fins educacionais.<br>Não é recomendação de investimento.
    </div>""", unsafe_allow_html=True)


# =============================================================================
# CABEÇALHO PRINCIPAL
# =============================================================================
fuso  = pytz.timezone('America/Sao_Paulo')
agora = datetime.now(fuso)
dias_pt = {'Monday':'Segunda-feira','Tuesday':'Terça-feira','Wednesday':'Quarta-feira',
           'Thursday':'Quinta-feira','Friday':'Sexta-feira','Saturday':'Sábado','Sunday':'Domingo'}
dia_pt = dias_pt.get(agora.strftime("%A"), agora.strftime("%A"))

st.markdown(f"""
<div class="main-header">
    <h1 class="main-title">📊 Monitor de Ações Nomad — Swing Trade Pro</h1>
    <p class="main-subtitle">Análise Técnica Avançada | Rastreamento de Oportunidades em Tempo Real</p>
    <p style="color:rgba(255,255,255,0.8);font-size:0.88rem;text-align:center;margin-top:0.4rem;">
        🕐 {dia_pt}, {agora.strftime('%d/%m/%Y às %H:%M')} (Horário de Brasília) &nbsp;|&nbsp;
        ~{len(tickers_analise)} tickers · NYSE + Nasdaq · ETFs · ADRs
    </p>
</div>
""", unsafe_allow_html=True)

col_i1, col_i2, col_i3 = st.columns(3)
with col_i1: st.markdown("**📈 Estratégia:** Reversão em Sobrevenda")
with col_i2: st.markdown("**🎯 Foco:** Ações em Queda com Potencial")
with col_i3: st.markdown("**⏱️ Timeframe:** 1 Ano | Diário")

st.markdown("---")

with st.expander("📚 Guia dos Indicadores — Entenda os Sinais", expanded=False):
    st.markdown("""
    ### 🎯 Índice de Sobrevenda (I.S.)
    **O que é:** Combina RSI e Estocástico para medir o nível de sobrevenda.
    - **75-100**: 🔴 Muito sobrevendido (alta probabilidade de reversão)
    - **60-75**: 🟠 Sobrevendido moderado
    - **< 60**: ⚪ Não sobrevendido

    ### 📉 RSI (Relative Strength Index)
    - **< 30**: 🟢 Zona de sobrevenda — possível reversão para alta
    - **> 70**: 🔴 Zona de sobrecompra — cuidado

    ### 📊 Estocástico
    - **< 20**: 🟢 Muito sobrevendido — sinal de compra potencial
    - **> 80**: 🔴 Sobrecomprado

    ### 🎨 Bandas de Bollinger
    - **Preço abaixo da banda inferior**: 🟢 Sobrevenda extrema (possível reversão)

    ### 🌟 Fibonacci 61.8% — Zona de Ouro
    Nível mais importante para reversão. Preço próximo a 61.8% = alta probabilidade de suporte.

    ### 📈 EMAs — Médias Móveis Exponenciais
    - **Preço acima das 3 EMAs**: Tendência de alta consolidada
    - **Ativo em queda MAS acima das EMAs**: Correção em tendência de alta = **oportunidade!**

    ### 💡 Como Usar
    1. **Filtre** por EMAs para encontrar correções em tendências de alta
    2. **Procure** I.S. alto (>75) = forte sobrevenda
    3. **Confirme** com RSI < 30 e Estocástico < 20
    4. **Verifique** se está próximo de Fibonacci 61.8%
    5. **Clique** na linha da tabela para ver o gráfico completo! 📈
    """)

st.markdown("---")


# =============================================================================
# EXECUÇÃO PRINCIPAL
# =============================================================================
if st.session_state.get('run') and 'oportunidades' not in st.session_state:

    with st.spinner("⬇️ Conectando à API e baixando dados…"):
        df = buscar_dados(tuple(tickers_analise))
        if df.empty:
            st.error("Erro ao carregar dados. Se o Yahoo tiver bloqueado, aguarde alguns minutos.")
            st.stop()
        n_ok = len(df.columns.get_level_values(1).unique())

    st.success(f"✅ {df.shape[0]} dias históricos | {n_ok} tickers válidos")

    with st.spinner("🔢 Calculando indicadores técnicos…"):
        df_calc = calcular_indicadores(df)

    with st.spinner("🔍 Varrendo oportunidades…"):
        oportunidades = analisar_oportunidades(df_calc)

    st.success(f"✅ {len(oportunidades)} oportunidades detectadas!")

    st.session_state['oportunidades'] = oportunidades
    st.session_state['df_calc']       = df_calc
    st.session_state['fund_cache']    = {}   # preenchido sob demanda pela tabela filtrada
    st.session_state['n_ok']          = n_ok
    st.session_state['run']           = False


# =============================================================================
# EXIBIÇÃO
# =============================================================================
if 'oportunidades' not in st.session_state:
    st.markdown("""
    <div style="text-align:center;padding:3rem;color:#94a3b8;">
        <h3>🎯 Pronto para analisar</h3>
        <p>Clique em <b>🔄 Atualizar Análise</b> na barra lateral para começar</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

oportunidades = st.session_state['oportunidades']
df_calc       = st.session_state['df_calc']
fund_cache    = st.session_state['fund_cache']
n_ok          = st.session_state.get('n_ok', 0)
df_opp        = pd.DataFrame(oportunidades)

st.success(f"✅ {len(oportunidades)} oportunidades detectadas!")

# ── Filtros inline (aparecem APÓS análise, como no modelo BDR) ────────────────
st.markdown('<h3 class="section-header">🎯 Filtros de Tendência</h3>', unsafe_allow_html=True)

st.markdown("""
<div class="tip-box">
    <p>💡 <strong>Dica:</strong> Selecione as médias móveis para filtrar ações em correção dentro de tendências de alta</p>
</div>""", unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    filtrar_ema20  = st.checkbox("📈 Acima da EMA20",  value=False, help="Preço acima da EMA20 (curto prazo)")
with col_f2:
    filtrar_ema50  = st.checkbox("📊 Acima da EMA50",  value=False, help="Preço acima da EMA50 (médio prazo)")
with col_f3:
    filtrar_ema200 = st.checkbox("📉 Acima da EMA200", value=False, help="Preço acima da EMA200 (longo prazo)")

st.markdown("**💧 Liquidez mínima:**")
liq_min = st.slider(
    "0 = sem filtro  |  10 = máxima exigência",
    min_value=0, max_value=10, value=0, step=1,
    help="Filtra ações pelo ranking de liquidez 0-10."
)

ordens = {'Baixa':0, 'Média':1, 'Alta':2, 'Muito Alta':3}
pot_min = st.selectbox("🎯 Potencial mínimo", ['Todos', 'Média', 'Alta', 'Muito Alta'])

# ── Aplicar filtros ────────────────────────────────────────────────────────────
df_res = df_opp.copy()

if pot_min != 'Todos':
    df_res = df_res[df_res['Potencial'].map(lambda x: ordens.get(x, -1)) >= ordens[pot_min]]
if liq_min > 0:
    df_res = df_res[df_res['Liquidez'] >= liq_min]

if filtrar_ema20 or filtrar_ema50 or filtrar_ema200:
    contadores = {'ema20': 0, 'ema50': 0, 'ema200': 0, 'sem_dados': 0}
    df_filtrado = []
    for _, opp in df_res.iterrows():
        tk = opp['Ticker']
        try:
            df_t  = df_calc.xs(tk, axis=1, level=1).dropna()
            tam   = len(df_t)
            if tam < 20: contadores['sem_dados'] += 1; continue
            preco = df_t['Close'].iloc[-1]
            ok    = True
            if filtrar_ema20 and 'EMA20' in df_t.columns and tam >= 20:
                ema20v = df_t['EMA20'].iloc[-1]
                if pd.notna(ema20v) and preco > ema20v: contadores['ema20'] += 1
                else: ok = False
            elif filtrar_ema20: ok = False
            if ok and filtrar_ema50 and 'EMA50' in df_t.columns and tam >= 50:
                ema50v = df_t['EMA50'].iloc[-1]
                if pd.notna(ema50v) and preco > ema50v: contadores['ema50'] += 1
                else: ok = False
            elif ok and filtrar_ema50: ok = False
            if ok and filtrar_ema200 and 'EMA200' in df_t.columns and tam >= 50:
                ema200v = df_t['EMA200'].iloc[-1]
                if pd.notna(ema200v) and preco > ema200v: contadores['ema200'] += 1
                else: ok = False
            elif ok and filtrar_ema200: ok = False
            if ok: df_filtrado.append(opp)
        except Exception:
            contadores['sem_dados'] += 1

    if df_filtrado:
        df_res = pd.DataFrame(df_filtrado).reset_index(drop=True)
        ativos = []
        if filtrar_ema20:  ativos.append(f"EMA20 ({contadores['ema20']} ✓)")
        if filtrar_ema50:  ativos.append(f"EMA50 ({contadores['ema50']} ✓)")
        if filtrar_ema200: ativos.append(f"EMA200 ({contadores['ema200']} ✓)")
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#d4fc79,#96e6a1);padding:1rem;border-radius:8px;margin:1rem 0;'>
            <p style='margin:0;color:#166534;font-weight:600;font-size:1rem;'>
                ✅ {len(df_res)} ações encontradas &nbsp;|&nbsp; Filtros ativos: {' + '.join(ativos)}
            </p>
        </div>""", unsafe_allow_html=True)
    else:
        ativos = []
        if filtrar_ema20:  ativos.append(f"EMA20 ({contadores['ema20']} acima)")
        if filtrar_ema50:  ativos.append(f"EMA50 ({contadores['ema50']} acima)")
        if filtrar_ema200: ativos.append(f"EMA200 ({contadores['ema200']} acima)")
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#ffeaa7,#fdcb6e);padding:1rem;border-radius:8px;margin:1rem 0;'>
            <p style='margin:0;color:#7c3626;font-weight:600;'>
                ⚠️ Nenhuma ação passou em todos os filtros combinados
            </p>
            <p style='margin:0.4rem 0 0;color:#7c3626;font-size:0.88rem;'>
                📊 {' | '.join(ativos)} | {contadores['sem_dados']} sem dados suficientes
            </p>
        </div>""", unsafe_allow_html=True)
        df_res = pd.DataFrame()

if df_res.empty:
    st.stop()

# ── Tabela principal ──────────────────────────────────────────────────────────
st.markdown('<h3 class="section-header">📊 Oportunidades Detectadas</h3>', unsafe_allow_html=True)

st.markdown("""
<div class="tip-box">
    <p>💡 <strong>Dica:</strong> Clique em qualquer linha da tabela para visualizar o gráfico técnico completo</p>
</div>""", unsafe_allow_html=True)

evento = st.dataframe(
    df_res.style
        .map(estilizar_potencial, subset=['Potencial'])
        .map(estilizar_is,        subset=['IS'])
        .map(estilizar_liquidez,  subset=['Liquidez'])
        .map(estilizar_queda,     subset=['Queda_Dia'])
        .format({
            'Preco':     '${:.2f}',
            'Queda_Dia': '{:.2f}%',
            'Gap':       '{:.2f}%',
            'IS':        '{:.0f}',
            'RSI14':     '{:.0f}',
            'Stoch':     '{:.0f}',
            'Liquidez':  '{:.0f}',
            'Volume':    '{:,.0f}',
        }),
    column_order=("Ticker", "Empresa", "Liquidez", "Preco", "Queda_Dia",
                  "IS", "Volume", "Gap", "Potencial", "Score", "Sinais"),
    column_config={
        "Empresa":  st.column_config.TextColumn("Empresa",     width="medium"),
        "Liquidez": st.column_config.NumberColumn("💧 Liq.",   width="small",
                        help="Ranking de liquidez 0-10 (🔴 baixa → 🟢 alta)"),
        "IS":       st.column_config.NumberColumn("I.S.",      help="Índice de Sobrevenda"),
        "Volume":   st.column_config.NumberColumn("Vol.",      help="Volume do dia"),
        "Score":    st.column_config.ProgressColumn("Força",   format="%d", min_value=0, max_value=10),
        "Potencial":st.column_config.Column("Sinal"),
        "Sinais":   st.column_config.TextColumn("Sinais Técnicos", width="large"),
    },
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row",
    height=min(700, 38 + 35 * len(df_res)),
)

# Download CSV
csv = df_res.drop(columns=['Explicacoes'], errors='ignore').to_csv(index=False).encode('utf-8')
st.download_button("⬇️ Exportar CSV", data=csv,
                   file_name=f"nomad_{agora.strftime('%Y%m%d_%H%M')}.csv",
                   mime="text/csv")

# ── Buscar fundamentos de todos os tickers na tabela filtrada ─────────────────
tickers_tabela  = df_res['Ticker'].tolist()
tickers_faltando = [tk for tk in tickers_tabela if tk not in fund_cache]
if tickers_faltando:
    pb_f = st.progress(0, text=f"💼 Buscando dados fundamentalistas ({len(tickers_faltando)} ações)…")
    for i, tk in enumerate(tickers_faltando):
        fund_cache[tk] = buscar_fundamentalista(tk)
        pb_f.progress((i + 1) / len(tickers_faltando))
    pb_f.empty()
    st.session_state['fund_cache'] = fund_cache


# =============================================================================
# ANÁLISE DETALHADA ao clicar na linha
# =============================================================================
if evento.selection and evento.selection.rows:
    idx    = evento.selection.rows[0]
    row    = df_res.iloc[idx]
    ticker = row['Ticker']
    empresa = row['Empresa']

    st.markdown("---")
    st.markdown(f'<h3 class="section-header">📈 Análise Técnica: {ticker} — {empresa}</h3>',
                unsafe_allow_html=True)

    # Gráfico (esquerda) + painel de métricas (direita)
    col_graf, col_info = st.columns([3, 1])

    with col_graf:
        try:
            df_t = df_calc.xs(ticker, axis=1, level=1).dropna()
            fig  = plotar_grafico(df_t, ticker, empresa)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao gerar gráfico: {e}")

    with col_info:
        pot = row['Potencial']
        if 'Alta' in pot:
            cor_bg = "linear-gradient(135deg,#d4fc79,#96e6a1)"; cor_tx = "#166534"; ico = "🟢"
        elif 'Média' in pot:
            cor_bg = "linear-gradient(135deg,#ffeaa7,#fdcb6e)"; cor_tx = "#7c3626"; ico = "🟡"
        else:
            cor_bg = "linear-gradient(135deg,#dfe6e9,#b2bec3)"; cor_tx = "#2d3436"; ico = "⚪"

        st.markdown(f"""
        <div style="background:{cor_bg};padding:0.8rem;border-radius:8px;
                    margin-bottom:0.75rem;text-align:center;">
            <h2 style="margin:0;color:{cor_tx};">{ico} {pot}</h2>
        </div>""", unsafe_allow_html=True)

        st.metric("💰 Preço Atual",    f"${row['Preco']:.2f}")
        st.metric("📉 Queda no Dia",   f"{row['Queda_Dia']:.2f}%",  delta_color="inverse")
        st.metric("🎯 I.S. (Sobrevenda)", f"{row['IS']:.0f}/100")
        if row['Gap'] < -1:
            st.metric("⚡ Gap Abertura", f"{row['Gap']:.2f}%", delta_color="inverse")
        st.markdown(f"**⭐ Score:** {row['Score']}/10")
        st.markdown(f"**📊 Volume:** {row['Volume']:,.0f}")

        st.markdown("""
        <div style="background:#e0e7ff;padding:0.6rem;border-radius:6px;margin-top:0.75rem;">
            <p style="margin:0;font-weight:600;color:#3730a3;font-size:0.85rem;">📋 Sinais Detectados</p>
        </div>""", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:0.82rem;color:#475569;'>{row['Sinais']}</p>",
                    unsafe_allow_html=True)

        if row.get('Explicacoes'):
            st.markdown("""
            <div style="background:#fef3c7;padding:0.6rem;border-radius:6px;margin-top:0.5rem;">
                <p style="margin:0;font-weight:600;color:#92400e;font-size:0.85rem;">💡 O que isso significa?</p>
            </div>""", unsafe_allow_html=True)
            for exp in row['Explicacoes']:
                st.markdown(f"<p style='font-size:0.8rem;color:#92400e;margin:0.2rem 0;'>• {exp}</p>",
                            unsafe_allow_html=True)

    # ── Painel fundamentalista ────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<h3 class="section-header">📊 Análise Fundamentalista</h3>', unsafe_allow_html=True)

    fd = fund_cache.get(ticker)
    if fd is None:
        with st.spinner(f"Buscando dados fundamentalistas de {ticker}…"):
            fd = buscar_fundamentalista(ticker)

    if fd:
        score = fd['score']
        st.markdown(f"""
        <div style="background:{fd['grad']};padding:1.5rem;border-radius:12px;
                    margin-bottom:1.5rem;text-align:center;">
            <h1 style="margin:0;color:{fd['tc']};font-size:4rem;font-weight:900;">{score:.0f}%</h1>
            <p style="margin:0.4rem 0 0;color:{fd['tc']};font-size:1.4rem;font-weight:600;">{fd['label']}</p>
        </div>""", unsafe_allow_html=True)

        det = fd['det']
        col_v, col_r, col_i = st.columns(3)

        with col_v:
            st.markdown("### 📈 Valuation")
            st.metric("P/E Ratio",
                      f"{det['pe']:.2f}" if det.get('pe') else "N/A")
            mc = det.get('mc')
            st.metric("Market Cap",
                      (f"${mc/1e12:.2f}T" if mc >= 1e12 else f"${mc/1e9:.1f}B") if mc else "N/A")

        with col_r:
            st.markdown("### 💰 Rentabilidade")
            st.metric("Dividend Yield",
                      f"{det['dy']:.2f}%" if det.get('dy') else "N/A")
            rg_v = det.get('rg')
            if rg_v is not None:
                st.metric("Crescimento Receita", f"{rg_v:+.1f}%",
                          delta=f"{rg_v:.1f}%" if rg_v > 0 else None)
            else:
                st.metric("Crescimento Receita", "N/A")

        with col_i:
            st.markdown("### 🎯 Info")
            rec_str = det.get('rec', 'N/A')
            cor_rec = '#1b5e20' if 'Compra' in rec_str else '#b71c1c' if 'Venda' in rec_str else '#e65100'
            st.markdown("**Analistas:**")
            st.markdown(f"<h3 style='color:{cor_rec};margin:0;'>{rec_str}</h3>",
                        unsafe_allow_html=True)
            if fd.get('setor'):
                st.markdown(f"**Setor:** {fd['setor']}")

        # Detalhamento da pontuação
        st.markdown("---")
        st.markdown("### 📋 Detalhamento da Pontuação")
        linhas = []
        if det.get('pe'):
            linhas.append({'Métrica':'P/E Ratio', 'Valor':f"{det['pe']:.2f}",
                           'Pontos':det.get('pe_pts','+0'), 'Avaliação':det.get('pe_av','')})
        if det.get('dy'):
            linhas.append({'Métrica':'Dividend Yield', 'Valor':f"{det['dy']:.2f}%",
                           'Pontos':det.get('dy_pts','+0'), 'Avaliação':det.get('dy_av','')})
        if det.get('rg') is not None:
            linhas.append({'Métrica':'Crescimento Receita', 'Valor':f"{det['rg']:+.1f}%",
                           'Pontos':det.get('rg_pts','+0'), 'Avaliação':det.get('rg_av','')})
        if det.get('rec'):
            pts_r = {'strong_buy':'+10','buy':'+5','hold':'+0','sell':'-5','strong_sell':'-10'}
            linhas.append({'Métrica':'Recomendação Analistas', 'Valor':det['rec'],
                           'Pontos':pts_r.get(det.get('rec_raw',''),'+0'), 'Avaliação':det.get('rec','')})
        mc = det.get('mc')
        if mc:
            linhas.append({'Métrica':'Market Cap',
                           'Valor': f"${mc/1e12:.2f}T" if mc >= 1e12 else f"${mc/1e9:.1f}B",
                           'Pontos':'+10' if mc > 1e12 else '+5' if mc > 100e9 else '+0',
                           'Avaliação':det.get('mc_av','')})
        if linhas:
            df_det = pd.DataFrame(linhas)
            st.dataframe(df_det, hide_index=True, use_container_width=True,
                         column_config={
                             'Métrica':   st.column_config.TextColumn("Métrica",   width="medium"),
                             'Valor':     st.column_config.TextColumn("Valor",     width="small"),
                             'Pontos':    st.column_config.TextColumn("Pts",       width="small"),
                             'Avaliação': st.column_config.TextColumn("Avaliação", width="medium"),
                         })
            st.caption(f"**Score Total:** {score:.0f}/100 (Base: 50 + Bônus/Penalidades)")
    else:
        st.warning(f"⚠️ Não foi possível obter dados fundamentalistas para {ticker}")
        st.info("""
        💡 **Por que isso acontece?**
        - ETF (dados fundamentalistas não aplicáveis)
        - Ativo com baixíssimo volume ou recém-listado
        - Dados não disponíveis nas APIs públicas consultadas
        """)

else:
    st.markdown("""
    <div class="select-prompt">
        <p>👆 Selecione uma ação na tabela acima para visualizar a análise técnica completa</p>
    </div>""", unsafe_allow_html=True)


# =============================================================================
# RODAPÉ
# =============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align:center;padding:1.5rem 0;color:#64748b;">
    <p style="margin:0;font-size:0.9rem;">
        <strong>Monitor de Ações Nomad — Swing Trade Pro</strong>
        &nbsp;|&nbsp; Powered by Python, yFinance &amp; Streamlit
    </p>
    <p style="margin:0.4rem 0 0;font-size:0.8rem;">
        ⚠️ Este sistema é apenas para fins educacionais. Não constitui recomendação de investimento.
    </p>
</div>""", unsafe_allow_html=True)
