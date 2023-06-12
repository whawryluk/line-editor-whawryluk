import os
import json
import shutil
import argparse
import logging


class LineEditor:
    """A class used to edit specific lines in a text file and apply changes based on a manifest file.

    Attributes
    ----------
    file_path : str
        The path to the file to be edited.
    manifest_path : str
        The path to the manifest file.
    backup_path : str
        The path to the backup file.
    """

    def __init__(self, file_path, manifest_path):
        """Initializes a 'LineEditor' instance.

        Parameters
        ----------
        file_path : str
            The path to the file to be edited.

        manifest_path : str
            The path to the manifest file containing metadata.

        Raises
        ------
        FileNotFoundError
            If the specified file_path or manifest_path does not exist.
        """

        self.file_path = file_path
        self.manifest_path = manifest_path
        self.backup_path = f"{file_path}.backup"
        self.setup_logging()

        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Configuration file not found at {self.file_path}")

        if not os.path.exists(self.manifest_path):
            raise FileNotFoundError(f"Manifest file not found at {self.manifest_path}")

        with open(self.manifest_path, 'r') as file:
            manifest = json.load(file)
        self.new_path = manifest['new_path']

    def setup_logging(self):
        """Creates a backup of the file."""

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def create_backup(self):
        """Creates a backup of the config file."""

        shutil.copyfile(self.file_path, self.backup_path)
        logging.info("Created a backup of the file.")

    def restore_backup(self):
        """Restores the config file from a backup file."""

        if os.path.exists(self.backup_path):
            shutil.copy2(self.backup_path, self.file_path)
            logging.info(f"Restored the file {self.file_path} from the backup file {self.backup_path}.")

            if self.new_path is not None:
                shutil.copy2(self.backup_path, self.new_path)
                logging.info(f"Restored the file {self.new_path} from the backup file {self.backup_path}.")

        else:
            raise FileNotFoundError(f"No backup file found at {self.backup_path}")

    def edit_line(self, line_num, new_content):
        """Edits a specific line in the file.

        Parameters
        ----------
        line_num : int
            The line number to be edited.
        new_content : str
            The new content for the line.
        """

        self.create_backup()
        with open(self.file_path, 'r') as file:
            lines = file.readlines()

        if not 1 <= line_num <= len(lines):
            raise ValueError(f"{line_num} is a invalid line number. The file has {len(lines)} lines.")

        lines[line_num - 1] = new_content + '\n'

        with open(self.file_path, 'w') as file:
            file.writelines(lines)

        logging.info(f"Edited line {line_num} with new content: {new_content}")
        self.apply_manifest()

    def apply_manifest(self):
        """Applies changes from the manifest file to the file."""

        try:
            with open(self.manifest_path, 'r') as file:
                manifest = json.load(file)

            self.new_path = manifest['new_path']
            shutil.copyfile(self.file_path, self.new_path)
            os.chmod(self.new_path, int(manifest['permissions'], 8))
            os.chown(self.new_path, int(manifest['owner']), int(manifest['group']))
            logging.info(f"Applied manifest to the file. New location: {self.new_path}")

        except FileNotFoundError as e:
            logging.error(f"Error occurred: {e} not found in {self.manifest_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Edit a specific line in a file.")
    parser.add_argument('--restore-backup', action='store_true', help="Undo changed line")
    parser.add_argument('line_num', type=int, nargs='?', default=None, help='Line number to edit')
    parser.add_argument('new_content', type=str, nargs='?', default=None, help='New line contents')
    args = parser.parse_args()

    try:
        editor = LineEditor('./config.txt', './manifest.json')
        if args.restore_backup:
            editor.restore_backup()
        else:
            if args.line_num is None or args.new_content is None:
                raise ValueError("Both line number and new content must be provided.")
            editor.edit_line(args.line_num, args.new_content)

    except (FileNotFoundError, ValueError) as e:
        logging.error(f"Error occurred: {e}")
