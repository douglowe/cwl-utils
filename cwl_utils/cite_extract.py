#!/usr/bin/env python3
import sys
import cwl_utils.parser_v1_0 as cwl
from typing import Generator, Union

ProcessType = Union[cwl.Workflow, cwl.CommandLineTool, cwl.ExpressionTool]


def main() -> int:
    top = cwl.load_document(sys.argv[1])
    traverse(top)
    return 0


def extract_software_packages(process: ProcessType):
    for req in extract_software_reqs(process):
        print(process.id)
        process_software_requirement(req)


def extract_software_reqs(
    process: ProcessType,
) -> Generator[cwl.SoftwareRequirement, None, None]:
    if process.requirements:
        for req in process.requirements:
            if isinstance(req, cwl.SoftwareRequirement):
                yield req
    if process.hints:
        for req in process.hints:
            if req["class"] == "SoftwareRequirement":
                yield cwl.load_field(
                    req,
                    cwl.SoftwareRequirementLoader,
                    process.id if process.id else "",
                    process.loadingOptions,
                )


def process_software_requirement(req: cwl.SoftwareRequirement):
    for package in req.packages:
        print(
            "Package: {}, version: {}, specs: {}".format(
                package.package, package.version, package.specs
            )
        )


def traverse(process: ProcessType):
    extract_software_packages(process)
    if isinstance(process, cwl.Workflow):
        traverse_workflow(process)


def get_process_from_step(step: cwl.WorkflowStep):
    if isinstance(step.run, str):
        return cwl.load_document(step.run)
    return step.run


def traverse_workflow(workflow: cwl.Workflow):
    for step in workflow.steps:
        extract_software_packages(step)
        traverse(get_process_from_step(step))


if __name__ == "__main__":
    sys.exit(main())
