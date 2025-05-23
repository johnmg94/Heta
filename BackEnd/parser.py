import re

def build_url(keywords_str):

    # Split the input string into individual keywords using commas or whitespace
    keywords = re.split(r'[,\s]+', keywords_str.strip())
    cleaned_keywords = []
    for keyword in keywords:
        # Remove special characters, keeping only alphanumeric characters
        cleaned = re.sub(r'[^A-Za-z0-9]', '', keyword)
        if cleaned:
            cleaned_keywords.append(cleaned)
    
    # Join the cleaned keywords with '+'
    joined_keywords = '+'.join(cleaned_keywords)
    
    # Append the API key to the URL
    keywords = str(joined_keywords) 
    return keywords
