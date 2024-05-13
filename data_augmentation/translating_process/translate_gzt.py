from tqdm import tqdm
from test_openai import GPTtranslate

def translate_gzt(path_to_input, path_to_output, from_lang, to_lang):
    with open(path_to_input, "r", encoding="utf-8") as reader, open(path_to_output, "w", encoding="utf-8") as writer:
        total_lines = sum(1 for _ in reader)
        reader.seek(0)
        for line in tqdm(reader, desc=f"Translating from {from_lang} to {to_lang}", total=total_lines):
            line = line.strip()
            translation = GPTtranslate(line, from_lang, to_lang)
            writer.write(translation + "\n")

if __name__ == "__main__":
    translate_gzt("datasets/rdrs/Disease.txt", "translating_process/output/translated_rdrs/SYMPTOM_AND_DISEASE", "ru", "vi")