
# ALT Linux Package Comparator

This project is a Python-based CLI utility designed to compare binary packages between two branches (`sisyphus` and `p10`) from the ALT Linux repository. The utility fetches package data for various architectures, compares them according to specific criteria, and outputs the results in JSON format.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Fetching Packages](#fetching-packages)
  - [Comparing Packages](#comparing-packages)
- [Output Files](#output-files)
- [Author](#author)

## Installation

### Prerequisites

- Python 3.8 or higher
- Linux-based operating system (ALT Linux version 10 recommended)
- Git

### Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/glebics/basealt_test_task.git
    cd altlinux_package_comparator
    ```

2. **Install dependencies:**

    Make sure you have `pip` installed. Run the following command to install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Fetching Packages

To fetch package data from both branches (`sisyphus` and `p10`) for a specific architecture and save them locally, use the following command:

```bash
python3 cli.py --arch aarch64 --fetch
```

- **`--arch`**: Specifies the architecture to compare (e.g., `aarch64`, `x86_64`, `i586`, `armh`).
- **`--fetch`**: Fetches the package data from the API and saves them to JSON files.

### Comparing Packages

After fetching the package data, you can run the comparison. The comparison is done automatically after fetching if you include the `--fetch` flag, or you can run it separately:

```bash
python3 cli.py --arch aarch64
```

This command will compare packages for the specified architecture (`aarch64` in this case) and save the results in JSON files.

### Output Files

The CLI utility will generate the following output files in the `comparison_results` directory:

1. **`comparison_result_{arch}.json`**: Contains the full comparison results for all criteria.
2. **`comparison_result_only_in_p10_{arch}.json`**: Contains packages that are present in `p10` but not in `sisyphus`.
3. **`comparison_result_only_in_sisyphus_{arch}.json`**: Contains packages that are present in `sisyphus` but not in `p10`.
4. **`comparison_result_version_higher_in_sisyphus_{arch}.json`**: Contains packages where the version in `sisyphus` is higher than in `p10`.

### Example Commands

- **Fetch and Compare Packages for `aarch64`:**

    ```bash
    python3 cli.py --arch aarch64 --fetch
    ```

- **Compare Packages for `x86_64` (assuming data is already fetched):**

    ```bash
    python3 cli.py --arch x86_64
    ```

## Author

This program was developed by **Rakhimzhanov Gleb** specifically for **BaseALT**.

---

If you have any questions or feedback, feel free to reach out!
