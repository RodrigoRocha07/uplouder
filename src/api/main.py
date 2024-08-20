from fastapi import FastAPI, Depends, Request, HTTPException, Depends,File, UploadFile, Form,File, UploadFile
from src.infra.sqlalchemy.config.database import get_db
from src.infra.sqlalchemy.repositorios.repositorio import *
from fastapi.middleware.cors import CORSMiddleware
from src.providers import token_provider
from sqlalchemy.orm import Session
import pandas as pd
from io import StringIO
import asyncio
import time
import os

#uvicorn nome_do_app:app --port 8080


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,  # Permite envio de credenciais (cookies, headers de autorização, etc)
    allow_methods=["*"],  # Permite todos os métodos HTTP (GET, POST, PUT, DELETE, etc)
    allow_headers=["*"],  # Permite todos os headers
)
#

async def token_authentication_in_header(request: Request):
    header = request.headers
    if 'authorization' in header:
        token = header['authorization'].split(' ')[1]
        if token_provider.verificar_token(token):
            return 
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    raise HTTPException(status_code=401, detail="Credenciais não fornecidas")

UPLOAD_DIRECTORY = "./uploads"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

async def process_csv(name: str, user_id: int, path: str, db: Session):
    inicio = time.time()
    

    try:
        print(f"Iniciando processamento do arquivo {path}")
        await asyncio.sleep(1)  # Simula um processamento longo, mas não bloqueante

        with open(path, newline='', encoding='utf-8') as csvfile:
            # Ler o conteúdo do arquivo usando o csv.reader
            content = csvfile.read()  # Lê todo o conteúdo do arquivo
            decoded_content = content.decode("utf-8") if isinstance(content, bytes) else content
            lines = decoded_content.splitlines()

            # Verificações e processamento
            first_line = lines[0]
    
            if "," in first_line:
                data = pd.read_csv(StringIO(decoded_content))
            elif ";" in first_line:
                data = pd.read_csv(StringIO(decoded_content), delimiter=';')
            else:
                return {"error": "Formato de CSV não reconhecido"}

            data.fillna(" ", inplace=True)

            data_dict = data.to_dict(orient="records")


            for record in data_dict:
                for key, value in record.items():
                    record[key] = str(value)

            base = RepositorioBases(db).criar(name, first_line.lower().replace(',',';'),user_id)
            total_salvo = 0
            batch_size = 50000

            for i in range(0, len(data_dict), batch_size):
                batch = data_dict[i:i + batch_size]
                RepositorioInfos(db).criar_com_session_privada(base.id, batch)
                total_salvo += batch_size
                print(f"Total salvo:{total_salvo}")
   
    except FileNotFoundError:
        print('Erro: Arquivo não encontrado')
    except Exception as e:
        print(f"Erro durante o processamento: {e}")
    finally:
        # Remover o arquivo após o processamento
        try:
            os.remove(path)
            print(f"Arquivo {path} deletado com sucesso.")
        except Exception as e:
            print(f"Erro ao deletar o arquivo {path}: {e}")
    
    fim = time.time()
    RepositorioBases(db).carregar(base.id)
    RepositorioCampaign(db).atualizar_disparos(base.id)
    print(f"Tempo de execução de {fim - inicio} segundos")

@app.post("/upload_csv")
async def salvar_csv(
    name: str = Form(...),
    csv_file: UploadFile = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    csv_file_location = os.path.join(UPLOAD_DIRECTORY, csv_file.filename)
    with open(csv_file_location, "wb") as f:
        f.write(await csv_file.read())

    # Cria uma tarefa assíncrona para processar o CSV
    asyncio.create_task(process_csv(name, user_id, csv_file_location, db))

    return {"info": f"Arquivo '{csv_file.filename}' salvo em '{csv_file_location}'. Processamento em segundo plano iniciado."}

