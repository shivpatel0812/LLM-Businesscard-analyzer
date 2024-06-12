def concatenate_fields(data):
    # Flatten the JSON data to concatenate all string values
    text_parts = []

    def extract_text(json_data):
        for key, value in json_data.items():
            if isinstance(value, dict):
                extract_text(value)
            else:
                text_parts.append(str(value))

    extract_text(data)
    return ". ".join(filter(None, text_parts))

concatenated_text = concatenate_fields(json_data)
print(concatenated_text)


import boto3

comprehend = boto3.client('comprehend')

def analyze_text_with_comprehend(text):
    sentiment = comprehend.detect_sentiment(Text=text, LanguageCode='en')
    entities = comprehend.detect_entities(Text=text, LanguageCode='en')
    key_phrases = comprehend.detect_key_phrases(Text=text, LanguageCode='en')
    return sentiment, entities, key_phrases


analysis_results = analyze_text_with_comprehend(concatenated_text)
print(analysis_results)


def analyze_business_card(json_data):
    # Concatenate fields into a single text string
    text = concatenate_fields(json_data)
    
    # Analyze the text with AWS Comprehend
    sentiment, entities, key_phrases = analyze_text_with_comprehend(text)
    
    # Combine the results into a single report
    report = {
        "Extracted Data": json_data,
        "Sentiment Analysis": sentiment,
        "Entities": entities,
        "Key Phrases": key_phrases
    }
    
    return report

# Example usage
json_data = {
    "organization": "Johns Hopkins University Applied Physics Laboratory",
    "name": "Jack M. Sheppard",
    "title": "Systems Engineer",
    "department": "Air & Missile Defense Department",
    "address": "11100 Johns Hopkins Road, Laurel MD 20723-6099",
    "office_phone": "240-228-5450",
    "fax": "240-228-5967",
    "cell_phone": "301-395-2894",
    "email": "jack.sheppard@jhuapl.edu"
}

report = analyze_business_card(json_data)
print(report)
