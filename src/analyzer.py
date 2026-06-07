from src.classifier import classify_response


def analyze_responses(df):

    responses = []

    for value in df["W trakcie leczenia"]:

        response = classify_response(value)

        responses.append(response)

    df["response_class"] = responses

    return df