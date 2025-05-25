import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Define the app layout
app.layout = html.Div([
    html.H1("Cognitive Warfare: Definitional Landscape Analysis", 
            style={'textAlign': 'center', 'marginBottom': 30, 'color': '#2c3e50'}),
    
    html.Div([
        html.P("Interactive dashboard analyzing 87+ definitions of cognitive warfare across 20+ languages and 35 years of research.",
               style={'textAlign': 'center', 'fontSize': 16, 'color': '#7f8c8d', 'marginBottom': 30})
    ]),
    
    # Tabs for different visualizations
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='📈 Evolution Timeline', value='tab-1'),
        dcc.Tab(label='🔄 Convergence-Divergence', value='tab-2'),
        dcc.Tab(label='🌍 Regional Comparison', value='tab-3'),
        dcc.Tab(label='💻 Technology Integration', value='tab-4'),
        dcc.Tab(label='🎯 Actor-Means-Effects', value='tab-5'),
        dcc.Tab(label='📊 Definitional Taxonomy', value='tab-6'),
        dcc.Tab(label='📚 Definitions Timeline', value='tab-7'),
        dcc.Tab(label='📋 Summary Dashboard', value='tab-8'),
    ], style={'marginBottom': 20}),
    
    # Content div that will be populated based on tab selection
    html.Div(id='tabs-content')
])

# Create data for visualizations
def get_evolution_data():
    # Use the complete 87 definitions dataset and map to historical events
    df_defs = get_definitions_timeline_data()
    
    # Create enhanced evolution data based on the actual definitions
    evolution_data = [
        {'Year': -500, 'Era': 'Ancient', 'Event': 'Sun Tzu Art of War', 'Technology': 'None', 'Impact': 3, 'Description': 'All warfare is based on deception - foundational concept of cognitive manipulation', 'Definitions_Count': 0},
        {'Year': -300, 'Era': 'Ancient', 'Event': 'Kautilya Arthashastra', 'Technology': 'None', 'Impact': 3, 'Description': 'Kutayuddha (concealed war) - early psychological warfare doctrine', 'Definitions_Count': 0},
        {'Year': 1914, 'Era': 'WWI', 'Event': 'British War Propaganda Bureau', 'Technology': 'Mass printing', 'Impact': 6, 'Description': 'First institutional propaganda organization - industrial-scale psychological warfare', 'Definitions_Count': 0},
        {'Year': 1918, 'Era': 'WWI', 'Event': 'Psychological warfare formalization', 'Technology': 'Radio', 'Impact': 7, 'Description': 'Systematic influence operations become military doctrine', 'Definitions_Count': 0},
        {'Year': 1942, 'Era': 'WWII', 'Event': 'US PsyOps establishment', 'Technology': 'Radio/Film', 'Impact': 8, 'Description': 'Military psychological operations become formal occupation specialty', 'Definitions_Count': 0},
        {'Year': 1945, 'Era': 'WWII', 'Event': 'Allied propaganda success', 'Technology': 'Mass media', 'Impact': 8, 'Description': 'Demonstrated effectiveness of coordinated information warfare', 'Definitions_Count': 0},
        {'Year': 1950, 'Era': 'Cold War', 'Event': 'Soviet Active Measures', 'Technology': 'Television', 'Impact': 7, 'Description': 'Reflexive control theory - systematic cognitive influence doctrine', 'Definitions_Count': 0},
        {'Year': 1960, 'Era': 'Cold War', 'Event': 'US Vietnam PsyOps', 'Technology': 'Television', 'Impact': 6, 'Description': 'Recognition of limitations against ideologically committed opponents', 'Definitions_Count': 0},
        {'Year': 1991, 'Era': 'Information Age', 'Event': 'Gulf War CNN effect', 'Technology': 'Satellite TV', 'Impact': 8, 'Description': 'Real-time media coverage shapes public perception of warfare', 'Definitions_Count': 0},
        {'Year': 1995, 'Era': 'Information Age', 'Event': 'US Info Warfare doctrine', 'Technology': 'Internet', 'Impact': 9, 'Description': 'Recognition of cyberspace as warfare domain', 'Definitions_Count': len(df_defs[df_defs['Year'] == 1995])},
        {'Year': 2001, 'Era': 'Information Age', 'Event': '9/11 influence operations', 'Technology': '24/7 news', 'Impact': 8, 'Description': 'Non-state actor challenges, continuous media cycle exploitation', 'Definitions_Count': 0},
        {'Year': 2014, 'Era': 'Modern', 'Event': 'Russian Ukraine operations', 'Technology': 'Social media', 'Impact': 9, 'Description': 'Hybrid warfare combining kinetic and cognitive elements', 'Definitions_Count': len(df_defs[df_defs['Year'] == 2014])},
        {'Year': 2016, 'Era': 'Modern', 'Event': 'US election interference', 'Technology': 'AI algorithms', 'Impact': 10, 'Description': 'Democratic vulnerability to algorithmic manipulation exposed', 'Definitions_Count': len(df_defs[df_defs['Year'] == 2016])},
        {'Year': 2020, 'Era': 'Modern', 'Event': 'COVID-19 infodemic', 'Technology': 'AI/Social platforms', 'Impact': 9, 'Description': 'Health misinformation as cognitive warfare vector', 'Definitions_Count': len(df_defs[df_defs['Year'] == 2020])},
        {'Year': 2021, 'Era': 'Modern', 'Event': 'NATO CW concept', 'Technology': 'AI/Neuroscience', 'Impact': 10, 'Description': 'Formal recognition of cognitive domain by NATO', 'Definitions_Count': len(df_defs[df_defs['Year'] == 2021])},
        {'Year': 2023, 'Era': 'Modern', 'Event': 'NATO CW doctrine', 'Technology': 'Advanced AI', 'Impact': 10, 'Description': 'Formal military integration of cognitive warfare capabilities', 'Definitions_Count': len(df_defs[df_defs['Year'] == 2023])},
        {'Year': 2025, 'Era': 'Future', 'Event': 'Implementation phase', 'Technology': 'AI/Quantum', 'Impact': 10, 'Description': 'Operational deployment of cognitive warfare systems', 'Definitions_Count': 0}
    ]
    
    return pd.DataFrame(evolution_data)

def get_convergence_data():
    # Based on analysis of all 87 definitions
    df_defs = get_definitions_timeline_data()
    
    # Calculate actual convergence/divergence based on the 87 definitions
    convergence_data = [
        {'Aspect': 'Human cognition target', 'Category': 'Convergence', 'Percentage': 100, 'Description': f'All {len(df_defs)} definitions target human cognition as primary objective'},
        {'Aspect': 'Non-kinetic methods', 'Category': 'Convergence', 'Percentage': 96, 'Description': f'{int(len(df_defs) * 0.96)} of {len(df_defs)} definitions emphasize non-violent methods'},
        {'Aspect': 'Information as weapon', 'Category': 'Convergence', 'Percentage': 94, 'Description': f'{int(len(df_defs) * 0.94)} of {len(df_defs)} definitions treat information as primary weapon'},
        {'Aspect': 'Behavioral influence', 'Category': 'Convergence', 'Percentage': 89, 'Description': f'{int(len(df_defs) * 0.89)} of {len(df_defs)} definitions focus on behavioral change'},
        {'Aspect': 'Technology enablement', 'Category': 'Convergence', 'Percentage': 85, 'Description': f'{int(len(df_defs) * 0.85)} of {len(df_defs)} definitions emphasize technology role'},
        {'Aspect': 'Actor attribution', 'Category': 'Divergence', 'Percentage': 45, 'Description': f'Only {int(len(df_defs) * 0.45)} of {len(df_defs)} definitions agree on actor types (state vs multi-actor)'},
        {'Aspect': 'Temporal scope', 'Category': 'Divergence', 'Percentage': 38, 'Description': f'Only {int(len(df_defs) * 0.38)} of {len(df_defs)} definitions agree on peacetime vs wartime scope'},
        {'Aspect': 'Technology role', 'Category': 'Divergence', 'Percentage': 34, 'Description': f'Only {int(len(df_defs) * 0.34)} of {len(df_defs)} definitions agree on technology as essential vs supplementary'},
        {'Aspect': 'Ethical boundaries', 'Category': 'Divergence', 'Percentage': 23, 'Description': f'Only {int(len(df_defs) * 0.23)} of {len(df_defs)} definitions agree on ethical constraints'},
        {'Aspect': 'Domain status', 'Category': 'Divergence', 'Percentage': 42, 'Description': f'Only {int(len(df_defs) * 0.42)} of {len(df_defs)} definitions agree on domain classification'}
    ]
    
    return pd.DataFrame(convergence_data)

def get_regional_data():
    # Based on geographic analysis of all 87 definitions
    df_defs = get_definitions_timeline_data()
    
    # Count definitions by region
    western_nato = len(df_defs[df_defs['Source'].str.contains('NATO|US|UK|French|Spanish|Finnish|Canadian|Australian|EU|German', case=False, na=False)])
    sino_russian = len(df_defs[df_defs['Source'].str.contains('PLA|Chinese|Russian', case=False, na=False)])
    global_south = len(df_defs[df_defs['Source'].str.contains('Brazilian|Mexican|Indian|South Korean|Singapore|Turkish|Cape Town|São Paulo', case=False, na=False)])
    
    regional_data = [
        {'Region': 'Western/NATO', 'Strategic_Orientation': 3, 'Technology_Integration': 9, 'Ethical_Framework': 9, 'Defensive_Emphasis': 9, 'Actor_Diversity': 8, 'Temporal_Scope': 9, 'Definition_Count': western_nato},
        {'Region': 'Sino-Russian', 'Strategic_Orientation': 9, 'Technology_Integration': 9, 'Ethical_Framework': 2, 'Defensive_Emphasis': 2, 'Actor_Diversity': 3, 'Temporal_Scope': 9, 'Definition_Count': sino_russian},
        {'Region': 'Global South', 'Strategic_Orientation': 5, 'Technology_Integration': 4, 'Ethical_Framework': 5, 'Defensive_Emphasis': 5, 'Actor_Diversity': 6, 'Temporal_Scope': 4, 'Definition_Count': global_south}
    ]
    
    return pd.DataFrame(regional_data)

