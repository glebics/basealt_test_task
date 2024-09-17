import os
import json
import requests

API_URL = "https://rdb.altlinux.org/api/export/branch_binary_packages"


def fetch_packages(branch, arch):
    """
    Функция для получения списка пакетов для указанной ветки и архитектуры.
    """
    try:
        response = requests.get(f"{API_URL}/{branch}", params={"arch": arch})
        response.raise_for_status()
        packages = response.json().get("packages", [])
        if not packages:
            print(f"Нет данных для ветки {branch} и архитектуры {arch}.")
        return packages
    except requests.RequestException as e:
        print(f"Ошибка запроса к API: {e}")
        return []


def create_directory(directory):
    """
    Функция для создания директории, если она не существует.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def save_packages_to_file(branch, arch, packages):
    """
    Функция для сохранения списка пакетов в файл.
    """
    if not packages:
        print(
            f"Нет пакетов для сохранения для ветки {branch} и архитектуры {arch}.")
        return

    # Создаем директорию, если она не существует
    create_directory("data")

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
        print(
            f"Нет доступного файла для загрузки пакетов из ветки {branch} для архитектуры {arch}")
        return []

    with open(filename, "r") as file:
        print(f"Загружен файл: {filename}")
        return json.load(file)


def rpm_compare_versions(version1, version2):
    """
    Функция для сравнения двух версий RPM в формате (epoch, version, release).
    Возвращает 1, если version1 > version2, -1 если version1 < version2, и 0 если равны.
    """
    def split_version(version):
        # Разделяем версии на части и приводим каждую часть к строке
        parts = [str(part) for part in version.split(".")]
        return tuple(parts)

    epoch1, ver1, rel1 = version1
    epoch2, ver2, rel2 = version2

    # Сравниваем epoch как строки
    if str(epoch1) != str(epoch2):
        return 1 if str(epoch1) > str(epoch2) else -1

    # Сравниваем version
    ver1_parts = split_version(ver1)
    ver2_parts = split_version(ver2)
    if ver1_parts != ver2_parts:
        return 1 if ver1_parts > ver2_parts else -1

    # Сравниваем release
    rel1_parts = split_version(rel1)
    rel2_parts = split_version(rel2)
    if rel1_parts != rel2_parts:
        return 1 if rel1_parts > rel2_parts else -1

    return 0


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
            p10_version = (p10_dict[name]['epoch'], p10_dict[name]
                           ['version'], p10_dict[name]['release'])
            if rpm_compare_versions(sisyphus_version, p10_version) > 0:
                result["version_higher_in_sisyphus"].append({
                    "name": pkg["name"],
                    "epoch": pkg["epoch"],
                    "version": pkg["version"],
                    "release": pkg["release"],
                    "arch": pkg["arch"]
                })

    return result


def main():
    architectures = ["aarch64", "armh", "mipsel", "ppc64le", "x86_64",
                     "i586", "s390x", "riscv64", "sparc64"]  # Полный список архитектур

    # Создаем директорию для результатов сравнения, если она не существует
    create_directory("comparison_results")

    for arch in architectures:
        # Получаем пакеты для обеих веток
        sisyphus_packages = fetch_packages("sisyphus", arch)
        p10_packages = fetch_packages("p10", arch)

        # Проверяем, есть ли данные для обеих веток
        if not sisyphus_packages or not p10_packages:
            print(
                f"Нет данных для архитектуры {arch}. Пропуск создания файлов.")
            continue

        # Сохраняем пакеты в файлы
        save_packages_to_file("sisyphus", arch, sisyphus_packages)
        save_packages_to_file("p10", arch, p10_packages)

        # Загружаем пакеты из файлов
        sisyphus_packages = load_packages_from_file("sisyphus", arch)
        p10_packages = load_packages_from_file("p10", arch)

        # Проверяем, есть ли данные после загрузки из файлов
        if not sisyphus_packages or not p10_packages:
            print(
                f"Нет данных для архитектуры {arch} после загрузки файлов. Пропуск создания файлов.")
            continue

        # Сравниваем пакеты
        comparison_result = compare_packages(sisyphus_packages, p10_packages)

        # Сохраняем результат сравнения в файл
        comparison_filename = os.path.join(
            "comparison_results", f"comparison_result_{arch}.json")
        with open(comparison_filename, "w") as result_file:
            json.dump(comparison_result, result_file, indent=2)
            print(
                f"Результаты сравнения для {arch} сохранены в {comparison_filename}")


if __name__ == "__main__":
    main()
