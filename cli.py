import argparse
from package_comparator import fetch_packages, save_packages_to_file, load_packages_from_file, compare_packages
import os
import json


def main():
    # Создаем парсер аргументов командной строки
    parser = argparse.ArgumentParser(
        description="Compare binary packages between sisyphus and p10 branches.")

    # Добавляем аргументы
    parser.add_argument("--arch", type=str, default="aarch64",
                        help="Architecture to compare (e.g., aarch64, x86_64).")
    parser.add_argument("--fetch", action="store_true",
                        help="Fetch packages from the API and save them to files.")

    args = parser.parse_args()

    if args.fetch:
        # Получаем пакеты для обеих веток
        sisyphus_packages = fetch_packages("sisyphus", args.arch)
        p10_packages = fetch_packages("p10", args.arch)

        # Сохраняем пакеты в файлы
        save_packages_to_file("sisyphus", args.arch, sisyphus_packages)
        save_packages_to_file("p10", args.arch, p10_packages)

    # Загружаем пакеты из файлов
    sisyphus_packages = load_packages_from_file("sisyphus", args.arch)
    p10_packages = load_packages_from_file("p10", args.arch)

    # Сравниваем пакеты
    comparison_result = compare_packages(sisyphus_packages, p10_packages)

    # Создаем папку для результатов сравнения, если она не существует
    os.makedirs("comparison_results", exist_ok=True)

    # Сохраняем полный результат сравнения в файл
    comparison_filename = os.path.join(
        "comparison_results", f"comparison_result_{args.arch}.json")
    with open(comparison_filename, "w") as result_file:
        json.dump(comparison_result, result_file, indent=2)
        print(
            f"Полные результаты сравнения для {args.arch} сохранены в {comparison_filename}")

    # Сохраняем каждый критерий сравнения в отдельный файл
    only_in_p10_filename = os.path.join(
        "comparison_results", f"comparison_result_only_in_p10_{args.arch}.json")
    with open(only_in_p10_filename, "w") as result_file:
        json.dump(comparison_result["only_in_p10"], result_file, indent=2)
        print(
            f"Результаты сравнения (только в p10) для {args.arch} сохранены в {only_in_p10_filename}")

    only_in_sisyphus_filename = os.path.join(
        "comparison_results", f"comparison_result_only_in_sisyphus_{args.arch}.json")
    with open(only_in_sisyphus_filename, "w") as result_file:
        json.dump(comparison_result["only_in_sisyphus"], result_file, indent=2)
        print(
            f"Результаты сравнения (только в sisyphus) для {args.arch} сохранены в {only_in_sisyphus_filename}")

    version_higher_in_sisyphus_filename = os.path.join(
        "comparison_results", f"comparison_result_version_higher_in_sisyphus_{args.arch}.json")
    with open(version_higher_in_sisyphus_filename, "w") as result_file:
        json.dump(
            comparison_result["version_higher_in_sisyphus"], result_file, indent=2)
        print(
            f"Результаты сравнения (более высокие версии в sisyphus) для {args.arch} сохранены в {version_higher_in_sisyphus_filename}")


if __name__ == "__main__":
    main()
