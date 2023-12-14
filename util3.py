# preprocess data to pass to VGT
# includes 2 functions 
# 1. convert the pages of a pdf to images in order to pass them to VGT
# 2. creates a pkl file using the BERT tokenizer and additional supplemental functions
from pdf2image import convert_from_path
import tempfile
import os
import shutil
from util1 import return_data
from util2 import rearrange_words
from transformers import BertTokenizer
import pickle
import numpy as np
import unicodedata

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
#private unicode characters to remove from string
pua_ranges = ( (0xE000, 0xF8FF), (0xF0000, 0xFFFFD), (0x100000, 0x10FFFD) )


def get_split_info(words_list, subwords_list):
    '''
    For a given word, get the number of subwords that BERT has broken it into
    '''
    result = []

    word_index = 0
    subword_index = 0

    while word_index < len(words_list) and subword_index < len(subwords_list):
        word = words_list[word_index]
        subword = subwords_list[subword_index].replace("##", "")

        count = 0
        # if subword=="[UNK]":
        #   print(word, subword)

        # in case BERT is unable to split a token any further, it tokenizes it as [UNK]
        # in that case, continue further with the loop
        # print(word)
        while word.lower() != subword and subword!="[UNK]":
            count += 1
            subword += subwords_list[subword_index + count].replace("##", "")
            # print(word, subword)

        result.append((word, count + 1))

        word_index += 1
        subword_index += count + 1

    return result


def adjust_bounding_boxes(bounding_boxes, split_info):
    '''
    Splits the bounding boxes equally amongst all subwords tokenized by BERT
    '''
    adjusted_boxes = []

    for box, (word, split_count) in zip(bounding_boxes, split_info):
        if split_count > 1:
            # Adjust the width and x-coordinate for the second part
            new_width = box[2] / split_count
            adjusted_boxes.append((box[0], box[1], new_width, box[3]))

            # Update x-coordinate for the second part
            x_offset = new_width
            for _ in range(split_count - 1):
                adjusted_boxes.append((box[0] + x_offset, box[1], new_width, box[3]))
                x_offset += new_width
        else:
            adjusted_boxes.append((box[0], box[1], box[2], box[3]))

    return adjusted_boxes

def is_pua_codepoint(c):
    '''
    Remove any characters that generate the [?] symbol due to being private
    '''
    return any(a <= c <= b for (a,b) in pua_ranges)

def create_dict(page_data):
    '''
    Fill the dictionary with the necessary information for the pkl file
    '''
    grid = {"input_ids":[], "bbox_subword_list":[], "texts":[], "bbox_texts_list":[]}
    texts = list()
    bbox = list()
    for ele in page_data:
        texts.append(ele["text"])
        bbox.append((ele["x0"], ele["top"], ele["x1"]-ele["x0"], ele["bottom"]-ele["top"]))
    
    assert len(texts) == len(bbox)

    for item in zip(texts, bbox):
        if any(is_pua_codepoint(ord(i)) for i in item[0]):
            pass
        else:
            grid["texts"].append(item[0])
            grid["bbox_texts_list"].append(item[1])
            
    words = grid["texts"]
    
    encoding = tokenizer.encode(" ".join(words))[1:-1]#Remove the CLS and SEP tokens
    grid["input_ids"]=np.array(encoding)
    
    subwords = tokenizer.convert_ids_to_tokens(encoding)
    # print(words)
    # print(subwords)
    split_info = get_split_info(words, subwords)

    grid["bbox_subword_list"] = adjust_bounding_boxes(grid["bbox_texts_list"], split_info)

    grid["bbox_texts_list"] = np.array(grid["bbox_texts_list"])
    grid["bbox_subword_list"] = np.array(grid["bbox_subword_list"])

    assert len(grid["bbox_subword_list"])==len(grid["input_ids"])
    return grid

def save_pkl_file(grid, pdf_path, output_dir, page_number):
    base_name, _ = os.path.splitext(os.path.basename(pdf_path))
    out_location = os.path.join(output_dir,f'{base_name}_page{page_number}.pdf.pkl')
    with open(out_location, 'wb') as handle:
        pickle.dump(grid, handle)

    return os.path.exists(out_location)

pdf_path = r"C:\Users\Yash\Documents\GitHub\InquireAI\textbooks\IX\inputPDF\english_beehive\iebe102.pdf"
page = 0
_, dedupe_words = return_data(pdf_path, page)
grid = create_dict(dedupe_words)
print(grid)

# base = r"C:\Users\Yash\Documents\GitHub\InquireAI\textbooks\IX\inputPDF"
# pages = 0
# for subject in os.listdir(base):
#     for chapter in os.listdir(os.path.join(base, subject)):
#         if ".pdf" in chapter:
#             pdf_path = os.path.join(base, subject, chapter)
#             if os.path.exists("pdf_retrieval/temp"):
#                 shutil.rmtree("pdf_retrieval/temp")
#             os.makedirs("pdf_retrieval/temp/images")
#             os.makedirs("pdf_retrieval/temp/grid")

#             outdir = convert_to_png(pdf_path, output_dir="pdf_retrieval/temp")
#             total_pages = len(os.listdir(os.path.join(outdir, "images")))

#             for page in range(total_pages):
#                 try:
#                     _, dedupe_words = return_data(pdf_path, page)
#                     grid = create_dict(dedupe_words)
#                     out = save_pkl_file(grid, pdf_path, os.path.join(outdir, "grid"), page)
#                 except Exception as e:
#                     pages+=1
#                     print(f"Couldn't process page number: {page} from {subject}, {chapter} due to some issues")
# print(f"Total pages unprocessed: {pages}")
# if "tmp" in outdir:
#     print(os.listdir(outdir+"/images"))
#     print(os.listdir(outdir+"/grid"))
# shutil.rmtree(outdir)
#     assert not os.path.exists(outdir)
