# interface streamlit

import streamlit as st
import sys
import os
import tempfile
from datetime import datetime

# Configuration de la page DOIT ÊTRE LA PREMIÈRE COMMANDE STREAMLIT
st.set_page_config(
    page_title="Compilateur Mini-Pascal",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ajouter le chemin actuel pour importer les modules locaux
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lexer import lexer
from parser_1 import parser, source_text
from ast_1 import Program, Block, ConstDecl, VarDecl, Assign, If, While, For, Repeat, Compound, BinaryOp, UnaryOp, VarRef, Literal
from errors import LexicalError, SyntaxError_
from compiler import PascalCompiler


#Initialise l'état de la session Streamlit"""
def init_session_state():
    if 'compiler' not in st.session_state:
        st.session_state.compiler = PascalCompiler()
    if 'last_analysis' not in st.session_state:
        st.session_state.last_analysis = None
    if 'analysis_type' not in st.session_state:
        st.session_state.analysis_type = None


#Affiche un message d'erreur formaté"""
def display_error(message):
    st.error(f"❌ {message}")


#Affiche les résultats de l'analyse lexicale"""
def display_lexical_results(tokens):
    st.success("✅ Analyse lexicale terminée avec succès!")
    
    # Statistiques
    st.subheader("📊 Statistiques Lexicales")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Tokens", len(tokens))
    with col2:
        unique_types = len(set(token['type'] for token in tokens))
        st.metric("Types de Tokens", unique_types)
    with col3:
        identifiers = len([t for t in tokens if t['type'] == 'ID'])
        st.metric("Identifiants", identifiers)
    
    # Table des tokens
    st.subheader("🔍 Tokens Détectés")
    token_data = []
    for token in tokens:
        token_data.append({
            'Type': token['type'],
            'Valeur': str(token['value']),
            'Ligne': token['line'],
            'Colonne': token['column']
        })
    
    st.dataframe(token_data, use_container_width=True)
    
    # Vue détaillée
    with st.expander("📋 Détails des Tokens"):
        for i, token in enumerate(tokens, 1):
            st.write(f"**{i}. {token['type']}** - `{token['value']}` "
                    f"(ligne {token['line']}, colonne {token['column']})")


#Affiche les résultats de l'analyse syntaxique"""
def display_syntax_results(ast):
    st.success("✅ Analyse syntaxique terminée avec succès!")

    # Informations basiques sur l'AST
    st.subheader("📐 Structure Syntaxique")
    
    if isinstance(ast, Program):
        st.info(f"**Programme:** {ast.name}")
        st.info(f"**Déclarations de constantes:** {len(ast.block.consts)}")
        st.info(f"**Déclarations de variables:** {len(ast.block.vars)}")
        st.info(f"**Instructions:** {len(ast.block.statements)}")
    
    # Aperçu de l'AST
    with st.expander("🌳 Aperçu de l'AST (format texte)"):
        if hasattr(ast, 'to_tree_string'):
            st.text(ast.to_tree_string())


#Affiche l'AST sous forme arborescente"""
def display_ast_results(ast_tree):
    st.success("✅ AST construit avec succès!")
    
    st.subheader("🌳 Arbre Syntaxique Abstrait")
    
    # Affichage formaté de l'AST
    st.text_area("Représentation textuelle de l'AST", 
                ast_tree, 
                height=400,
                help="Représentation hiérarchique de la structure du programme")
    
    # Informations sur la structure
    lines = ast_tree.split('\n')
    node_count = len([line for line in lines if line.strip()])
    depth = max(len(line) - len(line.lstrip()) for line in lines if line.strip()) // 2
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Nœuds dans l'AST", node_count)
    with col2:
        st.metric("Profondeur maximale", depth)


def main():
    # CSS personnalisé
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .analysis-section {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialisation de l'état
    init_session_state()
    
    # En-tête
    st.markdown('<h1 class="main-header">🔍 Compilateur Mini-Pascal</h1>', 
                unsafe_allow_html=True)
    
    # Layout principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Éditeur de Code Pascal")
        
        # Exemples de code prédéfinis
        example_choice = st.selectbox(
            "Charger un exemple:",
            ["Sélectionner un exemple...", "Programme simple", "Boucles et conditions", "Calculs mathématiques"]
        )
        
        examples = {
            "Programme simple": """program example;
const MAX = 10;
var x, y : integer;
begin
    if x < MAX then
        x := x + 1
    else
        x := 0;
    y := 5 * 2;
end.""",

            "Boucles et conditions": """program loops;
var i, sum : integer;
begin
    sum := 0;
    for i := 1 to 10 do
        sum := sum + i;
        
    while sum > 0 do
    begin
        sum := sum - 1;
    end;
    
    repeat
        sum := sum + 2;
    until sum > 20;
end.""",

            "Calculs mathématiques": """program calculus;
const PI = 3.14159;
var radius, area, circumference : real;
begin
    radius := 5.0;
    area := PI * radius * radius;
    circumference := 2 * PI * radius;
    
    if area > 50 then
        radius := radius / 2
    else
        radius := radius * 2;
end."""
        }
        
        # Zone de texte pour le code
        if example_choice != "Sélectionner un exemple...":
            code = st.text_area("Code Pascal:", examples[example_choice], height=300)
        else:
            code = st.text_area("Code Pascal:", height=300, 
                               placeholder="Entrez votre code Pascal ici...\n\nExemple:\nprogram example;\nconst MAX = 10;\nvar x : integer;\nbegin\n  x := 5;\nend.")
    
    with col2:
        st.subheader("⚙️ Contrôles d'Analyse")
        
        # Boutons d'analyse
        st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
        
        if st.button("🔍 Analyse Lexicale", use_container_width=True):
            if code.strip():
                st.session_state.compiler.set_source(code)
                tokens, error = st.session_state.compiler.lexical_analysis()
                st.session_state.last_analysis = (tokens, error)
                st.session_state.analysis_type = "lexical"
                st.rerun()
            else:
                st.warning("Veuillez entrer du code Pascal à analyser.")
        
        if st.button("📐 Analyse Syntaxique", use_container_width=True):
            if code.strip():
                st.session_state.compiler.set_source(code)
                ast, error = st.session_state.compiler.syntactic_analysis()
                st.session_state.last_analysis = (ast, error)
                st.session_state.analysis_type = "syntax"
                st.rerun()
            else:
                st.warning("Veuillez entrer du code Pascal à analyser.")
        
        if st.button("🌳 Construire l'AST", use_container_width=True):
            if code.strip():
                st.session_state.compiler.set_source(code)
                ast_tree, error = st.session_state.compiler.build_ast()
                st.session_state.last_analysis = (ast_tree, error)
                st.session_state.analysis_type = "ast"
                st.rerun()
            else:
                st.warning("Veuillez entrer du code Pascal à analyser.")
        
        if st.button("🗑️ Effacer les Résultats", use_container_width=True):
            st.session_state.last_analysis = None
            st.session_state.analysis_type = None
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Informations sur le compilateur
        st.subheader("ℹ️ Informations")
        st.info("""
        **Fonctionnalités:**
        - Analyse lexicale (tokenisation)
        - Analyse syntaxique (parsing)
        - Construction d'AST
        - Gestion d'erreurs détaillée
        
        **Syntaxe supportée:**
        - Déclarations const/var
        - Structures de contrôle
        - Expressions arithmétiques
        - Affectations
        """)
    
    # Affichage des résultats
    st.markdown("---")
    st.subheader("📊 Résultats de l'Analyse")
    
    if st.session_state.last_analysis is not None:
        result, error = st.session_state.last_analysis
        
        if error:
            display_error(error)
        else:
            if st.session_state.analysis_type == "lexical":
                display_lexical_results(result)
            elif st.session_state.analysis_type == "syntax":
                display_syntax_results(result)
            elif st.session_state.analysis_type == "ast":
                display_ast_results(result)
    else:
        st.info("👋 Utilisez les boutons ci-dessus pour analyser votre code Pascal. Les résultats s'afficheront ici.")
    
    # Pied de page
    st.markdown("---")
    st.caption(f"Compilateur mini-Pascal - Interface Streamlit | Dernière mise à jour: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()