import os
import json
import shutil
import argparse
import logging


class LineEditor:
    def __init__(self, file_path, manifest_path):
        self.file_path = file_path
        self.manifest_path = manifest_path
        self.backup_path = f"{file_path}.backup"
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def create_backup(self):
        shutil.copyfile(self.file_path, self.backup_path)
        logging.info("Created a backup of the file.")

    def restore_backup(self):
        if os.path.exists(self.backup_path):
            shutil.copyfile(self.backup_path, self.file_path)
            logging.info(f"Restored the file {self.file_path} from the backup file {self.backup_path}.")
        else:
            raise FileNotFoundError(f"No backup file found at {self.backup_path}")

    def edit_line(self, line_num, new_content):
        self.create_backup()
        with open(self.file_path, 'r') as file:
            lines = file.readlines()

        if not 1 <= line_num <= len(lines):
            raise ValueError(f"Invalid line number. The file has {len(lines)} lines.")

        try:
            lines[line_num - 1] = new_content + '\n'
            with open(self.file_path, 'w') as file:
                file.writelines(lines)

            logging.info(f"Edited line {line_num} with new content: {new_content}")
            self.apply_manifest()

        except Exception as e:
            logging.error(f"Error occurred: {e}")
            self.restore_backup()

    def apply_manifest(self):
        try:
            with open(self.manifest_path, 'r') as file:
                manifest = json.load(file)

            new_path = manifest['new_path']
            shutil.copyfile(self.file_path, new_path)
            os.chmod(new_path, int(manifest['permissions'], 8))
            os.chown(new_path, int(manifest['owner']), int(manifest['group']))
            logging.info(f"Applied manifest to the file. New location: {new_path}")

        except Exception as e:
            logging.error(f"Error occurred: {e} not found in {self.manifest_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Edit a specific line in a file.")
    parser.add_argument('--reverse', action='store_true', help="Undo changed line")
    parser.add_argument('line_num', type=int, nargs='?', default=0, help='Line number to edit')
    parser.add_argument('new_content', type=str, nargs='?', default='', help='New line contents')
    args = parser.parse_args()

    editor = LineEditor('./config.txt', './manifest.json')

    try:
        if not os.path.exists(editor.file_path):
            raise FileNotFoundError(f"Configuration file not found at {editor.file_path}")

        if not os.path.exists(editor.manifest_path):
            raise FileNotFoundError(f"Manifest file not found at {editor.manifest_path}")

        if args.reverse:
            editor.restore_backup()
        else:
            editor.edit_line(args.line_num, args.new_content)

    except FileNotFoundError as e:
        logging.error(f"Error occurred: {e}")
