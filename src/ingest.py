from utils import CONFIG, SOURCE_DIR, RAW_DIR, ensure_directories, read_csv, write_csv


def ingest_files() -> None:
    ensure_directories()

    for file_name in CONFIG["required_source_files"]:
        src = SOURCE_DIR / file_name
        dst = RAW_DIR / file_name

        if not src.exists():
            raise FileNotFoundError(f"Missing source file: {src}")

        df = read_csv(src)
        write_csv(df, dst)
        print(f"Ingested {file_name} -> {dst}")
