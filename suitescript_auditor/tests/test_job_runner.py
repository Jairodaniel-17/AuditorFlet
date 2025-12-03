import json
from datetime import datetime

from suitescript_auditor.core.jobs.models import Job, JobSettings, JobSourceType, JobStatus, JobStage
from suitescript_auditor.core.jobs.runner import JobRunner


SAMPLE_JS = """/**
 * @NApiVersion 2.x
 * @NScriptType UserEventScript
 */
define(['N/record', 'N/search'], function(record, search) {
    function afterSubmit(context) {
        var creds = { token: "abcd1234ABCD5678" };
        var ignore = { ignoreMandatoryFields: true };
        for (var i = 0; i < 2; i++) {
            record.load({type: 'salesorder', id: i});
        }
        search.create({type: 'salesorder'}).run().each(function(){});
        return true;
    }

    return { afterSubmit: afterSubmit };
});
"""


def test_job_runner_generates_docs(tmp_path):
    project = tmp_path / "repo"
    project.mkdir()
    (project / "script.js").write_text(SAMPLE_JS, encoding="utf-8")

    runner = JobRunner()
    job = Job(
        id="job1",
        project_name="Demo Project",
        source=project,
        source_type=JobSourceType.REPOSITORY,
        created_at=datetime.utcnow(),
        settings=JobSettings(llm_mode=True),
    )

    result = runner.run(job)

    assert job.status == JobStatus.COMPLETED
    assert job.stage == JobStage.COMPLETE
    assert result.docs_path.exists()
    index_data = json.loads((result.docs_path / "index.json").read_text(encoding="utf-8"))
    assert index_data["project"]["name"] == "Demo Project"
    assert result.artifacts
    assert (result.docs_path / "artifacts/Docs.zip").exists()
