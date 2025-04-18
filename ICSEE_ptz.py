from onvif import ONVIFCamera
import json
import os

CONFIG_FILE = "cameras.json"

def carregar_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def salvar_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def conectar_camera(info):
    camera = ONVIFCamera(info['ip'], int(info['port']), info['user'], info['password'])
    media_service = camera.create_media_service()
    ptz_service = camera.create_ptz_service()
    profile = media_service.GetProfiles()[0]
    return ptz_service, profile

def listar_presets(ptz_service, profile):
    presets = ptz_service.GetPresets({'ProfileToken': profile.token})
    if not presets:
        print("Nenhum preset encontrado.")
    for p in presets:
        print(f"Preset: {p.Name} | Token: {p.token}")

def criar_preset(ptz_service, profile):
    name = input("Nome do novo preset: ")
    result = ptz_service.SetPreset({
        'ProfileToken': profile.token,
        'PresetName': name
    })
    print(f"Preset salvo com token: {result}")

def ir_para_preset(ptz_service, profile):
    token = input("Token do preset: ")
    ptz_service.GotoPreset({
        'ProfileToken': profile.token,
        'PresetToken': token
    })
    print("Movendo para o preset...")

def remover_preset(ptz_service, profile):
    token = input("Token do preset a remover: ")
    ptz_service.RemovePreset({
        'ProfileToken': profile.token,
        'PresetToken': token
    })
    print("Preset removido.")

def remover_todos_presets(ptz_service, profile):
    presets = ptz_service.GetPresets({'ProfileToken': profile.token})
    for p in presets:
        ptz_service.RemovePreset({
            'ProfileToken': profile.token,
            'PresetToken': p.token
        })
        print(f"Removido preset: {p.Name}")
    print("Todos os presets foram removidos.")

def menu_camera(camera_info):
    ptz_service, profile = conectar_camera(camera_info)

    while True:
        print(f"\n--- Menu da câmera {camera_info['nome']} ({camera_info['ip']}) ---")
        print("1 - Listar presets")
        print("2 - Criar novo preset")
        print("3 - Ir para preset")
        print("4 - Remover preset")
        print("5 - Remover TODOS os presets")
        print("6 - Voltar")
        op = input("Escolha uma opção: ")

        if op == '1':
            listar_presets(ptz_service, profile)
        elif op == '2':
            criar_preset(ptz_service, profile)
        elif op == '3':
            ir_para_preset(ptz_service, profile)
        elif op == '4':
            remover_preset(ptz_service, profile)
        elif op == '5':
            remover_todos_presets(ptz_service, profile)
        elif op == '6':
            break
        else:
            print("Opção inválida.")

def menu_principal():
    config = carregar_config()

    while True:
        print("\n===== Menu Principal =====")
        print("Câmeras disponíveis:")
        for i, nome in enumerate(config):
            print(f"{i+1} - {nome}")
        print("a - Adicionar câmera")
        print("r - Remover câmera")
        print("s - Sair")

        escolha = input("Escolha uma opção: ")

        if escolha.isdigit():
            index = int(escolha) - 1
            if 0 <= index < len(config):
                nome = list(config.keys())[index]
                menu_camera(config[nome])
        elif escolha == 'a':
            nome = input("Nome da câmera: ")
            ip = input("IP da câmera: ")
            port = input("Porta (ex: 8899): ")
            user = input("Usuário: ")
            password = input("Senha: ")
            config[nome] = {
                "nome": nome,
                "ip": ip,
                "port": port,
                "user": user,
                "password": password
            }
            salvar_config(config)
            print("Câmera adicionada.")
        elif escolha == 'r':
            nome = input("Nome da câmera a remover: ")
            if nome in config:
                del config[nome]
                salvar_config(config)
                print("Câmera removida.")
            else:
                print("Câmera não encontrada.")
        elif escolha == 's':
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    menu_principal()
