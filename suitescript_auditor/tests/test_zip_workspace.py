import zipfile

from suitescript_auditor.core.io import workspace, zip_handler


def test_zip_handler_extracts_files(tmp_path):
    zip_path = tmp_path / "project.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("folder/file.txt", "content")
    target = tmp_path / "output"
    zip_handler.extract(zip_path, target)
    assert (target / "folder" / "file.txt").read_text() == "content"


def test_workspace_manager(tmp_path):
    manager = workspace.WorkspaceManager()
    workdir = manager.create("job-test")
    assert workdir.exists()
    manager.cleanup("job-test")
    assert not workdir.exists()
