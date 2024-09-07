import streamlit as st
import pandas as pd
import random
from streamlit_autorefresh import st_autorefresh

# Function to load a CSV file
def load_csv(default_file_path):
    return pd.read_csv(default_file_path)

# Load the CSV files for conversation, advanced vocabulary, and confusing vocabulary
default_conversation_file = 'dialoguebook.csv'
default_advanced_vocab_file = 'advanced_vocabulary.csv'
default_confusing_vocab_file = 'confusing_vocabulary.csv'

# Loading the CSV files
conversation_df = load_csv(default_conversation_file)
advanced_vocab_df = load_csv(default_advanced_vocab_file)
confusing_vocab_df = load_csv(default_confusing_vocab_file)  # Predefined confusing words

# Set the refresh interval in milliseconds
REFRESH_INTERVAL = 5000

# List of emojis related to learning, exercise, and food
emojis = ['📚', '✏️', '📖', '📝', '🧠', '💡', '🎓', '📅', '🏫', '🖋️', '🏋️', '🚴', '🥗', '🍎', '🍕', '🍔', '🍣', '🥑', '🥦', '🏃']

# Function to get random phrases and emojis
def get_random_phrases_and_emojis(data, num=1):
    phrases = data.sample(n=num)
    phrases['emoji'] = [random.choice(emojis) for _ in range(num)]
    return phrases

# Function for initializing session state specific to a tab
def initialize_session_state(tab_key):
    if f'random_phrases_{tab_key}' not in st.session_state:
        st.session_state[f'random_phrases_{tab_key}'] = pd.DataFrame()
        st.session_state[f'phrases_history_{tab_key}'] = pd.DataFrame()
        st.session_state[f'review_mode_{tab_key}'] = False
        st.session_state[f'review_cycle_{tab_key}'] = 0
        st.session_state[f'review_index_{tab_key}'] = 0
        st.session_state[f'study_history_{tab_key}'] = []

# Updated function to handle study cycles based on showing 10 phrases specific to each tab
def study_cycle(df, tab_key, auto_refresh_key, refresh_interval=REFRESH_INTERVAL):
    if st_autorefresh(interval=refresh_interval, limit=None, key=auto_refresh_key):
        # Check if we have shown 10 words, then switch to review mode
        if len(st.session_state[f'study_history_{tab_key}']) == 10 and not st.session_state[f'review_mode_{tab_key}']:
            st.session_state[f'phrases_history_{tab_key}'] = pd.DataFrame(st.session_state[f'study_history_{tab_key}'])  # Save last 10 words
            st.session_state[f'study_history_{tab_key}'] = []  # Clear history for the next set
            st.session_state[f'review_mode_{tab_key}'] = True
            st.session_state[f'review_cycle_{tab_key}'] = 1
            st.session_state[f'review_index_{tab_key}'] = 0
            st.write("<h2 style='text-align: center; color: red;'>복습 시작</h2>", unsafe_allow_html=True)

        # Update random phrases if in study mode
        if not st.session_state[f'review_mode_{tab_key}']:
            new_phrase = get_random_phrases_and_emojis(df)
            st.session_state[f'random_phrases_{tab_key}'] = new_phrase
            st.session_state[f'study_history_{tab_key}'].append(new_phrase.iloc[0])
        else:
            # Handle review mode
            handle_review_mode(tab_key)

