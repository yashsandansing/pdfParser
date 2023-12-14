from util1 import return_data

def if_lies_in_box(midpoint, box):
    mid_x, mid_y = midpoint
    return mid_x>=box[0] and mid_y>=box[1] and mid_x<=box[2] and mid_y<=box[3]

def rearrange_words(parent_box, individual_words, individual=True):
    '''
    Insert the individual words in their respective reading order inside the boxes based on their midpoint co-ordinates
    '''
    for ele in parent_box:
        text = list()
        kids = list()
        for word in individual_words:
            if if_lies_in_box(word["midpoint"], ele["bounds"]):
                text.append(word["text"])
                kids.append(word)
        ele["Text"] = " ".join(text)
        if individual:
            for ind,kid in enumerate(kids):
                ele["Kids"].update({f"{ind}": kid})
    return parent_box
