from fastapi import FastAPI, HTTPException
from typing import List
from datetime import datetime
from pydantic import BaseModel

app = FastAPI()

#foi criado uma lista para poder armazenar os clientes na fila a
fila_de_clientes = []

#definido um variavel para controlar o ID dos clientes
contador_id = 0

#foi definida uma classe "Cliente", que representa os clientes na tila
class Cliente:
    def __init__(self, cliente_id,nome_cliente, tipo_atendimento,atendido=False):
        self.cliente_id = cliente_id
        self.nome_cliente = nome_cliente
        self.tipo_atendimento = tipo_atendimento
        self.data_chegada = datetime.now()
        self.atendido = atendido
#foi definida uma classe "Cliente Response", que representa a resposta a ser retornada ao cliente
class ClienteResponse(BaseModel):
    cliente_id: int
    nome_cliente: str
    tipo_atendimento: str
    data_chegada: datetime
    posicao_na_fila:int
    atendido: bool
    
#(TÓPICO 01)
#foi criado um endpoint para listar os clientes na fila e definido uma rota/fila
@app.get("/fila", response_model=List[ClienteResponse])
async def listar_fila():
#se a fila estiver vazia vai retornar a resposta "não tem ninguém na fila!"
    if not fila_de_clientes:
        raise HTTPException(status_code=200, detail="Não tem ninguém na fila!")
    clientes_na_fila = []
#realiza a iteração pelos clientes na fila e cria objetos ClienteResponse para cada um deles
    for posicao, cliente in enumerate(fila_de_clientes, start=1):
        clientes_na_fila.append(ClienteResponse(
            cliente_id=cliente.cliente_id,
            nome_cliente=cliente.nome_cliente,
            tipo_atendimento=cliente.tipo_atendimento,
            data_chegada=cliente.data_chegada,
            posicao_na_fila=posicao,
            atendido=cliente.atendido
        ))
#reotrna a lista de clientes na fila com as informações 
    return clientes_na_fila

#(TÓPICO 02)
#foi criado um endpoint para retornar os cliente na fila pelo id e definido uma rota/fila pelo id
@app.get("/fila/{cliente_id}", response_model=ClienteResponse) 
def retornar_cliente_da_fila(cliente_id: int):
#procura o cliente na fila conforme o id informado
    cliente = next((c for c in fila_de_clientes if c.cliente_id == cliente_id), None)
    if cliente is None:
#se o cliente não for encontrado, retornar mensagem de erro
        raise HTTPException(status_code=404, detail="Cliente não encontrado na fila!")
#calcula a posição do cliente
    posicao_cliente = fila_de_clientes.index(cliente) + 1

# Cria um objeto ClienteResponse com informações detalhadas sobre o cliente
    return ClienteResponse(
        cliente_id=cliente.cliente_id,
        nome_cliente=cliente.nome_cliente,
        tipo_atendimento=cliente.tipo_atendimento,
        data_chegada=cliente.data_chegada,
        posicao_na_fila=posicao_cliente,
        atendido=cliente.atendido 
    )

#foi definido uma classe Novo Cliente 
class NovoCliente(BaseModel):
    nome_cliente: str #nome do cliente a ser adicionado 
    tipo_atendimento: str #o tipo de atendimento do novo cliente

#(TÓPICO 03)
#foi criado um endpoint para adicionar novo cliente  na fila
@app.post("/fila", response_model=ClienteResponse)
async def adicionar_cliente_na_fila(cliente: NovoCliente):
    global contador_id 
    contador_id += 1  
    id_cliente = contador_id
 #verifica se o campo nome_cliente tem no maximo 20 caracteres
    if len(cliente.nome_cliente) > 20:
        raise HTTPException(status_code=400, detail="O campo 'nome_cliente' deve ter no máximo 20 caracteres")
#verifica se no campo tipo_atendimento foi informado os valores corretos
    if cliente.tipo_atendimento not in ['N', 'P']:
        raise HTTPException(status_code=400, detail="O campo 'tipo_atendimento' só aceita os valores 'N' ou 'P")

# Cria um novo objeto Cliente com os dados do novo cliente e adiciona à fila
    novo_cliente = Cliente(cliente_id=id_cliente,nome_cliente=cliente.nome_cliente, tipo_atendimento=cliente.tipo_atendimento)
    fila_de_clientes.append(novo_cliente)

 # Retorna informações detalhadas sobre o cliente adicionado à fila
    return ClienteResponse(
        cliente_id=novo_cliente.cliente_id,
        nome_cliente=novo_cliente.nome_cliente,
        tipo_atendimento=novo_cliente.tipo_atendimento,
        data_chegada=novo_cliente.data_chegada,
        posicao_na_fila=len(fila_de_clientes),
        atendido=novo_cliente.atendido
    )


#(TÓPICO 04)
#criado um endpoint para atualizar a fila e marcar o primeiro cliente com atendido
@app.put("/fila")
async def atualizar_fila():
    if not fila_de_clientes:
#se a fila estiver vazia, retorna uma mensagem informando que não tem ninguém na fila
        raise HTTPException(status_code=200, detail="Não tem ninguém na fila!")

    if fila_de_clientes[0].atendido == False:
        #se o primeiro cliente estiver como false, ou seja não atendido, marcar como atendido (true)
        fila_de_clientes[0].atendido = True

#o restante do clientes fica como false, ou seja, não atendido
    for i in range(1, len(fila_de_clientes)):
        fila_de_clientes[i].atendido = False

#retorna mensagem que a fila for percorrida e atualizada com sucesso
    return {"message": "Fila atualizada com sucesso!"}

#(TÓPICO 05)
#endpoint para remover clientes da fila e atualizar a posição do restante
@app.delete("/fila/{cliente_id}")
async def remover_cliente_da_fila(cliente_id: int):
#procura o cliente na fila com base no id especificado
    cliente = next((c for c in fila_de_clientes if c.cliente_id == cliente_id), None)
#caso o id especificado não pertença a um cliente vai retornar essa mensagem de cliente não encontrado
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado na fila!")

#remove o cliente da fila
    fila_de_clientes.remove(cliente)

    # Atualiza a posição dos demais clientes na fila
    for i, cliente_na_fila in enumerate(fila_de_clientes, start=1):
        cliente_na_fila.posicao_na_fila = i

# Retorna uma mensagem indicando o sucesso da remoção do cliente
    return {"message": "Cliente removido com sucesso"}