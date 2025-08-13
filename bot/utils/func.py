import os

def checkForCommand(s: list):
    if s[0] == "/" or s[0] == "!":
        return True
    else: return False

def cmdnoprefandargs(s: list):
    del s[0]; c = "".join(s).split(" ")[0]
    return c

def list_all_files(directory):
    """
    Выводит все файлы в указанной директории и её поддиректориях
    
    :param directory: Путь к директории для поиска
    :return: Список полных путей ко всем файлам
    """
    all_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            all_files.append(full_path)
    
    return [f for _, _, files in os.walk(directory) for f in files]