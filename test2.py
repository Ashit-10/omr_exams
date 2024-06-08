text = """Exam: #class-10_english_2
Roll: 8
Total mark: 40
Correct: 38
wrong: 2
Not selected: 0


File already available !
Old file: class-10/class-10_english_2/eval_files/8_38.jpg
New file: class-10/class-10_english_2/eval_files/8_382.jpg
Still save it ?
"""

text_list = text.split(" ")
text_list.reverse()
for file_name in text_list:
    if ".jpg" in file_name:
        file1 = (file_name.split(".jpg")[0]).strip()
        final_name = file1 + ".jpg"
        print(final_name)
        break
# print(text_list)