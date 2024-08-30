import os
import json
import requests
from rpm import labelCompare  # Импортируем функцию для сравнения версий из rpm библиотеки

API_URL = "https://rdb.altlinux.org/api/export/branch_binary_packages"

def fetch_packages(branch, arch):
    """
    Функция для получения списка пакетов для указанной ветки и архитектуры.
    """
    try:
        response = requests.get(f"{API_URL}/{branch}", params={"arch": arch})
        response.raise_for_status()
        return response.json().get("packages", [])
    except requests.RequestException as e:
        print(f"Ошибка запроса к API: {e}")
        return []

def save_packages_to_file(branch, arch, packages):
    """
    Функция для сохранения списка пакетов в файл.
    """
    filename = os.path.join("data", f"{branch}_{arch}_packages.json")
    with open(filename, "w") as file:
        json.dump(packages, file, indent=2)
    print(f"Сохранено: {filename}")

def load_packages_from_file(branch, arch):
    """
    Функция для загрузки списка пакетов из последнего файла.
    """
    filename = os.path.join("data", f"{branch}_{arch}_packages.json")
    if not os.path.exists(filename):
        print(f"Нет доступного файла для загрузки пакетов из ветки {branch} для архитектуры {arch}")
        return []

    with open(filename, "r") as file:
        print(f"Загружен файл: {filename}")
        return json.load(file)

def compare_packages(sisyphus_packages, p10_packages):
    """
    Функция для сравнения списков пакетов между ветками sisyphus и p10.
    Возвращает JSON с информацией о различиях.
    """
    result = {
        "only_in_p10": [],
        "only_in_sisyphus": [],
        "version_higher_in_sisyphus": []
    }

    # Преобразуем списки пакетов в словари для быстрого доступа
    sisyphus_dict = {pkg["name"]: pkg for pkg in sisyphus_packages}
    p10_dict = {pkg["name"]: pkg for pkg in p10_packages}

    # Найти пакеты, которые есть в p10, но отсутствуют в sisyphus
    for name, pkg in p10_dict.items():
        if name not in sisyphus_dict:
            result["only_in_p10"].append({
                "name": pkg["name"],
                "epoch": pkg["epoch"],
                "version": pkg["version"],
                "release": pkg["release"],
                "arch": pkg["arch"]
            })

    # Найти пакеты, которые есть в sisyphus, но отсутствуют в p10
    for name, pkg in sisyphus_dict.items():
        if name not in p10_dict:
            result["only_in_sisyphus"].append({
                "name": pkg["name"],
                "epoch": pkg["epoch"],
                "version": pkg["version"],
                "release": pkg["release"],
                "arch": pkg["arch"]
            })

    # Найти пакеты, у которых version-release больше в sisyphus, чем в p10
    for name, pkg in sisyphus_dict.items():
        if name in p10_dict:
            sisyphus_version = (pkg['epoch'], pkg['version'], pkg['release'])
            p10_version = (p10_dict[name]['epoch'], p10_dict[name]['version'], p10_dict[name]['release'])
            if labelCompare(sisyphus_version, p10_version) > 0:
                result["version_higher_in_sisyphus"].append({
                    "name": pkg["name"],
                    "epoch": pkg["epoch"],
                    "version": pkg["version"],
                    "release": pkg["release"],
                    "arch": pkg["arch"]
                })

    return result

def main():
    architectures = ["aarch64", "x86_64", "i586", "armh"]  # Добавьте все архитектуры

    for arch in architectures:
        # Получаем пакеты для обеих веток
        sisyphus_packages = fetch_packages("sisyphus", arch)
        p10_packages = fetch_packages("p10", arch)

        # Сохраняем пакеты в файлы
        save_packages_to_file("sisyphus", arch, sisyphus_packages)
        save_packages_to_file("p10", arch, p10_packages)

        # Загружаем пакеты из файлов
        sisyphus_packages = load_packages_from_file("sisyphus", arch)
        p10_packages = load_packages_from_file("p10", arch)

        # Сравниваем пакеты
        comparison_result = compare_packages(sisyphus_packages, p10_packages)

        # Сохраняем результат сравнения в файл
        comparison_filename = os.path.join("comparison_results", f"comparison_result_{arch}.json")
        with open(comparison_filename, "w") as result_file:
            json.dump(comparison_result, result_file, indent=2)
            print(f"Результаты сравнения для {arch} сохранены в {comparison_filename}")

if __name__ == "__main__":
    main()