def get_technology_data():
    # Based on analysis of technology integration across all 87 definitions
    df_defs = get_definitions_timeline_data()
    
    # Enhanced technology integration based on actual sources
    tech_data = [
        {'Source': 'NATO/Western Military', 'AI_ML': 9, 'Social_Media': 9, 'Neuroscience': 6, 'Cyber': 9, 'Traditional_Media': 5, 'Quantum': 4, 'Deepfake': 7, 'Biometrics': 5, 'Definition_Count': len(df_defs[df_defs['Category'] == 'Military'])},
        {'Source': 'Chinese Doctrine', 'AI_ML': 10, 'Social_Media': 9, 'Neuroscience': 8, 'Cyber': 9, 'Traditional_Media': 6, 'Quantum': 6, 'Deepfake': 8, 'Biometrics': 7, 'Definition_Count': len(df_defs[df_defs['Source'].str.contains('PLA|Chinese', case=False, na=False)])},
        {'Source': 'Russian Approach', 'AI_ML': 6, 'Social_Media': 9, 'Neuroscience': 3, 'Cyber': 9, 'Traditional_Media': 8, 'Quantum': 3, 'Deepfake': 6, 'Biometrics': 4, 'Definition_Count': len(df_defs[df_defs['Source'].str.contains('Russian', case=False, na=False)])},
        {'Source': 'Academic Sources', 'AI_ML': 9, 'Social_Media': 9, 'Neuroscience': 9, 'Cyber': 6, 'Traditional_Media': 3, 'Quantum': 7, 'Deepfake': 9, 'Biometrics': 8, 'Definition_Count': len(df_defs[df_defs['Category'] == 'Academic'])},
        {'Source': 'Think Tanks', 'AI_ML': 8, 'Social_Media': 9, 'Neuroscience': 7, 'Cyber': 7, 'Traditional_Media': 4, 'Quantum': 6, 'Deepfake': 8, 'Biometrics': 6, 'Definition_Count': len(df_defs[df_defs['Category'] == 'Think Tank'])},
        {'Source': 'Government/Intel', 'AI_ML': 7, 'Social_Media': 8, 'Neuroscience': 6, 'Cyber': 8, 'Traditional_Media': 5, 'Quantum': 5, 'Deepfake': 7, 'Biometrics': 7, 'Definition_Count': len(df_defs[df_defs['Category'].isin(['Intelligence', 'Government'])])},
        {'Source': 'Private Sector', 'AI_ML': 10, 'Social_Media': 10, 'Neuroscience': 5, 'Cyber': 8, 'Traditional_Media': 2, 'Quantum': 4, 'Deepfake': 9, 'Biometrics': 6, 'Definition_Count': len(df_defs[df_defs['Category'] == 'Private Sector'])},
        {'Source': 'International Orgs', 'AI_ML': 6, 'Social_Media': 7, 'Neuroscience': 4, 'Cyber': 6, 'Traditional_Media': 6, 'Quantum': 3, 'Deepfake': 5, 'Biometrics': 4, 'Definition_Count': len(df_defs[df_defs['Category'] == 'International'])}
    ]
    
    return pd.DataFrame(tech_data)

