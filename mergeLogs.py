import json
import os
import glob

def merge_txt_files(input_folder='./Logs', output_file='merged_output.txt'):
    # Polja koja želimo da zadržimo
    wanted_fields = [
        'BROKER_TYPE',
        'opcije',
        'READY_COUNT',
        'MAX_AVAILABLE_RESOURCES',
        'CRITICAL_UTILISATION_PERCENT',
        'RESOURCE_ADD_NUMBER',
        'avg_utilization',
        'avg_wait',
        'USAGE_TIME',
        'SLA1_broke',
        'SLA2_broke',
        'SLA3_broke',
        'SLA4_broke'
    ]

    merged_data = []

    # Pronađi sve .txt fajlove u folderu
    txt_files = glob.glob(os.path.join(input_folder, '*.txt'))

    print(f"Pronađeno {len(txt_files)} .txt fajlova za obradu...")

    for file_path in txt_files:
        print(f"\nObrađujem: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            print(f"  Veličina fajla: {len(content)} karaktera")

            # PRVO: Očisti razmake iz ključeva (npr. "SLA4_broke " -> "SLA4_broke")
            import re
            content = re.sub(r'"(\w+)\s+"', r'"\1"', content)

            # DRUGO: Ukloni trailing zapete pre zatvorenih zagrada (,} -> })
            content = re.sub(r',(\s*})', r'\1', content)

            # Razdvoji objekte - traži pattern },\n{
            # Ali prvo wrap u array format
            content = content.strip()

            # Ako već nije array, napravi ga
            if not content.startswith('['):
                # Zameni },\n\n{ sa },\n{
                content = content.replace('},\n\n{', '},\n{')
                # Dodaj zagrade
                content = '[' + content
                # Ukloni trailing zarez ako postoji
                if content.endswith(','):
                    content = content[:-1]
                content = content + ']'

            # Sada parsiraj
            try:
                objects = json.loads(content)
                if not isinstance(objects, list):
                    objects = [objects]
                print(f"  ✓ Uspešno parsirano {len(objects)} objekata")
            except json.JSONDecodeError as e:
                print(f"  ✗ JSON Greška na poziciji {e.pos}: {e.msg}")
                print(f"  Problem oko: ...{content[max(0, e.pos - 50):e.pos + 50]}...")

                # Pokušaj alternativni pristup - citaj liniju po liniju i akumuliraj
                objects = []
                current_obj = ""
                brace_count = 0

                for line in content.split('\n'):
                    current_obj += line + '\n'
                    brace_count += line.count('{') - line.count('}')

                    if brace_count == 0 and current_obj.strip():
                        # Završen jedan objekat
                        obj_str = current_obj.strip().rstrip(',').strip('[]').strip()
                        if obj_str:
                            try:
                                obj = json.loads(obj_str)
                                objects.append(obj)
                                print(f"  ✓ Parsiran objekat liniju po liniju")
                            except:
                                pass
                        current_obj = ""

                print(f"  Alternativni metod: {len(objects)} objekata")

            # Filtriraj polja za svaki objekat
            for idx, obj in enumerate(objects):
                filtered_obj = {}

                for field in wanted_fields:
                    if field in obj:
                        value = obj[field]

                        # Konvertuj USAGE_TIME u string reprezentaciju liste ako je lista
                        if field == 'USAGE_TIME' and isinstance(value, list):
                            filtered_obj[field] = str(value)
                        # Konvertuj opcije u string ako je lista
                        elif field == 'opcije' and isinstance(value, list):
                            filtered_obj[field] = str(value)
                        else:
                            filtered_obj[field] = value

                # Dodaj samo ako ima podataka
                if filtered_obj:
                    merged_data.append(filtered_obj)
                    print(f"  → Objekat {idx + 1}: {list(filtered_obj.keys())}")

        except Exception as e:
            print(f"GREŠKA pri obradi fajla {file_path}: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Sačuvaj spojene podatke
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 50}")
    print(f"Gotovo! Spojeno {len(merged_data)} objekata u {output_file}")
    print(f"{'=' * 50}")

    if merged_data:
        print(f"\nPrimer prvog objekta:")
        print(json.dumps(merged_data[0], indent=2, ensure_ascii=False))

# Pokreni spajanje
merge_txt_files(input_folder='.', output_file='merged_output.txt')