# Function to handle the review process, specific to each tab
def handle_review_mode(tab_key):
    if st.session_state[f'review_cycle_{tab_key}'] == 1:
        if st.session_state[f'review_index_{tab_key}'] < len(st.session_state[f'phrases_history_{tab_key}']):
            st.session_state[f'random_phrases_{tab_key}'] = st.session_state[f'phrases_history_{tab_key}'].iloc[[st.session_state[f'review_index_{tab_key}']]]
            st.session_state[f'review_index_{tab_key}'] += 1
        else:
            st.session_state[f'review_cycle_{tab_key}'] = 2
            st.session_state[f'review_index_{tab_key}'] = 0
            st.write("<h2 style='text-align: center; color: orange;'>복습 시작 (역순)</h2>", unsafe_allow_html=True)
    elif st.session_state[f'review_cycle_{tab_key}'] == 2:
        if st.session_state[f'review_index_{tab_key}'] < len(st.session_state[f'phrases_history_{tab_key}']):
            st.session_state[f'random_phrases_{tab_key}'] = st.session_state[f'phrases_history_{tab_key}'].iloc[[-(st.session_state[f'review_index_{tab_key}'] + 1)]]
            st.session_state[f'review_index_{tab_key}'] += 1
        else:
            st.session_state[f'review_cycle_{tab_key}'] = 3
            st.session_state[f'review_index_{tab_key}'] = 0
            st.write("<h2 style='text-align: center; color: green;'>복습 시작 (뜻 없이)</h2>", unsafe_allow_html=True)
    elif st.session_state[f'review_cycle_{tab_key}'] == 3:
        if st.session_state[f'review_index_{tab_key}'] < len(st.session_state[f'phrases_history_{tab_key}']):
            st.session_state[f'random_phrases_{tab_key}'] = st.session_state[f'phrases_history_{tab_key}'].iloc[[st.session_state[f'review_index_{tab_key}']]]
            st.session_state[f'review_index_{tab_key}'] += 1
        else:
            # After reviewing all phrases, display "다시 시작" and move to next set of random phrases
            st.write("<h2 style='text-align: center; color: blue;'>다음 단어 세트</h2>", unsafe_allow_html=True)
            st.session_state[f'random_phrases_{tab_key}'] = get_random_phrases_and_emojis(conversation_df)
            st.session_state[f'review_mode_{tab_key}'] = False
            st.session_state[f'review_cycle_{tab_key}'] = 0
            st.session_state[f'review_index_{tab_key}'] = 0
            st.session_state[f'study_history_{tab_key}'] = []

# Function to display the phrases specific to each tab
def display_phrases(tab_key, word_font_size=30, meaning_font_size=20):
    random_phrases = st.session_state[f'random_phrases_{tab_key}']
    for index, row in random_phrases.iterrows():
        st.write(f"<h1 style='text-align: left; font-size: {word_font_size}px;'>{row['emoji']} {row['단어']}</h1>", unsafe_allow_html=True)
        st.write(f"<p style='text-align: center; font-size: {meaning_font_size}px;'>{row['주요뜻']}</p>", unsafe_allow_html=True)

# Main app layout
st.title('영어 학습 앱')

tabs = st.tabs(["영어 회화 연습", "고급 단어 학습", "헷갈리는 단어"])

# Tab for English Conversation Practice (refresh every 5 seconds)
with tabs[0]:
    tab_key = "conversation"
    initialize_session_state(tab_key)
    study_cycle(conversation_df, tab_key, auto_refresh_key="autorefresh_conv", refresh_interval=REFRESH_INTERVAL)
    display_phrases(tab_key)

    # Button for next set of phrases
    if st.button('다음 구절 보기', key=f'next_{tab_key}'):
        st.session_state[f'random_phrases_{tab_key}'] = get_random_phrases_and_emojis(conversation_df)
        st.session_state[f'review_mode_{tab_key}'] = False  # Exit review mode
        st.session_state[f'review_cycle_{tab_key}'] = 0  # Reset review cycle
        st.session_state[f'review_index_{tab_key}'] = 0  # Reset review index
        st.session_state[f'study_history_{tab_key}'] = []  # Clear study history

# Tab for Advanced Vocabulary (uses the same refresh interval)
with tabs[1]:
    tab_key = "advanced"
    initialize_session_state(tab_key)
    study_cycle(advanced_vocab_df, tab_key, auto_refresh_key="autorefresh_vocab", refresh_interval=REFRESH_INTERVAL)
    display_phrases(tab_key)

    if st.button('다른 단어 보기', key=f'next_{tab_key}'):
        st.session_state[f'random_phrases_{tab_key}'] = get_random_phrases_and_emojis(advanced_vocab_df)
        st.session_state[f'review_mode_{tab_key}'] = False
        st.session_state[f'review_cycle_{tab_key}'] = 0
        st.session_state[f'review_index_{tab_key}'] = 0
        st.session_state[f'study_history_{tab_key}'] = []

# Tab for Confusing Words (same random behavior as other tabs)
with tabs[2]:
    tab_key = "confusing"
    initialize_session_state(tab_key)
    study_cycle(confusing_vocab_df, tab_key, auto_refresh_key="autorefresh_confusing", refresh_interval=REFRESH_INTERVAL)
    display_phrases(tab_key)

    if st.button('다른 단어 보기', key=f'next_{tab_key}'):
        st.session_state[f'random_phrases_{tab_key}'] = get_random_phrases_and_emojis(confusing_vocab_df)
        st.session_state[f'review_mode_{tab_key}'] = False
        st.session_state[f'review_cycle_{tab_key}'] = 0
        st.session_state[f'review_index_{tab_key}'] = 0
        st.session_state[f'study_history_{tab_key}'] = []