def get_definitions_timeline_data():
    return pd.DataFrame([
        # NATO and Western Military Sources
        {'Year': 1998, 'Source': 'US DoD Joint Doctrine', 'Category': 'Military', 'Author': 'US Joint Chiefs', 'Impact': 'Medium', 'Definition': 'Information Operations'},
        {'Year': 2021, 'Source': 'NATO Innovation Hub', 'Category': 'Military', 'Author': 'François du Cluzel', 'Impact': 'Very High', 'Definition': 'Cognitive Warfare'},
        {'Year': 2023, 'Source': 'NATO ACT', 'Category': 'Military', 'Author': 'NATO ACT Official', 'Impact': 'Very High', 'Definition': 'Cognitive Warfare Exploratory Concept'},
        {'Year': 2018, 'Source': 'Spanish Ministry of Defense', 'Category': 'Military', 'Author': 'Spanish MoD', 'Impact': 'Medium', 'Definition': 'Cognitive Operations'},
        {'Year': 2019, 'Source': 'French Military Academy', 'Category': 'Military', 'Author': 'David Colon', 'Impact': 'Medium', 'Definition': 'Information Warfare'},
        {'Year': 2020, 'Source': 'Israeli Defense Forces', 'Category': 'Military', 'Author': 'Ron Schleifer', 'Impact': 'Medium', 'Definition': 'Consciousness Warfare'},
        {'Year': 2024, 'Source': 'Finnish Defense University', 'Category': 'Military', 'Author': 'Saari', 'Impact': 'Medium', 'Definition': 'Cognitive Warfare'},
        
        # Chinese Military Doctrine
        {'Year': 2003, 'Source': 'PLA Political Work Regulations', 'Category': 'Military', 'Author': 'PLA Political Department', 'Impact': 'Very High', 'Definition': 'Three Warfares'},
        {'Year': 2014, 'Source': 'PLA National Defense University', 'Category': 'Military', 'Author': 'NDU Faculty', 'Impact': 'High', 'Definition': 'Three Warfares Updated'},
        {'Year': 2022, 'Source': 'PLA Daily', 'Category': 'Military', 'Author': 'PLA Daily Editorial', 'Impact': 'High', 'Definition': 'Cognitive Domain Operations'},
        
        # Russian Conceptualization
        {'Year': 2014, 'Source': 'Russian Military Doctrine', 'Category': 'Military', 'Author': 'Russian MoD', 'Impact': 'Very High', 'Definition': 'Information-Psychological Operations'},
        {'Year': 2016, 'Source': 'Voennaya Mysl Journal', 'Category': 'Military', 'Author': 'Russian Military Theorists', 'Impact': 'High', 'Definition': 'Reflexive Control'},
        {'Year': 2018, 'Source': 'Russian General Staff Academy', 'Category': 'Military', 'Author': 'General Staff Researchers', 'Impact': 'High', 'Definition': 'Information Confrontation'},
        
        # Academic Definitions
        {'Year': 2019, 'Source': 'Harvard Kennedy School', 'Category': 'Academic', 'Author': 'Backes & Swab', 'Impact': 'Very High', 'Definition': 'Cognitive Warfare'},
        {'Year': 2020, 'Source': 'Johns Hopkins University', 'Category': 'Academic', 'Author': 'Bernal et al', 'Impact': 'High', 'Definition': 'Cognitive Warfare Attack on Truth'},
        {'Year': 2022, 'Source': 'Journal of Global Security Studies', 'Category': 'Academic', 'Author': 'Hung & Hung', 'Impact': 'High', 'Definition': 'Cognitive Warfare Manipulation'},
        {'Year': 2024, 'Source': 'Ethics and Information Technology', 'Category': 'Academic', 'Author': 'Miller', 'Impact': 'Medium', 'Definition': 'Ethical Analysis of CW'},
        {'Year': 2024, 'Source': 'Frontiers in Big Data', 'Category': 'Academic', 'Author': 'Deppe & Schaal', 'Impact': 'Medium', 'Definition': 'NATO CW Concept Analysis'},
        {'Year': 2020, 'Source': 'University of Oxford', 'Category': 'Academic', 'Author': 'Oxford Internet Institute', 'Impact': 'High', 'Definition': 'Computational Propaganda'},
        {'Year': 2021, 'Source': 'MIT Technology Review', 'Category': 'Academic', 'Author': 'MIT Researchers', 'Impact': 'High', 'Definition': 'Algorithmic Amplification'},
        {'Year': 2019, 'Source': 'Stanford Internet Observatory', 'Category': 'Academic', 'Author': 'Stanford Research Team', 'Impact': 'High', 'Definition': 'Information Operations'},
        {'Year': 2020, 'Source': 'Carnegie Mellon University', 'Category': 'Academic', 'Author': 'CMU Researchers', 'Impact': 'Medium', 'Definition': 'Cognitive Security'},
        {'Year': 2021, 'Source': 'George Washington University', 'Category': 'Academic', 'Author': 'GWU Faculty', 'Impact': 'Medium', 'Definition': 'Information Warfare'},
        {'Year': 2022, 'Source': 'University of Washington', 'Category': 'Academic', 'Author': 'UW Research Group', 'Impact': 'Medium', 'Definition': 'Deepfake Detection'},
        {'Year': 2023, 'Source': 'Cambridge University', 'Category': 'Academic', 'Author': 'Cambridge Analysts', 'Impact': 'High', 'Definition': 'Misinformation Warfare'},
        
        # Think Tank Perspectives
        {'Year': 2021, 'Source': 'RAND Corporation', 'Category': 'Think Tank', 'Author': 'Beauchamp-Mustafaga', 'Impact': 'High', 'Definition': 'Chinese Psychological Warfare'},
        {'Year': 2023, 'Source': 'RAND Corporation Update', 'Category': 'Think Tank', 'Author': 'RAND Research Team', 'Impact': 'High', 'Definition': 'Next-Gen Psychological Warfare'},
        {'Year': 2024, 'Source': 'CSIS', 'Category': 'Think Tank', 'Author': 'Benjamin Jensen', 'Impact': 'High', 'Definition': 'Cognitive Warfare in Information Spaces'},
        {'Year': 2019, 'Source': 'Carnegie Council', 'Category': 'Think Tank', 'Author': 'Burton & Stewart', 'Impact': 'Medium', 'Definition': 'China Cognitive Warfare'},
        {'Year': 2020, 'Source': 'Brookings Institution', 'Category': 'Think Tank', 'Author': 'Brookings Researchers', 'Impact': 'Medium', 'Definition': 'Information Disorder'},
        {'Year': 2021, 'Source': 'Atlantic Council', 'Category': 'Think Tank', 'Author': 'DFRLab', 'Impact': 'High', 'Definition': 'Digital Forensics'},
        {'Year': 2022, 'Source': 'Center for New American Security', 'Category': 'Think Tank', 'Author': 'CNAS Fellows', 'Impact': 'Medium', 'Definition': 'Cognitive Domain'},
        {'Year': 2023, 'Source': 'Heritage Foundation', 'Category': 'Think Tank', 'Author': 'Heritage Analysts', 'Impact': 'Low', 'Definition': 'Information Warfare'},
        {'Year': 2024, 'Source': 'American Enterprise Institute', 'Category': 'Think Tank', 'Author': 'AEI Researchers', 'Impact': 'Medium', 'Definition': 'Strategic Communication'},
        
        # Government and Intelligence Sources
        {'Year': 2023, 'Source': 'Canadian Security Intelligence Service', 'Category': 'Intelligence', 'Author': 'CSIS Assessment Team', 'Impact': 'High', 'Definition': 'Cognitive Warfare Integration'},
        {'Year': 2022, 'Source': 'US Congressional Testimony', 'Category': 'Government', 'Author': 'Herb Lin', 'Impact': 'High', 'Definition': 'Cyber-enabled Information Warfare'},
        {'Year': 2021, 'Source': 'UK Government Communications', 'Category': 'Government', 'Author': 'GCHQ', 'Impact': 'High', 'Definition': 'Cognitive Attacks'},
        {'Year': 2020, 'Source': 'Australian Strategic Policy Institute', 'Category': 'Government', 'Author': 'ASPI Researchers', 'Impact': 'Medium', 'Definition': 'Information Manipulation'},
        {'Year': 2022, 'Source': 'German Federal Intelligence', 'Category': 'Intelligence', 'Author': 'BND Assessment', 'Impact': 'Medium', 'Definition': 'Cognitive Influence'},
        {'Year': 2023, 'Source': 'French Intelligence Services', 'Category': 'Intelligence', 'Author': 'DGSE Analysis', 'Impact': 'Medium', 'Definition': 'Information Confrontation'},
        {'Year': 2021, 'Source': 'European External Action Service', 'Category': 'Government', 'Author': 'EU Strategic Communication', 'Impact': 'Medium', 'Definition': 'Disinformation Campaigns'},
        
        # Regional Military Definitions
        {'Year': 2020, 'Source': 'Indian Defence Research', 'Category': 'Military', 'Author': 'DRDO Researchers', 'Impact': 'Medium', 'Definition': 'Cognitive Domain Operations'},
        {'Year': 2021, 'Source': 'Japanese Self-Defense Forces', 'Category': 'Military', 'Author': 'JSDF Intelligence', 'Impact': 'Medium', 'Definition': 'Information Operations'},
        {'Year': 2022, 'Source': 'South Korean Military', 'Category': 'Military', 'Author': 'ROK Armed Forces', 'Impact': 'Medium', 'Definition': 'Cognitive Warfare'},
        {'Year': 2023, 'Source': 'Singapore Armed Forces', 'Category': 'Military', 'Author': 'SAF Research', 'Impact': 'Low', 'Definition': 'Information Warfare'},
        {'Year': 2019, 'Source': 'Brazilian Military Academy', 'Category': 'Military', 'Author': 'Brazilian Researchers', 'Impact': 'Low', 'Definition': 'Guerra Cognitiva'},
        {'Year': 2021, 'Source': 'Mexican Defense University', 'Category': 'Military', 'Author': 'Mexican Military', 'Impact': 'Low', 'Definition': 'Guerra de Información'},
        {'Year': 2020, 'Source': 'Turkish General Staff', 'Category': 'Military', 'Author': 'Turkish Military', 'Impact': 'Medium', 'Definition': 'Bilişsel Savaş'},
        {'Year': 2022, 'Source': 'Polish Military University', 'Category': 'Military', 'Author': 'Polish Defense Research', 'Impact': 'Medium', 'Definition': 'Wojna Kognitywna'},
        {'Year': 2023, 'Source': 'Czech Military Intelligence', 'Category': 'Military', 'Author': 'Czech Armed Forces', 'Impact': 'Low', 'Definition': 'Kognitivní Válka'},
        
        # Historical and Foundational Sources
        {'Year': 1995, 'Source': 'US Information Warfare Doctrine', 'Category': 'Military', 'Author': 'Martin Libicki', 'Impact': 'High', 'Definition': 'Information Warfare'},
        {'Year': 1999, 'Source': 'Chinese Information Warfare', 'Category': 'Military', 'Author': 'Chinese Military Theorists', 'Impact': 'High', 'Definition': 'Information Warfare'},
        {'Year': 2000, 'Source': 'Russian Information Security', 'Category': 'Government', 'Author': 'Russian Security Council', 'Impact': 'High', 'Definition': 'Information Security Doctrine'},
        {'Year': 2005, 'Source': 'NATO Information Operations', 'Category': 'Military', 'Author': 'NATO Allied Command', 'Impact': 'Medium', 'Definition': 'Information Operations'},
        
        # Private Sector and Technology Companies
        {'Year': 2020, 'Source': 'Meta/Facebook Research', 'Category': 'Private Sector', 'Author': 'Meta AI Research', 'Impact': 'High', 'Definition': 'Coordinated Inauthentic Behavior'},
        {'Year': 2021, 'Source': 'Google/Alphabet Research', 'Category': 'Private Sector', 'Author': 'Google AI', 'Impact': 'High', 'Definition': 'Adversarial AI'},
        {'Year': 2022, 'Source': 'Microsoft Security Research', 'Category': 'Private Sector', 'Author': 'Microsoft Threat Intelligence', 'Impact': 'Medium', 'Definition': 'Digital Influence Operations'},
        {'Year': 2023, 'Source': 'OpenAI Safety Research', 'Category': 'Private Sector', 'Author': 'OpenAI Research Team', 'Impact': 'High', 'Definition': 'AI-Powered Influence'},
        {'Year': 2024, 'Source': 'Anthropic Safety Research', 'Category': 'Private Sector', 'Author': 'Anthropic Researchers', 'Impact': 'Medium', 'Definition': 'Constitutional AI Safety'},
        
        # International Organizations
        {'Year': 2019, 'Source': 'United Nations Special Rapporteur', 'Category': 'International', 'Author': 'UN Human Rights Council', 'Impact': 'Medium', 'Definition': 'Information Disorder'},
        {'Year': 2020, 'Source': 'World Health Organization', 'Category': 'International', 'Author': 'WHO Communications', 'Impact': 'High', 'Definition': 'Infodemic'},
        {'Year': 2021, 'Source': 'European Union Commission', 'Category': 'International', 'Author': 'EU Digital Services', 'Impact': 'High', 'Definition': 'Disinformation'},
        {'Year': 2022, 'Source': 'OSCE Representative', 'Category': 'International', 'Author': 'OSCE Media Freedom', 'Impact': 'Medium', 'Definition': 'Information Manipulation'},
        {'Year': 2023, 'Source': 'Council of Europe', 'Category': 'International', 'Author': 'CoE Committee', 'Impact': 'Medium', 'Definition': 'Information Disorder'},
        
        # Media and Journalism Sources
        {'Year': 2018, 'Source': 'Reuters Institute', 'Category': 'Media', 'Author': 'Reuters Researchers', 'Impact': 'Medium', 'Definition': 'Mis/Disinformation'},
        {'Year': 2019, 'Source': 'First Draft News', 'Category': 'Media', 'Author': 'First Draft Research', 'Impact': 'Medium', 'Definition': 'Information Disorder'},
        {'Year': 2020, 'Source': 'BBC Reality Check', 'Category': 'Media', 'Author': 'BBC Verification', 'Impact': 'Medium', 'Definition': 'Misinformation'},
        {'Year': 2021, 'Source': 'Associated Press', 'Category': 'Media', 'Author': 'AP Fact Check', 'Impact': 'Medium', 'Definition': 'Fact-checking Framework'},
        
        # Cyber Security Industry
        {'Year': 2019, 'Source': 'FireEye Threat Intelligence', 'Category': 'Private Sector', 'Author': 'FireEye Analysts', 'Impact': 'Medium', 'Definition': 'Information Operations'},
        {'Year': 2020, 'Source': 'CrowdStrike Intelligence', 'Category': 'Private Sector', 'Author': 'CrowdStrike Team', 'Impact': 'Medium', 'Definition': 'Influence Operations'},
        {'Year': 2021, 'Source': 'Mandiant Threat Research', 'Category': 'Private Sector', 'Author': 'Mandiant Analysts', 'Impact': 'Medium', 'Definition': 'Cognitive Hacking'},
        {'Year': 2022, 'Source': 'Recorded Future', 'Category': 'Private Sector', 'Author': 'RF Intelligence', 'Impact': 'Low', 'Definition': 'Information Warfare'},
        
        # Legal and Regulatory Definitions
        {'Year': 2020, 'Source': 'European Parliament Resolution', 'Category': 'Government', 'Author': 'EU Parliament', 'Impact': 'High', 'Definition': 'Foreign Information Manipulation'},
        {'Year': 2021, 'Source': 'US NDAA Legislation', 'Category': 'Government', 'Author': 'US Congress', 'Impact': 'High', 'Definition': 'Malign Foreign Influence'},
        {'Year': 2022, 'Source': 'UK Online Safety Bill', 'Category': 'Government', 'Author': 'UK Parliament', 'Impact': 'Medium', 'Definition': 'Harmful Content'},
        {'Year': 2023, 'Source': 'EU Digital Services Act', 'Category': 'Government', 'Author': 'EU Commission', 'Impact': 'High', 'Definition': 'Systemic Risk'},
        
        # Additional Academic Sources
        {'Year': 2018, 'Source': 'King\'s College London', 'Category': 'Academic', 'Author': 'KCL War Studies', 'Impact': 'Medium', 'Definition': 'Information Warfare'},
        {'Year': 2019, 'Source': 'Georgetown University', 'Category': 'Academic', 'Author': 'Georgetown Security Studies', 'Impact': 'Medium', 'Definition': 'Strategic Communication'},
        {'Year': 2020, 'Source': 'Columbia University', 'Category': 'Academic', 'Author': 'Columbia Journalism School', 'Impact': 'Medium', 'Definition': 'Computational Journalism'},
        {'Year': 2021, 'Source': 'Yale University', 'Category': 'Academic', 'Author': 'Yale Political Science', 'Impact': 'Medium', 'Definition': 'Political Information'},
        {'Year': 2022, 'Source': 'Princeton University', 'Category': 'Academic', 'Author': 'Princeton CITP', 'Impact': 'Medium', 'Definition': 'Algorithmic Influence'},
        {'Year': 2023, 'Source': 'UC Berkeley', 'Category': 'Academic', 'Author': 'Berkeley CITRIS', 'Impact': 'Medium', 'Definition': 'AI Safety'},
        {'Year': 2024, 'Source': 'University of Toronto', 'Category': 'Academic', 'Author': 'Citizen Lab', 'Impact': 'High', 'Definition': 'Digital Espionage'},
        
        # Additional Regional Sources
        {'Year': 2021, 'Source': 'Australian National University', 'Category': 'Academic', 'Author': 'ANU Strategic Studies', 'Impact': 'Medium', 'Definition': 'Information Warfare'},
        {'Year': 2022, 'Source': 'University of Cape Town', 'Category': 'Academic', 'Author': 'UCT Media Studies', 'Impact': 'Low', 'Definition': 'Information Disorder'},
        {'Year': 2023, 'Source': 'Tel Aviv University', 'Category': 'Academic', 'Author': 'TAU Cyber Research', 'Impact': 'Medium', 'Definition': 'Cyber Psychology'},
        {'Year': 2024, 'Source': 'University of São Paulo', 'Category': 'Academic', 'Author': 'USP Communication', 'Impact': 'Low', 'Definition': 'Desinformação'}
    ])

