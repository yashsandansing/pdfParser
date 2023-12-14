'''
Util 1 - PDFPlumber
Returns 2 outputs
1. words + their coordinates
2. coordinates of paragraphs of text
'''


import pdfplumber


def return_data(input_pdf, page_number=0):

    pdf = pdfplumber.open(f"{input_pdf}", laparams = {})

    current_page = pdf.pages[page_number]
    
    elements = list()
    for ind, box in enumerate(current_page.objects["textboxhorizontal"]):
        tempDict = {"Text":"", "bounds":list(), "Type":"Paragraph", "Kids":{}}

        bounds = [box['x0'], box['top'], box['x1'], box['bottom'], box['width'], box['height']]

        tempDict["Text"] = box["text"]
        tempDict["bounds"] = bounds
        
        elements.append(tempDict)
    
    word_w_bbox = current_page.dedupe_chars().extract_words()
    for word in word_w_bbox:
        x_mid, y_mid = (word["x0"] + word["x1"])/2, (word["top"] + word["bottom"])/2
        word["midpoint"] = (x_mid, y_mid)

    return elements, word_w_bbox


# coords, dedupe_words = return_data(r"C:\Users\Yash\Documents\GitHub\InquireAI\textbooks\IX\inputPDF\english_beehive\iebe102.pdf", 0)
# print(dedupe_words)
# print(coords)