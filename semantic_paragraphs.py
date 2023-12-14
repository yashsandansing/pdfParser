from util1 import return_data
from util2 import rearrange_words
from statistics import mode

def line2para(page, height_threshold=0.5):
    n = len(page)
    ind = 0
    new_page = list()
    word_height = get_most_frequent_font_height(page)
    while ind < n:
        current_block_lines = findTotalLines(page[ind]["Kids"]) # Initialize lines to 1 for the current block
        merged_text = page[ind]["Text"]
        merged_x0, merged_top, merged_x1, merged_bottom, merged_width, merged_height = page[ind]["bounds"]
        ismerged=False
        tempDict = {"Text":"", "bounds":list(), "Type":"Paragraph", "Kids":{}, "isMerged":False}
        while ind + 1 < n:
            next_block = page[ind + 1]

            height = int(next_block["bounds"][3] - next_block["bounds"][1])
            top = int(next_block["bounds"][1])

            lines = findTotalLines(next_block["Kids"])

            if not(lines== 1 or current_block_lines==1):
                break  # Exit the merging loop if lines > 1
            
            last_word_current_block = page[ind]["Text"].strip()
            first_word_next_block = next_block["Kids"]["0"]["text"].strip()
            word_height_current_block = [page[ind]]
            word_height_next_block = [next_block]
            if 0 < top - merged_bottom <= word_height*height_threshold:
                # print(page[ind]["Text"],"~~",next_block["Text"])
            # if 0 < top - merged_bottom <= min(height, int(page[ind]["bounds"][3] - page[ind]["bounds"][1]))/height_threshold:
                ismerged = True
                # Merge the text and update bounding box coordinates
                merged_text += " " + next_block["Text"]
                merged_x0 = min(merged_x0, next_block["bounds"][0])
                merged_x1 = max(merged_x1, next_block["bounds"][2])
                merged_top = min(merged_top, next_block["bounds"][1])
                merged_bottom = max(merged_bottom, next_block["bounds"][3])
                merged_height = merged_bottom - merged_top
                merged_width = merged_x1 - merged_x0
                ind += 1  # Move to the next block
            
            elif not (last_word_current_block.endswith(".") and first_word_next_block[0].isupper()) and 0<top-merged_bottom<=word_height:# and (word_height_current_block == word_height_next_block):
                ismerged = True
                # Merge the text and update bounding box coordinates
                merged_text += " " + next_block["Text"]
                merged_x0 = min(merged_x0, next_block["bounds"][0])
                merged_x1 = max(merged_x1, next_block["bounds"][2])
                merged_top = min(merged_top, next_block["bounds"][1])
                merged_bottom = max(merged_bottom, next_block["bounds"][3])
                merged_height = merged_bottom - merged_top
                merged_width = merged_x1 - merged_x0
                ind += 1  # Move to the next block
                
            else:
                break  # Exit the merging loop if conditions are not met
        if merged_text:

            tempDict["Text"] = merged_text
            tempDict["bounds"] = [merged_x0, merged_top, merged_x1, merged_bottom, merged_width, merged_height]
            tempDict["isMerged"] = ismerged
            new_page.append(tempDict)
        ind += 1  # Move to the next block to start a new iteration
    
    return new_page

def findTotalLines(kids, line_threshold=5):
    mid = set()
    for j in kids:
        mid.add(int(kids[j]["midpoint"][1]))
    lines = len(mid)
    if lines>1:
        least = min(mid)
        largest = max(mid)
        if largest - least<line_threshold:
            return 1
    return lines

def word2line(page, y_threshold=5, x_threshold=5, line_threshold=5):
    n = len(page)
    ind = 0
    new_page = list()
    while ind < n:
        current_block = page[ind]
        current_block_lines = findTotalLines(current_block["Kids"], line_threshold)
        current_block_y_midpoint = (current_block["bounds"][3] + current_block["bounds"][1]) // 2
        ind2 = ind + 1
        tempDict = {"Text":"", "bounds":list(), "Type":"Paragraph", "Kids":{}}
        # Initialize a list to store blocks for merging
        blocks_to_merge = [current_block]
        kids = dict()
        while ind2 < n:
            next_block = page[ind2]
            next_block_lines = findTotalLines(next_block["Kids"], line_threshold)

            if next_block_lines and current_block_lines:
                next_block_y_midpoint = (next_block["bounds"][3] + next_block["bounds"][1]) // 2
                distance_bw_blocks_y = abs(next_block_y_midpoint - current_block_y_midpoint)
                distance_bw_blocks_x = next_block["bounds"][0] - current_block["bounds"][2]

                if distance_bw_blocks_y < y_threshold and 0 < distance_bw_blocks_x < x_threshold:
                    
                    # Add the next block to the list for merging
                    blocks_to_merge.append(next_block)
                    current_block = next_block
                    current_block_y_midpoint = (current_block["bounds"][3] + current_block["bounds"][1]) // 2
                    current_block_lines = next_block_lines
                else:
                    break

            ind2 += 1

        if len(blocks_to_merge)>1:
            top = min([ele["bounds"][1] for ele in blocks_to_merge])
            bottom = max([ele["bounds"][3] for ele in blocks_to_merge])

            x0 = min([ele["bounds"][0] for ele in blocks_to_merge])
            x1 = max([ele["bounds"][2] for ele in blocks_to_merge])
            
            width = x1-x0
            height = bottom- top

            text = " ".join([block["Text"] for block in blocks_to_merge])
            bounds = [x0, top, x1, bottom, width, height]
        else:
            block = blocks_to_merge[0]
            bounds = block["bounds"]
            text = block["Text"]
            kids = block["Kids"]
        tempDict["Text"] = text
        tempDict["bounds"] = bounds
        tempDict["Kids"] = kids
        new_page.append(tempDict)
        ind=ind2
    
    return new_page

def get_most_frequent_font_height(page):
    word_height = list()
    for block in page:
        for kid in block["Kids"]:
            ele = block["Kids"][kid]
            word_height.append(ele["bottom"]- ele["top"])
    return mode(word_height)

coords, dedupe_words = return_data(r"C:\Users\Yash\Documents\GitHub\InquireAI\textbooks\IX\inputPDF\english_beehive\iebe102.pdf", 0)
page = rearrange_words(coords, dedupe_words)
word_height = get_most_frequent_font_height(page)
# page = rearrange_words(coords, dedupe_words)
# out = word2line(page, 6, 4)
# out2 = rearrange_words(out, dedupe_words)
# finalOut = line2para(out)
# for i in finalOut:
#     print(i["Text"])
#     print(i["bounds"])
#     print("\n")