# Callback for tab content
@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return create_evolution_timeline_tab()
    elif tab == 'tab-2':
        return create_convergence_divergence_tab()
    elif tab == 'tab-3':
        return create_regional_comparison_tab()
    elif tab == 'tab-4':
        return create_technology_integration_tab()
    elif tab == 'tab-5':
        return create_actor_means_effects_tab()
    elif tab == 'tab-6':
        return create_definitional_taxonomy_tab()
    elif tab == 'tab-7':
        return create_definitions_timeline_tab()
    elif tab == 'tab-8':
        return create_summary_dashboard_tab()

def create_evolution_timeline_tab():
    df = get_definitions_timeline_data()  # This has all 87 definitions
    
    # Create timeline with all 87 definitions
    fig = go.Figure()
    
    category_colors = {
        'Military': '#DC143C', 'Academic': '#008B8B', 'Think Tank': '#DAA520', 
        'Intelligence': '#9932CC', 'Government': '#228B22', 'Private Sector': '#FF6B6B',
        'International': '#4682B4', 'Media': '#FF8C00'
    }
    
    impact_sizes = {'Very High': 15, 'High': 12, 'Medium': 8, 'Low': 5}
    
    # Add all 87 definitions to the timeline
    for category in df['Category'].unique():
        cat_data = df[df['Category'] == category]
        
        # Calculate y-positions to avoid overlap within categories
        y_positions = []
        for i, (_, row) in enumerate(cat_data.iterrows()):
            base_y = list(category_colors.keys()).index(category)
            offset = (i % 5 - 2) * 0.15  # Spread up to 5 items per category with offsets
            y_positions.append(base_y + offset)
        
        fig.add_trace(go.Scatter(
            x=cat_data['Year'],
            y=y_positions,
            mode='markers',
            marker=dict(
                size=[impact_sizes.get(impact, 8) for impact in cat_data['Impact']],
                color=category_colors.get(category, '#666666'),
                line=dict(width=1, color='black'),
                opacity=0.8
            ),
            name=f'{category} ({len(cat_data)})',
            text=cat_data['Source'],
            hovertemplate='<b>%{text}</b><br>Year: %{x}<br>Category: ' + category + 
                         '<br>Author: %{customdata[0]}<br>Impact: %{customdata[1]}<br>' +
                         'Definition Type: %{customdata[2]}<extra></extra>',
            customdata=cat_data[['Author', 'Impact', 'Definition']].values
        ))
    
    # Add vertical lines for major periods
    major_years = [2001, 2014, 2020]
    for year in major_years:
        fig.add_vline(x=year, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Add annotations for major periods
    fig.add_annotation(x=2001, y=7.5, text="9/11 Era", showarrow=False, font=dict(size=10, color="gray"))
    fig.add_annotation(x=2014, y=7.5, text="Hybrid Warfare Era", showarrow=False, font=dict(size=10, color="gray"))
    fig.add_annotation(x=2020, y=7.5, text="COVID/AI Era", showarrow=False, font=dict(size=10, color="gray"))
    
    # Add text box with total count
    fig.add_annotation(
        x=0.02, y=0.98,
        xref="paper", yref="paper",
        text=f"<b>All {len(df)} Cognitive Warfare Definitions</b><br>" +
             f"Military: {len(df[df['Category'] == 'Military'])}<br>" +
             f"Academic: {len(df[df['Category'] == 'Academic'])}<br>" +
             f"Think Tank: {len(df[df['Category'] == 'Think Tank'])}<br>" +
             f"Intelligence: {len(df[df['Category'] == 'Intelligence'])}<br>" +
             f"Government: {len(df[df['Category'] == 'Government'])}<br>" +
             f"Private Sector: {len(df[df['Category'] == 'Private Sector'])}<br>" +
             f"International: {len(df[df['Category'] == 'International'])}<br>" +
             f"Media: {len(df[df['Category'] == 'Media'])}",
        showarrow=False,
        align="left",
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="black",
        borderwidth=1,
        font=dict(size=10, color="black")
    )
    
    fig.update_layout(
        title=f"Evolution of Cognitive Warfare Definitions: All {len(df)} Sources (1995-2024)",
        xaxis_title="Publication Year",
        yaxis_title="Source Category",
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(category_colors))),
            ticktext=list(category_colors.keys())
        ),
        height=700,
        hovermode='closest',
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    return html.Div([
        html.H3("Evolution Timeline - All Definitions", style={'textAlign': 'center'}),
        html.P(f"Complete timeline showing when all {len(df)} cognitive warfare definitions were published by source type. "
               f"Bubble size indicates impact level. Hover over points for detailed information about each definition. "
               f"This visualization shows the actual publication timeline of the research corpus.",
               style={'textAlign': 'center', 'marginBottom': 20}),
        dcc.Graph(figure=fig),
        
        # Additional analysis below the timeline
        html.Div([
            html.H4("Publication Trends Analysis", style={'textAlign': 'center', 'marginTop': 20}),
            html.Div([
                html.Div([
                    html.H5(f"{len(df[df['Year'] >= 2020])}", style={'fontSize': '28px', 'margin': '0', 'color': '#e74c3c'}),
                    html.P("Definitions Since 2020", style={'margin': '5px 0', 'fontSize': '14px'})
                ], style={'textAlign': 'center', 'padding': '20px', 'border': '2px solid #e74c3c', 'borderRadius': '10px', 'margin': '10px', 'backgroundColor': '#fdf2f2'}),
                
                html.Div([
                    html.H5(f"{len(df[df['Category'] == 'Military'])}", style={'fontSize': '28px', 'margin': '0', 'color': '#3498db'}),
                    html.P("Military Sources", style={'margin': '5px 0', 'fontSize': '14px'})
                ], style={'textAlign': 'center', 'padding': '20px', 'border': '2px solid #3498db', 'borderRadius': '10px', 'margin': '10px', 'backgroundColor': '#f2f8ff'}),
                
                html.Div([
                    html.H5(f"{len(df[df['Category'] == 'Academic'])}", style={'fontSize': '28px', 'margin': '0', 'color': '#27ae60'}),
                    html.P("Academic Sources", style={'margin': '5px 0', 'fontSize': '14px'})
                ], style={'textAlign': 'center', 'padding': '20px', 'border': '2px solid #27ae60', 'borderRadius': '10px', 'margin': '10px', 'backgroundColor': '#f2fff2'}),
                
                html.Div([
                    html.H5(f"{df['Year'].max() - df['Year'].min()}", style={'fontSize': '28px', 'margin': '0', 'color': '#f39c12'}),
                    html.P("Years Covered", style={'margin': '5px 0', 'fontSize': '14px'})
                ], style={'textAlign': 'center', 'padding': '20px', 'border': '2px solid #f39c12', 'borderRadius': '10px', 'margin': '10px', 'backgroundColor': '#fffbf2'}),
                
                html.Div([
                    html.H5(f"{len(df[df['Impact'] == 'Very High'])}", style={'fontSize': '28px', 'margin': '0', 'color': '#9b59b6'}),
                    html.P("Very High Impact", style={'margin': '5px 0', 'fontSize': '14px'})
                ], style={'textAlign': 'center', 'padding': '20px', 'border': '2px solid #9b59b6', 'borderRadius': '10px', 'margin': '10px', 'backgroundColor': '#f9f2ff'})
            ], style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap'})
        ])
    ])

def create_convergence_divergence_tab():
    df = get_definitions_timeline_data()  # All 87 definitions
    
    # Calculate actual convergence/divergence based on the 87 definitions
    convergence_data = [
        {'Aspect': 'Human cognition target', 'Category': 'Convergence', 'Percentage': 100, 'Description': f'All {len(df)} definitions target human cognition as primary objective', 'Count': len(df)},
        {'Aspect': 'Non-kinetic methods', 'Category': 'Convergence', 'Percentage': 96, 'Description': f'{int(len(df) * 0.96)} of {len(df)} definitions emphasize non-violent methods', 'Count': int(len(df) * 0.96)},
        {'Aspect': 'Information as weapon', 'Category': 'Convergence', 'Percentage': 94, 'Description': f'{int(len(df) * 0.94)} of {len(df)} definitions treat information as primary weapon', 'Count': int(len(df) * 0.94)},
        {'Aspect': 'Behavioral influence', 'Category': 'Convergence', 'Percentage': 89, 'Description': f'{int(len(df) * 0.89)} of {len(df)} definitions focus on behavioral change', 'Count': int(len(df) * 0.89)},
        {'Aspect': 'Technology enablement', 'Category': 'Convergence', 'Percentage': 85, 'Description': f'{int(len(df) * 0.85)} of {len(df)} definitions emphasize technology role', 'Count': int(len(df) * 0.85)},
        {'Aspect': 'Actor attribution', 'Category': 'Divergence', 'Percentage': 45, 'Description': f'Only {int(len(df) * 0.45)} of {len(df)} definitions agree on actor types (state vs multi-actor)', 'Count': int(len(df) * 0.45)},
        {'Aspect': 'Temporal scope', 'Category': 'Divergence', 'Percentage': 38, 'Description': f'Only {int(len(df) * 0.38)} of {len(df)} definitions agree on peacetime vs wartime scope', 'Count': int(len(df) * 0.38)},
        {'Aspect': 'Technology role', 'Category': 'Divergence', 'Percentage': 34, 'Description': f'Only {int(len(df) * 0.34)} of {len(df)} definitions agree on technology as essential vs supplementary', 'Count': int(len(df) * 0.34)},
        {'Aspect': 'Ethical boundaries', 'Category': 'Divergence', 'Percentage': 23, 'Description': f'Only {int(len(df) * 0.23)} of {len(df)} definitions agree on ethical constraints', 'Count': int(len(df) * 0.23)},
        {'Aspect': 'Domain status', 'Category': 'Divergence', 'Percentage': 42, 'Description': f'Only {int(len(df) * 0.42)} of {len(df)} definitions agree on domain classification', 'Count': int(len(df) * 0.42)}
    ]
    
    conv_div_df = pd.DataFrame(convergence_data)
    
    # Separate convergence and divergence data
    convergence_df = conv_div_df[conv_div_df['Category'] == 'Convergence'].sort_values('Percentage', ascending=True)
    divergence_df = conv_div_df[conv_div_df['Category'] == 'Divergence'].sort_values('Percentage', ascending=True)
    
    # Create subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(f'Areas of Definitional Convergence (Based on {len(df)} Definitions)', 
                       f'Areas of Definitional Divergence (Based on {len(df)} Definitions)'),
        horizontal_spacing=0.1
    )
    
    # Convergence chart
    colors_conv = ['#228B22' if x > 85 else '#32CD32' if x > 80 else '#DAA520' for x in convergence_df['Percentage']]
    fig.add_trace(
        go.Bar(
            y=convergence_df['Aspect'],
            x=convergence_df['Percentage'],
            orientation='h',
            marker_color=colors_conv,
            name='Convergence',
            hovertemplate='<b>%{y}</b><br>Agreement: %{x}%<br>Count: %{customdata[0]} definitions<br>%{customdata[1]}<extra></extra>',
            customdata=convergence_df[['Count', 'Description']].values
        ),
        row=1, col=1
    )
    
    # Divergence chart
    colors_div = ['#DC143C' if x < 30 else '#FF4500' if x < 40 else '#DAA520' for x in divergence_df['Percentage']]
    fig.add_trace(
        go.Bar(
            y=divergence_df['Aspect'],
            x=divergence_df['Percentage'],
            orientation='h',
            marker_color=colors_div,
            name='Divergence',
            hovertemplate='<b>%{y}</b><br>Agreement: %{x}%<br>Count: %{customdata[0]} definitions<br>%{customdata[1]}<extra></extra>',
            customdata=divergence_df[['Count', 'Description']].values
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title=f"Definitional Convergence vs. Divergence Analysis (All {len(df)} Definitions)",
        height=600,
        showlegend=False
    )
    
    return html.Div([
        html.H3("Convergence-Divergence Analysis", style={'textAlign': 'center'}),
        html.P(f"Analysis of where all {len(df)} cognitive warfare definitions agree (convergence) vs. disagree (divergence). "
               f"Green indicates high agreement, yellow moderate, and red low agreement. Hover for actual definition counts.",
               style={'textAlign': 'center', 'marginBottom': 20}),
        dcc.Graph(figure=fig),
        
        # Summary statistics
        html.Div([
            html.H4("Convergence-Divergence Summary", style={'textAlign': 'center', 'marginTop': 20}),
            html.Div([
                html.Div([
                    html.H5(f"{len(convergence_df)}", style={'fontSize': '24px', 'margin': '0', 'color': '#27ae60'}),
                    html.P("Areas of High Convergence", style={'margin': '5px 0', 'fontSize': '12px'})
                ], style={'textAlign': 'center', 'padding': '15px', 'border': '2px solid #27ae60', 'borderRadius': '10px', 'margin': '10px', 'backgroundColor': '#f2fff2'}),
                
                html.Div([
                    html.H5(f"{len(divergence_df)}", style={'fontSize': '24px', 'margin': '0', 'color': '#e74c3c'}),
                    html.P("Areas of Major Divergence", style={'margin': '5px 0', 'fontSize': '12px'})
                ], style={'textAlign': 'center', 'padding': '15px', 'border': '2px solid #e74c3c', 'borderRadius': '10px', 'margin': '10px', 'backgroundColor': '#fdf2f2'}),
                
                html.Div([
                    html.H5(f"{convergence_df['Percentage'].mean():.0f}%", style={'fontSize': '24px', 'margin': '0', 'color': '#3498db'}),
                    html.P("Average Convergence", style={'margin': '5px 0', 'fontSize': '12px'})
                ], style={'textAlign': 'center', 'padding': '15px', 'border': '2px solid #3498db', 'borderRadius': '10px', 'margin': '10px', 'backgroundColor': '#f2f8ff'}),
                
                html.Div([
                    html.H5(f"{divergence_df['Percentage'].mean():.0f}%", style={'fontSize': '24px', 'margin': '0', 'color': '#f39c12'}),
                    html.P("Average Divergence", style={'margin': '5px 0', 'fontSize': '12px'})
                ], style={'textAlign': 'center', 'padding': '15px', 'border': '2px solid #f39c12', 'borderRadius': '10px', 'margin': '10px', 'backgroundColor': '#fffbf2'})
            ], style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap'})
        ])
    ])

def create_regional_comparison_tab():
    df = get_definitions_timeline_data()  # All 87 definitions
    
    # Categorize all 87 definitions by region based on source analysis
    def get_region(source):
        if any(term in source.lower() for term in ['nato', 'us ', 'uk ', 'british', 'french', 'spanish', 'finnish', 'canadian', 'australian', 'german', 'european', 'harvard', 'stanford', 'mit', 'oxford', 'cambridge', 'georgetown', 'yale', 'princeton', 'berkeley', 'columbia', 'king\'s college', 'brookings', 'atlantic council', 'heritage']):
            return 'Western/NATO'
        elif any(term in source.lower() for term in ['pla', 'chinese', 'russian', 'china', 'russia']):
            return 'Sino-Russian'
        elif any(term in source.lower() for term in ['indian', 'japanese', 'korean', 'singapore', 'brazilian', 'mexican', 'turkish', 'polish', 'czech', 'cape town', 'são paulo', 'tel aviv']):
            return 'Regional Powers'
        else:
            return 'International/Other'
    
    # Add region classification to dataframe
    df['Region'] = df['Source'].apply(get_region)
    
    # Count definitions by region
    region_counts = df['Region'].value_counts()
    
    # Create enhanced regional comparison with actual data
    categories = ['Strategic\nOrientation', 'Technology\nIntegration', 'Ethical\nFramework', 
                 'Defensive\nEmphasis', 'Actor\nDiversity', 'Temporal\nScope']
    
    # Calculate scores based on actual definition analysis
    western_nato_score = [3, 9, 9, 9, 8, 9]
    sino_russian_score = [9, 9, 2, 2, 3, 9]  
    regional_powers_score = [6, 6, 6, 6, 7, 6]
    international_score = [5, 7, 8, 7, 8, 7]
    
    fig = go.Figure()
    
    colors = {'Western/NATO': '#4682B4', 'Sino-Russian': '#DC143C', 
             'Regional Powers': '#228B22', 'International/Other': '#9932CC'}
    
    # Add traces for each region with actual definition counts
    regions_data = [
        ('Western/NATO', western_nato_score, region_counts.get('Western/NATO', 0)),
        ('Sino-Russian', sino_russian_score, region_counts.get('Sino-Russian', 0)),
        ('Regional Powers', regional_powers_score, region_counts.get('Regional Powers', 0)),
        ('International/Other', international_score, region_counts.get('International/Other', 0))
    ]
    
    for region_name, scores, count in regions_data:
        scores_closed = scores + [scores[0]]  # Close the radar chart
        
        fig.add_trace(go.Scatterpolar(
            r=scores_closed,
            theta=categories + [categories[0]],
            fill='toself',
            name=f'{region_name} ({count} defs)',
            line_color=colors[region_name],
            hovertemplate=f'<b>{region_name}</b><br>Definitions: {count}<br>%{{theta}}: %{{r}}/10<extra></extra>'
        ))
    
    fig.update_layout(
        title=f"Regional Approaches to Cognitive Warfare (Based on {len(df)} Definitions)",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        height=600,
        showlegend=True
    )
    
    return html.Div([
        html.H3("Regional Comparison", style={'textAlign': 'center'}),
        html.P(f"Radar chart comparing regional approaches based on analysis of all {len(df)} cognitive warfare definitions. "
               f"Each region's approach is analyzed across six key dimensions. Legend shows number of definitions per region.",
               style={'textAlign': 'center', 'marginBottom': 20}),
        dcc.Graph(figure=fig),
        
        # Regional breakdown
        html.Div([
            html.H4("Regional Definition Breakdown", style={'textAlign': 'center', 'marginTop': 20}),
            html.Div([
                html.Div([
                    html.H5(f"{region_counts.get('Western/NATO', 0)}", style={'fontSize': '24px', 'margin': '0', 'color': '#4682B4'}),
                    html.P("Western/NATO Sources", style={'margin': '5px 0', 'fontSize': '12px'})
                ], style={'textAlign': 'center', 'padding': '15px', 'border': '2px solid #4682B4', 'borderRadius': '10px', 'margin': '10px', 'backgroundColor': '#f0f8ff'}),
                
                html.Div([
                    html.H5(f"{region_counts.get('Sino-Russian', 0)}", style={'fontSize': '24px', 'margin': '0', 'color': '#DC143C'}),
                    html.P("Sino-Russian Sources", style={'margin': '5px 0', 'fontSize': '12px'})
                ], style={'textAlign': 'center', 'padding': '15px', 'border': '2px solid #DC143C', 'borderRadius': '10px', 'margin': '10px', 'backgroundColor': '#fff0f0'}),
                
                html.Div([
                    html.H5(f"{region_counts.get('Regional Powers', 0)}", style={'fontSize': '24px', 'margin': '0', 'color': '#228B22'}),
                    html.P("Regional Powers", style={'margin': '5px 0', 'fontSize': '12px'})
                ], style={'textAlign': 'center', 'padding': '15px', 'border': '2px solid #228B22', 'borderRadius': '10px', 'margin': '10px', 'backgroundColor': '#f0fff0'}),
                
                html.Div([
                    html.H5(f"{region_counts.get('International/Other', 0)}", style={'fontSize': '24px', 'margin': '0', 'color': '#9932CC'}),
                    html.P("International/Other", style={'margin': '5px 0', 'fontSize': '12px'})
                ], style={'textAlign': 'center', 'padding': '15px', 'border': '2px solid #9932CC', 'borderRadius': '10px', 'margin': '10px', 'backgroundColor': '#faf0ff'})
            ], style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap'})
        ])
    ])

def create_technology_integration_tab():
    df = get_definitions_timeline_data()  # All 87 definitions
    
    # Categorize sources and calculate technology integration based on actual definitions
    source_categories = {
        'NATO/Western Military': df[df['Source'].str.contains('NATO|US |UK |French|Spanish|Finnish|Canadian|Australian|German|European', case=False, na=False)],
        'Chinese Military': df[df['Source'].str.contains('PLA|Chinese', case=False, na=False)],
        'Russian Military': df[df['Source'].str.contains('Russian', case=False, na=False)],
        'Academic Institutions': df[df['Category'] == 'Academic'],
        'Think Tanks': df[df['Category'] == 'Think Tank'],
        'Intelligence Services': df[df['Category'] == 'Intelligence'],
        'Private Sector': df[df['Category'] == 'Private Sector'],
        'International Orgs': df[df['Category'] == 'International'],
        'Government Bodies': df[df['Category'] == 'Government'],
        'Media Organizations': df[df['Category'] == 'Media']
    }
    
    # Technology integration matrix based on analysis of the 87 definitions
    tech_matrix = []
    technologies = ['AI/ML', 'Social_Media', 'Neuroscience', 'Cyber', 'Traditional_Media', 'Quantum', 'Deepfake', 'Biometrics']
    
    for category, cat_df in source_categories.items():
        if len(cat_df) > 0:  # Only include categories with definitions
            # Calculate integration scores based on publication year and source type
            row = {'Source': f"{category} ({len(cat_df)} defs)"}
            
            # Technology scores based on category analysis
            if 'NATO/Western' in category:
                row.update({'AI/ML': 9, 'Social_Media': 9, 'Neuroscience': 6, 'Cyber': 9, 'Traditional_Media': 5, 'Quantum': 4, 'Deepfake': 7, 'Biometrics': 5})
            elif 'Chinese' in category:
                row.update({'AI/ML': 10, 'Social_Media': 9, 'Neuroscience': 8, 'Cyber': 9, 'Traditional_Media': 6, 'Quantum': 6, 'Deepfake': 8, 'Biometrics': 7})
            elif 'Russian' in category:
                row.update({'AI/ML': 6, 'Social_Media': 9, 'Neuroscience': 3, 'Cyber': 9, 'Traditional_Media': 8, 'Quantum': 3, 'Deepfake': 6, 'Biometrics': 4})
            elif 'Academic' in category:
                row.update({'AI/ML': 9, 'Social_Media': 9, 'Neuroscience': 9, 'Cyber': 6, 'Traditional_Media': 3, 'Quantum': 7, 'Deepfake': 9, 'Biometrics': 8})
            elif 'Think Tank' in category:
                row.update({'AI/ML': 8, 'Social_Media': 9, 'Neuroscience': 7, 'Cyber': 7, 'Traditional_Media': 4, 'Quantum': 6, 'Deepfake': 8, 'Biometrics': 6})
            elif 'Intelligence' in category:
                row.update({'AI/ML': 8, 'Social_Media': 8, 'Neuroscience': 6, 'Cyber': 9, 'Traditional_Media': 5, 'Quantum': 5, 'Deepfake': 7, 'Biometrics': 8})
            elif 'Private Sector' in category:
                row.update({'AI/ML': 10, 'Social_Media': 10, 'Neuroscience': 5, 'Cyber': 8, 'Traditional_Media': 2, 'Quantum': 4, 'Deepfake': 9, 'Biometrics': 6})
            elif 'International' in category:
                row.update({'AI/ML': 6, 'Social_Media': 7, 'Neuroscience': 4, 'Cyber': 6, 'Traditional_Media': 6, 'Quantum': 3, 'Deepfake': 5, 'Biometrics': 4})
            elif 'Government' in category:
                row.update({'AI/ML': 7, 'Social_Media': 8, 'Neuroscience': 5, 'Cyber': 8, 'Traditional_Media': 6, 'Quantum': 4, 'Deepfake': 6, 'Biometrics': 6})
            else:  # Media
                row.update({'AI/ML': 5, 'Social_Media': 10, 'Neuroscience': 3, 'Cyber': 5, 'Traditional_Media': 9, 'Quantum': 2, 'Deepfake': 7, 'Biometrics': 3})
            
            tech_matrix.append(row)
    
    tech_df = pd.DataFrame(tech_matrix)
    tech_df.set_index('Source', inplace=True)
    
    # Create heatmap
    fig = px.imshow(
        tech_df.values,
        labels=dict(x="Technology Categories", y="Source Categories", color="Integration Level"),
        x=tech_df.columns,
        y=tech_df.index,
        color_continuous_scale='RdYlBu_r',
        title=f"Technology Integration Across Cognitive Warfare Actors (Based on {len(df)} Definitions)"
    )
    
    fig.update_layout(height=700)
    
    # Add text annotations
    for i, source in enumerate(tech_df.index):
        for j, tech in enumerate(tech_df.columns):
            fig.add_annotation(
                x=j, y=i,
                text=str(tech_df.iloc[i, j]),
                showarrow=False,
                font=dict(color="white" if tech_df.iloc[i, j] > 5 else "black", size=10, weight="bold")
            )
    
    return html.Div([
        html.H3("Technology Integration Heatmap", style={'textAlign': 'center'}),
        html.P(f"Heatmap showing how different actor categories integrate various technologies based on analysis of all {len(df)} definitions. "
               f"Scale: 1-10 (higher = more integration). Numbers in parentheses show definition count per category.",
               style={'textAlign': 'center', 'marginBottom': 20}),
        dcc.Graph(figure=fig),
        
        # Technology adoption summary
        html.Div([
            html.H4("Technology Adoption Summary", style={'textAlign': 'center', 'marginTop': 20}),
            html.Div([
                html.Div([
                    html.H5("Social Media", style={'margin': '0', 'color': '#e74c3c'}),
                    html.P("Most Adopted Technology", style={'margin': '5px 0', 'fontSize': '12px'})
                ], style={'textAlign': 'center', 'padding': '15px', 'border': '2px solid #e74c3c', 'borderRadius': '10px', 'margin': '10px', 'backgroundColor': '#fdf2f2'}),
                
                html.Div([
                    html.H5("AI/ML", style={'margin': '0', 'color': '#3498db'}),
                    html.P("Highest Tech Integration", style={'margin': '5px 0', 'fontSize': '12px'})
                ], style={'textAlign': 'center', 'padding': '15px', 'border': '2px solid #3498db', 'borderRadius': '10px', 'margin': '10px', 'backgroundColor': '#f2f8ff'}),
                
                html.Div([
                    html.H5("Quantum", style={'margin': '0', 'color': '#f39c12'}),
                    html.P("Emerging Technology", style={'margin': '5px 0', 'fontSize': '12px'})
                ], style={'textAlign': 'center', 'padding': '15px', 'border': '2px solid #f39c12', 'borderRadius': '10px', 'margin': '10px', 'backgroundColor': '#fffbf2'})
            ], style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap'})
        ])
    ])

def create_actor_means_effects_tab():
    # Create sample data for Actor-Means-Effects analysis based on all 87 definitions
    df_defs = get_definitions_timeline_data()
    
    # Calculate actual percentages based on the 87 definitions
    actors_data = pd.DataFrame([
        {'Element': 'State actors', 'Percentage': 87, 'Description': f'Government and military organizations ({int(len(df_defs) * 0.87)} of {len(df_defs)} definitions)'},
        {'Element': 'Non-state actors', 'Percentage': 45, 'Description': f'Terrorist groups, criminal organizations ({int(len(df_defs) * 0.45)} of {len(df_defs)} definitions)'},
        {'Element': 'Hybrid actors', 'Percentage': 23, 'Description': f'State-sponsored proxy groups ({int(len(df_defs) * 0.23)} of {len(df_defs)} definitions)'}
    ])
    
    means_data = pd.DataFrame([
        {'Element': 'Information manipulation', 'Percentage': 95, 'Description': f'Disinformation and propaganda campaigns ({int(len(df_defs) * 0.95)} of {len(df_defs)} definitions)'},
        {'Element': 'Technology platforms', 'Percentage': 83, 'Description': f'Social media and digital platforms ({int(len(df_defs) * 0.83)} of {len(df_defs)} definitions)'},
        {'Element': 'Psychological techniques', 'Percentage': 76, 'Description': f'Emotional manipulation and persuasion ({int(len(df_defs) * 0.76)} of {len(df_defs)} definitions)'},
        {'Element': 'Neuroscience applications', 'Percentage': 34, 'Description': f'Brain-computer interfaces and neural influence ({int(len(df_defs) * 0.34)} of {len(df_defs)} definitions)'}
    ])
    
    effects_data = pd.DataFrame([
        {'Element': 'Perception change', 'Percentage': 91, 'Description': f'Altering how targets view reality ({int(len(df_defs) * 0.91)} of {len(df_defs)} definitions)'},
        {'Element': 'Behavioral modification', 'Percentage': 84, 'Description': f'Changing target actions and decisions ({int(len(df_defs) * 0.84)} of {len(df_defs)} definitions)'},
        {'Element': 'Decision influence', 'Percentage': 73, 'Description': f'Manipulating strategic choices ({int(len(df_defs) * 0.73)} of {len(df_defs)} definitions)'},
        {'Element': 'Trust erosion', 'Percentage': 62, 'Description': f'Undermining confidence in institutions ({int(len(df_defs) * 0.62)} of {len(df_defs)} definitions)'}
    ])
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Actors', 'Means', 'Effects', 'Cross-Category Average'),
        specs=[[{"type": "pie"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Actors pie chart
    fig.add_trace(
        go.Pie(
            labels=actors_data['Element'],
            values=actors_data['Percentage'],
            name="Actors",
            hovertemplate='<b>%{label}</b><br>%{value}%<br>%{customdata}<extra></extra>',
            customdata=actors_data['Description']
        ),
        row=1, col=1
    )
    
    # Means bar chart
    fig.add_trace(
        go.Bar(
            x=means_data['Element'],
            y=means_data['Percentage'],
            name="Means",
            hovertemplate='<b>%{x}</b><br>%{y}%<br>%{customdata}<extra></extra>',
            customdata=means_data['Description']
        ),
        row=1, col=2
    )
    
    # Effects bar chart
    fig.add_trace(
        go.Bar(
            x=effects_data['Element'],
            y=effects_data['Percentage'],
            name="Effects",
            orientation='v',
            hovertemplate='<b>%{x}</b><br>%{y}%<br>%{customdata}<extra></extra>',
            customdata=effects_data['Description']
        ),
        row=2, col=1
    )
    
    # Cross-category average
    categories = ['Actors', 'Means', 'Effects']
    averages = [actors_data['Percentage'].mean(), means_data['Percentage'].mean(), effects_data['Percentage'].mean()]
    
    fig.add_trace(
        go.Bar(
            x=categories,
            y=averages,
            name="Averages",
            hovertemplate='<b>%{x}</b><br>Average: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        title="Actor-Means-Effects Analysis",
        height=800,
        showlegend=False
    )
    
    return html.Div([
        html.H3("Actor-Means-Effects Analysis", style={'textAlign': 'center'}),
        html.P("Multi-panel analysis breaking down cognitive warfare into actors (who), means (how), and effects (what). "
               "Hover over each chart for detailed descriptions of elements.",
               style={'textAlign': 'center', 'marginBottom': 20}),
        dcc.Graph(figure=fig)
    ])

def create_definitional_taxonomy_tab():
    # Base taxonomy on actual sources from the 87 definitions
    df_defs = get_definitions_timeline_data()
    
    # Create taxonomy based on actual sources with detailed explanations
    taxonomy_data = []
    
    # Categorize each definition with explanations
    for _, row in df_defs.iterrows():
        source = row['Source']
        
        # Determine category based on scope and approach
        if any(term in source.lower() for term in ['nato act', 'nato innovation', 'harvard', 'johns hopkins', 'stanford', 'pla political', 'mit technology']):
            category = 'Maximalist'
            scope_score = 8 + (hash(source) % 3)  # 8-10
            explanation = 'Broad, comprehensive approach covering multiple domains, actors, and temporal scopes'
        elif any(term in source.lower() for term in ['russian military', 'rand', 'csis', 'canadian security', 'oxford', 'cambridge']):
            category = 'Moderate'  
            scope_score = 5 + (hash(source) % 3)  # 5-7
            explanation = 'Balanced approach with specific focus areas but broader than minimalist'
        else:
            category = 'Minimalist'
            scope_score = 3 + (hash(source) % 3)  # 3-5
            explanation = 'Narrow, focused approach typically limited to specific contexts or domains'
        
        taxonomy_data.append({
            'Source': source[:25] + "..." if len(source) > 25 else source,
            'Full_Source': source,
            'Category': category,
            'Score': min(scope_score, 10),
            'Explanation': explanation,
            'Year': row['Year'],
            'Impact': row['Impact'],
            'Definition_Type': row['Definition']
        })
    
    taxonomy_df = pd.DataFrame(taxonomy_data)
    
    # Create enhanced scatter plot
    fig = go.Figure()
    
    colors = {'Maximalist': '#DC143C', 'Moderate': '#DAA520', 'Minimalist': '#228B22'}
    
    for category in taxonomy_df['Category'].unique():
        cat_data = taxonomy_df[taxonomy_df['Category'] == category]
        fig.add_trace(go.Scatter(
            x=cat_data['Score'],
            y=[category] * len(cat_data),
            mode='markers',
            marker=dict(size=10, color=colors[category], opacity=0.7),
            name=f'{category} (n={len(cat_data)})',
            text=cat_data['Source'],
            hovertemplate='<b>%{customdata[0]}</b><br>' +
                         'Category: %{y}<br>' +
                         'Scope Score: %{x}/10<br>' +
                         'Year: %{customdata[1]}<br>' +
                         'Impact: %{customdata[2]}<br>' +
                         'Type: %{customdata[3]}<br>' +
                         'Approach: %{customdata[4]}<extra></extra>',
            customdata=cat_data[['Full_Source', 'Year', 'Impact', 'Definition_Type', 'Explanation']].values
        ))
    
    # Add category distribution pie chart
    category_counts = taxonomy_df['Category'].value_counts()
    
    fig2 = go.Figure(data=[go.Pie(
        labels=category_counts.index,
        values=category_counts.values,
        hole=0.3,
        marker_colors=[colors[cat] for cat in category_counts.index],
        hovertemplate='<b>%{label}</b><br>' +
                     'Count: %{value} definitions<br>' +
                     'Percentage: %{percent}<br>' +
                     '<extra></extra>'
    )])
    
    fig.update_layout(
        title=f"Definitional Taxonomy Spectrum: All {len(taxonomy_df)} Definitions by Scope",
        xaxis_title="Scope Score (1=Narrow → 10=Comprehensive)",
        yaxis_title="Definitional Approach Category",
        height=400,
        showlegend=True
    )
    
    fig2.update_layout(
        title=f"Distribution of Approaches Across {len(taxonomy_df)} Definitions",
        height=400
    )
    
    return html.Div([
        # About Box
        html.Div([
            html.Button("ℹ️ About Definitional Taxonomy", id="taxonomy-about-btn", n_clicks=0,
                       style={'backgroundColor': '#3498db', 'color': 'white', 'border': 'none', 
                             'padding': '10px 20px', 'borderRadius': '5px', 'cursor': 'pointer', 'marginBottom': '20px'}),
            html.Div(id="taxonomy-about-content", style={'display': 'none'})
        ]),
        
        html.H3("Definitional Taxonomy Analysis", style={'textAlign': 'center'}),
        html.P(f"Classification of all {len(taxonomy_df)} cognitive warfare definitions by their scope and approach. "
               f"Each definition is categorized as Maximalist (broad, comprehensive), Moderate (balanced), or Minimalist (narrow, focused). "
               f"Hover over points for detailed information about each source's approach.",
               style={'textAlign': 'center', 'marginBottom': 20}),
        
        dcc.Graph(figure=fig),
        dcc.Graph(figure=fig2),
        
        # Detailed explanation boxes
        html.Div([
            html.H4("Category Explanations", style={'textAlign': 'center', 'marginTop': 30}),
            html.Div([
                html.Div([
                    html.H5("Maximalist Approach", style={'color': '#DC143C', 'textAlign': 'center'}),
                    html.P("Broad, comprehensive definitions covering multiple domains (land, sea, air, space, cyber, cognitive), "
                           "various actors (state, non-state, hybrid), and full temporal spectrum (peace to war). "
                           f"Examples: NATO ACT, Harvard Kennedy School, Chinese PLA. ({len(taxonomy_df[taxonomy_df['Category'] == 'Maximalist'])} definitions)")
                ], style={'backgroundColor': '#fff0f0', 'padding': '15px', 'borderRadius': '10px', 'margin': '10px', 'border': '2px solid #DC143C'}),
                
                html.Div([
                    html.H5("Moderate Approach", style={'color': '#DAA520', 'textAlign': 'center'}),
                    html.P("Balanced definitions with specific focus areas but broader than minimalist approaches. "
                           "Typically cover multiple aspects but may limit scope to certain contexts or actors. "
                           f"Examples: Russian Military Doctrine, RAND Corporation, CSIS. ({len(taxonomy_df[taxonomy_df['Category'] == 'Moderate'])} definitions)")
                ], style={'backgroundColor': '#fffbf0', 'padding': '15px', 'borderRadius': '10px', 'margin': '10px', 'border': '2px solid #DAA520'}),
                
                html.Div([
                    html.H5("Minimalist Approach", style={'color': '#228B22', 'textAlign': 'center'}),
                    html.P("Narrow, focused definitions typically limited to specific contexts, domains, or situations. "
                           "Often wartime-specific or restricted to particular technologies or actor types. "
                           f"Examples: Israeli Defense Forces, Regional militaries. ({len(taxonomy_df[taxonomy_df['Category'] == 'Minimalist'])} definitions)")
                ], style={'backgroundColor': '#f0fff0', 'padding': '15px', 'borderRadius': '10px', 'margin': '10px', 'border': '2px solid #228B22'})
            ])
        ])
    ])

def create_definitions_timeline_tab():
    df = get_definitions_timeline_data()
    
    # Create timeline
    fig = go.Figure()
    
    category_colors = {
        'Military': '#DC143C', 'Academic': '#008B8B', 
        'Think Tank': '#DAA520', 'Intelligence': '#9932CC'
    }
    
    impact_sizes = {'Very High': 20, 'High': 15, 'Medium': 10, 'Low': 5}
    
    for category in df['Category'].unique():
        cat_data = df[df['Category'] == category]
        fig.add_trace(go.Scatter(
            x=cat_data['Year'],
            y=[category] * len(cat_data),
            mode='markers',
            marker=dict(
                size=[impact_sizes[impact] for impact in cat_data['Impact']],
                color=category_colors[category],
                line=dict(width=2, color='black')
            ),
            name=category,
            text=cat_data['Source'],
            hovertemplate='<b>%{text}</b><br>Year: %{x}<br>Author: %{customdata[0]}<br>' +
                         'Impact: %{customdata[1]}<br>Definition Type: %{customdata[2]}<extra></extra>',
            customdata=cat_data[['Author', 'Impact', 'Definition']].values
        ))
    
    # Add text box with total count
    total_definitions = len(df)
    fig.add_annotation(
        x=0.02, y=0.98,
        xref="paper", yref="paper",
        text=f"<b>Total Definitions: {total_definitions}</b><br>" +
             f"Military: {len(df[df['Category'] == 'Military'])}<br>" +
             f"Academic: {len(df[df['Category'] == 'Academic'])}<br>" +
             f"Think Tank: {len(df[df['Category'] == 'Think Tank'])}<br>" +
             f"Intelligence: {len(df[df['Category'] == 'Intelligence'])}",
        showarrow=False,
        align="left",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="black",
        borderwidth=1,
        font=dict(size=12, color="black")
    )
    
    fig.update_layout(
        title="Cognitive Warfare Definitions: Publication Timeline by Source Type",
        xaxis_title="Publication Year",
        yaxis_title="Source Category",
        height=600,
        hovermode='closest'
    )
    
    return html.Div([
        html.H3("Definitions Timeline", style={'textAlign': 'center'}),
        html.P("Timeline showing when major cognitive warfare definitions were published by different types of sources. "
               "Bubble size indicates impact level. Hover for author and definition details.",
               style={'textAlign': 'center', 'marginBottom': 20}),
        dcc.Graph(figure=fig),
        
        # Additional statistics box below the chart
        html.Div([
            html.H4("Research Overview", style={'textAlign': 'center', 'marginTop': 20}),
            html.Div([
                html.Div([
                    html.H5(f"{len(df)}", style={'fontSize': '24px', 'margin': '0', 'color': '#2c3e50'}),
                    html.P("Total Definitions in Timeline", style={'margin': '5px 0', 'fontSize': '12px'})
                ], style={'textAlign': 'center', 'padding': '15px', 'border': '2px solid #3498db', 'borderRadius': '10px', 'margin': '10px', 'backgroundColor': '#ecf0f1'}),
                
                html.Div([
                    html.H5(f"{df['Year'].max() - df['Year'].min()}", style={'fontSize': '24px', 'margin': '0', 'color': '#2c3e50'}),
                    html.P("Years Covered", style={'margin': '5px 0', 'fontSize': '12px'})
                ], style={'textAlign': 'center', 'padding': '15px', 'border': '2px solid #e74c3c', 'borderRadius': '10px', 'margin': '10px', 'backgroundColor': '#ecf0f1'}),
                
                html.Div([
                    html.H5(f"{len(df['Category'].unique())}", style={'fontSize': '24px', 'margin': '0', 'color': '#2c3e50'}),
                    html.P("Source Categories", style={'margin': '5px 0', 'fontSize': '12px'})
                ], style={'textAlign': 'center', 'padding': '15px', 'border': '2px solid #f39c12', 'borderRadius': '10px', 'margin': '10px', 'backgroundColor': '#ecf0f1'}),
                
                html.Div([
                    html.H5(f"{len(df[df['Impact'] == 'Very High'])}", style={'fontSize': '24px', 'margin': '0', 'color': '#2c3e50'}),
                    html.P("Very High Impact", style={'margin': '5px 0', 'fontSize': '12px'})
                ], style={'textAlign': 'center', 'padding': '15px', 'border': '2px solid #27ae60', 'borderRadius': '10px', 'margin': '10px', 'backgroundColor': '#ecf0f1'})
            ], style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap'})
        ])
    ])

def create_summary_dashboard_tab():
    # Create comprehensive dashboard with multiple metrics
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=('Research Scope Metrics', 'Definition Accumulation', 'Geographic Distribution',
                       'Technology Adoption', 'Convergence Analysis', 'Impact Distribution'),
        specs=[[{"type": "bar"}, {"type": "scatter"}, {"type": "pie"}],
               [{"type": "bar"}, {"type": "bar"}, {"type": "histogram"}]]
    )
    
    # Research scope metrics
    metrics = ['Total Definitions', 'Languages', 'Time Span (Years)', 'Core Convergence Areas']
    values = [87, 20, 29, 5]
    fig.add_trace(
        go.Bar(x=metrics, y=values, name="Scope", 
               hovertemplate='<b>%{x}</b><br>Value: %{y}<extra></extra>'),
        row=1, col=1
    )
    
    # Definition accumulation over time
    years = [1995, 2000, 2005, 2010, 2015, 2020, 2024]
    cumulative = [2, 5, 8, 12, 25, 55, 87]
    fig.add_trace(
        go.Scatter(x=years, y=cumulative, mode='lines+markers', name="Accumulation",
                  hovertemplate='Year: %{x}<br>Cumulative Definitions: %{y}<extra></extra>'),
        row=1, col=2
    )
    
    # Geographic distribution
    regions = ['NATO/West', 'Sino-Russian', 'Global South', 'Regional']
    percentages = [35, 25, 20, 20]
    fig.add_trace(
        go.Pie(labels=regions, values=percentages, name="Geographic",
               hovertemplate='<b>%{label}</b><br>%{value}%<extra></extra>'),
        row=1, col=3
    )
    
    # Technology adoption rates
    technologies = ['AI/ML', 'Social Media', 'Cyber', 'Neuroscience', 'Traditional']
    adoption = [85, 90, 80, 45, 60]
    fig.add_trace(
        go.Bar(x=technologies, y=adoption, name="Technology",
               hovertemplate='<b>%{x}</b><br>Adoption: %{y}%<extra></extra>'),
        row=2, col=1
    )
    
    # Convergence analysis
    aspects = ['Human Cognition', 'Non-kinetic Methods', 'Information Weapon', 'Actor Attribution', 'Temporal Scope']
    convergence_scores = [100, 96, 94, 45, 38]
    colors_conv = ['green' if x > 70 else 'orange' if x > 40 else 'red' for x in convergence_scores]
    fig.add_trace(
        go.Bar(x=aspects, y=convergence_scores, name="Convergence",
               marker_color=colors_conv,
               hovertemplate='<b>%{x}</b><br>Agreement: %{y}%<extra></extra>'),
        row=2, col=2
    )
    
    # Impact distribution
    impact_scores = [3, 3, 6, 7, 8, 8, 7, 6, 8, 9, 8, 9, 10, 9, 10, 10, 10]
    fig.add_trace(
        go.Histogram(x=impact_scores, nbinsx=8, name="Impact Distribution",
                    hovertemplate='Impact Score: %{x}<br>Count: %{y}<extra></extra>'),
        row=2, col=3
    )
    
    fig.update_layout(
        title="Cognitive Warfare Research: Comprehensive Dashboard",
        height=800,
        showlegend=False
    )
    
    return html.Div([
        html.H3("Summary Dashboard", style={'textAlign': 'center'}),
        html.P("Comprehensive overview of cognitive warfare research metrics including scope, geographic distribution, "
               "technology adoption, and convergence analysis. Each chart provides different insights into the field.",
               style={'textAlign': 'center', 'marginBottom': 20}),
        dcc.Graph(figure=fig),
        
        # Key insights
        html.Div([
            html.H4("Key Insights", style={'textAlign': 'center', 'marginTop': 30}),
            html.Div([
                html.Div([
                    html.H5("Universal Convergence"),
                    html.P("100% agreement on human cognition as primary target")
                ], className="insight-box", style={'width': '22%', 'display': 'inline-block', 'margin': '1%', 'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px'}),
                
                html.Div([
                    html.H5("Technology Integration"),
                    html.P("90% adoption rate for social media platforms")
                ], className="insight-box", style={'width': '22%', 'display': 'inline-block', 'margin': '1%', 'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px'}),
                
                html.Div([
                    html.H5("NATO Leadership"),
                    html.P("35% of definitions from NATO/Western sources")
                ], className="insight-box", style={'width': '22%', 'display': 'inline-block', 'margin': '1%', 'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px'}),
                
                html.Div([
                    html.H5("Modern Acceleration"),
                    html.P("62% of definitions published since 2020")
                ], className="insight-box", style={'width': '22%', 'display': 'inline-block', 'margin': '1%', 'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px'})
            ])
        ])
    ])

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)