from pathlib import Path
import pandas as pd
import numpy as np

# 1. Resolver diretórios base
CURRENT_FILE_PATH = Path(__file__).resolve()
CODE_ROOT = CURRENT_FILE_PATH.parent
PROJECT_HOME = CODE_ROOT.parent

# Definir paths de entrada e saída
base_input_dir = Path("../data/raw_data/extracted_data_keanu")
output_dir = Path("../data/formatted_extracted_data_keanu")
output_dir.mkdir(parents=True, exist_ok=True)

# 2. Localizar as pastas "30min" em ordem alfabética
target_folders = sorted(base_input_dir.glob("n*/30min"))

all_dataframes = []

# 3. Iterar por cada pasta "30min"
for folder_path in target_folders:
    # folder_path.parent.name extrai o nome do diretório acima (ex: "n640901")
    folder_name = folder_path.parent.name 
    
    file_dfs = []
    # Ler 30min0.txt, 30min1.txt e 30min2.txt
    for i in range(3):
        file_name = f"30min{i}.txt"
        file_path = folder_path / file_name
        
        if file_path.exists():
            # O ficheiro tem os dados separados por vírgula (ex: "63.5, 232")
            df = pd.read_csv(
                file_path, 
                header=None, 
                names=[f"Dist_mm_{i}", f"Column_Px_{i}"],
                skipinitialspace=True # Remove eventuais espaços após a vírgula
            )
        else:
            # Cria um DataFrame vazio; o pandas preencherá com NaN ao concatenar
            df = pd.DataFrame(columns=[f"Dist_mm_{i}", f"Column_Px_{i}"])
            
        file_dfs.append(df)
        
    # 4. Concatenar os 3 ficheiros da mesma pasta lado a lado (axis=1)
    combined_folder_df = pd.concat(file_dfs, axis=1)
    
    # Inserir o ID da pasta na primeira coluna para rastreabilidade
    combined_folder_df.insert(0, "folder_id", folder_name)
    
    all_dataframes.append(combined_folder_df)

# 5. Concatenar todas as pastas verticalmente num único ficheiro principal
final_df = pd.concat(all_dataframes, ignore_index=True)

# 6. Guardar resultados em CSV
output_filename = "keanu_30min_H_1964.csv"
output_path = output_dir / output_filename

final_df.to_csv(output_path, index=False, na_rep = np.nan)
