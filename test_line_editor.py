import json
import os

import pytest

from line_editor import LineEditor


@pytest.fixture
def config_file(tmp_path):
    config_path = tmp_path / 'test_config.txt'
    with open(config_path, 'w') as file:
        file.write('Line 1 content\n')
        file.write('Line 2 content\n')
        file.write('Line 3 content\n')

    yield config_path


@pytest.fixture
def new_config_file(tmp_path):
    new_location = tmp_path / 'new_location'
    new_location.mkdir()

    config_path = new_location / 'config.txt'
    with open(config_path, 'w') as file:
        file.write('New Line 1 content\n')
        file.write('New Line 2 content\n')
        file.write('New Line 3 content\n')

    yield config_path


@pytest.fixture
def config_backup_file(tmp_path):
    config_path = tmp_path / 'test_config.txt'
    with open(config_path, 'w') as file:
        file.write('Line 1 content\n')
        file.write('Line 2 backup\n')
        file.write('Line 3 content\n')

    yield config_path


@pytest.fixture
def manifest_file(tmp_path):
    manifest_path = tmp_path / 'test_manifest.json'
    manifest = {
        'new_path': str(tmp_path / 'new_location' / 'config.txt'),
        'permissions': '0644',
        'owner': '1001',
        'group': '1001'
    }
    with open(manifest_path, 'w') as file:
        json.dump(manifest, file)

    yield manifest_path


def test_no_config_file(manifest_file):
    with pytest.raises(FileNotFoundError):
        LineEditor('./nonexistent_config.txt', manifest_file)


def test_no_manifest_file(config_file):
    with pytest.raises(FileNotFoundError):
        LineEditor(config_file, './nonexistent_manifest.json')


def test_no_backup_file(config_file, manifest_file):
    editor = LineEditor(config_file, manifest_file)

    with pytest.raises(FileNotFoundError):
        editor.restore_backup()


def test_restore_backup(config_file, config_backup_file, manifest_file, new_config_file, monkeypatch):
    editor = LineEditor(config_file, manifest_file)

    def mock_chown(path, owner, group):
        pass

    monkeypatch.setattr(os, 'chown', mock_chown)

    editor.edit_line(2, "Modified line content")
    editor.restore_backup()

    with open(config_file, 'r') as file:
        lines = file.readlines()

    assert lines[1].strip() == "Line 2 backup"


def test_edit_line(config_file, manifest_file):
    editor = LineEditor(config_file, manifest_file)

    editor.edit_line(2, "New line content")

    with open(config_file, 'r') as file:
        lines = file.readlines()

    assert lines[1].strip() == "New line content"


def test_edit_line_invalid_line_num(config_file, manifest_file):
    editor = LineEditor(config_file, manifest_file)

    with pytest.raises(ValueError):
        editor.edit_line(10, "Invalid line content")
